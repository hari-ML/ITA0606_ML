import hashlib
import tempfile
from pathlib import Path
import pandas as pd

from androguard.core.apk import APK
from androguard.core.dex import DEX

try:
    from loguru import logger as _loguru_logger
    _loguru_logger.disable("androguard")
except Exception:
    pass

DANGEROUS_PERMISSIONS = {
    "SEND_SMS",
    "READ_SMS",
    "RECEIVE_SMS",
    "BIND_DEVICE_ADMIN",
    "REQUEST_INSTALL_PACKAGES",
    "SYSTEM_ALERT_WINDOW",
    "READ_CONTACTS",
    "RECORD_AUDIO",
    "ACCESS_FINE_LOCATION",
    "READ_PHONE_STATE",
}

def normalize_permission(perm_name: str) -> str:
    """Normalize Android permission name by stripping android.permission. prefix."""
    if not perm_name:
        return ""
    p = str(perm_name).strip()
    prefix = "android.permission."
    if p.startswith(prefix):
        p = p[len(prefix):]
    return p.upper()

def extract_cert_fingerprint(apk_obj: APK) -> str:
    """Extract SHA-256 fingerprint from APK signing certificates (v1/v2/v3)."""
    # Check v3 / v2 / v1 DER certificates
    for method_name in ["get_certificates_der_v3", "get_certificates_der_v2", "get_certificates_der_v1"]:
        if hasattr(apk_obj, method_name):
            try:
                der_list = getattr(apk_obj, method_name)()
                if der_list and len(der_list) > 0:
                    return hashlib.sha256(der_list[0]).hexdigest().upper()
            except Exception:
                pass

    # Fallback to get_certificates()
    try:
        certs = apk_obj.get_certificates()
        if certs and len(certs) > 0:
            c = certs[0]
            if hasattr(c, "sha256_fingerprint"):
                return c.sha256_fingerprint.replace(" ", "").upper()
            if hasattr(c, "dump"):
                return hashlib.sha256(c.dump()).hexdigest().upper()
    except Exception:
        pass

    return "UNKNOWN_OR_UNSIGNED"

def extract_apk_data(apk_input, is_bytes: bool = False) -> dict:
    """
    Statically extract package name, version, permissions, certificates, and API calls.
    Safely catches any corrupted or invalid APK error without crashing.
    """
    tmp_path: Path | None = None
    try:
        if is_bytes:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".apk")
            tmp_file.write(apk_input)
            tmp_file.close()
            target_path = Path(tmp_file.name)
            tmp_path = target_path
        else:
            target_path = Path(apk_input)

        if not target_path.exists() or target_path.stat().st_size == 0:
            return {"success": False, "error": "APK file is empty or does not exist."}

        file_size_bytes = target_path.stat().st_size
        if file_size_bytes >= 1024 * 1024:
            file_size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            file_size_str = f"{file_size_bytes / 1024:.1f} KB"

        # Fast static parsing of APK manifest and bytecode (no slow whole-program XREF)
        a = APK(str(target_path))
        if a is None or not a.is_valid_APK():
            return {"success": False, "error": "Failed to parse APK manifest. The file may be corrupt or not a valid Android APK."}

        package_name = str(a.get_package() or "Unknown")
        version_name = str(a.get_androidversion_name() or "Unknown")
        version_code = str(a.get_androidversion_code() or "Unknown")
        min_sdk = str(a.get_min_sdk_version() or "N/A")
        target_sdk = str(a.get_target_sdk_version() or "N/A")

        activities_count = len(a.get_activities() or [])
        services_count = len(a.get_services() or [])
        receivers_count = len(a.get_receivers() or [])
        providers_count = len(a.get_providers() or [])

        # Extract requested permissions
        raw_perms = a.get_permissions() or []
        normalized_perms = {normalize_permission(p) for p in raw_perms if p}
        
        # Identify dangerous permissions
        danger_found = sorted(list(normalized_perms.intersection(DANGEROUS_PERMISSIONS)))

        # Extract certificate SHA-256
        cert_sha256 = extract_cert_fingerprint(a)

        # Fast extraction of API calls, classes, and strings from DEX bytecode
        dex_methods = set()
        dex_classes = set()
        dex_strings = set()

        all_dex_list = list(a.get_all_dex())
        dex_count = len(all_dex_list)

        for dex_bytes in all_dex_list:
            try:
                d = DEX(dex_bytes)
                for m in d.get_methods():
                    m_name = m.get_name()
                    if m_name:
                        dex_methods.add(m_name)
                    cls_name = m.get_class_name()
                    if cls_name:
                        dex_classes.add(cls_name)
                        clean_cls = cls_name.lstrip("L").rstrip(";").replace("/", ".")
                        dex_classes.add(clean_cls)
                for s in d.get_strings():
                    if s:
                        dex_strings.add(str(s))
            except Exception:
                pass

        return {
            "success": True,
            "package_name": package_name,
            "version_name": version_name,
            "version_code": version_code,
            "file_size_bytes": file_size_bytes,
            "file_size_str": file_size_str,
            "min_sdk": min_sdk,
            "target_sdk": target_sdk,
            "activities_count": activities_count,
            "services_count": services_count,
            "receivers_count": receivers_count,
            "providers_count": providers_count,
            "dex_count": dex_count,
            "permissions": normalized_perms,
            "requested_perms_count": len(normalized_perms),
            "dangerous_permissions": danger_found,
            "cert_sha256": cert_sha256,
            "dex_methods": dex_methods,
            "dex_classes": dex_classes,
            "dex_strings": dex_strings,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Corrupt or invalid APK: {str(e)}"
        }
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

def build_apk_feature_vector(apk_data: dict, matchable_features: list) -> pd.DataFrame:
    """
    Builds the binary feature vector in the exact trained column order of svm_apk.pkl (missing = 0).
    """
    if not apk_data.get("success", False):
        raise ValueError("Cannot build feature vector from failed APK extraction.")

    perms = apk_data.get("permissions", set())
    dex_methods = apk_data.get("dex_methods", set())
    dex_classes = apk_data.get("dex_classes", set())
    dex_strings = apk_data.get("dex_strings", set())

    vector = {}
    for col in matchable_features:
        norm_col = normalize_permission(col)
        # 1. Match Permission
        if norm_col in perms or col in perms:
            vector[col] = 1
        # 2. Match API method or class name
        elif col in dex_methods or col in dex_classes or col in dex_strings:
            vector[col] = 1
        # 3. Match normalized Dalvik form (e.g. Ljava.lang.Class.getMethods vs Ljava/lang/Class;->getMethods)
        elif any(col in s for s in [dex_methods, dex_classes, dex_strings]):
            vector[col] = 1
        else:
            # Check partial signature match e.g. 'onServiceConnected' in methods
            pure_name = col.split(".")[-1]
            if pure_name in dex_methods:
                vector[col] = 1
            else:
                vector[col] = 0

    return pd.DataFrame([vector], columns=matchable_features)

def compare_apks(suspect_data: dict, original_data: dict, ml_risk_score: float) -> dict:
    """
    Compares suspect APK against reference APK.
    Calculates package match, cert match, permission diff, and transparent composite risk score.
    """
    suspect_pkg = suspect_data.get("package_name", "Unknown")
    orig_pkg = original_data.get("package_name", "Unknown")
    pkg_match = (suspect_pkg == orig_pkg) and (suspect_pkg != "Unknown")

    suspect_ver = suspect_data.get("version_name", "Unknown")
    orig_ver = original_data.get("version_name", "Unknown")
    ver_match = (suspect_ver == orig_ver)

    suspect_cert = suspect_data.get("cert_sha256", "UNKNOWN")
    orig_cert = original_data.get("cert_sha256", "UNKNOWN")
    
    if suspect_cert == "UNKNOWN_OR_UNSIGNED" or orig_cert == "UNKNOWN_OR_UNSIGNED":
        cert_match_status = "UNKNOWN"
        cert_penalty = 50.0
    elif suspect_cert == orig_cert:
        cert_match_status = "MATCH"
        cert_penalty = 0.0
    else:
        cert_match_status = "MISMATCH"
        cert_penalty = 100.0

    suspect_perms = set(suspect_data.get("permissions", set()))
    orig_perms = set(original_data.get("permissions", set()))

    extra_perms = sorted(list(suspect_perms - orig_perms))
    missing_perms = sorted(list(orig_perms - suspect_perms))
    shared_perms = sorted(list(suspect_perms.intersection(orig_perms)))

    # Extra dangerous permissions
    extra_dangerous = sorted(list(set(extra_perms).intersection(DANGEROUS_PERMISSIONS)))
    
    # Calculate Dangerous Perm Risk: min(100, (extra_dangerous_count / 4) * 100)
    extra_dang_count = len(extra_dangerous)
    perm_risk = min(100.0, (extra_dang_count / 4.0) * 100.0)

    # Transparent Composite Risk Formula:
    # Final Risk = 0.50 * ML_Risk + 0.30 * Dangerous_Perm_Risk + 0.20 * Cert_Mismatch_Risk
    w_ml = 0.50
    w_perm = 0.30
    w_cert = 0.20

    composite_risk = (w_ml * ml_risk_score) + (w_perm * perm_risk) + (w_cert * cert_penalty)
    composite_risk = round(min(100.0, max(0.0, composite_risk)), 1)

    return {
        "package_match": pkg_match,
        "suspect_package": suspect_pkg,
        "original_package": orig_pkg,
        "version_match": ver_match,
        "suspect_version": suspect_ver,
        "original_version": orig_ver,
        "cert_status": cert_match_status,
        "suspect_cert": suspect_cert,
        "original_cert": orig_cert,
        "extra_permissions": extra_perms,
        "missing_permissions": missing_perms,
        "shared_permissions": shared_perms,
        "extra_dangerous_permissions": extra_dangerous,
        "ml_risk_component": round(ml_risk_score, 1),
        "perm_risk_component": round(perm_risk, 1),
        "cert_risk_component": round(cert_penalty, 1),
        "final_risk_score": composite_risk,
        "formula": "Final Risk = (0.50 × ML_Risk) + (0.30 × Perm_Risk) + (0.20 × Cert_Risk)"
    }

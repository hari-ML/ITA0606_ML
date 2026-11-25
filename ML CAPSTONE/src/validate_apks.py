import os
import sys
sys.path.insert(0, os.path.abspath("."))
import joblib
import pandas as pd
from src.apk_utils import extract_apk_data, build_apk_feature_vector, DANGEROUS_PERMISSIONS

def run_apk_pipeline(apk_path, model_data):
    apk_svm = model_data["model"]
    apk_selector = model_data["selector"]
    matchable_cols = model_data["matchable_features"]
    chi2_scores = apk_selector.scores_

    # 1. Unpacking
    data = extract_apk_data(apk_path)
    if not data.get("success", False):
        return {"success": False, "error": data.get("error")}

    # 2. Features & Coverage
    X_apk = build_apk_feature_vector(data, matchable_cols)
    vec_series = X_apk.iloc[0]
    matched_features = [col for col in matchable_cols if vec_series[col] == 1]
    matched_count = len(matched_features)
    coverage_pct = (matched_count / 186.0) * 100.0
    low_coverage_flag = matched_count < 93  # < 50%

    # 3. ML Prediction & Risk Band
    X_apk_sel = apk_selector.transform(X_apk)
    ml_pred = apk_svm.predict(X_apk_sel)[0]
    ml_proba = apk_svm.predict_proba(X_apk_sel)[0, 1]
    ml_risk_pct = float(ml_proba * 100.0)

    if ml_risk_pct < 30.0:
        risk_band = "Low Risk (< 30%)"
    elif ml_risk_pct <= 70.0:
        risk_band = "Medium Risk (30% - 70%)"
    else:
        risk_band = "High Risk (> 70%)"

    # 4. Top 10 Present Features by Chi2
    present_scores = []
    for mf in matched_features:
        idx = matchable_cols.index(mf)
        score_val = float(chi2_scores[idx]) if idx < len(chi2_scores) else 0.0
        present_scores.append((mf, score_val))
    present_scores.sort(key=lambda x: x[1], reverse=True)
    top10 = present_scores[:10]

    return {
        "success": True,
        "filename": os.path.basename(apk_path),
        "package_name": data["package_name"],
        "version_name": data["version_name"],
        "file_size": data["file_size_str"],
        "min_sdk": data["min_sdk"],
        "target_sdk": data["target_sdk"],
        "activities": data["activities_count"],
        "services": data["services_count"],
        "receivers": data["receivers_count"],
        "providers": data["providers_count"],
        "dex_files": data["dex_count"],
        "cert_sha256": data["cert_sha256"][:16] + "...",
        "requested_perms": data["requested_perms_count"],
        "dangerous_perms": data["dangerous_permissions"],
        "matched_features_count": matched_count,
        "coverage_pct": round(coverage_pct, 1),
        "low_coverage_flag": low_coverage_flag,
        "ml_verdict": "MALWARE" if ml_pred == 1 else "BENIGN",
        "ml_risk_pct": round(ml_risk_pct, 2),
        "risk_band": risk_band,
        "top10_present": top10
    }

def main():
    print("=" * 70)
    print("VALIDATION SUITE: 5 REAL BENIGN APKS & EDGE CASES")
    print("=" * 70)

    model_data = joblib.load("models/svm_apk.pkl")

    test_apks = [
        "test_apks/Aegis_v3.4.3.apk",
        "test_apks/Fossify_Calendar_1.12.2.apk",
        "test_apks/Fossify_Gallery_1.14.3_arm64.apk",
        "test_apks/NewPipe_v0.29.1_fdroid.apk",
        "test_apks/NewPipe_v0.29.3.apk"
    ]

    results_table = []

    print("\n--- TEST 1 & 4: Evaluating 5 Real Modern Benign APKs ---")
    for apk_path in test_apks:
        if not os.path.exists(apk_path):
            print(f"Skipping missing APK: {apk_path}")
            continue
        res = run_apk_pipeline(apk_path, model_data)
        assert res["success"] is True, f"Failed on {apk_path}: {res['error']}"
        results_table.append(res)
        flag_str = " [FLAGGED < 50%]" if res["low_coverage_flag"] else ""
        print(f"\n[APK] {res['filename']}")
        print(f"  Package: {res['package_name']} | Version: {res['version_name']} | Size: {res['file_size']}")
        print(f"  SDK: Min {res['min_sdk']} / Target {res['target_sdk']}")
        print(f"  Components: {res['activities']} Acts, {res['services']} Servs, {res['receivers']} Recvs, {res['providers']} Provs, {res['dex_files']} DEX")
        print(f"  Permissions: {res['requested_perms']} total | Dangerous ({len(res['dangerous_perms'])}): {res['dangerous_perms']}")
        print(f"  Coverage: {res['matched_features_count']} of 186 ({res['coverage_pct']}深受%){flag_str}")
        print(f"  ML Verdict: {res['ml_verdict']} | Risk: {res['ml_risk_pct']}% | Band: {res['risk_band']}")
        print(f"  Top 3 Present Features (Chi2): {[f'{f} ({s:.1f})' for f, s in res['top10_present'][:3]]}")

    print("\n--- SUMMARY TABLE OF 5 APKS ---")
    summary_df = pd.DataFrame([{
        "APK": r["filename"],
        "Package": r["package_name"],
        "Verdict": r["ml_verdict"],
        "Risk %": f"{r['ml_risk_pct']:.2f}%",
        "Risk Band": r["risk_band"],
        "Features Matched": f"{r['matched_features_count']} / 186 ({r['coverage_pct']}%)",
        "< 50% Matched?": "YES (Flagged)" if r["low_coverage_flag"] else "No"
    } for r in results_table])
    print(summary_df.to_string(index=False))

    print("\n--- TEST 2: Determinism (Upload Same APK Twice) ---")
    res_a = run_apk_pipeline("test_apks/Aegis_v3.4.3.apk", model_data)
    res_b = run_apk_pipeline("test_apks/Aegis_v3.4.3.apk", model_data)
    print(f"Run 1 Risk: {res_a['ml_risk_pct']}%, Verdict: {res_a['ml_verdict']}, Features: {res_a['matched_features_count']}")
    print(f"Run 2 Risk: {res_b['ml_risk_pct']}%, Verdict: {res_b['ml_verdict']}, Features: {res_b['matched_features_count']}")
    assert res_a["ml_risk_pct"] == res_b["ml_risk_pct"]
    assert res_a["ml_verdict"] == res_b["ml_verdict"]
    assert res_a["matched_features_count"] == res_b["matched_features_count"]
    print(">> Determinism Verified: Identical results across multiple runs.")

    print("\n--- TEST 3: Corrupt & Non-APK Error Handling ---")
    # 3a. Corrupt file
    corrupt_data = extract_apk_data(b"PK\x03\x04corruptedziptruncatedbytes", is_bytes=True)
    print("Corrupt file result:", corrupt_data)
    assert corrupt_data["success"] is False
    assert "error" in corrupt_data
    print(">> Corrupt file safely caught with clear error message.")

    # 3b. Non-APK text file
    non_apk_data = extract_apk_data(b"Hello world, this is a plain text file not an android package.", is_bytes=True)
    print("Non-APK text file result:", non_apk_data)
    assert non_apk_data["success"] is False
    assert "error" in non_apk_data
    print(">> Non-APK file safely caught with clear error message.")

    print("\nALL VALIDATION CHECKS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import joblib

from src.reference_lookup import (
    search_all_reference_candidates,
    download_and_verify_fdroid_apk,
    fetch_play_metadata,
    CACHE_DIR
)
from src.apk_utils import extract_apk_data, build_apk_feature_vector, compare_apks

print("=" * 60)
print("TEST 1: Search 'NewPipe' -> F-Droid download & SHA-256 verification")
print("=" * 60)
cands, msg = search_all_reference_candidates("NewPipe")
print(msg)
for i, c in enumerate(cands):
    print(f"  [{i+1}] {c['display_name']}")

assert len(cands) > 0, "Should find candidates for NewPipe"
newpipe_cand = next((c for c in cands if "org.schabi.newpipe" in c["package_id"]), cands[0])
print(f"Selected candidate: {newpipe_cand['name']} ({newpipe_cand['package_id']}) [{newpipe_cand['source']}]")

ok, dl_msg, apk_path = download_and_verify_fdroid_apk(newpipe_cand, timeout=60)
print(f"Download result: {ok}")
print(f"Message: {dl_msg}")
print(f"Path: {apk_path}")
assert ok is True, f"Failed download: {dl_msg}"
assert os.path.exists(apk_path), f"File not found: {apk_path}"
print(f"Verified size: {os.path.getsize(apk_path):,} bytes")

print("\n" + "=" * 60)
print("TEST 2: Analyze NewPipe APK as both Suspect and Reference")
print("=" * 60)
suspect_data = extract_apk_data(apk_path)
print(f"Package Name: {suspect_data['package_name']}")
print(f"Version Name: {suspect_data['version_name']}")
print(f"Cert SHA-256: {suspect_data['cert_sha256']}")
print(f"Permissions ({len(suspect_data['permissions'])}): {list(suspect_data['permissions'])[:5]}")
print(f"Dangerous Permissions: {suspect_data['dangerous_permissions']}")

# Evaluate ML model on suspect
model_apk = joblib.load("models/svm_apk.pkl")
vec = build_apk_feature_vector(suspect_data, model_apk["matchable_features"])
vec_sel = model_apk["selector"].transform(vec)
pred = model_apk["model"].predict(vec_sel)[0]
proba = model_apk["model"].predict_proba(vec_sel)[0, 1]
ml_risk = proba * 100.0
verdict_str = "MALWARE" if pred == 1 else "BENIGN"
print(f"ML Evaluation: {verdict_str} (Probability: {ml_risk:.2f}%)")

# Compare with reference (self)
comp = compare_apks(suspect_data, suspect_data, ml_risk)
print(f"Package Match: {comp['package_match']}")
print(f"Version Match: {comp['version_match']}")
print(f"Certificate Status: {comp['cert_status']}")
print(f"Extra Permissions: {comp['extra_permissions']} (Count: {len(comp['extra_permissions'])})")
print(f"Final Composite Risk: {comp['final_risk_score']}%")

assert comp["package_match"] is True
assert comp["cert_status"] == "MATCH"
assert len(comp["extra_permissions"]) == 0
print(">> Self-comparison PASSED: 100% Match, 0 extra permissions.")

print("\n" + "=" * 60)
print("TEST 3: Search 'WhatsApp' -> Fallback to Google Play Metadata")
print("=" * 60)
wp_cands, wp_msg = search_all_reference_candidates("WhatsApp")
print(wp_msg)
for i, c in enumerate(wp_cands):
    print(f"  [{i+1}] {c['display_name']}")

wp_cand = next((c for c in wp_cands if "com.whatsapp" in c["package_id"]), None)
assert wp_cand is not None, "Google Play candidate for 'com.whatsapp' must be found"
print(f"Selected candidate: {wp_cand['name']} ({wp_cand['package_id']}) [{wp_cand['source']}]")

ok_wp, wp_meta, wp_meta_msg = fetch_play_metadata(wp_cand["package_id"])
print(f"Metadata fetch status: {ok_wp}")
print(f"Title: {wp_meta.get('title')}")
print(f"Developer: {wp_meta.get('developer')}")
print(f"Version: {wp_meta.get('version')}")
print(f"Listed Permissions count: {len(wp_meta.get('listed_permissions', []))}")
assert ok_wp is True, f"Failed metadata: {wp_meta_msg}"
print(">> Google Play metadata fallback PASSED.")

print("\n" + "=" * 60)
print("TEST 4: Edge Cases: Unknown Name & Graceful Handling")
print("=" * 60)
unk_cands, unk_msg = search_all_reference_candidates("randomnonexistentapp99999999")
print(f"Unknown query returned {len(unk_cands)} candidates. Message: {unk_msg}")
assert len(unk_cands) == 0

print("\nALL REFERENCE LOOKUP TESTS COMPLETED AND VERIFIED SUCCESSFULLY!")

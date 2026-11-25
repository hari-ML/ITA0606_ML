import os
import sys
sys.path.insert(0, os.path.abspath("."))
import joblib
import pandas as pd
from src.apk_utils import extract_apk_data, build_apk_feature_vector, compare_apks

print("=== ACCEPTANCE CHECK 1: Full Model Artifacts & Outputs ===")
required_files = [
    "models/svm_model.pkl",
    "models/svm_apk.pkl",
    "data/sample.csv",
    "outputs/results.csv",
    "outputs/results_apk.csv",
    "outputs/dataset_summary.txt",
    "outputs/f1_vs_k.png",
    "outputs/class_distribution.png",
    "outputs/top_features.png",
    "outputs/svm_confusion_matrix.png",
    "outputs/roc_curves.png",
    "outputs/shap_summary.png"
]
for f in required_files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    status = "PASS" if exists else "FAIL"
    print(f"  [{status}] {f} ({size:,} bytes)")
    assert exists, f"Missing required file: {f}"

print("\n=== ACCEPTANCE CHECK 2: Try Sample Data (CSV Batch Prediction) ===")
sample_df = pd.read_csv("data/sample.csv")
print(f"  Loaded sample.csv with {len(sample_df)} rows and {len(sample_df.columns)} columns.")
full_artifact = joblib.load("models/svm_model.pkl")
features = full_artifact["all_features"]
selector = full_artifact["selector"]
model = full_artifact["model"]

X_sample = sample_df[features]
X_sel = selector.transform(X_sample)
preds = model.predict(X_sel)
probas = model.predict_proba(X_sel)[:, 1]
print(f"  Predictions on sample: {sum(preds==1)} Malware, {sum(preds==0)} Benign")
if "class" in sample_df.columns:
    true_labels = sample_df["class"].astype(int)
    correct = sum(preds == true_labels)
    print(f"  Sample Accuracy: {correct}/{len(preds)} ({correct/len(preds)*100:.1f}%)")

print("\n=== ACCEPTANCE CHECK 3: APK Self-Comparison (All Match) ===")
app_a = {
    "success": True,
    "package_name": "org.sample.calculator",
    "version_name": "2.4.1",
    "version_code": "241",
    "permissions": {"INTERNET", "ACCESS_NETWORK_STATE", "VIBRATE"},
    "cert_sha256": "11223344556677889900AABBCCDDEEFF",
    "dex_methods": {"transact"},
    "dex_classes": {"android.os.Binder"},
    "dex_strings": {"calc"}
}
self_comp = compare_apks(app_a, app_a, 15.0)
print("  Package match:", self_comp["package_match"])
print("  Version match:", self_comp["version_match"])
print("  Cert status:", self_comp["cert_status"])
print("  Extra permissions:", self_comp["extra_permissions"])
print(f"  Final composite risk: {self_comp['final_risk_score']}%")
assert self_comp["package_match"] is True
assert self_comp["cert_status"] == "MATCH"
assert len(self_comp["extra_permissions"]) == 0
assert self_comp["final_risk_score"] == 7.5  # 0.5 * 15.0 = 7.5

print("\n=== ACCEPTANCE CHECK 4: APK Differing/Tampered Comparison ===")
app_b = {
    "success": True,
    "package_name": "org.sample.calculator",
    "version_name": "2.4.2",
    "version_code": "242",
    "permissions": {"INTERNET", "ACCESS_NETWORK_STATE", "VIBRATE", "SEND_SMS", "READ_SMS"},
    "cert_sha256": "FFEEDDCCBBAA00998877665544332211",
    "dex_methods": {"transact"},
    "dex_classes": {"android.os.Binder"},
    "dex_strings": {"calc"}
}
diff_comp = compare_apks(app_b, app_a, 90.0)
print("  Cert status:", diff_comp["cert_status"])
print("  Extra dangerous perms:", diff_comp["extra_dangerous_permissions"])
print("  Perm risk component:", diff_comp["perm_risk_component"])
print("  Cert risk component:", diff_comp["cert_risk_component"])
print(f"  Final composite risk: {diff_comp['final_risk_score']}%")
assert diff_comp["cert_status"] == "MISMATCH"
assert len(diff_comp["extra_dangerous_permissions"]) == 2
# Perm risk: (2/4)*100 = 50. Final: 0.5*90 + 0.3*50 + 0.2*100 = 45 + 15 + 20 = 80.0
assert diff_comp["final_risk_score"] == 80.0

print("\n=== ALL ACCEPTANCE CHECKS COMPLETED AND VERIFIED! ===")

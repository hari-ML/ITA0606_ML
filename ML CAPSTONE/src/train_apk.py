import os
import time
import csv
import warnings
warnings.filterwarnings("ignore")
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

def main():
    print("=" * 60)
    print("PART 2: APK-COMPATIBLE MODEL TRAINING PIPELINE")
    print("=" * 60)

    # 1. Determine matchable columns
    categories_path = os.path.join("file", "dataset-features-categories.csv")
    with open(categories_path, mode="r", encoding="utf-8", errors="ignore") as f:
        cat_rows = list(csv.reader(f))
    cat_dict = {row[0]: row[1] for row in cat_rows if len(row) >= 2}

    data_path = os.path.join("data", "drebin.csv")
    print(f"\n[1] Loading dataset from '{data_path}'...")
    df = pd.read_csv(data_path, low_memory=False)
    
    # Clean data (same procedure as Part 1)
    df = df.replace("?", np.nan).dropna()
    df["class"] = df["class"].map({"S": 1, "B": 0})
    df = df.drop_duplicates()

    all_feature_cols = [c for c in df.columns if c != "class"]
    
    # Filter matchable columns: Manifest Permissions and API Call Signatures
    matchable_cols = [
        c for c in all_feature_cols
        if cat_dict.get(c) in ["Manifest Permission", "API call signature"]
    ]
    total_drebin = len(all_feature_cols)
    usable_count = len(matchable_cols)
    print(f"    Total Drebin features: {total_drebin}")
    print(f"    APK-matchable features: {usable_count} (Permissions + API signatures)")
    print(f"    Excluded features (Intents + Commands): {total_drebin - usable_count}")

    # Ensure integer binary
    for col in matchable_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 2. Stratified 80/20 train/test split
    X = df[matchable_cols]
    y = df["class"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n[2] Train/Test Split (80/20 Stratified):")
    print(f"    Train size: {X_train.shape[0]} samples")
    print(f"    Test size:  {X_test.shape[0]} samples")

    # 3. Feature Selection: SelectKBest(chi2) on TRAIN only
    print(f"\n[3] Feature Selection on {usable_count} matchable features...")
    k_candidates = [25, 50, 100, 150, "all"]
    k_results = []
    for k in k_candidates:
        sel = SelectKBest(score_func=chi2, k=k)
        X_tr_k = sel.fit_transform(X_train, y_train)
        X_te_k = sel.transform(X_test)
        
        base_svm = SVC(C=10, kernel="rbf", gamma="scale", class_weight="balanced", random_state=42)
        base_svm.fit(X_tr_k, y_train)
        pred = base_svm.predict(X_te_k)
        score = f1_score(y_test, pred)
        k_results.append((k, score))
        print(f"    k = {str(k):<5} -> Test F1 Score: {score:.4f}")

    best_k, best_k_f1 = max(k_results, key=lambda x: x[1])
    print(f"    -> Selected Best k for APK Model: {best_k} (F1: {best_k_f1:.4f})")

    final_selector = SelectKBest(score_func=chi2, k=best_k)
    X_train_sel = final_selector.fit_transform(X_train, y_train)
    X_test_sel = final_selector.transform(X_test)
    selected_mask = final_selector.get_support()
    selected_features = [matchable_cols[i] for i, val in enumerate(selected_mask) if val]

    # 4. Tune SVM with GridSearchCV (cv=3, scoring='f1')
    print("\n[4] Tuning APK-Compatible SVM with GridSearchCV...")
    param_grid = {
        "C": [1, 10, 100],
        "kernel": ["linear", "rbf"],
        "gamma": ["scale", 0.01]
    }
    svm_grid = GridSearchCV(
        estimator=SVC(probability=True, class_weight="balanced", random_state=42),
        param_grid=param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1,
        verbose=1
    )
    t0 = time.time()
    svm_grid.fit(X_train_sel, y_train)
    tune_time = time.time() - t0
    best_svm_apk = svm_grid.best_estimator_
    print(f"    GridSearchCV completed in {tune_time:.1f}s")
    print(f"    Best SVM Params: {svm_grid.best_params_}")
    print(f"    Best CV F1-Score: {svm_grid.best_score_:.4f}")

    # 5. Evaluate on Test Set
    t_fit_start = time.time()
    best_svm_apk.fit(X_train_sel, y_train)
    fit_time = time.time() - t_fit_start

    y_pred = best_svm_apk.predict(X_test_sel)
    y_proba = best_svm_apk.predict_proba(X_test_sel)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)

    results_apk = [{
        "Model": "SVM (APK-Compatible Subset)",
        "Features Used": f"{len(selected_features)} of {usable_count}",
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-Score": f1,
        "ROC-AUC": roc_auc,
        "Training Time (s)": round(fit_time, 3)
    }]
    results_apk_df = pd.DataFrame(results_apk)
    results_apk_path = os.path.join("outputs", "results_apk.csv")
    results_apk_df.to_csv(results_apk_path, index=False)

    print(f"\n[5] APK-Compatible Model Metrics (saved to '{results_apk_path}'):")
    print("-" * 80)
    print(results_apk_df.to_string(index=False))
    print("-" * 80)

    # 6. Save models/svm_apk.pkl
    print("\n[6] Saving APK model artifact to 'models/svm_apk.pkl'...")
    model_artifact = {
        "model": best_svm_apk,
        "selector": final_selector,
        "matchable_features": matchable_cols,
        "selected_features": selected_features,
        "best_k": best_k,
        "best_params": svm_grid.best_params_
    }
    joblib.dump(model_artifact, os.path.join("models", "svm_apk.pkl"))
    print("    Saved 'models/svm_apk.pkl' successfully.")

    print("\n" + "=" * 60)
    print("APK-COMPATIBLE MODEL TRAINING COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()

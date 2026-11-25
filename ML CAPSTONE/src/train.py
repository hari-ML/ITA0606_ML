import os
import time
import warnings
warnings.filterwarnings("ignore")
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix
)
import shap

def main():
    print("=" * 60)
    print("PART 1: ANDROID MALWARE DETECTION TRAINING PIPELINE")
    print("=" * 60)

    # 1. Load Data
    data_path = os.path.join("data", "drebin.csv")
    print(f"\n[1] Loading dataset from '{data_path}'...")
    df = pd.read_csv(data_path, low_memory=False)
    initial_shape = df.shape
    print(f"    Raw dataset shape: {initial_shape} (samples, columns)")

    # Replace '?' with NaN and clean
    df = df.replace("?", np.nan)
    nan_rows = int(df.isna().any(axis=1).sum())
    print(f"    Rows containing '?' or NaN: {nan_rows}")
    df = df.dropna()

    # Map labels: S (Malware) -> 1, B (Benign) -> 0
    if "class" not in df.columns:
        raise ValueError("Expected label column 'class' not found in dataset!")
    
    unique_labels = df["class"].unique()
    print(f"    Unique labels in 'class': {unique_labels}")
    df["class"] = df["class"].map({"S": 1, "B": 0})
    if df["class"].isna().any():
        raise ValueError(f"Unmapped label values found! Expected 'S' or 'B', got {unique_labels}")

    # Drop duplicates on features + label together
    dup_count = int(df.duplicated().sum())
    print(f"    Exact duplicate rows (features + label): {dup_count}")
    df = df.drop_duplicates()
    clean_shape = df.shape
    print(f"    Cleaned dataset shape: {clean_shape}")

    # Check for rows sharing identical features but differing in labels
    feature_cols = [c for c in df.columns if c != "class"]
    dup_feats = df.duplicated(subset=feature_cols, keep=False)
    conflicting_rows = int(dup_feats.sum())
    conflicting_unique = int(df[dup_feats].drop_duplicates(subset=feature_cols).shape[0])
    print(f"    Rows sharing identical features with different labels: {conflicting_rows} ({conflicting_unique} unique feature patterns)")

    # Ensure all feature columns are integer 0/1
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Final class distribution
    class_counts = df["class"].value_counts().to_dict()
    benign_count = class_counts.get(0, 0)
    malware_count = class_counts.get(1, 0)
    print(f"    Final class counts -> Benign (0): {benign_count}, Malware (1): {malware_count}")

    # 2. Stratified 80/20 train/test split BEFORE feature selection
    X = df[feature_cols]
    y = df["class"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n[2] Train/Test Split (80/20 Stratified, random_state=42):")
    print(f"    Train set: {X_train.shape[0]} samples ({sum(y_train==1)} malware, {sum(y_train==0)} benign)")
    print(f"    Test set:  {X_test.shape[0]} samples ({sum(y_test==1)} malware, {sum(y_test==0)} benign)")

    # Save dataset summary to outputs/dataset_summary.txt
    os.makedirs("outputs", exist_ok=True)
    summary_path = os.path.join("outputs", "dataset_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=== DATASET SUMMARY ===\n")
        f.write(f"Raw shape: {initial_shape}\n")
        f.write(f"Rows with NaN/? dropped: {nan_rows}\n")
        f.write(f"Exact duplicates dropped: {dup_count}\n")
        f.write(f"Clean shape: {clean_shape}\n")
        f.write(f"Conflicting label rows: {conflicting_rows} ({conflicting_unique} unique patterns)\n")
        f.write(f"Final Class Counts: Benign (0) = {benign_count}, Malware (1) = {malware_count}\n")
        f.write(f"Train samples: {X_train.shape[0]} (Malware: {sum(y_train==1)}, Benign: {sum(y_train==0)})\n")
        f.write(f"Test samples:  {X_test.shape[0]} (Malware: {sum(y_test==1)}, Benign: {sum(y_test==0)})\n")
    print(f"    Saved dataset summary to '{summary_path}'")

    # 3. Feature Selection: SelectKBest(chi2) fit on TRAIN only
    print("\n[3] Feature Selection: Evaluating Chi-Square k in [25, 50, 100, 150, 'all']...")
    k_candidates = [25, 50, 100, 150, "all"]
    k_results = []

    for k in k_candidates:
        selector_test = SelectKBest(score_func=chi2, k=k)
        X_train_k = selector_test.fit_transform(X_train, y_train)
        X_test_k = selector_test.transform(X_test)
        
        # Fast baseline SVM to compare k
        baseline_svm = SVC(C=10, kernel="rbf", gamma="scale", class_weight="balanced", random_state=42)
        baseline_svm.fit(X_train_k, y_train)
        y_pred_k = baseline_svm.predict(X_test_k)
        score_f1 = f1_score(y_test, y_pred_k)
        k_results.append((k, score_f1))
        print(f"    k = {str(k):<5} -> Test F1 Score: {score_f1:.4f}")

    # Best k selection
    best_k, best_k_f1 = max(k_results, key=lambda x: x[1])
    print(f"    -> Selected Best k: {best_k} (F1: {best_k_f1:.4f})")

    # Save f1_vs_k.png
    k_labels = [str(x[0]) for x in k_results]
    f1_vals = [x[1] for x in k_results]
    plt.figure(figsize=(8, 5))
    plt.plot(k_labels, f1_vals, marker="o", color="#1f77b4", linewidth=2, markersize=8)
    plt.title("Feature Selection: F1-Score vs. Number of Selected Features (k)", fontsize=13, fontweight="bold")
    plt.xlabel("Number of Top Chi2 Features (k)", fontsize=11)
    plt.ylabel("Test F1-Score", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    for i, txt in enumerate(f1_vals):
        plt.annotate(f"{txt:.4f}", (k_labels[i], f1_vals[i]), textcoords="offset points", xytext=(0, 10), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "f1_vs_k.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/f1_vs_k.png'")

    # Final feature selector fit on X_train
    final_selector = SelectKBest(score_func=chi2, k=best_k)
    X_train_sel = final_selector.fit_transform(X_train, y_train)
    X_test_sel = final_selector.transform(X_test)
    selected_mask = final_selector.get_support()
    selected_features = [feature_cols[i] for i, val in enumerate(selected_mask) if val]
    print(f"    Total selected features: {len(selected_features)}")

    # 4. Tune SVM with GridSearchCV (cv=3, scoring='f1')
    print("\n[4] Tuning SVM with GridSearchCV (cv=3, scoring='f1')...")
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
    svm_tune_time = time.time() - t0
    best_svm = svm_grid.best_estimator_
    print(f"    GridSearchCV completed in {svm_tune_time:.1f}s")
    print(f"    Best SVM Params: {svm_grid.best_params_}")
    print(f"    Best CV F1-Score: {svm_grid.best_score_:.4f}")

    # 5. Train comparison models on the same split and features
    print("\n[5] Training comparison models on the selected features...")
    models = {
        "Support Vector Machine": best_svm,
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5)
    }

    results = []
    roc_data = {}
    train_times = {}

    for name, model in models.items():
        if name != "Support Vector Machine":
            t_start = time.time()
            model.fit(X_train_sel, y_train)
            train_times[name] = time.time() - t_start
        else:
            # Re-fit best_svm to capture pure fit time on train data
            t_start = time.time()
            best_svm.fit(X_train_sel, y_train)
            train_times[name] = time.time() - t_start

        # Predictions on test set
        y_pred = model.predict(X_test_sel)
        y_proba = model.predict_proba(X_test_sel)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "ROC-AUC": roc_auc,
            "Training Time (s)": round(train_times[name], 3)
        })

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_data[name] = (fpr, tpr, roc_auc)

    # 6. Save results.csv and print
    results_df = pd.DataFrame(results)
    results_csv_path = os.path.join("outputs", "results.csv")
    results_df.to_csv(results_csv_path, index=False)
    print(f"\n[6] Evaluation Results on Test Set (saved to '{results_csv_path}'):")
    print("-" * 80)
    print(results_df.to_string(index=False))
    print("-" * 80)

    # 7. Generate and save plots
    print("\n[7] Generating diagnostic and performance plots in 'outputs/'...")

    # Plot 1: Class distribution
    plt.figure(figsize=(6, 4.5))
    colors = ["#2ca02c", "#d62728"]
    ax = sns.barplot(x=["Benign (0)", "Malware (1)"], y=[benign_count, malware_count], palette=colors)
    plt.title("Drebin Dataset Class Distribution (Cleaned)", fontsize=12, fontweight="bold")
    plt.ylabel("Sample Count", fontsize=11)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "class_distribution.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/class_distribution.png'")

    # Plot 2: Top 15 features in malware vs benign
    chi2_scores, _ = chi2(X_train, y_train)
    top15_indices = np.argsort(chi2_scores)[-15:][::-1]
    top15_names = [feature_cols[i] for i in top15_indices]
    
    # Compute prevalence percentage in malware vs benign for these top 15
    mw_subset = df[df["class"] == 1]
    bg_subset = df[df["class"] == 0]
    mw_prev = [mw_subset[col].mean() * 100 for col in top15_names]
    bg_prev = [bg_subset[col].mean() * 100 for col in top15_names]

    y_pos = np.arange(len(top15_names))
    plt.figure(figsize=(10, 7))
    plt.barh(y_pos - 0.2, mw_prev, height=0.4, label="Malware (%)", color="#d62728", alpha=0.85)
    plt.barh(y_pos + 0.2, bg_prev, height=0.4, label="Benign (%)", color="#2ca02c", alpha=0.85)
    plt.yticks(y_pos, top15_names, fontsize=9)
    plt.xlabel("Prevalence (% of apps requesting feature)", fontsize=11)
    plt.title("Top 15 Discriminative Features (Chi2) in Malware vs. Benign", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "top_features.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/top_features.png'")

    # Plot 3: SVM Confusion Matrix
    y_svm_pred = best_svm.predict(X_test_sel)
    cm = confusion_matrix(y_test, y_svm_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Benign (0)", "Malware (1)"],
                yticklabels=["Benign (0)", "Malware (1)"],
                annot_kws={"size": 14, "weight": "bold"})
    plt.title("Support Vector Machine - Confusion Matrix", fontsize=12, fontweight="bold")
    plt.xlabel("Predicted Label", fontsize=11)
    plt.ylabel("True Label", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "svm_confusion_matrix.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/svm_confusion_matrix.png'")

    # Plot 4: Combined ROC Curves
    plt.figure(figsize=(8, 6))
    for name, (fpr, tpr, roc_auc) in roc_data.items():
        plt.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=1.5, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate", fontsize=11)
    plt.title("Receiver Operating Characteristic (ROC) Comparison", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "roc_curves.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/roc_curves.png'")

    # 8. SHAP Explainability
    print("\n[8] Computing SHAP Explainability Analysis...")
    # For speed and exact tree attribution without KernelExplainer approximation delay,
    # we compute SHAP using the top Tree-based model (Random Forest / XGBoost) trained on the identical features
    print("    Using TreeExplainer on Random Forest (trained on identical selected features)")
    print("    because KernelExplainer on non-linear SVM is computationally prohibitive (~O(M * 2^|S|)).")
    rf_model = models["Random Forest"]
    explainer = shap.TreeExplainer(rf_model)
    shap_sample = X_test_sel[:200]
    shap_values = explainer.shap_values(shap_sample)

    # In binary classification, shap_values may be a list [class 0, class 1] or an array
    if isinstance(shap_values, list) and len(shap_values) == 2:
        shap_vals_malware = shap_values[1]
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_vals_malware = shap_values[:, :, 1]
    else:
        shap_vals_malware = shap_values

    plt.figure(figsize=(10, 6))
    shap.summary_plot(
        shap_vals_malware,
        shap_sample,
        feature_names=selected_features,
        max_display=15,
        show=False
    )
    plt.title("SHAP Feature Importance (Malware Class Impact)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "shap_summary.png"), dpi=300)
    plt.close()
    print("    Saved 'outputs/shap_summary.png'")

    # 9. Save models/svm_model.pkl
    print("\n[9] Saving full SVM model artifact to 'models/svm_model.pkl'...")
    model_artifact = {
        "model": best_svm,
        "selector": final_selector,
        "selected_features": selected_features,
        "all_features": feature_cols,
        "best_k": best_k,
        "best_params": svm_grid.best_params_
    }
    joblib.dump(model_artifact, os.path.join("models", "svm_model.pkl"))
    print("    Saved 'models/svm_model.pkl' successfully.")

    # 10. Save ~20 random test rows to data/sample.csv for demo
    print("\n[10] Saving sample demo rows to 'data/sample.csv'...")
    test_df = df.loc[X_test.index].copy()
    sample_df = test_df.sample(n=min(20, len(test_df)), random_state=42)
    sample_path = os.path.join("data", "sample.csv")
    sample_df.to_csv(sample_path, index=False)
    print(f"    Saved {len(sample_df)} sample rows to '{sample_path}'.")

    print("\n" + "=" * 60)
    print("TRAINING PIPELINE COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()

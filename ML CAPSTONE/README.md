# Android Malware Detection Using Permission and API-Call Features with Feature Selection and Support Vector Machine

A complete, end-to-end Machine Learning Capstone project that detects Android malware via static analysis of Android manifest permissions and Dalvik bytecode API call signatures. The system integrates a differential **APK Analyzer** to detect repackaged, tampered, and trojanized applications compared against original reference binaries.

---

## 📌 Project Architecture

```
ML CAPSTONE/
├── data/
│   ├── drebin.csv                  # Drebin benchmark dataset (215 features + class label)
│   └── sample.csv                  # 20 held-out test apps for instant demo
├── src/
│   ├── __init__.py                 # Python package init
│   ├── train.py                    # Part 1: Full 215-feature training & benchmarking pipeline
│   ├── train_apk.py                # Part 2: 186-feature APK-compatible model training
│   └── apk_utils.py                # Part 3: Static APK parser (Androguard) & differential comparator
├── models/
│   ├── svm_model.pkl               # Tuned SVM model (all Drebin features)
│   └── svm_apk.pkl                 # Tuned SVM model (APK-matchable features)
├── outputs/
│   ├── results.csv                 # Evaluation metrics across 5 machine learning models
│   ├── results_apk.csv             # Metrics for the APK-compatible model
│   ├── dataset_summary.txt         # Dataset cleaning, duplicate drops, and split summary
│   ├── f1_vs_k.png                 # Chi-Square feature selection curve (F1 vs k)
│   ├── class_distribution.png      # Cleaned dataset class balance
│   ├── top_features.png            # Top 15 discriminative features in malware vs benign
│   ├── svm_confusion_matrix.png    # Confusion matrix of the tuned SVM
│   ├── roc_curves.png              # Receiver Operating Characteristic (ROC) curve comparison
│   └── shap_summary.png            # SHAP feature attribution plot
├── app.py                          # Streamlit interactive dark-themed web dashboard
├── requirements.txt                # Project dependencies
└── README.md                       # Project documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Windows OS (PowerShell)
- Python 3.12 (Do **NOT** use Python 3.14)

### 1. Create and Activate Virtual Environment
```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Execution & Training Guide

### Step 1: Train the Full Model Pipeline
Trains the tuned Support Vector Machine and 4 comparison models (Logistic Regression, Random Forest, XGBoost, K-Nearest Neighbors) on the full Drebin dataset with Chi-Square feature selection and SHAP explainability.
```powershell
.\venv\Scripts\python src/train.py
```
*Outputs: `models/svm_model.pkl`, `outputs/results.csv`, `outputs/dataset_summary.txt`, `data/sample.csv`, and all visualization plots.*

### Step 2: Train the APK-Compatible Model
Trains a dedicated SVM on the 186 features that can be statically extracted from real-world APK files (113 Manifest Permissions + 73 API Call Signatures).
```powershell
.\venv\Scripts\python src/train_apk.py
```
*Outputs: `models/svm_apk.pkl`, `outputs/results_apk.csv`.*

### Step 3: Launch the Streamlit Web Application
Runs the interactive dark-themed web dashboard on `http://localhost:8501`.
```powershell
.\venv\Scripts\streamlit run app.py
```

---

## 📊 Experimental Results & Benchmarks

All models were evaluated on an **80/20 stratified split** of the cleaned Drebin dataset ($N = 7,259$ unique apps after dropping duplicates and missing values; 5,807 train / 1,452 test; 344 malware / 1,108 benign).

### 1. Full Benchmark Comparison (`outputs/results.csv`)

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Training Time (s) |
|---|---|---|---|---|---|---|
| **Support Vector Machine (Tuned)** | **98.28%** | **97.05%** | **95.64%** | **96.34%** | **0.9943** | 27.361 |
| **XGBoost** | 98.00% | 97.87% | 93.60% | 95.69% | 0.9957 | 1.062 |
| **Random Forest** | 97.04% | 93.88% | 93.60% | 93.74% | 0.9927 | 2.926 |
| **Logistic Regression** | 96.56% | 90.16% | 95.93% | 92.96% | 0.9907 | 0.450 |
| **K-Nearest Neighbors** | 96.83% | 96.27% | 90.12% | 93.09% | 0.9863 | 0.019 |

> **Best Hyperparameters (GridSearchCV, 3-fold, scoring="f1"):**
> `{'C': 100, 'gamma': 'scale', 'kernel': 'rbf'}`

### 2. APK-Compatible Model (`outputs/results_apk.csv`)

Real APKs can only reliably extract manifest permissions and Dalvik API call signatures statically (excluding dynamic intents and system commands). We retrained the pipeline on this 186-feature subset:

| Model | Features Used | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Training Time (s) |
|---|---|---|---|---|---|---|---|
| **SVM (APK-Compatible Subset)** | 186 of 186 | **98.00%** | **96.46%** | **95.06%** | **95.75%** | **0.9942** | 18.141 |

*Note: While slightly lower in recall by ~0.5% compared to the full 215-feature model, the APK-compatible model achieves a 98.00% accuracy and 95.75% F1-score while remaining 100% extractable from static APK files.*

---

## 🔍 Static APK Analyzer & Automated Reference Lookup Engine

The APK Analyzer in Tab 2 enables static differential security analysis without requiring the user to upload a reference binary:

### 1. Multi-Tiered Reference App Resolution
1. **Local Preloaded Cache (`reference_apks/<package>.apk`)**:
   - Immediately checks if a verified APK matching the package name exists in the `reference_apks/` directory.
2. **F-Droid Official Repository (Full Mode)**:
   - Downloads the official F-Droid index (caches locally for 24 hours).
   - Searches applications by title and package ID, picks the latest version, streams the APK, and **verifies its SHA-256 against the index signature**.
   - Validates the downloaded APK package name before saving to `reference_apks/<package>.apk`.
3. **Google Play Store Metadata Fallback (Metadata-Only Mode)**:
   - Uses `google-play-scraper` to search official Google Play listings.
   - Extracts developer identity, store version, and declared permissions.
   - Operates strictly as a metadata comparison (no binary downloads, no Google credentials, no mirror scraping).

### 2. Operational Modes
- **Full Comparative Mode** (Local Cache or F-Droid):
  - Runs identical static bytecode/manifest analysis on both apps.
  - Compares Package Name and Version.
  - **Signing Certificate Verification**: Computes SHA-256 certificate fingerprints (MATCH vs MISMATCH). *Note: F-Droid may re-sign apps with its own release key, so a mismatch against a developer's own build is not always malicious.*
  - **Permission Differentials**: Identifies Added, Missing, and Shared permissions.
  - **Dangerous Permissions Flags**: Highlights high-risk permissions (`SEND_SMS`, `READ_SMS`, `RECEIVE_SMS`, `BIND_DEVICE_ADMIN`, `REQUEST_INSTALL_PACKAGES`, `SYSTEM_ALERT_WINDOW`, `READ_CONTACTS`, `RECORD_AUDIO`, `ACCESS_FINE_LOCATION`).
  - **Machine Learning Evaluation**: Evaluates `svm_apk.pkl` on **BOTH** suspect and reference APKs.
  - **Transparent Composite Risk Score**:
    $$\text{Final Risk} = (0.50 \times \text{ML\_Risk}) + (0.30 \times \text{Perm\_Risk}) + (0.20 \times \text{Cert\_Risk})$$
- **Metadata-Only Mode** (Google Play):
  - Compares suspect APK package, version, and developer against official Play Store listings.
  - Displays Play listed permissions next to the suspect's requested permissions and flagged dangerous permissions.
  - States clearly: *"Certificate comparison not possible: no reference APK available (Google Play is metadata-only)."*

### 3. How to Pre-Load Reference APKs
You can pre-load reference APKs manually into the local cache for instant offline comparison:
1. Obtain an authentic APK from a verified source (e.g., developer website or internal repository).
2. Rename the file to its exact package ID (e.g. `org.schabi.newpipe.apk` or `com.example.app.apk`).
3. Place it in the `reference_apks/` directory:
   ```powershell
   Copy-Item -Path "path\to\app.apk" -Destination "reference_apks\com.example.app.apk"
   ```
4. The system will detect it automatically in **Local Cache** mode.

---

## 🧠 Explainability & Interpretability (SHAP & Chi2)

- **Chi-Square Feature Ranking**: Telephony permissions (`SEND_SMS`, `RECEIVE_SMS`, `READ_PHONE_STATE`) and reflection APIs (`Ljava.lang.Class.getMethods`, `Ljava.lang.Class.cast`) display the highest discriminative power between malicious and benign applications.
- **SHAP Feature Attribution**: Visualized in `outputs/shap_summary.png`. Confirms that SMS-related permissions and reflection hooks contribute positively toward a malware classification, mirroring known Android trojan behaviors (e.g. FakeInstaller and Opfake).

---

## ⚠️ Academic Considerations & Limitations

1. **Older Dataset (Drebin)**: The Drebin dataset reflects Android permissions and malware behaviors from early Android versions (Android 2.x - 4.x). Contemporary Android versions (Android 10 - 14+) enforce runtime permissions and scoped storage, which altered permission grant dynamics.
2. **Static Analysis Scope**: Static inspection cannot monitor runtime behavior, dynamic code loading (`DexClassLoader`), or payloads downloaded from command-and-control (C2) servers post-installation.
3. **Obfuscation Evasion**: Advanced packers, native libraries (`.so` via JNI), and string encryption can obscure API calls from static Dalvik bytecode disassembly.
4. **Feature Subset for Real APKs**: The APK analyzer operates on a 186-feature subset because dynamic system command signatures and implicit intent distributions cannot be matched deterministically from static manifest/dex parsing alone.
5. **Reference Lookup Scope (F-Droid & Google Play)**:
   - **F-Droid**: Limited to open-source software cataloged in the F-Droid repository. F-Droid frequently signs applications using its own build-server release keys, meaning an F-Droid build will mismatch the cryptographic certificate of an official Google Play APK from the same developer without being malicious.
   - **Google Play**: Google Play operates strictly in metadata-only mode. Downloading commercial APKs from the Play Store without authenticated Google user sessions violates platform terms; therefore, cryptographic certificate comparison is not possible for Play-only applications.
   - **Scraper Reliance**: The Google Play metadata scraper relies on unofficial web endpoints, which may be subject to layout shifts, regional differences, or rate-limiting.

import os
import csv
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = Path(os.environ.get("MODEL_DIR", str(PROJECT_ROOT / "model")))
CACHE_PATH = MODEL_DIR / "diagnostics_cache.json"
LEGACY_CACHE_PATH = PROJECT_ROOT / "outputs" / "diagnostics_cache.json"

# Domain explanations keyed by real Drebin permission/API identifiers
FEATURE_EXPLANATIONS = {
    "transact": "Core Binder IPC transaction call. Found in 68.3% of benign apps vs. 8.9% of malware because full-featured benign apps use modular AIDL services extensively, acting as a strong benign boundary indicator.",
    "WRITE_HISTORY_BOOKMARKS": "Allows modifying browser bookmarks/history (26.4% malware vs. 3.0% benign). Heavily exploited by adware and browser-hijacking trojans to inject malicious shortcuts.",
    "READ_HISTORY_BOOKMARKS": "Allows reading browser history and saved bookmarks (28.0% malware vs. 4.4% benign). Spyware harvests browsing patterns for profiling and credential phishing.",
    "onServiceConnected": "Bound-service lifecycle callback (69.8% benign vs. 12.3% malware). Benign multi-component apps and Google Play Services SDKs rely heavily on bound services.",
    "bindService": "Connects UI components to background services (69.3% benign vs. 12.0% malware). Standard modular app architecture cue that distinguishes rich benign apps from standalone trojans.",
    "attachInterface": "Registers a Binder AIDL interface (65.7% benign vs. 8.9% malware). Indicates structured multi-process SDK/IPC architecture typical of legitimate apps.",
    "ServiceConnection": "Manages service-binding callbacks (69.6% benign vs. 12.5% malware). Strongly co-occurs with standard IPC-heavy benign applications.",
    "android.os.Binder": "Low-level Android IPC backbone (74.0% benign vs. 16.8% malware); its high prevalence in standard frameworks makes it a top negative/benign boundary signal.",
    "SEND_SMS": "Permits sending SMS without user interaction (30.5% malware vs. 5.8% benign). Classic vector for silent premium-rate SMS billing fraud and worm propagation.",
    "READ_PHONE_STATE": "Exposes IMEI, IMSI, phone number, and carrier state. Exploited by spyware and adware for persistent device fingerprinting and tracking.",
    "RECEIVE_SMS": "Intercepts incoming SMS messages silently, allowing banking trojans to steal two-factor authentication OTPs before the user sees them.",
    "READ_SMS": "Reads the SMS inbox (29.2% malware vs. 7.0% benign), enabling theft of OTP codes and private messages.",
    "TelephonyManager.getDeviceId": "Extracts the unique hardware IMEI/MEID identifier for botnet C2 registration and victim device profiling.",
    "TelephonyManager.getSubscriberId": "Reads the SIM subscriber IMSI identifier used by spyware to track victims across app installs.",
    "TelephonyManager.getLine1Number": "Reads the SIM phone number (48.9% malware vs. 15.3% benign). Frequently harvested by SMS trojans and spyware for fraud and tracking.",
    "TelephonyManager.getSimSerialNumber": "Extracts SIM card serial number for persistent device tracking.",
    "android.telephony.SmsManager": "Programmatic SMS engine invoked directly in Dalvik bytecode to send hidden SMS payloads.",
    "android.telephony.gsm.SmsManager": "Legacy GSM SMS API referenced by SMS trojans targeting pre-runtime-permission Android versions.",
    "Ljava.lang.Class.getCanonicalName": "Java reflection utility common in benign serialization/UI libraries (52.3% benign vs. 4.4% malware); helps separate standard Java SDKs from simple malware.",
    "Ljava.lang.Class.getMethods": "Reflection inspection method heavily compiled into standard benign frameworks (44.6% benign vs. 5.4% malware).",
    "Ljava.lang.Class.cast": "Dynamic class casting frequently emitted by standard Android compiler/SDK wrappers (48.1% benign vs. 7.6% malware).",
    "android.content.pm.Signature": "Inspects app signing certificates (52.8% benign vs. 8.8% malware); commonly invoked by legitimate licensing SDKs and Play Services checks.",
    "Ljava.lang.Class.forName": "Dynamically loads Java classes by string name at runtime, used both in reflection libraries and dynamic malware loaders.",
    "DexClassLoader": "Loads secondary `.dex`/`.jar`/`.apk` payloads dynamically from storage or encrypted assets after installation.",
    "RECEIVE_BOOT_COMPLETED": "Triggers app launch automatically on device boot, establishing persistence across restarts.",
    "BIND_DEVICE_ADMIN": "Grants device administrator privileges, abused by ransomware/lockers to block uninstallation.",
    "SYSTEM_ALERT_WINDOW": "Draws floating overlays atop other apps; abused by banking trojans for credential-harvesting overlays and tapjacking.",
    "REQUEST_INSTALL_PACKAGES": "Enables dropper apps to prompt or install secondary malicious APKs.",
    "READ_CONTACTS": "Harvests the victim's address book for worm propagation or spyware exfiltration.",
    "RECORD_AUDIO": "Captures microphone audio; high-risk surveillance permission when paired with background services.",
    "ACCESS_FINE_LOCATION": "Reads precise GPS coordinates; exploited by stalkerware and geo-tracking SDKs.",
    "Runtime.exec": "Executes OS shell commands (`su`, `chmod`, `mount`), characteristic of root exploits and droppers.",
    "Ljavax.crypto.Cipher": "Performs cryptographic operations, used both for TLS/storage security and decrypting obfuscated malware payloads.",
}


def get_feature_explanation(feature_name: str, category: str, mw_pct: float, bg_pct: float) -> str:
    """Return a concise, accurate security explanation for a Drebin feature."""
    if feature_name in FEATURE_EXPLANATIONS:
        return FEATURE_EXPLANATIONS[feature_name]
    diff = mw_pct - bg_pct
    if diff >= 0:
        return (
            f"{category} appearing in {mw_pct:.1f}% of malware samples vs. {bg_pct:.1f}% of benign apps; "
            f"provides strong positive signal toward malicious behavior classification."
        )
    return (
        f"{category} present in {bg_pct:.1f}% of benign apps vs. {mw_pct:.1f}% of malware samples; "
        f"acts as a counter-indicator helping the SVM separate standard SDK patterns from malware."
    )


def load_feature_categories() -> dict:
    """Load Drebin feature category mapping from model/dataset-features-categories.csv (with local fallback)."""
    cat_file = MODEL_DIR / "dataset-features-categories.csv"
    if not cat_file.exists():
        cat_file = PROJECT_ROOT / "file" / "dataset-features-categories.csv"
    cat_dict = {}
    if cat_file.exists():
        with cat_file.open("r", encoding="utf-8", errors="ignore") as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    cat_dict[row[0].strip()] = row[1].strip()
    return cat_dict


def _downsample_roc(fpr: np.ndarray, tpr: np.ndarray, max_points: int = 180) -> tuple:
    """Reduce ROC curve array length evenly while keeping endpoints crisp."""
    if len(fpr) <= max_points:
        return [round(float(x), 5) for x in fpr], [round(float(y), 5) for y in tpr]
    idx = np.linspace(0, len(fpr) - 1, max_points, dtype=int)
    return [round(float(fpr[i]), 5) for i in idx], [round(float(tpr[i]), 5) for i in idx]


def compute_and_cache_diagnostics(force: bool = False) -> dict:
    """
    Load real evaluation diagnostics from model/diagnostics_cache.json (or outputs/ fallback).
    Recomputes from data/drebin.csv only if explicitly forced or cache is absent locally.
    """
    if not force:
        for candidate in (CACHE_PATH, LEGACY_CACHE_PATH):
            if candidate.exists():
                return json.loads(candidate.read_text(encoding="utf-8"))

    from sklearn.model_selection import train_test_split
    from sklearn.feature_selection import SelectKBest, chi2
    from sklearn.svm import SVC
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from xgboost import XGBClassifier
    from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix, f1_score

    data_path = PROJECT_ROOT / "data" / "drebin.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Neither '{CACHE_PATH}' nor '{data_path}' exists.")

    df_raw = pd.read_csv(data_path, low_memory=False)
    raw_rows, raw_cols = df_raw.shape

    df = df_raw.replace("?", np.nan).dropna()
    df["class"] = df["class"].map({"S": 1, "B": 0})
    df = df.drop_duplicates()
    clean_rows = int(df.shape[0])

    feature_cols = [c for c in df.columns if c != "class"]
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    benign_count = int((df["class"] == 0).sum())
    malware_count = int((df["class"] == 1).sum())

    X = df[feature_cols]
    y = df["class"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    art = joblib.load(MODEL_DIR / "svm_model.pkl")
    selector = art["selector"]
    best_svm = art["model"]
    all_feats = art.get("all_features", feature_cols)

    X_train_sel = selector.transform(X_train[all_feats])
    X_test_sel = selector.transform(X_test[all_feats])

    # Confusion Matrix of saved tuned SVM on real held-out test set
    y_svm_pred = best_svm.predict(X_test_sel)
    y_svm_prob = best_svm.predict_proba(X_test_sel)[:, 1]
    cm = confusion_matrix(y_test, y_svm_pred).tolist()

    # Exact ROC curves computed on identical split and features
    models_for_roc = {
        "Support Vector Machine (Tuned)": y_svm_prob,
    }
    comp_models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    }
    for m_name, m_obj in comp_models.items():
        m_obj.fit(X_train_sel, y_train)
        models_for_roc[m_name] = m_obj.predict_proba(X_test_sel)[:, 1]

    roc_curves = {}
    for m_name, prob in models_for_roc.items():
        fpr, tpr, _ = roc_curve(y_test, prob)
        auc_val = float(roc_auc_score(y_test, prob))
        fpr_ds, tpr_ds = _downsample_roc(fpr, tpr)
        roc_curves[m_name] = {
            "fpr": fpr_ds,
            "tpr": tpr_ds,
            "auc": round(auc_val, 4),
        }

    # Feature selection curve (k in [25, 50, 100, 150, all]) on exact split
    k_curve = []
    for k in [25, 50, 100, 150, "all"]:
        sel_k = SelectKBest(score_func=chi2, k=k)
        X_tr_k = sel_k.fit_transform(X_train[all_feats], y_train)
        X_te_k = sel_k.transform(X_test[all_feats])
        clf_k = SVC(C=10, kernel="rbf", gamma="scale", class_weight="balanced", random_state=42)
        clf_k.fit(X_tr_k, y_train)
        f1_k = float(f1_score(y_test, clf_k.predict(X_te_k)))
        k_curve.append({"k": str(k), "f1": round(f1_k, 4)})

    # Top 15 features by Chi2 on X_train
    cat_dict = load_feature_categories()
    chi2_scores, _ = chi2(X_train[all_feats], y_train)
    top15_idx = np.argsort(chi2_scores)[-15:][::-1]
    mw_df = df[df["class"] == 1]
    bg_df = df[df["class"] == 0]

    top_features = []
    for i in top15_idx:
        fname = all_feats[i]
        cat = cat_dict.get(fname, "API Signature / Permission")
        mw_pct = round(float(mw_df[fname].mean() * 100.0), 2)
        bg_pct = round(float(bg_df[fname].mean() * 100.0), 2)
        score = round(float(chi2_scores[i]), 2)
        top_features.append({
            "feature": fname,
            "category": cat,
            "chi2_score": score,
            "malware_pct": mw_pct,
            "benign_pct": bg_pct,
            "explanation": get_feature_explanation(fname, cat, mw_pct, bg_pct),
        })

    apk_art = joblib.load(MODEL_DIR / "svm_apk.pkl")

    cache_data = {
        "dataset": {
            "raw_rows": int(raw_rows),
            "raw_cols": int(raw_cols),
            "clean_rows": clean_rows,
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "train_malware": int((y_train == 1).sum()),
            "train_benign": int((y_train == 0).sum()),
            "test_malware": int((y_test == 1).sum()),
            "test_benign": int((y_test == 0).sum()),
            "benign_count": benign_count,
            "malware_count": malware_count,
            "full_feature_count": len(all_feats),
            "apk_feature_count": len(apk_art.get("matchable_features", [])),
        },
        "svm_params": art.get("best_params", {}),
        "svm_apk_params": apk_art.get("best_params", {}),
        "confusion_matrix": cm,
        "roc_curves": roc_curves,
        "f1_vs_k": k_curve,
        "top_features": top_features,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")

    return cache_data


# -----------------------------------------------------------------------------
# PLOTLY DARK CYBERSECURITY CHARTS
# -----------------------------------------------------------------------------
PLOTLY_LAYOUT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18, 26, 51, 0.45)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0", size=12),
    title_font=dict(family="Space Grotesk, sans-serif", color="#f8fafc", size=16),
    margin=dict(l=40, r=24, t=54, b=40),
    hoverlabel=dict(
        bgcolor="#121a33",
        bordercolor="#22d3ee",
        font=dict(family="Inter, sans-serif", color="#f8fafc", size=12),
    ),
)


def make_confidence_gauge(risk_pct: float, is_malicious: bool) -> go.Figure:
    """Interactive Plotly confidence / malware probability gauge."""
    bar_color = "#ef4444" if is_malicious else ("#f97316" if risk_pct >= 30.0 else "#10b981")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(risk_pct, 2),
            number={"suffix": "%", "font": {"size": 36, "family": "Space Grotesk, sans-serif", "color": "#f8fafc"}},
            title={"text": "Malware Probability Score", "font": {"size": 14, "family": "Space Grotesk, sans-serif", "color": "#94a3b8"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748b"},
                "bar": {"color": bar_color, "thickness": 0.34},
                "bgcolor": "rgba(11, 16, 32, 0.7)",
                "borderwidth": 1,
                "bordercolor": "rgba(255, 255, 255, 0.08)",
                "steps": [
                    {"range": [0, 30], "color": "rgba(16, 185, 129, 0.14)"},
                    {"range": [30, 70], "color": "rgba(249, 115, 22, 0.14)"},
                    {"range": [70, 100], "color": "rgba(239, 68, 68, 0.16)"},
                ],
                "threshold": {
                    "line": {"color": "#22d3ee", "width": 3},
                    "thickness": 0.8,
                    "value": 50,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#e2e8f0"),
        height=230,
        margin=dict(l=20, r=20, t=38, b=10),
    )
    return fig


def make_class_donut(benign_count: int, malware_count: int, title: str = "Dataset Class Distribution") -> go.Figure:
    """Interactive Plotly class distribution donut chart."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Benign", "Malicious"],
                values=[benign_count, malware_count],
                hole=0.62,
                marker=dict(
                    colors=["#22d3ee", "#ef4444"],
                    line=dict(color="#0b1020", width=3),
                ),
                textinfo="percent+label",
                textfont=dict(size=13, family="Space Grotesk, sans-serif"),
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    total = benign_count + malware_count
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=title,
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        annotations=[
            dict(
                text=f"<b>{total:,}</b><br><span style='font-size:11px;color:#94a3b8'>Total Apps</span>",
                x=0.5, y=0.5, font=dict(size=18, family="Space Grotesk, sans-serif", color="#f8fafc"),
                showarrow=False,
            )
        ],
    )
    return fig


def make_confusion_matrix_chart(cm: list) -> go.Figure:
    """Interactive Plotly confusion matrix heatmap from real test predictions."""
    z = cm
    labels = ["Benign (0)", "Malicious (1)"]
    text = [[f"TN: {cm[0][0]:,}", f"FP: {cm[0][1]:,}"], [f"FN: {cm[1][0]:,}", f"TP: {cm[1][1]:,}"]]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=15, family="Space Grotesk, sans-serif", color="#f8fafc"),
            colorscale=[
                [0.0, "#121a33"],
                [0.25, "#0e4a63"],
                [0.6, "#0891b2"],
                [1.0, "#22d3ee"],
            ],
            showscale=True,
            hovertemplate="Actual: <b>%{y}</b><br>Predicted: <b>%{x}</b><br>Samples: %{z:,}<extra></extra>",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title="Tuned SVM Confusion Matrix (Held-Out Test Set, n=1,452)",
        xaxis_title="Predicted Label",
        yaxis_title="Actual Label",
        height=380,
    )
    fig.update_yaxes(autorange="reversed")
    return fig


def make_roc_curve_chart(roc_curves: dict, selected_models: list = None) -> go.Figure:
    """Interactive Plotly ROC curves with AUC scores."""
    palette = {
        "Support Vector Machine (Tuned)": "#22d3ee",
        "Random Forest": "#38bdf8",
        "Logistic Regression": "#a78bfa",
        "XGBoost": "#34d399",
        "K-Nearest Neighbors": "#f59e0b",
    }
    fig = go.Figure()
    for name, data in roc_curves.items():
        if selected_models and name not in selected_models:
            continue
        is_svm = "Support Vector Machine" in name
        fig.add_trace(
            go.Scatter(
                x=data["fpr"],
                y=data["tpr"],
                mode="lines",
                name=f"{name} (AUC = {data['auc']:.4f})",
                line=dict(
                    color=palette.get(name, "#94a3b8"),
                    width=3.2 if is_svm else 2.0,
                    dash="solid" if is_svm else "dot",
                ),
                hovertemplate=f"<b>{name}</b><br>FPR: %{{x:.3f}}<br>TPR: %{{y:.3f}}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random Baseline (AUC = 0.5000)",
            line=dict(color="#475569", width=1.2, dash="dash"),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title="ROC Curves & AUC Comparison (Real Test Set)",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=400,
        legend=dict(yanchor="bottom", y=0.04, xanchor="right", x=0.98, bgcolor="rgba(11,16,32,0.72)"),
    )
    fig.update_xaxes(range=[0, 1], gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(range=[0, 1.02], gridcolor="rgba(255,255,255,0.06)")
    return fig


def make_f1_vs_k_chart(f1_vs_k: list) -> go.Figure:
    """Interactive Plotly Chi2 k-selection F1-Score curve."""
    ks = [item["k"] for item in f1_vs_k]
    f1s = [item["f1"] * 100.0 for item in f1_vs_k]
    fig = go.Figure(
        go.Scatter(
            x=ks,
            y=f1s,
            mode="lines+markers+text",
            text=[f"{v:.2f}%" for v in f1s],
            textposition="top center",
            line=dict(color="#22d3ee", width=3),
            marker=dict(size=10, color="#22d3ee", line=dict(color="#0b1020", width=2)),
            hovertemplate="<b>k = %{x}</b><br>Test F1-Score: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title="Chi-Square Feature Selection: Test F1-Score vs. Feature Count (k)",
        xaxis_title="Selected Feature Subset (k)",
        yaxis_title="Test F1-Score (%)",
        height=350,
    )
    fig.update_yaxes(range=[max(85, min(f1s) - 2), 100.2], gridcolor="rgba(255,255,255,0.06)")
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    return fig


def make_feature_importance_chart(top_features: list, metric: str = "prevalence") -> go.Figure:
    """
    Interactive Plotly feature importance chart.
    metric='prevalence' shows Malware % vs Benign % prevalence.
    metric='chi2' shows raw Chi-Square statistic.
    """
    ordered = list(reversed(top_features))
    names = [f["feature"] for f in ordered]

    fig = go.Figure()
    if metric == "chi2":
        scores = [f["chi2_score"] for f in ordered]
        cats = [f["category"] for f in ordered]
        fig.add_trace(
            go.Bar(
                y=names,
                x=scores,
                orientation="h",
                marker=dict(
                    color=scores,
                    colorscale=[[0, "#0e7490"], [1, "#22d3ee"]],
                    line=dict(color="rgba(255,255,255,0.1)", width=1),
                ),
                customdata=cats,
                hovertemplate="<b>%{y}</b><br>Category: %{customdata}<br>Chi² Score: %{x:,.2f}<extra></extra>",
                name="Chi-Square Score",
            )
        )
        title = "Top 15 Permissions & API Calls Driving Classification (Chi² Statistic)"
        xlab = "Chi-Square (χ²) Association Score (Train Split)"
    else:
        mw_vals = [f["malware_pct"] for f in ordered]
        bg_vals = [f["benign_pct"] for f in ordered]
        fig.add_trace(
            go.Bar(
                y=names,
                x=mw_vals,
                name="Malware Prevalence (%)",
                orientation="h",
                marker=dict(color="#ef4444"),
                hovertemplate="<b>%{y}</b><br>Present in Malware: %{x:.2f}%<extra></extra>",
            )
        )
        fig.add_trace(
            go.Bar(
                y=names,
                x=bg_vals,
                name="Benign Prevalence (%)",
                orientation="h",
                marker=dict(color="#22d3ee"),
                hovertemplate="<b>%{y}</b><br>Present in Benign: %{x:.2f}%<extra></extra>",
            )
        )
        title = "Top 15 Discriminative Features: Prevalence in Malware vs. Benign Apps"
        xlab = "Prevalence (% of Applications)"

    layout_cfg = {
        **PLOTLY_LAYOUT_BASE,
        "title": title,
        "xaxis_title": xlab,
        "barmode": "group",
        "height": 560,
        "margin": dict(l=215, r=36, t=76, b=44),
        "legend": dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0.0),
    }
    fig.update_layout(**layout_cfg)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(tickfont=dict(family="JetBrains Mono, monospace", size=11))
    return fig

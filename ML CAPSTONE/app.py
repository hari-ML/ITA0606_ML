import os
import html
import tempfile
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(os.environ.get("MODEL_DIR", str(BASE_DIR / "model")))
TEST_APKS_DIR = BASE_DIR / "test_apks"
MAX_APK_UPLOAD_MB = int(os.environ.get("MAX_APK_UPLOAD_MB", "30"))
MAX_APK_UPLOAD_BYTES = MAX_APK_UPLOAD_MB * 1024 * 1024


def _resolve_asset(filename: str, fallback_subdir: str | None = None) -> Path | None:
    """Resolve an artifact cleanly from model/ first, with optional legacy fallback."""
    primary = MODEL_DIR / filename
    if primary.exists():
        return primary
    if fallback_subdir:
        fb = BASE_DIR / fallback_subdir / filename
        if fb.exists():
            return fb
    return None

from styles import load_styles
from src.apk_utils import (
    extract_apk_data,
    build_apk_feature_vector,
    compare_apks,
    DANGEROUS_PERMISSIONS,
)
from src.reference_lookup import (
    search_all_reference_candidates,
    download_and_verify_fdroid_apk,
    fetch_play_metadata,
)
from src.diagnostics import (
    compute_and_cache_diagnostics,
    load_feature_categories,
    get_feature_explanation,
    make_confidence_gauge,
    make_class_donut,
    make_confusion_matrix_chart,
    make_roc_curve_chart,
    make_f1_vs_k_chart,
    make_feature_importance_chart,
)
from src.ui_components import (
    render_hero_header,
    render_how_it_works,
    render_countup_metrics,
    render_radar_scanner,
    render_verdict_card,
    render_permission_chips,
    render_predictions_table,
    render_footer,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & SINGLE GLOBAL CSS LOAD
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Android Malware Detection | Static SVM Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_styles()


# -----------------------------------------------------------------------------
# CACHED REAL ARTIFACT LOADERS (MODELS + PRECOMPUTED REAL DIAGNOSTICS)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_full_model():
    path = _resolve_asset("svm_model.pkl", "models")
    return joblib.load(path) if path is not None else None


@st.cache_resource
def get_apk_model():
    path = _resolve_asset("svm_apk.pkl", "models")
    return joblib.load(path) if path is not None else None


@st.cache_data
def get_diagnostics_data():
    return compute_and_cache_diagnostics(force=False)


@st.cache_data
def get_categories():
    return load_feature_categories()


@st.cache_data
def get_results_tables():
    res_p = _resolve_asset("results.csv", "outputs")
    apk_p = _resolve_asset("results_apk.csv", "outputs")
    full_df = pd.read_csv(res_p) if res_p is not None else None
    apk_df = pd.read_csv(apk_p) if apk_p is not None else None
    return full_df, apk_df


@st.cache_data(ttl=1800, show_spinner=False)
def cached_reference_search(query: str, suspect_pkg: str | None = None, limit: int = 5):
    return search_all_reference_candidates(query, suspect_pkg=suspect_pkg, limit=limit)


diagnostics = get_diagnostics_data()
full_model_art = get_full_model()
apk_model_art = get_apk_model()
cat_dict = get_categories()
results_df, results_apk_df = get_results_tables()

ds_stats = diagnostics["dataset"]
svm_acc_pct = 98.28
if results_df is not None and not results_df.empty:
    svm_rows = results_df[results_df["Model"].str.contains("Support Vector Machine", na=False)]
    if not svm_rows.empty:
        svm_acc_pct = float(svm_rows.iloc[0]["Accuracy"]) * 100.0


# -----------------------------------------------------------------------------
# HERO SECTION & PIPELINE FLOW
# -----------------------------------------------------------------------------
render_hero_header(
    clean_apps=ds_stats["clean_rows"],
    raw_apps=ds_stats["raw_rows"],
    accuracy_pct=svm_acc_pct,
    n_features=ds_stats["full_feature_count"],
)
render_how_it_works()


# -----------------------------------------------------------------------------
# 4 NAVIGATION TABS (PILL-STYLED)
# -----------------------------------------------------------------------------
tab_csv, tab_apk, tab_results, tab_explain = st.tabs([
    "📄 Predict CSV",
    "🛡️ APK Analyzer",
    "📊 Model Results",
    "🧠 Explainability",
])


# =============================================================================
# TAB 1: PREDICT CSV (BATCH FEATURE MATRIX CLASSIFICATION)
# =============================================================================
with tab_csv:
    st.markdown('<div class="section-heading">Batch Feature Matrix Classification (Drebin 215-Feature SVM)</div>', unsafe_allow_html=True)

    if full_model_art is None:
        st.error("Trained model `model/svm_model.pkl` not found. Ensure the `model/` directory is present.")
    else:
        full_feats = full_model_art["all_features"]
        full_selector = full_model_art["selector"]
        full_svm = full_model_art["model"]

        col_up_csv, col_demo_csv = st.columns([2.2, 1])
        with col_up_csv:
            uploaded_csv = st.file_uploader(
                "Upload Drebin Feature CSV (215 permission & API-call binary columns)",
                type=["csv"],
                key="csv_batch_uploader",
                help="Accepts CSV files formatted with the 215 binary Drebin features. Optional 'class' column enables real ground-truth comparison.",
            )
        with col_demo_csv:
            st.markdown(
                """
                <div class="glass-card-static" style="padding: 16px; margin-bottom: 8px;">
                    <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:#f8fafc; margin-bottom:6px;">
                        Held-Out Test Sample
                    </div>
                    <div style="font-size:0.82rem; color:#94a3b8; margin-bottom:10px;">
                        Load the real 20 held-out test records saved in <code class="mono-text">model/sample.csv</code>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            use_sample_clicked = st.button("Load Real Test Sample (20 Apps)", width="stretch", key="btn_load_sample_csv")
            if use_sample_clicked:
                st.session_state["csv_use_sample"] = True
            if uploaded_csv is not None:
                st.session_state["csv_use_sample"] = False

        csv_df = None
        source_label = None
        if uploaded_csv is not None:
            try:
                csv_df = pd.read_csv(uploaded_csv)
                source_label = f"Uploaded CSV: {uploaded_csv.name}"
            except Exception as exc:
                st.error(f"Could not read CSV file: {exc}")
        elif st.session_state.get("csv_use_sample", False):
            sample_path = _resolve_asset("sample.csv", "data")
            if sample_path is not None:
                csv_df = pd.read_csv(sample_path)
                source_label = f"Held-Out Test Split ({sample_path.relative_to(BASE_DIR).as_posix()})"

        if csv_df is not None:
            if csv_df.empty:
                st.warning("The provided CSV contains 0 rows.")
            else:
                st.caption(f"Source loaded: **{source_label}** · Shape: **{len(csv_df):,} rows × {len(csv_df.columns)} columns**")

                # Validate feature overlap before predicting
                matched_cols = [c for c in full_feats if c in csv_df.columns]
                if len(matched_cols) == 0:
                    st.error(
                        "None of the 215 expected Drebin feature columns were found in this CSV. "
                        "Please upload a CSV with binary permission/API feature columns matching the Drebin schema."
                    )
                else:
                    if len(matched_cols) < len(full_feats):
                        st.warning(
                            f"Matched {len(matched_cols)} of {len(full_feats)} feature columns. "
                            "Missing columns are zero-filled before inference."
                        )

                    # Preview table inside expander
                    with st.expander("Preview Uploaded Feature Matrix (First 10 Rows)", expanded=False):
                        st.dataframe(csv_df.head(10), width="stretch")

                    # Build exact feature dataframe in trained order
                    X_batch = pd.DataFrame(0, index=csv_df.index, columns=full_feats)
                    for col in matched_cols:
                        X_batch[col] = pd.to_numeric(csv_df[col], errors="coerce").fillna(0).astype(int)

                    X_batch_sel = full_selector.transform(X_batch)
                    preds = full_svm.predict(X_batch_sel)
                    probs = full_svm.predict_proba(X_batch_sel)[:, 1]
                    margins = full_svm.decision_function(X_batch_sel)

                    mal_count = int((preds == 1).sum())
                    ben_count = int((preds == 0).sum())
                    total_count = len(preds)

                    # Ground truth if 'class' exists
                    has_gt = "class" in csv_df.columns
                    gt_series = None
                    gt_acc_str = None
                    if has_gt:
                        raw_gt = csv_df["class"]
                        if raw_gt.dtype == object:
                            gt_mapped = raw_gt.map({"S": 1, "B": 0, "Malware": 1, "Malicious": 1, "Benign": 0, "1": 1, "0": 0})
                        else:
                            gt_mapped = pd.to_numeric(raw_gt, errors="coerce")
                        if gt_mapped.notna().all():
                            gt_series = gt_mapped.astype(int)
                            correct_gt = int((preds == gt_series.values).sum())
                            gt_acc_str = f"{correct_gt}/{total_count} ({(correct_gt / total_count) * 100:.1f}%)"

                    # Build display dataframe & export CSV
                    display_rows = []
                    for i in range(total_count):
                        row_dict = {
                            "App #": i + 1,
                            "Active Features": int(X_batch.iloc[i].sum()),
                            "Prediction": "Malicious" if preds[i] == 1 else "Benign",
                            "Malware Prob": f"{probs[i] * 100:.2f}%",
                            "SVM Score": f"{margins[i]:+.3f}",
                        }
                        if gt_series is not None:
                            row_dict["Ground Truth"] = "Malicious" if gt_series.iloc[i] == 1 else "Benign"
                            row_dict["Match"] = "Exact" if preds[i] == gt_series.iloc[i] else "Mismatch"
                        display_rows.append(row_dict)

                    res_table_df = pd.DataFrame(display_rows)

                    # Full downloadable output
                    export_df = csv_df.copy()
                    export_df["Predicted_Label"] = ["Malicious" if p == 1 else "Benign" for p in preds]
                    export_df["Malware_Probability"] = [round(float(p), 6) for p in probs]
                    export_df["SVM_Decision_Score"] = [round(float(m), 6) for m in margins]

                    # KPI Row + Donut Chart + Results Table
                    gt_html = (
                        f'<div class="kv-card"><div class="kv-label">Ground-Truth Accuracy</div><div class="kv-val" style="color:#22d3ee;">{html.escape(gt_acc_str)}</div></div>'
                        if gt_acc_str
                        else '<div class="kv-card"><div class="kv-label">Model Used</div><div class="kv-val" style="color:#22d3ee;">SVM (RBF, C=100)</div></div>'
                    )
                    st.markdown(
                        f"""
                        <div class="kv-grid">
                            <div class="kv-card"><div class="kv-label">Total Records Evaluated</div><div class="kv-val">{total_count:,}</div></div>
                            <div class="kv-card"><div class="kv-label">Predicted Malicious</div><div class="kv-val" style="color:#f87171;">{mal_count:,}</div></div>
                            <div class="kv-card"><div class="kv-label">Predicted Benign</div><div class="kv-val" style="color:#34d399;">{ben_count:,}</div></div>
                            {gt_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    col_donut, col_tbl = st.columns([1, 1.55])
                    with col_donut:
                        fig_batch_donut = make_class_donut(ben_count, mal_count, title="Batch Prediction Breakdown")
                        st.plotly_chart(fig_batch_donut, width="stretch", key="csv_donut_chart")

                    with col_tbl:
                        st.markdown('<div style="margin-bottom:8px; font-family:\'Space Grotesk\',sans-serif; font-weight:600; color:#f8fafc;">Classification Results Table</div>', unsafe_allow_html=True)
                        render_predictions_table(res_table_df, max_rows=200)
                        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                        st.download_button(
                            label="Download Predictions CSV",
                            data=export_df.to_csv(index=False).encode("utf-8"),
                            file_name="drebin_svm_predictions.csv",
                            mime="text/csv",
                            width="stretch",
                        )
        else:
            st.markdown(
                """
                <div class="glass-card-static">
                    <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:#f8fafc; margin-bottom:6px;">
                        Ready for Batch Inference
                    </div>
                    <div style="font-size:0.88rem; color:#94a3b8;">
                        Drag and drop a Drebin-formatted CSV on the left or click <strong>Load Real Test Sample (20 Apps)</strong> to run live predictions with <code class="mono-text">model/svm_model.pkl</code>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# TAB 2: APK ANALYZER (STATIC INSPECTION + BACKEND REFERENCE LOOKUP)
# =============================================================================
with tab_apk:
    st.markdown('<div class="section-heading">Static APK Binary Inspector & Backend Reference Verification</div>', unsafe_allow_html=True)

    if apk_model_art is None:
        st.error("APK-compatible model `model/svm_apk.pkl` not found. Ensure the `model/` directory is present.")
    else:
        apk_svm = apk_model_art["model"]
        apk_selector = apk_model_art["selector"]
        matchable_cols = apk_model_art["matchable_features"]
        chi2_scores_apk = apk_selector.scores_

        # Locate real local APKs in test_apks/ if present locally (excluded in Cloud Run)
        local_test_apks = []
        if TEST_APKS_DIR.is_dir():
            local_test_apks = sorted([p.name for p in TEST_APKS_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".apk"])

        col_apk_in, col_ref_in = st.columns([1.15, 1])
        with col_apk_in:
            suspect_file = st.file_uploader(
                f"Upload Suspect APK (.apk, max {MAX_APK_UPLOAD_MB} MB) — Static Analysis Only",
                type=["apk"],
                key="apk_analyzer_uploader",
                help=f"Max {MAX_APK_UPLOAD_MB} MB per upload (Cloud Run 32 MB limit). Parsed statically via Androguard without installation or execution.",
            )
            selected_local_apk = None
            if suspect_file is None and local_test_apks:
                selected_local_apk = st.selectbox(
                    "Or select a real local APK from test_apks/ for live analysis:",
                    options=["— Select a real test APK —"] + local_test_apks,
                    key="apk_local_selector",
                )
        with col_ref_in:
            custom_ref_name = st.text_input(
                "Original App Name (Backend Reference Lookup)",
                placeholder="e.g., NewPipe, Aegis, WhatsApp (blank = auto package lookup)",
                key="apk_ref_name_input",
                help="Searches Local Cache, official F-Droid repository (with SHA-256 verification), and Google Play metadata.",
            )
            st.markdown(
                """
                <div class="glass-card-static" style="padding:12px 16px; margin-top:8px;">
                    <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
                        <strong style="color:#22d3ee;">Backend Lookup Mode:</strong> Automatically resolves the authentic reference app by name or package ID from Local Cache → F-Droid (SHA-256 verified APK) → Google Play (metadata only). No reference APK upload required.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Determine active binary source (uploaded bytes OR real local test APK) with 30 MB Cloud Run guard
        apk_source_bytes = None
        apk_source_path = None
        apk_display_name = None
        apk_size_rejected = False

        if suspect_file is not None:
            if suspect_file.size > MAX_APK_UPLOAD_BYTES:
                size_mb = suspect_file.size / (1024 * 1024)
                st.error(
                    f"Uploaded APK exceeds the {MAX_APK_UPLOAD_MB} MB size limit ({size_mb:.2f} MB). "
                    "Google Cloud Run enforces a 32 MB request body limit; please upload an APK under 30 MB."
                )
                apk_size_rejected = True
            else:
                apk_source_bytes = suspect_file.read()
                if len(apk_source_bytes) > MAX_APK_UPLOAD_BYTES:
                    size_mb = len(apk_source_bytes) / (1024 * 1024)
                    st.error(
                        f"Uploaded APK exceeds the {MAX_APK_UPLOAD_MB} MB size limit ({size_mb:.2f} MB). "
                        "Please upload an APK under 30 MB."
                    )
                    apk_source_bytes = None
                    apk_size_rejected = True
                else:
                    apk_display_name = suspect_file.name
        elif selected_local_apk and selected_local_apk != "— Select a real test APK —":
            candidate_local_path = TEST_APKS_DIR / selected_local_apk
            if candidate_local_path.exists():
                apk_source_path = str(candidate_local_path)
                apk_display_name = selected_local_apk

        # Scenario A: An APK is provided (uploaded or chosen from real test_apks/)
        if not apk_size_rejected and (apk_source_bytes is not None or apk_source_path is not None):
            scanner_placeholder = st.empty()

            # Stage 1: Real extraction
            scanner_placeholder.markdown(
                render_radar_scanner(
                    "Extracting permissions & manifest...",
                    f"Disassembling {apk_display_name} statically with Androguard (no code executed).",
                ),
                unsafe_allow_html=True,
            )
            if apk_source_bytes is not None:
                suspect_data = extract_apk_data(apk_source_bytes, is_bytes=True)
            else:
                suspect_data = extract_apk_data(apk_source_path, is_bytes=False)

            if not suspect_data.get("success", False):
                scanner_placeholder.empty()
                st.error(f"Static Unpacking Failed: {suspect_data.get('error', 'Corrupt or invalid APK file.')}")
            else:
                suspect_pkg = suspect_data.get("package_name", "Unknown")

                # Stage 2: Real feature vector mapping
                scanner_placeholder.markdown(
                    render_radar_scanner(
                        "Mapping API calls & building feature vector...",
                        f"Scanning {suspect_data.get('dex_count', 0)} DEX block(s) across 186 static Drebin signatures.",
                    ),
                    unsafe_allow_html=True,
                )
                X_apk = build_apk_feature_vector(suspect_data, matchable_cols)
                X_apk_sel = apk_selector.transform(X_apk)

                # Stage 3: Real SVM classifier + backend reference lookup
                ref_query = custom_ref_name.strip() if custom_ref_name.strip() else suspect_pkg
                scanner_placeholder.markdown(
                    render_radar_scanner(
                        "Running SVM classifier & backend reference lookup...",
                        f"Evaluating calibrated RBF SVM and querying backend reference for '{ref_query}'.",
                    ),
                    unsafe_allow_html=True,
                )
                ml_pred = int(apk_svm.predict(X_apk_sel)[0])
                ml_proba = float(apk_svm.predict_proba(X_apk_sel)[0, 1])
                ml_decision = float(apk_svm.decision_function(X_apk_sel)[0])
                ml_risk_pct = ml_proba * 100.0

                candidates, lookup_status = cached_reference_search(
                    ref_query, suspect_pkg=suspect_pkg, limit=5
                )

                # Done scanning -> clear radar box
                scanner_placeholder.empty()

                # Risk Band Assignment
                if ml_risk_pct < 30.0:
                    risk_band = "Low Risk (< 30%)"
                elif ml_risk_pct <= 70.0:
                    risk_band = "Medium Risk (30% - 70%)"
                else:
                    risk_band = "High Risk (> 70%)"

                is_malicious = ml_pred == 1
                if is_malicious:
                    verdict_label = "MALICIOUS"
                elif ml_risk_pct >= 30.0:
                    verdict_label = "BENIGN (ELEVATED)"
                else:
                    verdict_label = "BENIGN"

                # --- Verdict Card + Plotly Confidence Gauge ---
                v_left, v_right = st.columns([1.25, 1])
                with v_left:
                    render_verdict_card(is_malicious, verdict_label, ml_risk_pct, ml_decision, risk_band)
                with v_right:
                    st.plotly_chart(
                        make_confidence_gauge(ml_risk_pct, is_malicious),
                        width="stretch",
                        key="apk_confidence_gauge",
                    )

                # --- Static Binary Telemetry Matrix ---
                st.markdown('<div class="section-heading">Extracted APK Telemetry & Cryptographic Fingerprint</div>', unsafe_allow_html=True)
                cert_fp = html.escape(str(suspect_data.get("cert_sha256", "UNKNOWN")))
                st.markdown(
                    f"""
                    <div class="kv-grid">
                        <div class="kv-card"><div class="kv-label">Package Identifier</div><div class="kv-val mono-text">{html.escape(suspect_pkg)}</div></div>
                        <div class="kv-card"><div class="kv-label">Version</div><div class="kv-val">{html.escape(str(suspect_data.get('version_name')))} ({html.escape(str(suspect_data.get('version_code')))})</div></div>
                        <div class="kv-card"><div class="kv-label">Binary Size & DEX</div><div class="kv-val">{html.escape(str(suspect_data.get('file_size_str')))} · {suspect_data.get('dex_count', 0)} DEX</div></div>
                        <div class="kv-card"><div class="kv-label">SDK Target</div><div class="kv-val">Min {html.escape(str(suspect_data.get('min_sdk')))} / Target {html.escape(str(suspect_data.get('target_sdk')))}</div></div>
                        <div class="kv-card"><div class="kv-label">Activities / Services</div><div class="kv-val">{suspect_data.get('activities_count', 0)} / {suspect_data.get('services_count', 0)}</div></div>
                        <div class="kv-card"><div class="kv-label">Receivers / Providers</div><div class="kv-val">{suspect_data.get('receivers_count', 0)} / {suspect_data.get('providers_count', 0)}</div></div>
                        <div class="kv-card"><div class="kv-label">Declared Permissions</div><div class="kv-val">{suspect_data.get('requested_perms_count', 0)}</div></div>
                        <div class="kv-card"><div class="kv-label">Dangerous Flagged</div><div class="kv-val" style="color:{'#f87171' if suspect_data.get('dangerous_permissions') else '#34d399'};">{len(suspect_data.get('dangerous_permissions', []))}</div></div>
                    </div>
                    <div class="glass-card-static" style="padding: 12px 18px;">
                        <span style="font-size:0.78rem; color:#94a3b8;">Signing Certificate SHA-256: </span>
                        <code class="mono-text" style="color:#22d3ee; word-break:break-all;">{cert_fp}</code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # --- Permissions Risk Chips & Suspicious API Calls List ---
                all_requested_perms = sorted(list(suspect_data.get("permissions", [])))
                vec_series = X_apk.iloc[0]
                matched_features = [col for col in matchable_cols if vec_series[col] == 1]
                matched_count = len(matched_features)
                coverage_pct = (matched_count / len(matchable_cols)) * 100.0

                col_perms, col_apis = st.columns([1.05, 1])
                with col_perms:
                    st.markdown('<div class="section-heading">Extracted Permissions (Risk Chips)</div>', unsafe_allow_html=True)
                    with st.container(border=True):
                        st.caption(
                            f"Total Declared: {len(all_requested_perms)} · "
                            f"High-Risk Dangerous: {len(suspect_data.get('dangerous_permissions', []))} "
                            "(Red = High Risk, Orange = Sensitive System, Cyan = Standard)"
                        )
                        render_permission_chips(all_requested_perms, DANGEROUS_PERMISSIONS)

                with col_apis:
                    st.markdown('<div class="section-heading">Matched Model API Calls & Signatures</div>', unsafe_allow_html=True)
                    with st.container(border=True):
                        st.markdown(f"**Model Feature Coverage:** `{matched_count}` of `{len(matchable_cols)}` static features (**{coverage_pct:.1f}%**)")
                        st.progress(min(1.0, matched_count / float(len(matchable_cols))))
                        if matched_count < (len(matchable_cols) / 2.0):
                            st.caption(
                                f"Low coverage ({coverage_pct:.1f}% < 50%): Modern APKs use newer AndroidX/Kotlin APIs outside the Drebin signature catalog."
                            )

                        api_rows = []
                        for mf in matched_features:
                            idx = matchable_cols.index(mf)
                            c_score = float(chi2_scores_apk[idx]) if idx < len(chi2_scores_apk) else 0.0
                            f_cat = cat_dict.get(mf, "API call signature")
                            api_rows.append({
                                "Signature": mf,
                                "Type": f_cat,
                                "Chi² Weight": round(c_score, 2),
                            })
                        api_rows.sort(key=lambda x: x["Chi² Weight"], reverse=True)
                        if api_rows:
                            api_df = pd.DataFrame(api_rows)
                            st.dataframe(api_df.head(15), width="stretch", hide_index=True, height=300)
                            if len(api_rows) > 15:
                                with st.expander(f"View All {len(api_rows)} Matched Static Signatures"):
                                    st.dataframe(api_df, width="stretch", hide_index=True)
                        else:
                            st.info("No matching Drebin API/permission signatures detected.")

                # --- Automated Backend Reference Lookup & Differential Analysis ---
                st.markdown('<div class="section-heading">Backend Reference Verification (Differential Integrity)</div>', unsafe_allow_html=True)
                with st.expander(f"Reference Lookup Results for '{ref_query}' ({len(candidates)} candidate(s) found)", expanded=True):
                    st.caption(lookup_status)
                    if not candidates:
                        st.info(f"No matching reference app found for '{ref_query}'. Displaying standalone static inspection above.")
                    else:
                        selected_cand = st.selectbox(
                            "Confirm authentic reference application:",
                            options=candidates,
                            format_func=lambda c: c["display_name"],
                            key="ref_candidate_select",
                        )
                        chosen_pkg = selected_cand.get("package_id", "")
                        cand_source = selected_cand.get("source", "Unknown")

                        if suspect_pkg != "Unknown" and chosen_pkg and suspect_pkg != chosen_pkg:
                            st.warning(
                                f"Package ID Mismatch: Suspect declares `{suspect_pkg}`, while selected reference is `{chosen_pkg}`."
                            )

                        # Full Binary Mode (Local Cache or F-Droid)
                        if "F-Droid" in cand_source or "Local Cache" in cand_source:
                            ref_apk_path = None
                            if cand_source == "Local Cache" and selected_cand.get("local_path"):
                                ref_apk_path = selected_cand["local_path"]
                                dl_ok, dl_msg = True, "Loaded from verified local reference cache."
                            else:
                                with st.spinner("Fetching reference APK from F-Droid & verifying SHA-256..."):
                                    dl_ok, dl_msg, ref_apk_path = download_and_verify_fdroid_apk(selected_cand)

                            if not dl_ok or not ref_apk_path:
                                st.error(f"Reference acquisition failed: {dl_msg}")
                            else:
                                try:
                                    orig_data = extract_apk_data(ref_apk_path)
                                finally:
                                    # Clean up temp-downloaded F-Droid binary immediately to preserve Cloud Run RAM
                                    tmp_root = Path(tempfile.gettempdir()).resolve()
                                    ref_p = Path(ref_apk_path).resolve()
                                    if tmp_root in ref_p.parents:
                                        ref_p.unlink(missing_ok=True)
                                if not orig_data.get("success", False):
                                    st.error(f"Reference extraction failed: {orig_data.get('error')}")
                                else:
                                    X_ref = build_apk_feature_vector(orig_data, matchable_cols)
                                    X_ref_sel = apk_selector.transform(X_ref)
                                    ref_pred = int(apk_svm.predict(X_ref_sel)[0])
                                    ref_risk = float(apk_svm.predict_proba(X_ref_sel)[0, 1]) * 100.0
                                    comp = compare_apks(suspect_data, orig_data, ml_risk_pct)

                                    st.markdown(
                                        f"""
                                        <div class="kv-grid">
                                            <div class="kv-card"><div class="kv-label">Mode / Source</div><div class="kv-val" style="color:#22d3ee;">Full ({html.escape(cand_source)})</div></div>
                                            <div class="kv-card"><div class="kv-label">Reference ML Score</div><div class="kv-val">{'MALWARE' if ref_pred == 1 else 'BENIGN'} ({ref_risk:.2f}%)</div></div>
                                            <div class="kv-card"><div class="kv-label">Cert SHA-256 Status</div><div class="kv-val" style="color:{'#34d399' if comp['cert_status']=='MATCH' else '#f87171'};">{html.escape(comp['cert_status'])}</div></div>
                                            <div class="kv-card"><div class="kv-label">Composite Tampering Risk</div><div class="kv-val" style="color:{'#f87171' if comp['final_risk_score']>=60 else ('#fb923c' if comp['final_risk_score']>=30 else '#34d399')};">{comp['final_risk_score']}%</div></div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    st.caption(
                                        f"Formula: {comp['formula']} · Added Dangerous Permissions: {len(comp['extra_dangerous_permissions'])}. "
                                        "Note: F-Droid may re-sign open-source builds with its own key, so a mismatch vs developer builds is not always malicious."
                                    )
                                    c_add, c_rem, c_shr = st.columns(3)
                                    with c_add:
                                        st.markdown(f"**Added Permissions ({len(comp['extra_permissions'])})**")
                                        if comp["extra_permissions"]:
                                            render_permission_chips(comp["extra_permissions"], DANGEROUS_PERMISSIONS)
                                        else:
                                            st.write("None added.")
                                    with c_rem:
                                        st.markdown(f"**Removed Permissions ({len(comp['missing_permissions'])})**")
                                        st.write(", ".join(comp["missing_permissions"][:12]) if comp["missing_permissions"] else "None removed.")
                                    with c_shr:
                                        st.markdown(f"**Shared Permissions ({len(comp['shared_permissions'])})**")
                                        st.write(f"{len(comp['shared_permissions'])} matching manifest declarations.")

                        # Metadata-Only Mode (Google Play)
                        elif "Google Play" in cand_source:
                            st.info(f"Metadata-Only Mode (Source: Google Play) for `{chosen_pkg}` — Certificate comparison not possible without binary.")
                            with st.spinner("Querying Google Play Store metadata..."):
                                play_ok, play_data, play_msg = fetch_play_metadata(chosen_pkg)
                            if not play_ok:
                                st.error(f"Google Play lookup failed: {play_msg}")
                            else:
                                meta_df = pd.DataFrame({
                                    "Attribute": ["App Title", "Package ID", "Developer", "Version", "Installs"],
                                    "Suspect APK": [suspect_pkg, suspect_pkg, "Local Binary", suspect_data.get("version_name"), "Local File"],
                                    "Google Play Store": [play_data["title"], play_data["package_id"], play_data["developer"], play_data["version"], play_data.get("installs", "N/A")],
                                })
                                st.dataframe(meta_df, width="stretch", hide_index=True)

        # Scenario B: User entered an app name without uploading an APK yet -> show live backend reference lookup!
        elif custom_ref_name.strip():
            q_only = custom_ref_name.strip()
            with st.spinner(f"Querying backend repositories for '{q_only}'..."):
                cands, st_msg = cached_reference_search(q_only, None, limit=5)
            st.info(f"Backend Reference Lookup for **{q_only}**: {st_msg}")
            if cands:
                sel_c = st.selectbox(
                    "Found official reference candidates (upload a suspect `.apk` above to run differential comparison):",
                    options=cands,
                    format_func=lambda c: c["display_name"],
                    key="ref_only_select",
                )
                if "F-Droid" in sel_c.get("source", "") or "Local Cache" in sel_c.get("source", ""):
                    if st.button("Fetch F-Droid Official APK & Run Static Scan", key="btn_scan_fdroid_ref"):
                        with st.spinner("Downloading & verifying SHA-256 hash from F-Droid..."):
                            ok_dl, msg_dl, path_dl = download_and_verify_fdroid_apk(sel_c)
                        if not ok_dl:
                            st.error(msg_dl)
                        else:
                            st.success(f"{msg_dl} — Analyzing verified binary...")
                            try:
                                ref_data = extract_apk_data(path_dl)
                            finally:
                                tmp_root = Path(tempfile.gettempdir()).resolve()
                                ref_p = Path(path_dl).resolve()
                                if tmp_root in ref_p.parents:
                                    ref_p.unlink(missing_ok=True)
                            if ref_data.get("success"):
                                X_r = build_apk_feature_vector(ref_data, matchable_cols)
                                X_rs = apk_selector.transform(X_r)
                                r_pred = int(apk_svm.predict(X_rs)[0])
                                r_prob = float(apk_svm.predict_proba(X_rs)[0, 1]) * 100.0
                                r_dec = float(apk_svm.decision_function(X_rs)[0])
                                r_band = "Low Risk (< 30%)" if r_prob < 30 else ("Medium Risk (30% - 70%)" if r_prob <= 70 else "High Risk (> 70%)")
                                c1, c2 = st.columns([1.2, 1])
                                with c1:
                                    render_verdict_card(r_pred == 1, "MALICIOUS" if r_pred == 1 else "BENIGN", r_prob, r_dec, r_band)
                                with c2:
                                    st.plotly_chart(make_confidence_gauge(r_prob, r_pred == 1), width="stretch", key="ref_only_gauge")
                                st.markdown("**Extracted Permissions:**")
                                render_permission_chips(sorted(list(ref_data.get("permissions", []))), DANGEROUS_PERMISSIONS)
                elif "Google Play" in sel_c.get("source", ""):
                    ok_p, p_data, p_msg = fetch_play_metadata(sel_c["package_id"])
                    if ok_p:
                        st.markdown(f"**{p_data['title']}** (`{p_data['package_id']}`) by **{p_data['developer']}** · Version: `{p_data['version']}` · Installs: `{p_data.get('installs', 'N/A')}`")
                        if p_data.get("listed_permissions"):
                            with st.expander(f"View {len(p_data['listed_permissions'])} Listed Play Store Permissions"):
                                for lp in p_data["listed_permissions"]:
                                    st.write(f"- {lp}")
        else:
            st.markdown(
                """
                <div class="glass-card-static">
                    <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:#f8fafc; margin-bottom:6px;">
                        Ready for Static Binary Inspection
                    </div>
                    <div style="font-size:0.88rem; color:#94a3b8;">
                        Upload any suspect <code class="mono-text">.apk</code> package or pick a verified binary from <code class="mono-text">test_apks/</code> to run Androguard extraction, SVM malware scoring, risk chip categorization, and automated reference verification.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# TAB 3: MODEL RESULTS (REAL BENCHMARKS + INTERACTIVE PLOTLY CHARTS)
# =============================================================================
with tab_results:
    st.markdown('<div class="section-heading">Model Performance & Real Benchmark Evaluation</div>', unsafe_allow_html=True)

    # Pull real SVM metrics from outputs/results.csv
    acc_v, prec_v, rec_v, f1_v, auc_v = 98.28, 97.05, 95.64, 96.34, 0.9943
    if results_df is not None and not results_df.empty:
        svm_r = results_df[results_df["Model"].str.contains("Support Vector Machine", na=False)]
        if not svm_r.empty:
            r0 = svm_r.iloc[0]
            acc_v = float(r0["Accuracy"]) * 100.0
            prec_v = float(r0["Precision"]) * 100.0
            rec_v = float(r0["Recall"]) * 100.0
            f1_v = float(r0["F1-Score"]) * 100.0
            auc_v = float(r0["ROC-AUC"])

    # Count-up JS animated metric cards (Accuracy, Precision, Recall, F1)
    render_countup_metrics([
        {"label": "SVM Test Accuracy", "value": acc_v, "suffix": "%", "sub": f"n = {ds_stats['test_rows']:,} test apps"},
        {"label": "Precision", "value": prec_v, "suffix": "%", "sub": "Low false-alarm rate"},
        {"label": "Recall (Sensitivity)", "value": rec_v, "suffix": "%", "sub": "329 / 344 malware caught"},
        {"label": "F1-Score (Balanced)", "value": f1_v, "suffix": "%", "sub": f"ROC-AUC = {auc_v:.4f}"},
    ])

    # Dataset Size, Split & SVM Hyperparameter Cards
    svm_p = diagnostics.get("svm_params", {})
    apk_p = diagnostics.get("svm_apk_params", {})
    st.markdown(
        f"""
        <div class="kv-grid">
            <div class="kv-card"><div class="kv-label">Cleaned Dataset Size</div><div class="kv-val">{ds_stats['clean_rows']:,} Unique Apps</div></div>
            <div class="kv-card"><div class="kv-label">Stratified 80/20 Split</div><div class="kv-val">{ds_stats['train_rows']:,} Train / {ds_stats['test_rows']:,} Test</div></div>
            <div class="kv-card"><div class="kv-label">Full SVM Kernel & Params</div><div class="kv-val mono-text">{html.escape(str(svm_p.get('kernel','rbf')).upper())} · C={svm_p.get('C',100)} · γ={svm_p.get('gamma','scale')}</div></div>
            <div class="kv-card"><div class="kv-label">APK Subset SVM Params</div><div class="kv-val mono-text">{html.escape(str(apk_p.get('kernel','rbf')).upper())} · C={apk_p.get('C',10)} · {ds_stats['apk_feature_count']} feats</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Comparison Table (SVM vs Random Forest, Logistic Regression, XGBoost, KNN)
    if results_df is not None:
        st.markdown('<div class="section-heading">Model Comparison Table (Same Stratified Test Split)</div>', unsafe_allow_html=True)
        fmt_df = results_df.copy()
        for col in ["Accuracy", "Precision", "Recall", "F1-Score"]:
            if col in fmt_df.columns:
                fmt_df[col] = fmt_df[col].apply(lambda x: f"{float(x) * 100:.2f}%")
        if "ROC-AUC" in fmt_df.columns:
            fmt_df["ROC-AUC"] = fmt_df["ROC-AUC"].apply(lambda x: f"{float(x):.4f}")
        st.dataframe(fmt_df, width="stretch", hide_index=True)

    if results_apk_df is not None:
        with st.expander("View APK-Compatible Subset Model Performance (186 Static Features)", expanded=False):
            fmt_apk = results_apk_df.copy()
            for col in ["Accuracy", "Precision", "Recall", "F1-Score"]:
                if col in fmt_apk.columns:
                    fmt_apk[col] = fmt_apk[col].apply(lambda x: f"{float(x) * 100:.2f}%")
            if "ROC-AUC" in fmt_apk.columns:
                fmt_apk["ROC-AUC"] = fmt_apk["ROC-AUC"].apply(lambda x: f"{float(x):.4f}")
            st.dataframe(fmt_apk, width="stretch", hide_index=True)

    # Interactive Plotly Diagnostics Grid
    c_cm, c_roc = st.columns(2)
    with c_cm:
        st.plotly_chart(make_confusion_matrix_chart(diagnostics["confusion_matrix"]), width="stretch", key="res_cm")
    with c_roc:
        st.plotly_chart(make_roc_curve_chart(diagnostics["roc_curves"]), width="stretch", key="res_roc")

    c_donut, c_k = st.columns(2)
    with c_donut:
        st.plotly_chart(
            make_class_donut(ds_stats["benign_count"], ds_stats["malware_count"], title="Cleaned Drebin Class Distribution"),
            width="stretch",
            key="res_donut",
        )
    with c_k:
        st.plotly_chart(make_f1_vs_k_chart(diagnostics["f1_vs_k"]), width="stretch", key="res_k")


# =============================================================================
# TAB 4: EXPLAINABILITY (INTERACTIVE FEATURE BAR CHART + PLAIN-TEXT INSIGHTS)
# =============================================================================
with tab_explain:
    st.markdown('<div class="section-heading">Model Interpretability: Permissions & API Calls Driving Predictions</div>', unsafe_allow_html=True)

    top_feats = diagnostics["top_features"]
    col_ctrl, _ = st.columns([1.4, 2])
    with col_ctrl:
        chart_mode = st.selectbox(
            "Chart Metric View:",
            options=["Malware vs. Benign Prevalence (%)", "Chi-Square (χ²) Importance Score"],
            key="explain_chart_mode",
        )

    metric_arg = "prevalence" if "Prevalence" in chart_mode else "chi2"
    st.plotly_chart(
        make_feature_importance_chart(top_feats, metric=metric_arg),
        width="stretch",
        key="explain_top_features_chart",
    )

    st.markdown('<div class="section-heading">Why Each Top Feature Matters for Android Malware Detection</div>', unsafe_allow_html=True)

    # Render clean 2-column glass cards explaining each top feature in plain English
    left_cards, right_cards = st.columns(2)
    for idx, feat in enumerate(top_feats):
        target_col = left_cards if idx % 2 == 0 else right_cards
        f_name = html.escape(feat["feature"])
        f_cat = html.escape(feat["category"])
        mw_pct = feat["malware_pct"]
        bg_pct = feat["benign_pct"]
        chi2_val = feat["chi2_score"]
        expl = html.escape(feat.get("explanation") or get_feature_explanation(feat["feature"], feat["category"], mw_pct, bg_pct))

        is_mw_driver = mw_pct >= bg_pct
        signal_badge = (
            '<span class="badge-malicious">Malware Risk Driver</span>'
            if is_mw_driver
            else '<span class="badge-benign">Benign Architecture Signal</span>'
        )
        with target_col:
            st.markdown(
                f"""
                <div class="glass-card" style="padding:16px 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                        <code class="mono-text" style="font-size:0.95rem; font-weight:600; color:#22d3ee;">#{idx + 1} · {f_name}</code>
                        {signal_badge}
                    </div>
                    <div style="font-size:0.78rem; color:#94a3b8; margin-bottom:8px;">
                        Type: <strong style="color:#cbd5e1;">{f_cat}</strong> · χ² Score: <strong style="color:#f8fafc;">{chi2_val:.2f}</strong> · Malware: <strong style="color:#f87171;">{mw_pct:.1f}%</strong> vs Benign: <strong style="color:#34d399;">{bg_pct:.1f}%</strong>
                    </div>
                    <div style="font-size:0.86rem; color:#e2e8f0; line-height:1.5;">
                        {expl}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    shap_img_path = _resolve_asset("shap_summary.png", "outputs")
    if shap_img_path is not None:
        with st.expander("View Saved Training SHAP Beeswarm Plot (Random Forest TreeExplainer on 200 Test Apps)", expanded=False):
            st.image(
                str(shap_img_path),
                caption="SHAP Feature Attribution computed on identical selected Drebin features",
                width="stretch",
            )


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
render_footer()

"""
Reusable UI component builders for the Cybersecurity Static Malware Dashboard.
Relies strictly on CSS classes from styles.py and real model/APK values.
"""
import html
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

ELEVATED_SENSITIVE_PERMISSIONS = {
    "RECEIVE_BOOT_COMPLETED",
    "WRITE_EXTERNAL_STORAGE",
    "READ_EXTERNAL_STORAGE",
    "CAMERA",
    "ACCESS_COARSE_LOCATION",
    "CALL_PHONE",
    "GET_ACCOUNTS",
    "MANAGE_ACCOUNTS",
    "WRITE_SETTINGS",
    "GET_TASKS",
    "KILL_BACKGROUND_PROCESSES",
    "WAKE_LOCK",
    "INTERNET",
    "ACCESS_NETWORK_STATE",
}


@st.cache_data
def load_lottie_file(filepath: str):
    """Load a local Lottie JSON animation safely via pathlib."""
    p = Path(filepath)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def render_hero_header(clean_apps: int, raw_apps: int, accuracy_pct: float, n_features: int) -> None:
    """Render the animated gradient hero section with 3 real stat chips and optional Lottie shield."""
    lottie_shield = load_lottie_file(str(ASSETS_DIR / "shield_pulse.json"))

    col_hero, col_anim = st.columns([5, 1]) if lottie_shield else (st.container(), None)

    with col_hero:
        st.markdown(
            f"""
            <div class="hero-banner">
                <div class="hero-eyebrow">
                    <span class="live-dot"></span>
                    STATIC MALWARE INTELLIGENCE ENGINE · SVM KERNEL
                </div>
                <h1 class="hero-title">Android Malware Detection Using Permission and API-Call Features with SVM</h1>
                <p class="hero-subtitle">
                    Zero-execution static bytecode and manifest inspector classifying malicious Android packages via Chi-Square feature selection and RBF Support Vector Machines.
                </p>
                <div class="stat-chips-row">
                    <div class="stat-chip">
                        <span>Dataset:</span>
                        <strong>{clean_apps:,} Unique Apps</strong>
                        <span>({raw_apps:,} raw)</span>
                    </div>
                    <div class="stat-chip">
                        <span>Tuned SVM Accuracy:</span>
                        <strong>{accuracy_pct:.2f}%</strong>
                    </div>
                    <div class="stat-chip">
                        <span>Feature Space:</span>
                        <strong>{n_features} Signatures</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if col_anim is not None and lottie_shield is not None:
        with col_anim:
            st_lottie(lottie_shield, height=160, key="hero_shield_lottie", speed=1.0, loop=True)
            st.markdown(
                "<div style='text-align:center; font-family:\"Space Grotesk\",sans-serif; font-size:0.78rem; color:#22d3ee; font-weight:600; margin-top:-6px;'>ACTIVE SHIELD TELEMETRY</div>",
                unsafe_allow_html=True,
            )


def render_how_it_works() -> None:
    """Render the 5-step connected pipeline flow below the hero."""
    steps = [
        ("STEP 01", "APK Binary", "Upload Android package or feature matrix without execution."),
        ("STEP 02", "Permission & API Extraction", "Parse AndroidManifest & Dalvik DEX method signatures."),
        ("STEP 03", "Feature Vector", "Encode binary presence vector across Chi² selected features."),
        ("STEP 04", "SVM Classifier", "Evaluate RBF decision hyperplane & probability calibration."),
        ("STEP 05", "Verdict & Audit", "Output Malicious/Benign verdict, risk chips & explainability."),
    ]
    cards_html = []
    for idx, (badge, title, desc) in enumerate(steps, start=1):
        cards_html.append(
            f'<div class="pipeline-step stagger-{idx}">'
            f'<div class="step-badge">{badge}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="pipeline-flow">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def render_countup_metrics(metrics: list) -> None:
    """
    Render 4 animated metric cards counting up smoothly from 0 to their real values
    using a minimal self-contained JS snippet inside st.components.v1.html.
    metrics = [{"label": "Accuracy", "value": 98.28, "suffix": "%", "sub": "Test Set"}]
    """
    cards_markup = []
    for idx, m in enumerate(metrics):
        val = float(m["value"])
        label = html.escape(str(m["label"]))
        suffix = html.escape(str(m.get("suffix", "%")))
        sub = html.escape(str(m.get("sub", "")))
        decimals = int(m.get("decimals", 2))
        cards_markup.append(
            f"""
            <div class="m-card" style="animation-delay: {idx * 0.08}s;">
                <div class="m-label">{label}</div>
                <div class="m-value" data-target="{val}" data-suffix="{suffix}" data-decimals="{decimals}">0{suffix}</div>
                <div class="m-sub">{sub}</div>
            </div>
            """
        )

    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: transparent;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            padding: 4px 2px;
        }}
        @media (max-width: 720px) {{
            .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        .m-card {{
            background: rgba(18, 26, 51, 0.72);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 18px 18px;
            box-shadow: 0 10px 26px -10px rgba(0, 0, 0, 0.55);
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }}
        .m-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(34, 211, 238, 0.42);
            box-shadow: 0 14px 32px -12px rgba(34, 211, 238, 0.25);
        }}
        .m-label {{
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
            margin-bottom: 6px;
        }}
        .m-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 30px;
            font-weight: 700;
            color: #22d3ee;
            line-height: 1.1;
            margin-bottom: 4px;
        }}
        .m-sub {{
            font-size: 11.5px;
            color: #64748b;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    </head>
    <body>
        <div class="grid">
            {''.join(cards_markup)}
        </div>
        <script>
            const els = document.querySelectorAll('.m-value');
            els.forEach((el) => {{
                const target = parseFloat(el.dataset.target);
                const suffix = el.dataset.suffix || '';
                const decimals = parseInt(el.dataset.decimals || '2', 10);
                const duration = 900;
                const start = performance.now();
                function step(now) {{
                    const p = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - p, 3);
                    const current = target * eased;
                    el.textContent = current.toFixed(decimals) + suffix;
                    if (p < 1) requestAnimationFrame(step);
                    else el.textContent = target.toFixed(decimals) + suffix;
                }}
                requestAnimationFrame(step);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_doc, height=134)


def render_radar_scanner(status_text: str, detail_text: str) -> str:
    """Return HTML markup for the animated radar/pulse scanner box."""
    s_txt = html.escape(status_text)
    d_txt = html.escape(detail_text)
    return f"""
    <div class="radar-scanner-box">
        <div class="radar-disc"></div>
        <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; font-weight: 600; color: #22d3ee; margin-bottom: 4px;">
                {s_txt}
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8;">
                {d_txt}
            </div>
        </div>
    </div>
    """


def render_verdict_card(is_malicious: bool, verdict_label: str, risk_pct: float, decision_score: float, risk_band: str) -> None:
    """Render the animated Malicious (red shake + glow) or Benign (green check + glow) verdict card."""
    card_cls = "verdict-malicious" if is_malicious else "verdict-benign"
    icon_cls = "verdict-icon-warn" if is_malicious else "verdict-icon-check"
    icon_char = "⚠️" if is_malicious else "✓"
    title_color = "#f87171" if is_malicious else "#34d399"
    v_label = html.escape(verdict_label)
    r_band = html.escape(risk_band)

    st.markdown(
        f"""
        <div class="verdict-card {card_cls}">
            <div style="display:flex; align-items:center; gap:14px;">
                <div class="{icon_cls}">{icon_char}</div>
                <div>
                    <div style="font-size:0.78rem; color:#94a3b8; font-weight:600;">STATIC SVM CLASSIFICATION VERDICT</div>
                    <div class="verdict-title" style="color:{title_color}; margin:2px 0 0 0;">{v_label}</div>
                </div>
            </div>
            <div style="margin-top:16px; display:flex; flex-wrap:wrap; gap:14px; font-size:0.86rem; color:#cbd5e1;">
                <span>Risk Band: <strong style="color:#f8fafc;">{r_band}</strong></span>
                <span>SVM Margin: <strong class="mono-text" style="color:#22d3ee;">{decision_score:+.3f}</strong></span>
                <span>Probability: <strong style="color:{title_color};">{risk_pct:.2f}%</strong></span>
            </div>
            <div style="margin-top:10px; font-size:0.75rem; color:#64748b;">
                Static analysis only (Androguard DEX + Manifest). Fixed threshold bands (&lt;30% Low, 30-70% Medium, &gt;70% High).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_permission_chips(perms: list, dangerous_set: set) -> None:
    """Render Android permissions as colored risk chips (dangerous=red, sensitive=orange, standard=cyan/slate)."""
    if not perms:
        st.info("No permissions declared in AndroidManifest.xml.")
        return

    danger_chips = []
    warn_chips = []
    safe_chips = []

    for p in sorted(perms):
        p_esc = html.escape(str(p))
        if p in dangerous_set:
            danger_chips.append(f'<span class="risk-chip risk-chip-danger">HIGH RISK · {p_esc}</span>')
        elif p in ELEVATED_SENSITIVE_PERMISSIONS:
            warn_chips.append(f'<span class="risk-chip risk-chip-warn">SENSITIVE · {p_esc}</span>')
        else:
            safe_chips.append(f'<span class="risk-chip risk-chip-safe">{p_esc}</span>')

    st.markdown(
        f'<div class="chips-wrap">{"".join(danger_chips + warn_chips + safe_chips)}</div>',
        unsafe_allow_html=True,
    )


def render_predictions_table(df_results: pd.DataFrame, max_rows: int = 100) -> None:
    """Render CSV batch prediction results with colored Malicious/Benign HTML badges."""
    subset = df_results.head(max_rows)
    cols = list(subset.columns)

    headers_html = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols)
    rows_html = []
    for _, row in subset.iterrows():
        cells = []
        for c in cols:
            val = row[c]
            if c == "Prediction":
                if str(val).lower() == "malicious":
                    cells.append('<td><span class="badge-malicious">Malicious</span></td>')
                else:
                    cells.append('<td><span class="badge-benign">Benign</span></td>')
            elif c == "Ground Truth":
                if str(val).lower() == "malicious":
                    cells.append('<td><span class="badge-malicious">Malicious</span></td>')
                else:
                    cells.append('<td><span class="badge-benign">Benign</span></td>')
            else:
                cells.append(f"<td>{html.escape(str(val))}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(
        f"""
        <div class="pred-table-wrap">
            <table class="pred-table">
                <thead><tr>{headers_html}</tr></thead>
                <tbody>{''.join(rows_html)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render consistent footer line with project title, student name, and course."""
    st.markdown(
        """
        <div class="app-footer">
            <div>
                <strong>Android Malware Detection Using Permission and API-Call Features with SVM</strong>
            </div>
            <div>
                Student: <span class="accent">Hareaindiran Sankar</span> (1925260046) · Course: <span class="accent">Machine Learning Capstone</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

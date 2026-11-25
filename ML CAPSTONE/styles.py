"""
Centralized cybersecurity dark glassmorphism theme, typography, layout rules,
and keyframe animations for the Streamlit dashboard.
Loaded once at the top of app.py via load_styles().
"""
import streamlit as st


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-primary: #0b1020;
    --bg-secondary: #121a33;
    --bg-glass: rgba(18, 26, 51, 0.62);
    --bg-glass-strong: rgba(18, 26, 51, 0.82);
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-accent: rgba(34, 211, 238, 0.38);
    --accent: #22d3ee;
    --accent-soft: rgba(34, 211, 238, 0.14);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --danger: #ef4444;
    --danger-bg: rgba(239, 68, 68, 0.14);
    --warn: #f97316;
    --warn-bg: rgba(249, 115, 22, 0.14);
    --success: #10b981;
    --success-bg: rgba(16, 185, 129, 0.14);
    --radius-card: 16px;
    --shadow-soft: 0 12px 32px -10px rgba(0, 0, 0, 0.6);
}

/* 1. REMOVE DEFAULT STREAMLIT CHROME & SET VIEWPORT CONSTRAINTS */
#MainMenu,
footer,
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeaderActionElements"],
.hero-title a,
.stDeployButton,
[data-testid="stAppDeployButton"] {
    visibility: hidden !important;
    display: none !important;
    height: 0 !important;
}

html, body {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    overflow-x: hidden !important;
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(34, 211, 238, 0.09) 0%, transparent 38%),
        radial-gradient(circle at 88% 18%, rgba(34, 211, 238, 0.06) 0%, transparent 42%),
        linear-gradient(180deg, #0b1020 0%, #090e1c 100%) !important;
    color: var(--text-primary);
    overflow-x: hidden !important;
}

/* Preserve Material icons while forcing Inter body + Space Grotesk headings */
.stApp p, .stApp li, .stApp td, .stApp th, .stApp label,
.stApp input, .stApp textarea, .stApp .stMarkdown,
.stApp [data-testid="stCaptionContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, h4, h5, h6,
.hero-title, .section-heading, .step-title, .verdict-title {
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}

.mono-text, code {
    font-family: 'JetBrains Mono', monospace !important;
}

.main .block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 1280px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Custom Thin Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.28);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(34, 211, 238, 0.65);
}

/* 2. KEYFRAME ANIMATIONS */
@keyframes heroGradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulseRing {
    0% { transform: scale(0.85); opacity: 0.85; }
    70% { transform: scale(1.45); opacity: 0; }
    100% { transform: scale(1.45); opacity: 0; }
}

@keyframes radarSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes flowPulse {
    0%, 100% { opacity: 0.35; transform: translateX(0); }
    50% { opacity: 1; transform: translateX(3px); }
}

@keyframes verdictShake {
    0%, 100% { transform: translateX(0); }
    15% { transform: translateX(-6px); }
    30% { transform: translateX(5px); }
    45% { transform: translateX(-4px); }
    60% { transform: translateX(3px); }
    75% { transform: translateX(-2px); }
}

@keyframes checkPop {
    0% { transform: scale(0.7); opacity: 0; }
    60% { transform: scale(1.12); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
}

.fade-in-up {
    animation: fadeSlideUp 0.48s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.12s; }
.stagger-3 { animation-delay: 0.19s; }
.stagger-4 { animation-delay: 0.26s; }
.stagger-5 { animation-delay: 0.33s; }

/* 3. HERO HEADER */
.hero-banner {
    position: relative;
    overflow: hidden;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 16px;
    background: linear-gradient(
        125deg,
        rgba(18, 26, 51, 0.92),
        rgba(14, 34, 61, 0.88),
        rgba(18, 26, 51, 0.94),
        rgba(11, 44, 66, 0.88)
    );
    background-size: 260% 260%;
    animation: heroGradientShift 12s ease infinite, fadeSlideUp 0.5s ease both;
    border: 1px solid rgba(34, 211, 238, 0.24);
    box-shadow: 0 20px 48px -18px rgba(0, 0, 0, 0.72), 0 0 40px -16px rgba(34, 211, 238, 0.22);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.28);
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 12px;
}

.live-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    position: relative;
    display: inline-block;
}
.live-dot::after {
    content: "";
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 2px solid var(--accent);
    animation: pulseRing 1.8s cubic-bezier(0.22, 1, 0.36, 1) infinite;
}

.hero-title {
    font-size: clamp(1.45rem, 2.5vw, 2.05rem);
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 8px 0;
    color: #ffffff !important;
}

.hero-subtitle {
    font-size: 0.98rem;
    line-height: 1.5;
    color: var(--text-secondary);
    margin: 0 0 18px 0;
    max-width: 780px;
}

.stat-chips-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(11, 16, 32, 0.65);
    border: 1px solid var(--border-glass);
    font-size: 0.84rem;
    color: var(--text-secondary);
    transition: transform 0.25s ease, border-color 0.25s ease;
}
.stat-chip:hover {
    transform: translateY(-2px);
    border-color: var(--border-accent);
}
.stat-chip strong {
    color: var(--accent);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
}

/* 4. HOW IT WORKS PIPELINE FLOW */
.pipeline-flow {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}

.pipeline-step {
    position: relative;
    background: var(--bg-glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-card);
    padding: 14px 16px;
    box-shadow: var(--shadow-soft);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.pipeline-step:hover {
    transform: translateY(-4px);
    border-color: var(--border-accent);
    box-shadow: 0 14px 32px -12px rgba(34, 211, 238, 0.24);
}

.pipeline-step:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -11px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--accent);
    font-weight: 700;
    font-size: 14px;
    z-index: 2;
    animation: flowPulse 2.2s ease-in-out infinite;
}

.step-badge {
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 4px;
    font-family: 'Space Grotesk', sans-serif;
}

.step-title {
    font-size: 0.94rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 2px;
}

.step-desc {
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.35;
}

@media (max-width: 960px) {
    .pipeline-flow {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .pipeline-step::after {
        display: none;
    }
}
@media (max-width: 560px) {
    .pipeline-flow {
        grid-template-columns: 1fr;
    }
}

/* 5. GLASSMORPHISM CARDS */
.glass-card {
    background: var(--bg-glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-card);
    padding: 20px 24px;
    box-shadow: var(--shadow-soft);
    margin-bottom: 16px;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.glass-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-accent);
    box-shadow: 0 16px 36px -12px rgba(34, 211, 238, 0.18);
}

.glass-card-static {
    background: var(--bg-glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-card);
    padding: 20px 24px;
    box-shadow: var(--shadow-soft);
    margin-bottom: 16px;
    animation: fadeSlideUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.section-heading {
    font-size: 1.18rem;
    font-weight: 600;
    color: #ffffff;
    margin: 8px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.kv-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 12px 0 16px 0;
}
@media (max-width: 900px) {
    .kv-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 520px) {
    .kv-grid { grid-template-columns: 1fr; }
}

.kv-card {
    background: rgba(18, 26, 51, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-radius: 16px;
    padding: 16px;
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.kv-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-accent);
}
.kv-label {
    font-size: 0.76rem;
    color: var(--text-secondary);
    margin-bottom: 4px;
}
.kv-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f8fafc;
    word-break: break-word;
}

/* 6. PILL TABS WITH ANIMATED ACTIVE INDICATOR */
[data-baseweb="tab-list"],
[role="tablist"] {
    background: rgba(18, 26, 51, 0.78) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 9999px !important;
    padding: 6px !important;
    gap: 6px !important;
    margin-bottom: 20px !important;
    width: fit-content !important;
    max-width: 100% !important;
    flex-wrap: wrap !important;
    box-shadow: var(--shadow-soft) !important;
}

[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    background: transparent !important;
}

button[role="tab"],
[data-baseweb="tab"] {
    border-radius: 9999px !important;
    padding: 9px 20px !important;
    color: var(--text-secondary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
    height: auto !important;
    margin: 0 !important;
}

button[role="tab"]:hover,
[data-baseweb="tab"]:hover {
    color: #ffffff !important;
    background: rgba(34, 211, 238, 0.08) !important;
    transform: translateY(-1px);
}

button[role="tab"][aria-selected="true"],
[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(34, 211, 238, 0.24) 0%, rgba(14, 165, 233, 0.16) 100%) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(34, 211, 238, 0.48) !important;
    border-radius: 9999px !important;
    box-shadow: 0 0 22px rgba(34, 211, 238, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
}

[data-baseweb="tab-panel"] {
    animation: fadeSlideUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* Native glassmorphism container for Plotly charts & bordered Streamlit containers */
[data-testid="stPlotlyChart"],
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background: var(--bg-glass) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 16px !important;
    padding: 14px 16px !important;
    box-shadow: var(--shadow-soft) !important;
    margin-bottom: 14px !important;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease !important;
}

[data-testid="stPlotlyChart"]:hover {
    transform: translateY(-4px);
    border-color: var(--border-accent) !important;
    box-shadow: 0 16px 36px -12px rgba(34, 211, 238, 0.18) !important;
}

/* Blend Lottie iframe seamlessly over dark glassmorphism */
[data-testid="stColumn"]:has(iframe[title*="streamlit_lottie"]) {
    background: linear-gradient(145deg, rgba(18, 26, 51, 0.88), rgba(11, 36, 56, 0.78));
    border: 1px solid rgba(34, 211, 238, 0.24);
    border-radius: 20px;
    padding: 14px 10px 8px 10px;
    box-shadow: 0 20px 44px -18px rgba(0, 0, 0, 0.7), 0 0 30px -16px rgba(34, 211, 238, 0.2);
    backdrop-filter: blur(12px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 16px;
}

iframe[title*="streamlit_lottie"] {
    mix-blend-mode: lighten !important;
    border-radius: 14px;
}

/* 7. BUTTONS, UPLOADERS, SELECTBOXES, INPUTS, TABLES */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #0891b2 0%, #22d3ee 100%) !important;
    color: #06111f !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 1.25rem !important;
    box-shadow: 0 8px 22px -8px rgba(34, 211, 238, 0.5) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 14px 28px -8px rgba(34, 211, 238, 0.68) !important;
    filter: brightness(1.06);
}

[data-testid="stFileUploader"] {
    background: rgba(18, 26, 51, 0.6) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px dashed rgba(34, 211, 238, 0.35) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 24px rgba(34, 211, 238, 0.12);
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: rgba(34, 211, 238, 0.14) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(34, 211, 238, 0.35) !important;
    border-radius: 10px !important;
}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    background-color: rgba(18, 26, 51, 0.78) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.18) !important;
}

[data-testid="stExpander"] {
    background: rgba(18, 26, 51, 0.56) !important;
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass) !important;
    border-radius: 16px !important;
    overflow: hidden;
}

[data-testid="stDataFrame"] {
    background: rgba(18, 26, 51, 0.65) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 16px !important;
    padding: 4px;
    overflow: hidden;
}

[data-testid="stAlert"] {
    background: rgba(18, 26, 51, 0.76) !important;
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass) !important;
    border-radius: 16px !important;
}

/* 8. VERDICT CARDS & RADAR SCANNER */
.verdict-card {
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 220px;
}

.verdict-malicious {
    background: linear-gradient(145deg, rgba(127, 29, 29, 0.36), rgba(18, 26, 51, 0.85));
    border: 1px solid rgba(239, 68, 68, 0.55);
    box-shadow: 0 0 36px rgba(239, 68, 68, 0.28);
    animation: verdictShake 0.65s ease both;
}

.verdict-benign {
    background: linear-gradient(145deg, rgba(6, 78, 59, 0.36), rgba(18, 26, 51, 0.85));
    border: 1px solid rgba(16, 185, 129, 0.55);
    box-shadow: 0 0 36px rgba(16, 185, 129, 0.25);
    animation: fadeSlideUp 0.5s ease both;
}

.verdict-icon-check {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: rgba(16, 185, 129, 0.18);
    border: 1px solid rgba(16, 185, 129, 0.5);
    color: #34d399;
    font-size: 24px;
    animation: checkPop 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.verdict-icon-warn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.55);
    color: #f87171;
    font-size: 24px;
}

.verdict-title {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 12px 0 4px 0;
}

.radar-scanner-box {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 24px;
    border-radius: 16px;
    background: rgba(18, 26, 51, 0.78);
    border: 1px solid rgba(34, 211, 238, 0.35);
    box-shadow: 0 0 28px rgba(34, 211, 238, 0.14);
    margin: 12px 0 20px 0;
}

.radar-disc {
    position: relative;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 2px solid rgba(34, 211, 238, 0.45);
    background: radial-gradient(circle, rgba(34, 211, 238, 0.18) 0%, rgba(11, 16, 32, 0.85) 70%);
    flex-shrink: 0;
    overflow: hidden;
}
.radar-disc::before {
    content: "";
    position: absolute;
    inset: 0;
    background: conic-gradient(from 0deg, rgba(34, 211, 238, 0.65), transparent 110deg);
    border-radius: 50%;
    animation: radarSpin 1.3s linear infinite;
}
.radar-disc::after {
    content: "";
    position: absolute;
    inset: 14px;
    border-radius: 50%;
    border: 1px dashed rgba(34, 211, 238, 0.4);
}

/* 9. RISK & STATUS CHIPS + TABLE BADGES */
.chips-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.risk-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    transition: transform 0.2s ease;
}
.risk-chip:hover {
    transform: translateY(-2px);
}

.risk-chip-danger {
    background: var(--danger-bg);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.45);
}

.risk-chip-warn {
    background: var(--warn-bg);
    color: #fdba74;
    border: 1px solid rgba(249, 115, 22, 0.45);
}

.risk-chip-safe {
    background: rgba(34, 211, 238, 0.08);
    color: #bae6fd;
    border: 1px solid rgba(34, 211, 238, 0.22);
}

/* Custom styled HTML prediction table for colored Malicious/Benign badges */
.pred-table-wrap {
    max-height: 440px;
    overflow-y: auto;
    border-radius: 16px;
    border: 1px solid var(--border-glass);
    background: rgba(18, 26, 51, 0.62);
    backdrop-filter: blur(12px);
}
.pred-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
}
.pred-table th {
    position: sticky;
    top: 0;
    background: #121a33;
    color: var(--accent);
    text-align: left;
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-glass);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    z-index: 2;
}
.pred-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
}
.pred-table tr:hover td {
    background: rgba(34, 211, 238, 0.05);
}

.badge-malicious {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    background: rgba(239, 68, 68, 0.18);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.48);
}

.badge-benign {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.18);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.48);
}

/* 10. FOOTER */
.app-footer {
    margin-top: 36px;
    padding: 18px 24px;
    border-top: 1px solid var(--border-glass);
    background: rgba(18, 26, 51, 0.45);
    border-radius: 16px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    font-size: 0.84rem;
    color: var(--text-secondary);
}
.app-footer strong {
    color: var(--text-primary);
}
.app-footer span.accent {
    color: var(--accent);
    font-weight: 600;
}
</style>
"""


def load_styles() -> None:
    """Inject the complete application theme and animations once into Streamlit."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

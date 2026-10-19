"""

Karandaaz Pakistan

Run locally:   streamlit run app.py
Data files:    put both workbooks in a folder called `data/` next to this file
               (or upload them from the sidebar at runtime).
"""

from __future__ import annotations

import io
import json
import re
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Treasury Income FY 2026-27",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).parent
DATA_DIRS = [APP_DIR / "data", APP_DIR]

FY_START = pd.Timestamp("2026-07-01")
FY_END = pd.Timestamp("2027-06-30")
FY_LABEL = "FY 2026-27"
PY_LABEL = "FY 2025-26"
MONTHS = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]

# Design tokens. Two palettes: the neutrals change with night mode, the accents stay recognisable.
LIGHT = dict(INK="#0B2436", PAPER="#F4F6F8", SURFACE="#FFFFFF", GREEN="#004369", GREEN_DEEP="#002B46",
             BRASS="#DB1F48", SAGE="#7FA9C4", SLATE="#2E7FA8", PLUM="#5E5A8C", RUST="#C41B40",
             MUTED="#5F7484", LINE="#DDE4EA", GRID="#E9EEF2", GREY="#8496A3")
DARK = dict(INK="#E6EEF5", PAPER="#08151F", SURFACE="#0F2233", GREEN="#4E9BD1", GREEN_DEEP="#04172B",
            BRASS="#FF4D6D", SAGE="#8FBEDC", SLATE="#3E86B8", PLUM="#9B8FD0", RUST="#FF5C7A",
            MUTED="#93A9BC", LINE="#1D3448", GRID="#16293A", GREY="#7F94A4")

INK = PAPER = SURFACE = GREEN = GREEN_DEEP = BRASS = SAGE = SLATE = PLUM = RUST = MUTED = LINE = GRID = GREY = ""
DARK_MODE = False

PROGRAM_COLORS: dict = {}
CATEGORY_COLORS: dict = {}
TENOR_COLORS: dict = {}

BANK_NAMES = {
    "BAFL": "Bank Alfalah",
    "UBL": "United Bank",
    "HBL": "Habib Bank",
    "HMBL": "Habib Metropolitan",
    "JSBL": "JS Bank",
    "Faysal": "Faysal Bank",
    "ABL": "Allied Bank",
    "Samba": "Samba Bank",
    "BIPL": "BankIslami",
    "MIB": "MCB Islamic",
    "Meezan": "Meezan Bank",
    "Soneri": "Soneri Bank",
    "NBP": "National Bank",
    "BOP": "Bank of Punjab",
}
BANK_ALIASES = {"HMB": "HMBL", "SAMBA": "Samba", "MEEZAN": "Meezan", "FAYSAL": "Faysal", "SONERI": "Soneri"}

# ─────────────────────────────────────────────────────────────────────────────
# Theme: applied once the night-mode toggle has been read
# ─────────────────────────────────────────────────────────────────────────────
def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


def apply_theme(dark: bool) -> None:
    """Set the palette globals, the derived colour maps and the Plotly template."""
    g = globals()
    g["DARK_MODE"] = dark
    g.update(DARK if dark else LIGHT)
    g["PROGRAM_COLORS"] = {"OSR": GREEN, "GF (BMGF)": BRASS, "FIP": SLATE, "RPA": SAGE, "Escrow": PLUM}
    g["CATEGORY_COLORS"] = {"Savings": GREEN, "TDR": BRASS, "Buy/Sell": SLATE, "T-bills": PLUM}
    g["TENOR_COLORS"] = {"1M": SAGE, "3M": GREEN, "6M": BRASS, "12M": SLATE}
    pio.templates["treasury"] = go.layout.Template(
        layout=dict(
            font=dict(family="Manrope, Segoe UI, sans-serif", color=INK, size=13),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=[GREEN, BRASS, SLATE, SAGE, PLUM, RUST, GREY],
            xaxis=dict(showgrid=False, linecolor=LINE, tickcolor=LINE, ticks="outside", zeroline=False),
            yaxis=dict(gridcolor=GRID, zeroline=False, linecolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor=SURFACE if dark else INK, bordercolor=LINE,
                            font=dict(color=INK if dark else "white", family="Manrope, sans-serif", size=12)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
            margin=dict(l=8, r=8, t=36, b=8),
            transition=dict(duration=700, easing="cubic-in-out"),
            hovermode="closest",
        )
    )
    pio.templates.default = "treasury"


apply_theme(False)


# ─────────────────────────────────────────────────────────────────────────────
# Styling and motion
# ─────────────────────────────────────────────────────────────────────────────
def inject_css(reduce_motion: bool) -> None:
    motion_off = """
    *, *::before, *::after { animation: none !important; transition: none !important; }
    .stApp::before, .stApp::after { display: none !important; }
    """ if reduce_motion else ""

    # Tints derived from the active palette so night mode keeps the same relationships
    acc06, acc10, acc16 = rgba(GREEN, .06), rgba(GREEN, .10), rgba(GREEN, .16)
    brass14, brass22 = rgba(BRASS, .14), rgba(BRASS, .22)
    slate08 = rgba(SLATE, .08)
    glow = rgba(GREEN, .55 if DARK_MODE else .45)
    shadow_1 = rgba("#000000", .5) if DARK_MODE else rgba(INK, .35)
    shadow_2 = rgba("#000000", .25) if DARK_MODE else rgba(INK, .04)
    hero_ink = "#FFFFFF"
    hero_sub = "#A9C6DC" if DARK_MODE else "#BDD3E3"
    accent_soft = "#FF7D9B" if DARK_MODE else "#FF88A3"
    dark_tables = """
[data-testid="stDataFrame"] { filter: invert(.92) hue-rotate(180deg); }
[data-testid="stDataFrame"] img { filter: invert(1) hue-rotate(180deg); }
""" if DARK_MODE else ""

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

:root {{
  --ink:{INK}; --paper:{PAPER}; --surface:{SURFACE}; --green:{GREEN}; --green-deep:{GREEN_DEEP};
  --brass:{BRASS}; --sage:{SAGE}; --slate:{SLATE}; --rust:{RUST}; --muted:{MUTED}; --line:{LINE};
  --acc06:{acc06}; --acc10:{acc10}; --acc16:{acc16}; --brass14:{brass14}; --brass22:{brass22};
  --ease: cubic-bezier(.22,.72,.24,1);
  --spring: cubic-bezier(.34,1.42,.64,1);
  --glow: 0 22px 52px -28px {glow};
  --lift: 0 1px 2px {shadow_2}, 0 14px 32px -22px {shadow_1};
}}
@property --n {{ syntax: '<integer>'; initial-value: 0; inherits: false; }}
@property --sweep {{ syntax: '<percentage>'; initial-value: 0%; inherits: false; }}

html, body, .stApp {{ background: var(--paper) !important; color: var(--ink); font-family: Manrope, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased; }}
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div {{ font-family: Manrope, 'Segoe UI', sans-serif; }}
.stApp, .stApp p, .stApp li, .stApp label, [data-testid="stMarkdownContainer"] p {{ color: var(--ink); }}
h1, h2, h3, h4, .sora {{ font-family: Sora, Manrope, sans-serif !important; letter-spacing: -0.01em; color: var(--ink); }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container, [data-testid="stMainBlockContainer"] {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1420px; }}
.material-symbols-rounded, [data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}
::selection {{ background: var(--acc16); }}
[data-testid="stCaptionContainer"], .stCaption, [data-testid="stWidgetLabel"] label p {{ color: var(--muted) !important; }}

/* Ambient light: slow washes plus one drifting aurora band, always running */
.stApp::before {{
  content: ""; position: fixed; inset: -20% -10% auto -10%; height: 115vh; pointer-events: none; z-index: 0;
  background:
    radial-gradient(48vw 38vw at 12% 8%, {rgba(GREEN, .14 if DARK_MODE else .09)}, transparent 62%),
    radial-gradient(42vw 34vw at 88% 18%, {rgba(BRASS, .13 if DARK_MODE else .10)}, transparent 60%),
    radial-gradient(38vw 30vw at 60% 82%, {rgba(SLATE, .11 if DARK_MODE else .07)}, transparent 65%);
  animation: drift 34s ease-in-out infinite alternate;
}}
.stApp::after {{
  content: ""; position: fixed; left: -30%; right: -30%; top: 0; height: 340px; pointer-events: none; z-index: 0; will-change: transform;
  background: linear-gradient(100deg, transparent 30%, {rgba(SAGE, .13 if DARK_MODE else .09)} 50%, transparent 70%);
  animation: aurora 18s ease-in-out infinite;
}}
@keyframes drift {{
  0%   {{ transform: translate3d(0,0,0) scale(1); }}
  50%  {{ transform: translate3d(-2%,2%,0) scale(1.06); }}
  100% {{ transform: translate3d(2%,-1%,0) scale(1.02); }}
}}
@keyframes aurora {{ 0%,100% {{ transform: translate3d(-8%,0,0) skewY(-1.5deg); opacity: .5; }} 50% {{ transform: translate3d(8%,26px,0) skewY(1.5deg); opacity: 1; }} }}
[data-testid="stMainBlockContainer"], [data-testid="stSidebar"] {{ position: relative; z-index: 1; }}

::-webkit-scrollbar {{ width: 11px; height: 11px; }}
::-webkit-scrollbar-thumb {{ background: var(--line); border-radius: 8px; border: 3px solid var(--paper); }}
::-webkit-scrollbar-thumb:hover {{ background: var(--sage); }}
::-webkit-scrollbar-track {{ background: transparent; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: linear-gradient(175deg, var(--green-deep), {rgba(GREEN_DEEP, .82)}); box-shadow: 14px 0 44px -34px #000; }}
[data-testid="stSidebar"] * {{ color: #E4EEEA; }}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] h2 {{ position: relative; margin-bottom: 18px !important; }}
[data-testid="stSidebar"] h2::after {{ content: ""; position: absolute; left: 0; bottom: -8px; height: 2px; width: 46px; opacity: .85;
  background: linear-gradient(90deg, var(--brass), transparent); transform-origin: left; animation: line 1.1s .3s var(--ease) both; }}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{ background: rgba(255,255,255,.06); border: 1px dashed rgba(255,255,255,.25);
  transition: background .3s var(--ease), border-color .3s var(--ease), transform .3s var(--ease); }}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {{ background: rgba(255,255,255,.11); border-color: var(--brass); transform: translateY(-1px); }}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button, [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {{ color: #10231F !important; }}
[data-testid="stSidebar"] [data-baseweb="select"] * {{ color: #10231F; }}
[data-testid="stSidebar"] [data-baseweb="tag"] {{ background: var(--brass) !important; transition: transform .25s var(--spring); }}
[data-testid="stSidebar"] [data-baseweb="tag"]:hover {{ transform: translateY(-1px) scale(1.03); }}
[data-testid="stSidebar"] [data-baseweb="tag"] * {{ color: #fff !important; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ color: #E4EEEA !important; }}
.side-note {{ font-size: .8rem; line-height: 1.5; color: #B9CEC7 !important; }}

/* Ticker */
.ticker {{ overflow: hidden; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); margin-bottom: 14px;
  box-shadow: var(--lift); mask-image: linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent); animation: rise .7s var(--ease) both; }}
.ticker-track {{ display: inline-flex; gap: 42px; padding: 9px 0; white-space: nowrap; animation: tick 38s linear infinite; }}
.ticker:hover .ticker-track {{ animation-play-state: paused; }}
.ticker-item {{ font-size: .86rem; color: var(--muted); }}
.ticker-item b {{ color: var(--ink); font-family: Sora, sans-serif; font-weight: 600; margin-left: 6px; }}
.up {{ color: var(--green) !important; }} .down {{ color: var(--rust) !important; }}
@keyframes tick {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}

/* Hero */
.hero {{ position: relative; overflow: hidden; border-radius: 22px; padding: 30px 34px 26px; color: {hero_ink};
  background: radial-gradient(1200px 400px at 85% -20%, {brass22}, transparent 60%), linear-gradient(135deg, var(--green-deep), var(--green) 74%);
  box-shadow: 0 34px 80px -46px #000, inset 0 1px 0 rgba(255,255,255,.08);
  display: grid; grid-template-columns: minmax(280px, 1fr) minmax(320px, 1.35fr); gap: 34px; align-items: end;
  animation: heroIn .95s var(--ease) both; }}
@keyframes heroIn {{ from {{ opacity: 0; transform: translateY(16px) scale(.99); }} to {{ opacity: 1; transform: none; }} }}
.hero .glow-ring {{ position: absolute; width: 620px; height: 620px; right: -190px; top: -320px; border-radius: 50%; pointer-events: none;
  background: conic-gradient(from 0deg, transparent, {rgba(BRASS, .22)}, transparent 55%, {rgba(SAGE, .16)}, transparent);
  animation: spin 26s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.hero::before {{ content: ""; position: absolute; width: 520px; height: 520px; right: -140px; top: -260px; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, {rgba(BRASS, .20)}, transparent 62%); animation: breathe 9s ease-in-out infinite; }}
@keyframes breathe {{ 0%,100% {{ transform: scale(1); opacity: .7; }} 50% {{ transform: scale(1.14); opacity: 1; }} }}
.hero::after {{ content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.10) 45%, transparent 60%); transform: translateX(-100%);
  animation: sheen 3s .7s var(--ease) forwards, sheen 3s 14s var(--ease) infinite; }}
@keyframes sheen {{ to {{ transform: translateX(100%); }} }}
.hero h1 {{ color: #fff !important; font-size: clamp(1.7rem, 2.6vw, 2.35rem); font-weight: 600; margin: 0 0 4px; line-height: 1.15; padding: 0; }}
.hero .sub {{ color: {hero_sub}; font-size: .95rem; margin-bottom: 22px; }}
.hero .big {{ font-family: Sora, sans-serif; font-weight: 600; font-size: clamp(2.6rem, 5vw, 3.9rem); line-height: 1; letter-spacing: -0.02em;
  text-shadow: 0 10px 34px rgba(0,0,0,.35); position: relative; }}
.hero .big small {{ font-size: .38em; font-weight: 500; color: {accent_soft}; margin-right: 8px; letter-spacing: 0; }}
.hero .big-label {{ color: {hero_sub}; font-size: .9rem; margin-top: 8px; }}
.rise {{ opacity: 0; transform: translateY(14px); animation: rise .8s var(--ease) forwards; }}
@keyframes rise {{ to {{ opacity: 1; transform: none; }} }}
.fy-progress {{ margin-top: 20px; }}
.fy-progress .bar {{ height: 6px; border-radius: 6px; background: rgba(255,255,255,.14); overflow: hidden; }}
.fy-progress .fill {{ height: 100%; border-radius: 6px; width: 0; animation: grow 1.7s .5s var(--ease) forwards, sweep 3.4s 2.3s linear infinite;
  background: linear-gradient(90deg, var(--brass), {accent_soft}, var(--brass)); background-size: 220% 100%; box-shadow: 0 0 16px {rgba(BRASS, .5)}; }}
@keyframes sweep {{ from {{ background-position: 0% 0; }} to {{ background-position: 220% 0; }} }}
.fy-progress .meta {{ display: flex; justify-content: space-between; font-size: .8rem; color: {hero_sub}; margin-top: 6px; }}
@keyframes grow {{ to {{ width: var(--w); }} }}

/* Fiscal ribbon */
.ribbon {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 8px; align-items: end; height: 190px; }}
.rib {{ display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }}
.rib .col {{ position: relative; border-radius: 8px 8px 3px 3px; background: rgba(255,255,255,.08); height: 100%; overflow: hidden; transition: background .3s var(--ease); }}
.rib:hover .col {{ background: rgba(255,255,255,.16); }}
.rib .val {{ position: absolute; left: 0; right: 0; bottom: 0; height: 0; border-radius: 8px 8px 3px 3px;
  background: linear-gradient(180deg, {accent_soft}, var(--brass)); box-shadow: 0 0 18px -2px {rgba(BRASS, .45)};
  animation: fillup 1.15s var(--spring) forwards, shimmerY 5s linear infinite; animation-delay: var(--d), 2s;
  background-size: 100% 220%; transition: filter .3s var(--ease); }}
@keyframes shimmerY {{ from {{ background-position: 0 0%; }} to {{ background-position: 0 220%; }} }}
.rib:hover .val {{ filter: brightness(1.14); }}
.rib .val.py {{ background: none; box-shadow: none; border-top: 2px dashed rgba(255,255,255,.55); border-radius: 0; animation: fillup 1.15s var(--spring) forwards; animation-delay: var(--d); }}
.rib .amt {{ position: absolute; left: 0; right: 0; text-align: center; font-size: .72rem; color: #fff; font-family: Sora, sans-serif;
  bottom: calc(var(--h) + 4px); opacity: 0; animation: fade .6s ease forwards; animation-delay: calc(var(--d) + .9s); }}
.rib .m {{ text-align: center; font-size: .75rem; color: {hero_sub}; margin-top: 6px; transition: color .25s ease; }}
.rib:hover .m {{ color: #fff; }}
.rib.now .m {{ color: #fff; font-weight: 700; }}
.rib.now .col::after {{ content: ""; position: absolute; inset: 0; border-radius: 8px 8px 3px 3px; border: 1px solid {rgba(BRASS, .55)}; animation: haloPulse 2.8s ease-in-out infinite; }}
@keyframes haloPulse {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: .9; }} }}
@keyframes fillup {{ to {{ height: var(--h); }} }}
@keyframes fade {{ to {{ opacity: 1; }} }}
.ribbon-legend {{ display: flex; gap: 18px; font-size: .78rem; color: {hero_sub}; margin-top: 10px; }}
.ribbon-legend i {{ display: inline-block; width: 14px; height: 8px; border-radius: 2px; margin-right: 6px; vertical-align: middle; }}

/* KPI band */
.kpis {{ position: relative; display: grid; grid-template-columns: repeat(6, 1fr); background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; margin: 16px 0 6px; box-shadow: var(--lift); overflow: hidden; }}
.kpis::after {{ content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(105deg, transparent 40%, {acc10} 50%, transparent 60%); transform: translateX(-100%); animation: sheen 3.6s 9s var(--ease) infinite; }}
.kpi {{ padding: 16px 18px; border-left: 1px solid var(--line); position: relative; transition: background .35s var(--ease), transform .35s var(--ease);
  animation: kpiIn .7s var(--ease) both; animation-delay: var(--in); }}
@keyframes kpiIn {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
.kpi:first-child {{ border-left: none; }}
.kpi:hover {{ background: linear-gradient(180deg, {acc06}, transparent); transform: translateY(-2px); }}
.kpi:hover .v {{ transform: scale(1.045); }}
.kpi .l {{ font-size: .8rem; color: var(--muted); }}
.kpi .v {{ font-family: Sora, sans-serif; font-size: 1.55rem; font-weight: 600; margin-top: 4px; color: var(--ink); white-space: nowrap;
  transform-origin: left center; transition: transform .35s var(--spring); }}
.kpi .v .u {{ font-size: .62em; font-weight: 500; color: var(--muted); margin-left: 3px; }}
.kpi .d {{ font-size: .78rem; margin-top: 3px; color: var(--muted); }}
.kpi::before {{ content: ""; position: absolute; left: 18px; right: 18px; top: 0; height: 2px; transform: scaleX(0); transform-origin: left;
  background: linear-gradient(90deg, var(--brass), {rgba(BRASS, .2)}); animation: line .9s var(--ease) forwards; animation-delay: var(--d); }}
@keyframes line {{ to {{ transform: scaleX(1); }} }}
.num {{ font-variant-numeric: tabular-nums; }}

/* Splash: first paint of a session only */
.splash {{ position: fixed; inset: 0; z-index: 2147483000; display: grid; place-items: center; overflow: hidden;
  background: linear-gradient(140deg, {GREEN_DEEP}, {GREEN} 120%);
  animation: splashOut .8s 4.2s var(--ease) forwards; }}
@keyframes splashOut {{ to {{ opacity: 0; visibility: hidden; transform: scale(1.04); }} }}
.splash-bg {{ position: absolute; width: 150vmax; height: 150vmax; border-radius: 50%; pointer-events: none;
  background: conic-gradient(from 0deg, transparent, {rgba(BRASS, .20)}, transparent 45%, {rgba(SAGE, .16)}, transparent 80%);
  animation: spin 9s linear infinite; }}
.splash .dots {{ position: absolute; inset: 0; pointer-events: none; }}
.splash .dots i {{ position: absolute; left: var(--x); bottom: -10px; width: 6px; height: 6px; border-radius: 50%;
  background: {rgba(BRASS, .7)}; filter: none; animation: floatUp var(--dur) linear var(--dl) infinite; opacity: 0; }}
@keyframes floatUp {{ 0% {{ transform: translate3d(0,0,0) scale(.6); opacity: 0; }} 12% {{ opacity: .9; }}
  100% {{ transform: translate3d(28px,-104vh,0) scale(1.2); opacity: 0; }} }}
.splash-inner {{ position: relative; text-align: center; color: #fff; padding: 0 22px; animation: rise .9s .1s var(--ease) both; }}
.rings {{ position: relative; width: 132px; height: 132px; margin: 0 auto 26px; }}
.rings span {{ position: absolute; inset: 0; border-radius: 50%; border: 2px solid transparent; }}
.rings span:nth-child(1) {{ border-top-color: {accent_soft}; border-right-color: {rgba(BRASS, .6)}; animation: spin 1.9s linear infinite; }}
.rings span:nth-child(2) {{ inset: 16px; border-bottom-color: {SAGE}; border-left-color: rgba(255,255,255,.45); animation: spin 2.8s linear infinite reverse; }}
.rings span:nth-child(3) {{ inset: 32px; border-top-color: rgba(255,255,255,.8); animation: spin 1.4s linear infinite; }}
.rings b {{ position: absolute; inset: 0; display: grid; place-items: center; font-family: Sora, sans-serif; font-size: 2rem; color: {accent_soft};
  animation: coinFlip 3.2s var(--ease) infinite; }}
@keyframes coinFlip {{ 0%, 62% {{ transform: rotateY(0deg); }} 80% {{ transform: rotateY(180deg); }} 100% {{ transform: rotateY(360deg); }} }}
.splash-org {{ font-family: Sora, sans-serif; font-size: .95rem; letter-spacing: .32em; text-transform: uppercase; color: {accent_soft};
  animation: rise .9s .35s var(--ease) both; }}
.splash-title {{ font-family: Sora, sans-serif; font-size: clamp(1.6rem, 4.4vw, 2.9rem); font-weight: 600; margin: 10px 0 4px; line-height: 1.1;
  background: linear-gradient(100deg, #fff 20%, {accent_soft} 42%, #fff 64%); background-size: 250% 100%;
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  animation: rise .9s .5s var(--ease) both, shine 3.4s 1s linear infinite; }}
@keyframes shine {{ from {{ background-position: 250% 0; }} to {{ background-position: -50% 0; }} }}
.splash-fy {{ font-family: Sora, sans-serif; font-size: 1.12rem; color: rgba(255,255,255,.88); letter-spacing: .16em;
  animation: rise .9s .65s var(--ease) both; }}
.splash-bar {{ width: min(340px, 74vw); height: 3px; border-radius: 3px; margin: 30px auto 12px; overflow: hidden; background: rgba(255,255,255,.16);
  animation: rise .9s .8s var(--ease) both; }}
.splash-bar i {{ display: block; height: 100%; width: 0; border-radius: 3px; background: linear-gradient(90deg, {SAGE}, {accent_soft});
  animation: fillBar 4.3s linear forwards; }}
@keyframes fillBar {{ to {{ width: 100%; }} }}
.splash-note {{ font-size: .82rem; color: rgba(255,255,255,.6); animation: rise .9s .95s var(--ease) both; }}

/* Section headings */
.sec {{ margin: 26px 0 6px; }}
.sec h3 {{ font-size: 1.15rem; font-weight: 600; margin: 0; padding: 0; position: relative; display: inline-block; }}
.sec h3::after {{ content: ""; position: absolute; left: 0; bottom: -5px; height: 2px; width: 100%; transform: scaleX(0); transform-origin: left;
  background: linear-gradient(90deg, var(--brass), transparent); animation: line 1s .2s var(--ease) forwards; }}
.sec p {{ color: var(--muted); font-size: .88rem; margin: 8px 0 0; max-width: 78ch; }}

/* Panels */
[class*="st-key-panel"] {{ position: relative; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px 6px;
  box-shadow: var(--lift); transition: transform .4s var(--ease), border-color .4s var(--ease); will-change: transform; }}
[class*="st-key-panel"]:hover {{ transform: translateY(-4px); border-color: {rgba(GREEN, .35)}; }}
[class*="st-key-panel"]::after {{ content: ""; position: absolute; inset: -1px; border-radius: 17px; pointer-events: none; opacity: 0; padding: 1px;
  background: linear-gradient(135deg, {acc16}, {brass14} 55%, transparent 75%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude;
  transition: opacity .45s var(--ease); }}
[class*="st-key-panel"]:hover::after {{ opacity: 1; }}
.ph {{ font-family: Sora, sans-serif; font-weight: 600; font-size: .98rem; color: var(--ink); }}
.pc {{ font-size: .8rem; color: var(--muted); margin-top: 1px; }}

/* Entrance: everything arrives one after another, then repeats on scroll where supported */
[class*="st-key-panel"], .stats, .sec, [data-testid="stExpander"], [data-testid="stDataFrame"] {{ animation: blockIn .8s var(--ease) both; }}
@keyframes blockIn {{ from {{ opacity: 0; transform: translateY(26px) scale(.99); }} to {{ opacity: 1; transform: none; }} }}
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:nth-child(1),
[data-testid="stVerticalBlock"] > div:nth-child(1) {{ animation-delay: .04s; }}
[data-testid="stVerticalBlock"] > div:nth-child(2) {{ animation-delay: .12s; }}
[data-testid="stVerticalBlock"] > div:nth-child(3) {{ animation-delay: .2s; }}
[data-testid="stVerticalBlock"] > div:nth-child(4) {{ animation-delay: .28s; }}
[data-testid="stVerticalBlock"] > div:nth-child(5) {{ animation-delay: .36s; }}
[data-testid="stVerticalBlock"] > div:nth-child(n+6) {{ animation-delay: .44s; }}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [class*="st-key-panel"] {{ animation-delay: .16s; }}
[data-testid="stHorizontalBlock"] > div:nth-child(3) [class*="st-key-panel"] {{ animation-delay: .28s; }}

@supports (animation-timeline: view()) {{
  [class*="st-key-panel"], .stats, .sec, [data-testid="stExpander"], [data-testid="stDataFrame"] {{
    animation: blockIn linear both; animation-timeline: view(); animation-range: entry 2% entry 46%; animation-delay: 0s;
  }}
  [data-testid="stPlotlyChart"] {{ animation: chartIn linear both; animation-timeline: view(); animation-range: entry 4% entry 48%; }}
  [data-testid="stPlotlyChart"]::after {{ animation: unveil linear both; animation-timeline: view(); animation-range: entry 8% entry 62%; }}
  .js-plotly-plot .pielayer {{ animation: pieIn linear both; animation-timeline: view(); animation-range: entry 6% entry 60%; }}
}}

/* Charts: wipe in, pies sweep open, bars and points settle, lines draw themselves */
[data-testid="stPlotlyChart"] {{ position: relative; border-radius: 10px; transition: filter .4s var(--ease); animation: chartIn .7s var(--ease) both; }}
@keyframes chartIn {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
[data-testid="stPlotlyChart"]::after {{ content: ""; position: absolute; inset: 0; pointer-events: none; border-radius: 10px; background: var(--surface);
  transform-origin: right center; will-change: transform; animation: unveil 1.05s .1s var(--ease) both; }}
@keyframes unveil {{ from {{ transform: scaleX(1); }} to {{ transform: scaleX(0); }} }}
.js-plotly-plot .pielayer {{ transform-box: fill-box; transform-origin: center; animation: pieIn 1.2s var(--ease) both; }}
@keyframes pieIn {{ from {{ transform: rotate(-140deg) scale(.6); opacity: 0; }} 55% {{ opacity: 1; }} to {{ transform: none; opacity: 1; }} }}
.js-plotly-plot .pielayer .slice {{ animation: sliceIn .55s var(--ease) both; }}
@keyframes sliceIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.js-plotly-plot .pielayer .slice:nth-child(1) {{ animation-delay: .35s; }}
.js-plotly-plot .pielayer .slice:nth-child(2) {{ animation-delay: .5s; }}
.js-plotly-plot .pielayer .slice:nth-child(3) {{ animation-delay: .65s; }}
.js-plotly-plot .pielayer .slice:nth-child(4) {{ animation-delay: .8s; }}
.js-plotly-plot .pielayer .slice:nth-child(5) {{ animation-delay: .95s; }}
.js-plotly-plot .pielayer .slice:nth-child(6) {{ animation-delay: 1.1s; }}
.js-plotly-plot .pielayer .slice:nth-child(n+7) {{ animation-delay: 1.25s; }}
/* Inner SVG nodes are faded in only. Never animate their transform: Plotly uses
   transform attributes for positioning and a CSS transform would move them. */
.js-plotly-plot .barlayer .point, .js-plotly-plot .scatterlayer .points path {{ animation: pointIn .75s var(--ease) both; }}
@keyframes pointIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.js-plotly-plot .barlayer .point:nth-child(1), .js-plotly-plot .scatterlayer .points path:nth-child(1) {{ animation-delay: .05s; }}
.js-plotly-plot .barlayer .point:nth-child(2), .js-plotly-plot .scatterlayer .points path:nth-child(2) {{ animation-delay: .12s; }}
.js-plotly-plot .barlayer .point:nth-child(3), .js-plotly-plot .scatterlayer .points path:nth-child(3) {{ animation-delay: .19s; }}
.js-plotly-plot .barlayer .point:nth-child(4), .js-plotly-plot .scatterlayer .points path:nth-child(4) {{ animation-delay: .26s; }}
.js-plotly-plot .barlayer .point:nth-child(5), .js-plotly-plot .scatterlayer .points path:nth-child(5) {{ animation-delay: .33s; }}
.js-plotly-plot .barlayer .point:nth-child(6), .js-plotly-plot .scatterlayer .points path:nth-child(6) {{ animation-delay: .4s; }}
.js-plotly-plot .barlayer .point:nth-child(7), .js-plotly-plot .scatterlayer .points path:nth-child(7) {{ animation-delay: .47s; }}
.js-plotly-plot .barlayer .point:nth-child(8), .js-plotly-plot .scatterlayer .points path:nth-child(8) {{ animation-delay: .54s; }}
.js-plotly-plot .barlayer .point:nth-child(n+9), .js-plotly-plot .scatterlayer .points path:nth-child(n+9) {{ animation-delay: .6s; }}
.js-plotly-plot .bartext, .js-plotly-plot .textpoint text, .js-plotly-plot .annotation-text {{ animation: pointIn .8s .55s var(--ease) both; }}
.js-plotly-plot .plotly .modebar {{ opacity: 0; transition: opacity .35s var(--ease); }}
[class*="st-key-panel"]:hover .js-plotly-plot .plotly .modebar {{ opacity: .9; }}
[class*="st-key-panel"]:hover [data-testid="stPlotlyChart"] {{ filter: saturate(1.06); }}
.modebar-btn path {{ fill: var(--muted) !important; }}

/* Tabs */
.stTabs [role="tablist"] {{ gap: 4px; border-bottom: 1px solid var(--line); }}
.stTabs [role="tab"] {{ min-height: 46px; padding: 0 16px; background: transparent; border-radius: 10px 10px 0 0; cursor: pointer;
  transition: background .3s var(--ease), transform .3s var(--spring); }}
.stTabs [role="tab"] p {{ font-family: Sora, sans-serif !important; font-size: .92rem; font-weight: 500; color: var(--muted); transition: color .25s ease; }}
.stTabs [role="tab"]:hover {{ background: {acc06}; transform: translateY(-2px); }}
.stTabs [role="tab"][aria-selected="true"] p {{ color: var(--green) !important; font-weight: 600; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs .react-aria-SelectionIndicator {{ height: 3px !important; border-radius: 3px;
  background: linear-gradient(90deg, var(--brass), var(--green)) !important; box-shadow: 0 2px 12px -2px {glow}; transition: all .45s var(--ease) !important; }}
.stTabs [role="tabpanel"] {{ animation: panelSlide .5s var(--ease) both; }}
@keyframes panelSlide {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
[data-testid="stHeaderActionElements"] {{ display: none; }}

/* Chips and badges */
.chip {{ display: inline-flex; align-items: center; gap: 6px; font-size: .78rem; padding: 4px 10px; border-radius: 999px; background: {acc10};
  color: var(--green); font-weight: 600; animation: rise .7s .4s var(--ease) both, floaty 6s 1.2s ease-in-out infinite;
  transition: box-shadow .35s var(--ease); }}
@keyframes floaty {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
.chip:hover {{ box-shadow: 0 12px 26px -18px {glow}; }}
.chip.warn {{ background: {rgba(RUST, .12)}; color: var(--rust); }}
.dot {{ width: 7px; height: 7px; border-radius: 50%; background: currentColor; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 {rgba(GREEN, .45)}; }} 70% {{ box-shadow: 0 0 0 8px {rgba(GREEN, 0)}; }} 100% {{ box-shadow: 0 0 0 0 {rgba(GREEN, 0)}; }} }}

/* Stat strips */
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(128px, 1fr)); gap: 10px; margin: 4px 0 10px; }}
.stat {{ border-left: 3px solid var(--sage); padding: 4px 10px; border-radius: 0 8px 8px 0; transition: background .35s var(--ease), transform .35s var(--ease); }}
.stat:hover {{ background: {acc06}; transform: translateX(3px); }}
.stat .l {{ font-size: .76rem; color: var(--muted); }}
.stat .v {{ font-family: Sora, sans-serif; font-weight: 600; font-size: 1.12rem; animation: popIn .75s var(--spring) both; }}
.stat:nth-child(1) .v {{ animation-delay: .06s; }} .stat:nth-child(2) .v {{ animation-delay: .16s; }}
.stat:nth-child(3) .v {{ animation-delay: .26s; }} .stat:nth-child(4) .v {{ animation-delay: .36s; }}
.stat:nth-child(5) .v {{ animation-delay: .46s; }} .stat:nth-child(6) .v {{ animation-delay: .56s; }}
@keyframes popIn {{ from {{ opacity: 0; transform: translateY(10px) scale(.92); }} to {{ opacity: 1; transform: none; }} }}

/* Tables, widgets, expanders */
[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; box-shadow: var(--lift); }}
[data-testid="stExpander"] {{ border-radius: 12px; overflow: hidden; border: 1px solid var(--line); background: var(--surface);
  transition: box-shadow .4s var(--ease), transform .4s var(--ease); }}
[data-testid="stExpander"]:hover {{ box-shadow: var(--glow); transform: translateY(-2px); }}
[data-testid="stExpander"] summary:hover {{ color: var(--green); }}
[data-testid="stExpander"] details, [data-testid="stExpander"] summary {{ background: var(--surface) !important; color: var(--ink); }}
.stButton button, .stDownloadButton button {{ border-radius: 10px; border: 1px solid var(--line); background: var(--surface); color: var(--ink);
  transition: all .3s var(--ease); }}
.stButton button:hover, .stDownloadButton button:hover {{ border-color: var(--green); color: var(--green); transform: translateY(-2px); box-shadow: var(--glow); }}
.stButton button:active, .stDownloadButton button:active {{ transform: translateY(0) scale(.97); }}
[data-testid="stSlider"] [role="slider"] {{ background: var(--green); transition: box-shadow .3s var(--ease), transform .25s var(--spring); }}
[data-testid="stSlider"] [role="slider"]:hover {{ transform: scale(1.18); box-shadow: 0 0 0 8px {acc16}; }}
[data-baseweb="select"] > div {{ transition: box-shadow .3s var(--ease), border-color .3s var(--ease); }}
[data-baseweb="select"] > div:hover {{ border-color: var(--sage); }}
{dark_tables}

@media (max-width: 1100px) {{
  .hero {{ grid-template-columns: 1fr; }}
  .kpis {{ grid-template-columns: repeat(3, 1fr); }}
  .kpi:nth-child(4) {{ border-left: none; }}
  .kpi:nth-child(n+4) {{ border-top: 1px solid var(--line); }}
}}
@media (max-width: 640px) {{
  .kpis {{ grid-template-columns: repeat(2, 1fr); }}
  .kpi {{ border-left: none; border-top: 1px solid var(--line); }}
  .ribbon {{ height: 150px; gap: 4px; }}
  .rib .amt {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
  .rise, .stat .v, .kpi {{ opacity: 1; transform: none; }}
  .stApp::before, .stApp::after {{ display: none; }}
}}
{motion_off}
</style>
""",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def to_float(v) -> float:
    """Turn messy spreadsheet cells ('Closed', '-', ' 179,205.48', '#REF!') into floats."""
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip().replace(",", "")
    if s in {"", "-", "Closed", "closed"} or s.startswith("#"):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def is_blank(v) -> bool:
    return v is None or (isinstance(v, float) and np.isnan(v)) or (isinstance(v, str) and not v.strip()) or v is pd.NaT


def clean_str(v) -> str:
    return "" if is_blank(v) else str(v).strip()


TITLE_WORDS = ["Karandaaz", "Pakistan", "Own", "Source", "Revenue", "Bank", "Punjab", "Escrow", "Account", "Investments", "Reserve"]


def tidy_account(name: str) -> str:
    name = name.rstrip("*").strip()
    for w in TITLE_WORDS:
        name = re.sub(rf"\b{w.upper()}\b", w, name)
    name = re.sub(r"\bOF\b", "of", name)
    return re.sub(r"\s+", " ", name)


def norm_bank(v) -> str:
    s = clean_str(v)
    return BANK_ALIASES.get(s.upper(), s)


def mask_account(v, masked: bool) -> str:
    s = clean_str(v)
    if not s:
        return ""
    if not masked:
        return s
    digits = re.sub(r"\D", "", s)
    return f"•••• {digits[-4:]}" if len(digits) >= 4 else "••••"


def shade(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # blend towards white rather than using transparency, so labels stay crisp
    mix = lambda c: int(c * alpha + 255 * (1 - alpha))
    return f"rgb({mix(r)},{mix(g)},{mix(b)})"


def fiscal_index(ts) -> int:
    ts = pd.Timestamp(ts)
    return (ts.month - 7) % 12


def money(v: float, unit: str = "auto", dp: int = 1) -> str:
    if v is None or pd.isna(v):
        return "–"
    a = abs(v)
    if unit == "auto":
        unit = "B" if a >= 1e9 else "M" if a >= 1e6 else "K" if a >= 1e3 else ""
    div = {"B": 1e9, "M": 1e6, "K": 1e3, "": 1}[unit]
    return f"{v / div:,.{dp}f}{unit}"


def pct(v: float, dp: int = 2) -> str:
    return "–" if v is None or pd.isna(v) else f"{v * 100:.{dp}f}%"


def show_chart(fig, key: str | None = None) -> None:
    # Streamlit fills unset layout colours from the app theme, so set the essentials explicitly.
    fig.update_layout(
        template=pio.templates["treasury"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, Segoe UI, sans-serif", color=INK, size=13),
    )
    if fig.layout.margin.l is None:
        fig.update_layout(margin=dict(l=8, r=8, t=36, b=8))
    fig.update_xaxes(automargin=True, linecolor=LINE, tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    fig.update_yaxes(automargin=True, gridcolor=GRID, tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    cfg = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}
    try:
        st.plotly_chart(fig, width="stretch", theme=None, config=cfg, key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, theme=None, config=cfg, key=key)


def show_table(df: pd.DataFrame, **kw) -> None:
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def section(title: str, caption: str = "") -> None:
    cap = f"<p>{caption}</p>" if caption else ""
    st.markdown(f'<div class="sec"><h3>{title}</h3>{cap}</div>', unsafe_allow_html=True)


def panel_head(title: str, caption: str = "") -> None:
    cap = f'<div class="pc">{caption}</div>' if caption else ""
    st.markdown(f'<div class="ph">{title}</div>{cap}', unsafe_allow_html=True)


_panel_counter = {"n": 0}


def panel():
    _panel_counter["n"] += 1
    try:
        return st.container(key=f"panel_{_panel_counter['n']}")
    except TypeError:  # very old Streamlit
        return st.container(border=True)


def count_html(value: float, dp: int, suffix: str = "", prefix: str = "", delay: float = 0.0) -> str:
    """A figure that counts up. The animation is driven by requestAnimationFrame in
    boot_animations(); if that cannot run, the final value is already in the markup."""
    if value is None or pd.isna(value):
        return "–"
    shown = f"{value:,.{dp}f}".replace("-", "−")
    return (
        f'{prefix}<span class="num" data-t="{value}" data-dp="{dp}" data-delay="{delay}">{shown}</span>'
        f'<span class="u">{suffix}</span>'
    )


def boot_animations(reduce_motion: bool) -> None:
    """Runs once per page, after everything is on screen.

    Streamlit renders custom components in a same-origin srcdoc iframe, so this can
    reach the parent document. If a future version sandboxes it, every animation here
    is an enhancement over markup that is already correct, so nothing breaks.
    """
    if reduce_motion:
        return
    components.html(
        """
<script>
(function () {
  var doc;
  try { doc = window.parent.document; } catch (e) { return; }
  if (!doc) return;
  // The component frame has no height, so its own rAF never fires. Drive every
  // animation from the parent window, which is the one actually painting.
  var win = window.parent;
  var raf = (win.requestAnimationFrame || window.requestAnimationFrame).bind(win);
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 3); };

  function countUp(el) {
    if (el.dataset.done === "1") return;
    el.dataset.done = "1";
    var target = parseFloat(el.dataset.t);
    var dp = parseInt(el.dataset.dp || "0", 10);
    var delay = (parseFloat(el.dataset.delay || "0") + 0.15) * 1000;
    var dur = 1500;
    var fmt = function (v) {
      return v.toLocaleString(undefined, { minimumFractionDigits: dp, maximumFractionDigits: dp }).replace("-", "\u2212");
    };
    var final = fmt(target);
    el.dataset.final = final;
    setTimeout(function () {
      el.textContent = fmt(0);
      var t0 = null;
      function step(ts) {
        if (t0 === null) t0 = ts;
        var k = Math.min((ts - t0) / dur, 1);
        el.textContent = fmt(target * easeOut(k));
        if (k < 1) raf(step); else el.textContent = final;
      }
      raf(step);
      // Safety net: if this frame is torn down mid-flight, never leave a stale figure
      setTimeout(function () { if (el.isConnected) el.textContent = final; }, dur + 400);
    }, delay);
  }

  // Lines draw themselves, but only where the path is small enough to stay smooth
  function drawLine(path) {
    if (path.dataset.drawn === "1") return;
    path.dataset.drawn = "1";
    var d = path.getAttribute("d") || "";
    if (d.length > 9000) return;
    var len;
    try { len = path.getTotalLength(); } catch (e) { return; }
    if (!len || len > 12000) return;
    if (path.getAttribute("stroke-dasharray")) return;
    path.animate(
      [{ strokeDasharray: len, strokeDashoffset: len }, { strokeDasharray: len, strokeDashoffset: 0 }],
      { duration: 1500, easing: "cubic-bezier(.22,.72,.24,1)", fill: "backwards" }
    );
  }

  function sweep() {
    doc.querySelectorAll(".num").forEach(countUp);
    doc.querySelectorAll(".js-plotly-plot .scatterlayer .js-line").forEach(drawLine);
  }

  sweep();
  [300, 900, 1800, 3200, 5200].forEach(function (ms) { setTimeout(sweep, ms); });

  // If Streamlit replaces this frame, put every figure back to its final value first
  window.addEventListener("pagehide", function () {
    doc.querySelectorAll(".num").forEach(function (el) { if (el.dataset.final) el.textContent = el.dataset.final; });
  });

  var main = doc.querySelector('[data-testid="stMain"]') || doc.body;
  var queued = null;
  new MutationObserver(function () {
    clearTimeout(queued);
    queued = setTimeout(sweep, 260);
  }).observe(main, { childList: true, subtree: true });
})();
</script>
""",
        height=0,
    )


def splash_html() -> str:
    dots = "".join(
        f'<i style="--x:{(i * 37) % 100}%;--dl:{i * 0.42:.2f}s;--dur:{7 + (i % 5)}s"></i>' for i in range(14)
    )
    return f"""
<div class="splash">
  <div class="splash-bg"></div>
  <div class="dots">{dots}</div>
  <div class="splash-inner">
    <div class="rings"><span></span><span></span><span></span><b>₨</b></div>
    <div class="splash-org">Karandaaz Pakistan</div>
    <div class="splash-title">Treasury Income Dashboard</div>
    <div class="splash-fy">FY 26'27</div>
    <div class="splash-bar"><i></i></div>
    <div class="splash-note">Reading the treasury workbooks</div>
  </div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────
def find_file(patterns: list[str]) -> Path | None:
    for d in DATA_DIRS:
        if not d.exists():
            continue
        for pat in patterns:
            hits = sorted(d.glob(pat))
            if hits:
                return hits[0]
    return None


@st.cache_data(show_spinner=False)
def read_book(data: bytes) -> dict[str, pd.DataFrame]:
    return pd.read_excel(io.BytesIO(data), sheet_name=None, header=None)


def get_sheet(book: dict, name: str) -> pd.DataFrame | None:
    """Find a sheet by name, ignoring case and stray spaces."""
    key = name.strip().lower()
    for k, v in book.items():
        if k.strip().lower() == key:
            return v
    for k, v in book.items():
        if key in k.strip().lower():
            return v
    return None


def parse_bank_profits(df: pd.DataFrame | None, fy_label: str, masked: bool) -> pd.DataFrame:
    """Parse a 'Treasury Bank Profits' sheet into long format: program, bank, account, month, amount."""
    cols = ["fy", "program", "tag", "bank", "account", "account_no", "month_idx", "month", "amount"]
    if df is None:
        return pd.DataFrame(columns=cols)
    section_map = {"sr.no": "OSR", "bmgf": "GF (BMGF)", "fip": "FIP", "rpa": "RPA", "escrow": "Escrow"}
    rows, program, active = [], None, False
    for _, r in df.iterrows():
        v = r.tolist() + [None] * 20
        c0, c2 = clean_str(v[0]), clean_str(v[2])
        if c2 == "Account Title":
            if c0 and c0.lower() in section_map:
                program = section_map[c0.lower()]
            active = True
            continue
        if not active or program is None:
            continue
        month_vals = [to_float(x) for x in v[5:17]]
        if not c2:
            if any(not np.isnan(x) for x in month_vals):
                active = False  # totals row closes the block
            continue
        for i, amt in enumerate(month_vals):
            if np.isnan(amt) or amt == 0:
                continue
            rows.append(
                dict(
                    fy=fy_label,
                    program=program,
                    tag=clean_str(v[1]),
                    bank=norm_bank(v[4]),
                    account=tidy_account(c2),
                    account_no=mask_account(v[3], masked),
                    month_idx=i,
                    month=MONTHS[i],
                    amount=amt,
                )
            )
    return pd.DataFrame(rows, columns=cols)


def parse_quarterly(df: pd.DataFrame | None) -> pd.DataFrame:
    cols = ["fund", "line", "Q1", "Q2", "Q3", "Q4"]
    if df is None:
        return pd.DataFrame(columns=cols)
    rows, fund = [], None
    for _, r in df.iterrows():
        v = r.tolist() + [None] * 8
        c1 = clean_str(v[1])
        if c1 in {"OSR", "FIP", "GF"}:
            fund = c1
            continue
        if fund and c1 and c1 not in {"Total", "Amount in PKR", "Q1"}:
            nice = {"Savings OSR": "OSR savings", "Savings RPA": "RPA savings", "Savings Escrow": "Escrow savings",
                    "Buy Sell": "Buy/Sell", "Tbills": "T-bills"}.get(c1, c1)
            rows.append(dict(fund=fund, line=nice, **{f"Q{i}": to_float(v[1 + i]) for i in range(1, 5)}))
    out = pd.DataFrame(rows, columns=cols)
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        out[q] = out[q].fillna(0.0)
    return out


def parse_tdr(df: pd.DataFrame | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    inst_cols = ["bank", "account", "start", "rate", "principal"]
    if df is None:
        return pd.DataFrame(columns=inst_cols), pd.DataFrame(columns=["month_idx", "amount"])
    hdr = None
    for i, r in df.iterrows():
        if "Booked On" in [clean_str(x) for x in r.tolist()]:
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame(columns=inst_cols), pd.DataFrame(columns=["month_idx", "amount"])
    header = [clean_str(x) for x in df.loc[hdr].tolist()]
    month_cols = {}
    for j, h in enumerate(header):
        for k, m in enumerate(["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]):
            if h.lower().startswith(m):
                month_cols[j] = k
    inst, acc = [], []
    for i in range(hdr + 1, len(df)):
        v = df.loc[i].tolist()
        bank = clean_str(v[0])
        if not bank:
            continue
        inst.append(dict(bank=norm_bank(bank), account=clean_str(v[1]), start=pd.to_datetime(v[2], errors="coerce"),
                         rate=to_float(v[3]), principal=to_float(v[4])))
        for j, k in month_cols.items():
            amt = to_float(v[j])
            if not np.isnan(amt):
                acc.append(dict(bank=norm_bank(bank), month_idx=k, amount=amt))
    return pd.DataFrame(inst, columns=inst_cols), pd.DataFrame(acc)


def parse_buysell(df: pd.DataFrame | None) -> pd.DataFrame:
    cols = ["bank", "program", "days", "start", "end", "rate", "principal", "face", "profit"]
    if df is None:
        return pd.DataFrame(columns=cols)
    hdr = None
    for i, r in df.iterrows():
        vals = [clean_str(x) for x in r.tolist()]
        if vals and vals[0] == "Bank" and any("Purchase" in x for x in vals):
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame(columns=cols)
    header = [clean_str(x).lower() for x in df.loc[hdr].tolist()]

    def col(name):
        for j, h in enumerate(header):
            if h.startswith(name):
                return j
        return None

    ci = dict(days=col("no of days"), start=col("purchase"), end=col("maturity"), rate=col("profit rate"),
              principal=col("cheque"), face=col("face"), profit=col("profit"))
    # 'profit' startswith matches 'profit rate' first, so pick the exact 'profit' column
    for j, h in enumerate(header):
        if h == "profit":
            ci["profit"] = j
    rows = []
    for i in range(hdr + 1, len(df)):
        v = df.loc[i].tolist()
        if not clean_str(v[0]):
            break
        rows.append(dict(
            bank=norm_bank(v[0]), program=clean_str(v[1]), days=to_float(v[ci["days"]]),
            start=pd.to_datetime(v[ci["start"]], errors="coerce"), end=pd.to_datetime(v[ci["end"]], errors="coerce"),
            rate=to_float(v[ci["rate"]]), principal=to_float(v[ci["principal"]]), face=to_float(v[ci["face"]]),
            profit=to_float(v[ci["profit"]]),
        ))
    return pd.DataFrame(rows, columns=cols)


def parse_tbills(df: pd.DataFrame | None) -> pd.DataFrame:
    cols = ["bank", "start", "end", "rate", "days", "principal", "face", "profit_fy", "profit_total"]
    if df is None:
        return pd.DataFrame(columns=cols)
    rows = []
    started = False
    for i, r in df.iterrows():
        v = r.tolist() + [None] * 14
        if clean_str(v[0]) == "Bank":
            if started:
                break  # second table (monthly breakdown) repeats the same bills
            started = True
            continue
        if not started:
            continue
        if not clean_str(v[0]):
            if rows:
                break
            continue
        principal, face = to_float(v[7]), to_float(v[8])
        rows.append(dict(
            bank=norm_bank(v[0]), start=pd.to_datetime(v[2], errors="coerce"), end=pd.to_datetime(v[3], errors="coerce"),
            rate=to_float(v[4]), days=to_float(v[6]), principal=principal, face=face,
            profit_fy=to_float(v[9]), profit_total=face - principal,
        ))
    return pd.DataFrame(rows, columns=cols)


def parse_old_tbill_months(df: pd.DataFrame | None) -> pd.DataFrame:
    """Prior-year T-bill income by month from 'OLD T-Bills_TDR - Mapped'."""
    if df is None:
        return pd.DataFrame(columns=["month_idx", "amount"])
    hdr_row = None
    for i, r in df.iterrows():
        if clean_str(r.iloc[0]).lower().startswith("sr"):
            hdr_row = i
            break
    if hdr_row is None:
        return pd.DataFrame(columns=["month_idx", "amount"])
    header = df.loc[hdr_row].tolist()
    date_cols = [j for j, h in enumerate(header) if isinstance(h, (datetime, pd.Timestamp))]
    py_cols = [j for j in date_cols if pd.Timestamp("2025-07-01") <= pd.Timestamp(header[j]) <= pd.Timestamp("2026-06-30")]
    for i in range(hdr_row + 1, len(df)):
        v = df.loc[i].tolist()
        if clean_str(v[1]):
            continue
        vals = [to_float(v[j]) for j in py_cols]
        if len(vals) == 12 and sum(0 if np.isnan(x) else 1 for x in vals) >= 10:
            return pd.DataFrame({"month_idx": range(12), "amount": [0 if np.isnan(x) else x for x in vals]})
    return pd.DataFrame(columns=["month_idx", "amount"])


def parse_pool(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame(columns=["fund", "month_idx", "month", "amount"])
    hdr = None
    for i, r in df.iterrows():
        if any(clean_str(x).lower().startswith("july") for x in r.tolist()):
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame(columns=["fund", "month_idx", "month", "amount"])
    header = df.loc[hdr].tolist()
    mcols = {}
    for j, h in enumerate(header):
        hs = clean_str(h).lower()
        for k, m in enumerate(["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]):
            if hs.startswith(m):
                mcols[j] = k
    rows = []
    for i in range(hdr + 1, len(df)):
        v = df.loc[i].tolist()
        name = clean_str(v[1]) if len(v) > 1 else ""
        if not name or "total" in name.lower() or "average" in name.lower():
            continue
        for j, k in mcols.items():
            amt = to_float(v[j]) if j < len(v) else np.nan
            if not np.isnan(amt) and amt != 0:
                rows.append(dict(fund=name, month_idx=k, month=MONTHS[k], amount=amt))
    return pd.DataFrame(rows, columns=["fund", "month_idx", "month", "amount"])


def parse_mpr(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame(columns=["date", "rate"])
    out = []
    for i, r in df.iterrows():
        d = pd.to_datetime(r.iloc[0], errors="coerce")
        if pd.notna(d):
            out.append(dict(date=d, rate=to_float(r.iloc[1]) if len(r) > 1 else np.nan))
    return pd.DataFrame(out, columns=["date", "rate"])


def parse_profit_rates(df: pd.DataFrame | None) -> pd.DataFrame:
    rows = []
    if df is None:
        return pd.DataFrame(columns=["month", "rank", "bank", "rate"])
    hdr = None
    for i, r in df.iterrows():
        if clean_str(r.iloc[0]).lower().startswith("july"):
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame(columns=["month", "rank", "bank", "rate"])
    for j in range(min(12, df.shape[1])):
        for i in range(hdr + 1, len(df)):
            txt = clean_str(df.iloc[i, j])
            for m in re.finditer(r"(\d)\.\s*([A-Za-z/ ]+?)\s+([\d.]+)%", txt):
                rows.append(dict(month=MONTHS[j], rank=int(m.group(1)), bank=m.group(2).strip(), rate=float(m.group(3)) / 100))
    return pd.DataFrame(rows, columns=["month", "rank", "bank", "rate"])


def parse_pkrv(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    hdr = None
    for i, r in df.iterrows():
        if clean_str(r.iloc[0]).upper() == "TENOR":
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame()
    tenors = [clean_str(x) for x in df.loc[hdr].tolist()[1:]]
    data = df.loc[hdr + 1:].copy()
    data.columns = ["date"] + tenors
    data = data[data["date"].map(lambda x: isinstance(x, (datetime, pd.Timestamp)))]
    data["date"] = pd.to_datetime(data["date"])
    for t in tenors:
        data[t] = pd.to_numeric(data[t], errors="coerce")
    return data.drop_duplicates("date").sort_values("date").set_index("date")[tenors]


def parse_kibor(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    header = [clean_str(x) for x in df.iloc[0].tolist()]
    data = df.iloc[1:].copy()
    data.columns = header
    data = data.rename(columns={header[0]: "date"})
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"])
    for c in header[1:]:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    return data.drop_duplicates("date").sort_values("date").set_index("date")


def parse_mps(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame(columns=["label", "date", "rate", "delta_bps", "attribute"])
    hdr = None
    for i, r in df.iterrows():
        if clean_str(r.iloc[0]).upper() == "MPS":
            hdr = i
            break
    if hdr is None:
        return pd.DataFrame(columns=["label", "date", "rate", "delta_bps", "attribute"])
    rows = []
    for i in range(hdr + 1, len(df)):
        v = df.loc[i].tolist() + [None] * 7
        label = clean_str(v[0])
        if not label:
            continue
        d = pd.to_datetime(v[1], errors="coerce")
        if pd.isna(d):
            d = pd.to_datetime(label, format="%B %Y", errors="coerce")
        rows.append(dict(label=label, date=d, rate=to_float(v[3]), delta_bps=to_float(v[2]), attribute=clean_str(v[6]).title()))
    out = pd.DataFrame(rows).dropna(subset=["date", "rate"]).sort_values("date")
    return out


@st.cache_data(show_spinner=False)
def build_model(treasury_bytes: bytes, pkrv_bytes: bytes | None, masked: bool) -> dict:
    tb = read_book(treasury_bytes)
    m: dict = {}
    m["bank_cy"] = parse_bank_profits(get_sheet(tb, "Treasury Bank Profits mappe (2)"), FY_LABEL, masked)
    m["bank_py"] = parse_bank_profits(get_sheet(tb, "Treasury Bank Profits forcasted"), PY_LABEL, masked)
    m["quarterly"] = parse_quarterly(get_sheet(tb, "Quarterly"))
    m["tdr"], m["tdr_acc"] = parse_tdr(get_sheet(tb, "New TDR Mapped"))
    m["buysell"] = parse_buysell(get_sheet(tb, "New Buy Sell Mapped"))
    m["tbills"] = parse_tbills(get_sheet(tb, "New TBILLS Mapped"))
    m["tbill_py"] = parse_old_tbill_months(get_sheet(tb, "OLD T-Bills_TDR - Mapped"))
    m["pool"] = parse_pool(get_sheet(tb, "Treasury Pool"))
    m["mpr"] = parse_mpr(get_sheet(tb, "MPR"))
    m["profit_rates"] = parse_profit_rates(get_sheet(tb, "Profit Rates"))

    if pkrv_bytes:
        pb = read_book(pkrv_bytes)
        m["pkrv"] = parse_pkrv(get_sheet(pb, "PKRVs"))
        m["kibor"] = parse_kibor(get_sheet(pb, "KIBORRates"))
        m["mps"] = parse_mps(get_sheet(pb, "MPS"))
    else:
        m["pkrv"], m["kibor"], m["mps"] = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Monthly income for the current year by category and program
    rows = []
    bc = m["bank_cy"]
    if not bc.empty:
        g = bc.groupby(["month_idx", "program"], as_index=False)["amount"].sum()
        for _, r in g.iterrows():
            rows.append(dict(month_idx=int(r.month_idx), category="Savings", program=r.program, amount=r.amount))
    for _, r in m["tdr_acc"].iterrows():
        rows.append(dict(month_idx=int(r.month_idx), category="TDR", program="OSR", amount=r.amount))
    for _, r in m["buysell"].iterrows():
        if pd.notna(r.end) and FY_START <= r.end <= FY_END:
            rows.append(dict(month_idx=fiscal_index(r.end), category="Buy/Sell", program="OSR", amount=r.profit))
    inc = pd.DataFrame(rows, columns=["month_idx", "category", "program", "amount"])
    inc["month"] = inc["month_idx"].map(lambda i: MONTHS[int(i)])
    m["income_cy"] = inc

    # Prior year monthly (savings + T-bills)
    py_rows = []
    bp = m["bank_py"]
    if not bp.empty:
        for k, a in bp.groupby("month_idx")["amount"].sum().items():
            py_rows.append(dict(month_idx=int(k), category="Savings", amount=a))
    for _, r in m["tbill_py"].iterrows():
        py_rows.append(dict(month_idx=int(r.month_idx), category="T-bills", amount=r.amount))
    m["income_py"] = pd.DataFrame(py_rows, columns=["month_idx", "category", "amount"])

    # Instruments with market benchmark
    m["instruments"] = build_instruments(m)
    return m


def tenor_for_days(days: float) -> str:
    if pd.isna(days):
        return "3M"
    return "1M" if days <= 45 else "3M" if days <= 120 else "6M" if days <= 250 else "12M"


def pkrv_asof(pkrv: pd.DataFrame, when, tenor: str) -> float:
    if pkrv.empty or tenor not in pkrv.columns or pd.isna(when):
        return np.nan
    s = pkrv[tenor].dropna()
    s = s[s.index <= pd.Timestamp(when)]
    return float(s.iloc[-1]) if len(s) else np.nan


def build_instruments(m: dict) -> pd.DataFrame:
    rows = []
    for _, r in m["tbills"].iterrows():
        rows.append(dict(type="T-bill", bank=r.bank, start=r.start, end=r.end, days=r.days, rate=r.rate,
                         principal=r.principal, profit=r.profit_total, profit_fy=r.profit_fy))
    for _, r in m["buysell"].iterrows():
        rows.append(dict(type="Buy/Sell", bank=r.bank, start=r.start, end=r.end, days=r.days, rate=r.rate,
                         principal=r.principal, profit=r.profit, profit_fy=r.profit))
    acc = m["tdr_acc"]
    for _, r in m["tdr"].iterrows():
        prof = acc.loc[acc.bank == r.bank, "amount"].sum() if not acc.empty else np.nan
        last_idx = int(acc.loc[acc.bank == r.bank, "month_idx"].max()) if not acc.empty and (acc.bank == r.bank).any() else 0
        end = (FY_START + pd.DateOffset(months=last_idx + 1)) - pd.Timedelta(days=1)
        rows.append(dict(type="TDR", bank=r.bank, start=r.start, end=end, days=(end - r.start).days if pd.notna(r.start) else np.nan,
                         rate=r.rate, principal=r.principal, profit=prof, profit_fy=prof))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["tenor"] = df["days"].map(tenor_for_days)
    df.loc[df.type == "TDR", "tenor"] = "3M"
    df["pkrv"] = [pkrv_asof(m["pkrv"], s, t) for s, t in zip(df.start, df.tenor)]
    df["spread_bps"] = (df["rate"] - df["pkrv"]) * 10000
    labels, seen = [], {}
    for r in df.itertuples():
        term = f"{int(r.days)}d" if r.type == "Buy/Sell" and pd.notna(r.days) else (r.tenor if r.type == "T-bill" else "")
        when = f"{r.start:%d %b %y}" if pd.notna(r.start) else ""
        lab = " ".join(x for x in [r.type, term, r.bank, when] if x) + f" ({money(r.principal, 'B', 1)})"
        seen[lab] = seen.get(lab, 0) + 1
        labels.append(lab if seen[lab] == 1 else f"{lab} #{seen[lab]}")
    df["label"] = labels
    return df


def policy_rate_series(mps: pd.DataFrame, index: pd.DatetimeIndex) -> pd.Series:
    if mps.empty:
        return pd.Series(np.nan, index=index)
    s = mps.set_index("date")["rate"].sort_index()
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(s.index.union(index)).ffill().reindex(index)


def holt_damped(y: np.ndarray, h: int, phi: float = 0.92):
    """Damped-trend exponential smoothing with a small grid search. Illustrative forecasting only."""
    best = None
    for a in (0.2, 0.35, 0.5, 0.65, 0.8, 0.95):
        for b in (0.01, 0.05, 0.1, 0.2):
            lvl, tr = y[0], y[1] - y[0]
            sse, res = 0.0, []
            for t in range(1, len(y)):
                f = lvl + phi * tr
                e = y[t] - f
                res.append(e)
                sse += e * e
                new = a * y[t] + (1 - a) * (lvl + phi * tr)
                tr = b * (new - lvl) + (1 - b) * phi * tr
                lvl = new
            if best is None or sse < best[0]:
                best = (sse, a, b, lvl, tr, np.array(res))
    _, a, b, lvl, tr, res = best
    sigma = float(np.std(res[-250:]))
    steps = np.arange(1, h + 1)
    damp = np.array([sum(phi ** i for i in range(1, k + 1)) for k in steps])
    fc = lvl + damp * tr
    band = sigma * np.sqrt(steps)
    return fc, band, a, b


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Treasury desk")
    st.markdown('<div class="side-note">Income, investments and market rates for the treasury pool.</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("### Data")
    up_t = st.file_uploader("Treasury income workbook", type=["xlsx"], key="up_t")
    up_p = st.file_uploader("PKRV and rates workbook", type=["xlsx"], key="up_p")
    st.markdown("### View")
    night = st.toggle("Night mode", value=False)
    mask = st.toggle("Mask account numbers", value=True)
    reduce_motion = st.toggle("Reduce motion", value=False)
    st.write("")
    st.markdown(
        '<div class="side-note">Workbooks are read from the <b>data/</b> folder unless you upload newer copies here. '
        "Uploaded files stay in this session only.</div>",
        unsafe_allow_html=True,
    )

apply_theme(night)
inject_css(reduce_motion)

if not st.session_state.get("splash_shown") and not reduce_motion:
    st.session_state["splash_shown"] = True
    st.markdown(splash_html(), unsafe_allow_html=True)

t_path = find_file(["Treasury_Income*.xlsx", "*Treasury*Income*.xlsx", "*reasury*.xlsx"])
p_path = find_file(["PKRV*.xlsx", "*PKRV*.xlsx", "*pkrv*.xlsx"])
t_bytes = up_t.getvalue() if up_t else (t_path.read_bytes() if t_path else None)
p_bytes = up_p.getvalue() if up_p else (p_path.read_bytes() if p_path else None)

if t_bytes is None:
    st.markdown(
        '<div class="hero"><div><h1>Add the treasury workbook to begin</h1>'
        '<div class="sub">Place <b>Treasury_Income_FY26_27_-_July26.xlsx</b> in a <b>data/</b> folder next to app.py, '
        "or upload it from the sidebar.</div></div><div></div></div>",
        unsafe_allow_html=True,
    )
    st.stop()

with st.spinner("Reading workbooks…"):
    try:
        M = build_model(t_bytes, p_bytes, mask)
    except Exception as exc:  # show a clear message instead of a stack trace
        st.error(f"The workbook could not be read: {exc}. Check that the sheet names match the original template.")
        st.stop()

bank_cy, bank_py = M["bank_cy"], M["bank_py"]
income_cy, income_py = M["income_cy"], M["income_py"]
quarterly, pool, inst = M["quarterly"], M["pool"], M["instruments"]
pkrv, kibor, mps, mpr = M["pkrv"], M["kibor"], M["mps"], M["mpr"]

with st.sidebar:
    programs_all = sorted(set(bank_cy.program) | set(bank_py.program), key=lambda p: list(PROGRAM_COLORS).index(p) if p in PROGRAM_COLORS else 99)
    st.markdown("### Filters")
    sel_programs = st.multiselect("Programs", programs_all, default=programs_all)
    if not sel_programs:
        sel_programs = programs_all

# ─────────────────────────────────────────────────────────────────────────────
# Headline numbers
# ─────────────────────────────────────────────────────────────────────────────
q_total = quarterly[["Q1", "Q2", "Q3", "Q4"]].sum().sum() if not quarterly.empty else income_cy.amount.sum()
monthly_cy = income_cy.groupby("month_idx")["amount"].sum().reindex(range(12), fill_value=0.0)
py_sav_months = set(income_py.loc[income_py.category == "Savings", "month_idx"])
monthly_py = income_py[income_py.month_idx.isin(py_sav_months)].groupby("month_idx")["amount"].sum().reindex(range(12))
recon_diff = income_cy.amount.sum() - q_total

savings_months = sorted(bank_cy.month_idx.unique()) if not bank_cy.empty else []
last_full = int(max(savings_months)) if savings_months else 0
pool_tot = pool.groupby("month_idx")["amount"].sum() if not pool.empty else pd.Series(dtype=float)
avg_pool = float(pool_tot.mean()) if len(pool_tot) else np.nan
yield_by_month = pd.Series(
    {k: monthly_cy[k] / pool_tot[k] * 12 for k in savings_months if k in pool_tot.index and pool_tot[k] > 0}, dtype=float
)

today = pd.Timestamp(date.today())
fy_elapsed = float(np.clip((today - FY_START).days / ((FY_END - FY_START).days + 1), 0, 1))
current_policy = float(mps.rate.iloc[-1]) if not mps.empty else (float(mpr.rate.dropna().iloc[-1]) if not mpr.rate.dropna().empty else np.nan)
next_mpc = mpr.loc[mpr.date >= today, "date"].min() if not mpr.empty else pd.NaT

pk_latest_date = pkrv.index.max() if not pkrv.empty else pd.NaT
pk3 = float(pkrv["3M"].dropna().iloc[-1]) if not pkrv.empty and "3M" in pkrv else np.nan
pk3_prev = pkrv_asof(pkrv, pk_latest_date - pd.Timedelta(days=30), "3M") if pd.notna(pk_latest_date) else np.nan
pk3_chg = (pk3 - pk3_prev) * 10000 if pd.notna(pk3_prev) else np.nan

# ─────────────────────────────────────────────────────────────────────────────
# Ticker
# ─────────────────────────────────────────────────────────────────────────────
tick = []
if not pkrv.empty:
    for t in pkrv.columns:
        s = pkrv[t].dropna()
        if len(s) < 2:
            continue
        chg = (s.iloc[-1] - s.iloc[-2]) * 10000
        cls = "up" if chg > 0 else "down" if chg < 0 else ""
        arrow = "▲" if chg > 0 else "▼" if chg < 0 else "■"
        tick.append(f'<span class="ticker-item">PKRV {t}<b>{s.iloc[-1] * 100:.2f}%</b> <span class="{cls}">{arrow} {abs(chg):.0f} bps</span></span>')
if pd.notna(current_policy):
    tick.append(f'<span class="ticker-item">Policy rate<b>{current_policy * 100:.2f}%</b></span>')
if not kibor.empty:
    for c in kibor.columns:
        s = kibor[c].dropna()
        if len(s):
            tick.append(f'<span class="ticker-item">KIBOR {c.replace("MK", "M")}<b>{s.iloc[-1] * 100:.2f}%</b> <span class="ticker-item">as of {s.index[-1]:%d %b %Y}</span></span>')
if pd.notna(next_mpc):
    tick.append(f'<span class="ticker-item">Next MPC<b>{next_mpc:%d %b %Y}</b></span>')
if len(pool_tot):
    tick.append(f'<span class="ticker-item">Treasury pool<b>PKR {money(pool_tot.iloc[-1], "B", 2)}</b></span>')
if tick:
    track = "".join(tick) * 2
    st.markdown(f'<div class="ticker"><div class="ticker-track">{track}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Hero with fiscal ribbon
# ─────────────────────────────────────────────────────────────────────────────
peak = max(monthly_cy.max(), monthly_py.max(skipna=True) if monthly_py.notna().any() else 0, 1)
ribs = []
for k in range(12):
    cy = monthly_cy[k]
    py = monthly_py[k] if pd.notna(monthly_py[k]) else 0
    h_cy = cy / peak * 100
    h_py = py / peak * 100
    d = 0.35 + k * 0.08
    now_cls = " now" if k == fiscal_index(today) and FY_START <= today <= FY_END else ""
    amt = f'<div class="amt" style="--h:{h_cy:.1f}%;--d:{d:.2f}s">{cy / 1e6:,.0f}</div>' if cy > 0 else ""
    py_line = f'<div class="val py" style="--h:{h_py:.1f}%;--d:{d:.2f}s"></div>' if py > 0 else ""
    cy_bar = f'<div class="val" style="--h:{h_cy:.1f}%;--d:{d:.2f}s"></div>' if cy > 0 else ""
    ribs.append(f'<div class="rib{now_cls}"><div class="col">{py_line}{cy_bar}{amt}</div><div class="m">{MONTHS[k]}</div></div>')

q1_whole = count_html(q_total / 1e6, 1, "M", delay=0.15)
recon_chip = (
    '<span class="chip"><span class="dot"></span>Monthly working reconciles to the quarterly summary</span>'
    if abs(recon_diff) < 1
    else f'<span class="chip warn">Monthly working differs from quarterly summary by PKR {money(recon_diff)}</span>'
)
st.markdown(
    f"""
<div class="hero">
  <div class="glow-ring"></div>
  <div>
    <div class="rise" style="animation-delay:.05s"><h1>Treasury income, <span style="white-space:nowrap">{FY_LABEL}</span></h1></div>
    <div class="sub rise" style="animation-delay:.15s">Karandaaz Pakistan. Figures in PKR, as reported in the treasury working file.</div>
    <div class="big rise" style="animation-delay:.25s"><small>PKR</small>{q1_whole}</div>
    <div class="big-label rise" style="animation-delay:.35s">Income recognised so far this fiscal year</div>
    <div class="fy-progress rise" style="animation-delay:.45s">
      <div class="bar"><div class="fill" style="--w:{fy_elapsed * 100:.1f}%"></div></div>
      <div class="meta"><span>{fy_elapsed * 100:.0f}% of the fiscal year elapsed</span><span>1 Jul 2026 to 30 Jun 2027</span></div>
    </div>
  </div>
  <div>
    <div class="ribbon">{''.join(ribs)}</div>
    <div class="ribbon-legend"><span><i style="background:{BRASS}"></i>{FY_LABEL} monthly income (PKR M)</span>
    <span><i style="border-top:2px dashed rgba(255,255,255,.6);height:0"></i>{PY_LABEL} savings and T-bills</span></div>
  </div>
</div>
<div style="margin-top:10px">{recon_chip}</div>
""",
    unsafe_allow_html=True,
)

# KPI band
jul_income = monthly_cy[0]
jul_py = monthly_py[0] if pd.notna(monthly_py[0]) else np.nan
jul_delta = (jul_income / jul_py - 1) if pd.notna(jul_py) and jul_py else np.nan
latest_yield = yield_by_month.iloc[-1] if len(yield_by_month) else np.nan
kpis = [
    ("Q1 income", count_html(q_total / 1e6, 1, "M", delay=0.3), "Quarterly summary, all funds"),
    (f"{MONTHS[last_full]} income", count_html(monthly_cy[last_full] / 1e6, 1, "M", delay=0.4),
     f"{'▲' if monthly_cy[last_full] >= (monthly_py[last_full] if pd.notna(monthly_py[last_full]) else 0) else '▼'} vs {money(monthly_py[last_full])} last year" if pd.notna(monthly_py[last_full]) else "Latest month with bank data"),
    ("Average treasury pool", count_html(avg_pool / 1e9, 2, "B", delay=0.5), f"{len(pool_tot)} months reported"),
    ("Yield on pool", count_html(latest_yield * 100, 2, "%", delay=0.6), f"Annualised, {MONTHS[int(yield_by_month.index[-1])] if len(yield_by_month) else ''}"),
    ("Policy rate", count_html(current_policy * 100, 2, "%", delay=0.7), f"Next MPC {next_mpc:%d %b}" if pd.notna(next_mpc) else "SBP"),
    ("3M PKRV", count_html(pk3 * 100, 2, "%", delay=0.8),
     (f'<span class="{"up" if pk3_chg > 0 else "down"}">{pk3_chg:+.0f} bps</span> over 30 days' if pd.notna(pk3_chg) else "")),
]
kpi_html = "".join(
    f'<div class="kpi" style="--in:{0.25 + i * 0.09:.2f}s;--d:{0.5 + i * 0.1:.2f}s"><div class="l">{l}</div><div class="v">{v}</div><div class="d">{d}</div></div>'
    for i, (l, v, d) in enumerate(kpis)
)
st.markdown(f'<div class="kpis">{kpi_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Treasury Committee presentation: slide content (edit figures here)
# Source: Treasury_Committee_Presentation_Q1-_26-27.pptx
# ─────────────────────────────────────────────────────────────────────────────
TC_DECK_DATA = {
    "meeting_date": "October 20, 2026",
    "period": "Q1 · FY 2026–27",
    "economy": {
        "title": "Pakistan Economic Update — FY2026",
        "subtitle": "Pakistan's macroeconomic footing",
        "stats": [
            {"value": 4.8,  "dec": 1, "prefix": "",  "suffix": "%", "label": "Real GDP Growth",     "sub": "Highest in 4 years"},
            {"value": 45.8, "dec": 1, "prefix": "$", "suffix": "T", "label": "Economy Size",        "sub": "YoY GDP"},
            {"value": 10.3, "dec": 1, "prefix": "",  "suffix": "%", "label": "CPI Inflation (YoY)", "sub": "Sep 2026"},
            {"value": 11.5, "dec": 1, "prefix": "",  "suffix": "%", "label": "Policy Rate",         "sub": "MPC decision, 15 Jun 2026"},
        ],
        "markets": [
            "The economy continued to consolidate gains from macroeconomic stabilization during the first two months of FY2027.",
            "The Bureau of Emigration and Overseas Employment registered 27,656 Pakistani workers for overseas employment in August 2026, supporting access to international labour markets.",
            "Core inflation came in slightly below expectations, and the policy rate remains positive in real terms.",
            "The KSE-100 index gained 882 points, or about 0.5%.",
        ],
        "bars": [
            {"label": "Inflation (Sep 2026)", "value": 11.7, "color": "#FF4D6D"},
            {"label": "Monetary Policy Rate", "value": 11.5, "color": "#8FBEDC"},
        ],
        "mpc_note": "<b>MPC Decision (14 Sep 2026):</b> Policy rate maintained at 11.5%",
    },
    "policy": {
        "labels": ["Jun 10, '24", "Jul 29, '24", "Apr 30, '25", "May 5, '25", "Dec 15, '25", "Apr 27, '26", "Jun 15, '26", "Dec '26 (proj.)", "Jun '27 (proj.)"],
        "actual": [20.5, 19.5, 13.0, 11.0, 10.5, 11.5, 11.5, None, None],
        "hold":   [None, None, None, None, None, None, 11.5, 11.5, 11.5],
        "ease":   [None, None, None, None, None, None, 11.5, 12.0, 12.5],
        "hold_name": "Scenario: Extended Hold",
        "ease_name": "Scenario: Gradual Easing",
        "chips": [
            {"value": "22.0%", "label": "Peak (pre-Jun 2024)"},
            {"value": "10.5%", "label": "Trough (Dec 2025)"},
            {"value": "11.5%", "label": "Current (held Sep 2026)"},
        ],
        "outlook": [
            "FY2027 inflation is broadly projected to average just above 8%, still outside SBP's 5–7% target band.",
            "Near term: analysts see little room for either a further hike or hold — most expect an extended hold near 11.5%.",
            "Elevated and volatile global oil prices remain the key upside risk to both inflation and the rate path.",
            "If oil prices ease and inflation cools as expected from H2 CY2026 onward, a gradual, modest easing cycle could resume later in FY2027.",
            "Two scenarios are illustrated on the chart: an extended hold vs. a gradual hike toward the 11.5–12.5% range.",
        ],
        "disclaimer": "Not financial advice. Scenarios are illustrative only — actual policy moves depend on incoming data and MPC decisions.",
        "source": "Source: State Bank of Pakistan (SBP) monetary policy statements, Jun 2024 – Jun 2026",
    },
    "pkrv": {
        "short_labels": ["Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"],
        "m1":  [10.19, 10.35, 11.21, 11.34, 11.51, 11.56, 11.48, 11.48, 11.58],
        "m3":  [10.18, 10.34, 11.28, 11.69, 11.94, 11.60, 11.45, 11.51, 11.64],
        "long_labels": ["Dec '25", "Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"],
        "m6":  [10.41, 10.28, 10.56, 11.64, 11.87, 12.37, 11.63, 11.65, 11.70, 11.84],
        "m12": [10.39, 10.35, 10.62, 11.90, 12.04, 12.52, 11.60, 11.81, 11.95, 12.20],
        "y2":  [10.45, 10.27, 10.55, 12.46, 12.38, 12.62, 11.69, 11.65, 11.87, 12.46],
        "as_of": "Sep 30, 2026",
    },
    "pool": {
        "as_of": "September 30, 2026",
        # [Account, Rate %, Bucket, PKR Mn]
        "accounts": [
            ["HBL Liquidity Reserve A/c", 9.50, "LR", 0.27],
            ["HMBL OSR A/c", 10.00, "LR", 6.64],
            ["Faysal OSR A/c", 10.25, "LR", 2035.84],
            ["Samba OSR A/c", 10.30, "LR", 1041.92],
            ["ABL OSR A/c", 9.00, "LR", 0.08],
            ["UBL T-Bills", 11.42, "LR", 2354.07],
            ["HMBL Buy & Sell", 11.57, "OSR", 4000.52],
            ["Faysal OSR A/c", 10.25, "OSR", 1934.22],
            ["BAFL OSR A/c", 10.75, "OSR", 1775.95],
            ["UBL OSR A/c", 11.00, "OSR", 258.58],
            ["BIPL OSR A/c", 8.00, "OSR", 513.69],
            ["UBL Investment Account", 11.00, "Investment", 477.59],
            ["BAFL Investment Account", 10.75, "Investment", 10.83],
            ["BAFL CIC A/c (For PFSL)", 10.75, "Investment", 94.46],
            ["BAFL RPA A/c", 10.75, "RPA", 86.68],
            ["JSBL RPA A/c", 6.73, "RPA", 24.58],
            ["Meezan RPA A/c", 2.52, "RPA", 5.39],
            ["MIB RPA A/c", 6.42, "RPA", 1058.93],
            ["HMBL RPA A/c", 10.00, "RPA", 0.07],
            ["Soneri RPA A/c", 6.50, "RPA", 21.84],
            ["UBL WV A/c", 11.00, "WV", 0.01],
            ["Faysal WV A/c", 10.25, "WV", 332.04],
            ["Samba KCBL A/c", 10.30, "WV", 105.72],
        ],
        "highlight": ["UBL T-Bills", "HMBL Buy & Sell"],
        "buckets": [
            {"key": "LR", "name": "Liquidity Reserve", "value": 5438.82},
            {"key": "OSR", "name": "OSR", "value": 8482.96},
            {"key": "Investment", "name": "Investment", "value": 582.88},
            {"key": "RPA", "name": "RPA", "value": 1197.50},
            {"key": "WV", "name": "WV", "value": 437.76},
        ],
        "total": 16139.92,
        "weighted_rate": 10.51,
    },
    "grants": {
        "as_of": "September 30, 2026",
        # [Account, GF, FIP]  (PKR Mn)
        "accounts": [
            ["BAFL USD A/c (USD to PKR)*", 2042.99, None],
            ["BAFL Ehsaas A/c", 10.88, None],
            ["BAFL CCT A/c", 8.97, None],
            ["BAFL Raast A/c", 1.81, None],
            ["BAFL PCDFI A/c", 17.35, None],
            ["UBL PCDFI A/c", 1.74, None],
            ["BAFL FBR A/c", 34.09, None],
            ["BAFL FIP A/c", None, 0.59],
            ["UBL FIP A/c", None, 254.86],
            ["HMBL FIP A/c", None, 0.00],
        ],
        "gf": 2117.83, "fip": 255.46, "total": 2373.29,
        "note": "* USD amounts are converted to PKR @ 277.50 (September 30, 2026 NBP rate sheet)",
    },
    "banks": {
        "as_of": "June 30, 2026",
        # [Bank, Long-Term Rating, Balance, Portfolio %, Rate offered, Utilization %, Institutional Limit, Under/(Over)]
        "rows": [
            ["Faysal", "AA+", 4302, 25.96, 10.25, 38, 11233, 6931],
            ["Samba", "AA", 1148, 6.92, 10.30, 97, 1178, 30],
            ["BAFL", "AAA", 2097, 12.65, 10.75, 11, 19210, 17113],
            ["UBL", "AAA", 1039, 6.27, 11.00, 2, 44431, 43392],
            ["MIB", "A+", 1059, 6.39, 6.24, 49, 2171, 1113],
            ["BIPL", "AA-", 514, 3.10, 8.00, 11, 4657, 4143],
            ["Other Banks", None, 61, 0.37, None, None, None, None],
            ["T-Bills", None, 2354, 14.20, 10.92, None, None, None],
            ["Buy & Sell", None, 4001, 24.14, 10.65, None, None, None],
        ],
        "total": 16573,
        "notes": [
            "Bank-wise portfolio includes all PKR balances except USD funds available in account",
            "Does not include escrow funds (PKR 220M)",
        ],
    },
    "income": {
        "headline": "Treasury has generated PKR 444.6M income during Q1 FY 26-27",
        # [Type, Opening Balance (PKR), Q1 Income (PKR)]
        "rows": [
            ["Income on LR deposit - EAGR", 5438817702, 147828615.30],
            ["Income on escrow a/cs - EAGR", 205720218, 7162137],
            ["Treasury income - EAGR", 10653957151, 289577591.93],
        ],
        "opening_total": 16298495071, "income_total": 444568344,
    },
    "forecast": {
        # [Income bucket, Avg balance for the year, Q1 (Actual), Q2, Q3, Q4]  (PKR)
        "rows": [
            ["Income on LR deposit - EAGR", 5662166647, 147828615, 147780872, 148698418, 152656322],
            ["Income on escrow a/cs - EAGR", 214169051, 7162137, 5532690, 5681488, 5834287],
            ["Treasury income - EAGR", 11050013806, 289577592, 286530151, 313030275, 310173160],
        ],
        "avg_total": 16926349504,
        "q_totals": [444568344, 439843713, 467410180, 468663769],
        "grand_total": 1820486007,
    },
}

TC_DECK_TEMPLATE = r'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Manrope:ital,wght@0,300;0,400;0,500;0,700;0,800;1,400&display=swap" rel="stylesheet">
<style>
:root{--orange:#FF4D6D;--sky:#8FBEDC;--gold:#A99CF0;--brand:#004369;--muted:rgba(255,255,255,.64);--faint:rgba(255,255,255,.42);--line:rgba(143,190,220,.18)}
*{box-sizing:border-box;margin:0;padding:0;font-family:'Manrope','Segoe UI',sans-serif}
.title,.cover h1,.stat .v,.big,.kstrip .k .v,.chip .v,.close-h{font-family:'Sora','Manrope',sans-serif!important}
html,body{width:100%;height:100%;overflow:hidden;color:#fff;background:transparent}
#viewport{position:absolute;left:0;right:0;top:0;bottom:60px;overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform-origin:center center;border-radius:20px;overflow:hidden;box-shadow:0 24px 70px rgba(4,27,40,.45);background:#03111E}
:fullscreen body,:fullscreen #viewport{background:#020d14}
:fullscreen #stage{border-radius:0}
.num{font-variant-numeric:tabular-nums}

/* ---------- slides ---------- */
.slide{position:absolute;inset:0;padding:54px 72px 64px;opacity:0;visibility:hidden;transform:translateX(46px) scale(.985);
  transition:opacity .75s cubic-bezier(.2,.7,.2,1),transform .75s cubic-bezier(.2,.7,.2,1),visibility 0s linear .75s;
  background:radial-gradient(1100px 650px at 92% -12%,rgba(0,67,105,.62),transparent 62%),
             radial-gradient(800px 520px at -8% 112%,rgba(255,77,109,.11),transparent 60%),
             linear-gradient(160deg,#0A2A44 0%,#04192B 55%,#03111E 100%)}
.slide.before{transform:translateX(-46px) scale(.985)}
.slide.active{opacity:1;visibility:visible;transform:none;transition:opacity .75s cubic-bezier(.2,.7,.2,1),transform .75s cubic-bezier(.2,.7,.2,1),visibility 0s}
.rings{position:absolute;right:-260px;top:-300px;width:760px;height:760px;pointer-events:none;opacity:.55}
.rings circle{fill:none;stroke:rgba(143,190,220,.10);stroke-width:1.2}
.slide.active .rings{animation:spin 90s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

.rv{opacity:0;transform:translateY(20px)}
.slide.active .rv{animation:rise .85s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 180ms)}
@keyframes rise{to{opacity:1;transform:none}}
.rvx{opacity:0;transform:translateX(-16px)}
.slide.active .rvx{animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 180ms)}

/* header */
.hd{position:relative;display:flex;gap:28px;justify-content:space-between;align-items:flex-end;margin-bottom:30px;z-index:2}
.eyebrow{display:flex;align-items:center;gap:14px;font-size:14px;letter-spacing:4px;text-transform:uppercase;color:var(--orange);font-weight:700}
.eyebrow .no{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;border:1.5px solid rgba(255,77,109,.6);font-size:13px;letter-spacing:0;color:#fff;background:rgba(255,77,109,.14)}
.title{font-size:48px;font-weight:900;line-height:1.06;margin-top:14px;letter-spacing:-.6px}
.sub{font-size:19px;color:var(--muted);margin-top:8px;font-weight:300;font-style:italic}
.ft{position:absolute;left:72px;right:72px;bottom:24px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:var(--faint);letter-spacing:2px;text-transform:uppercase;z-index:2}
.ft b{color:rgba(255,255,255,.7);font-weight:700}

/* cards */
.card{position:relative;background:linear-gradient(180deg,rgba(255,255,255,.065),rgba(255,255,255,.02));border:1px solid var(--line);border-radius:22px;padding:26px 30px;box-shadow:0 18px 40px rgba(0,0,0,.25)}
.ct{font-size:13px;letter-spacing:3px;text-transform:uppercase;color:var(--sky);font-weight:700;margin-bottom:18px;display:flex;align-items:baseline;gap:10px;line-height:1.4}
.ct .dot{flex:none;transform:translateY(-1px)}
.ct .dot{width:8px;height:8px;border-radius:50%;background:var(--orange);box-shadow:0 0 12px var(--orange)}
.grid{display:grid;gap:24px}

/* stats */
.stat{padding:26px 28px;overflow:hidden}
.stat .v{font-size:60px;font-weight:900;line-height:1;letter-spacing:-1.5px}
.stat .l{font-size:18px;font-weight:700;margin-top:14px}
.stat .s{font-size:14px;color:var(--faint);margin-top:6px;letter-spacing:.5px}
.stat .glow{position:absolute;right:-40px;top:-40px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(255,77,109,.35),transparent 70%)}
.stat:nth-child(2) .glow{background:radial-gradient(circle,rgba(143,190,220,.35),transparent 70%)}
.stat:nth-child(3) .glow{background:radial-gradient(circle,rgba(169,156,240,.30),transparent 70%)}
.stat:nth-child(4) .glow{background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%)}

/* lists */
.bl{list-style:none}
.bl li{position:relative;padding-left:34px;font-size:18px;line-height:1.5;color:rgba(255,255,255,.9);margin-bottom:16px;font-weight:300}
.bl li:before{content:"";position:absolute;left:4px;top:9px;width:12px;height:12px;border-radius:3px 50% 50% 50%;background:var(--orange);transform:rotate(45deg);box-shadow:0 0 10px rgba(255,77,109,.6)}
.bl.sky li:before{background:var(--sky);box-shadow:0 0 10px rgba(143,190,220,.6)}
.bl.sm li{font-size:16.5px;margin-bottom:13px}

/* bars */
.hb{margin-bottom:26px}
.hb .top{display:flex;justify-content:space-between;font-size:17px;margin-bottom:10px}
.hb .top b{font-size:26px;font-weight:900}
.track{height:16px;border-radius:10px;background:rgba(255,255,255,.07);overflow:hidden}
.fill{height:100%;border-radius:10px;transform-origin:left center;transform:scaleX(0)}
.slide.active .fill{animation:growx 1.4s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 350ms)}
@keyframes growx{to{transform:scaleX(1)}}
.callout{margin-top:22px;padding:18px 22px;border-radius:16px;background:rgba(255,77,109,.10);border:1px solid rgba(255,77,109,.35);font-size:17px;line-height:1.5}
.callout b{color:var(--orange)}

/* chips */
.chips{display:flex;gap:14px}
.chip{padding:12px 18px;border-radius:16px;background:rgba(255,255,255,.05);border:1px solid var(--line);text-align:center;white-space:nowrap}
.chip .v{font-size:26px;font-weight:900;line-height:1}
.chip .l{font-size:11px;color:var(--faint);letter-spacing:1.2px;text-transform:uppercase;margin-top:8px}
.chip.hot{background:rgba(255,77,109,.14);border-color:rgba(255,77,109,.5)}
.chip.hot .v{color:var(--orange)}

/* charts */
svg text{font-family:'Manrope','Segoe UI',sans-serif}
.gl{stroke:rgba(255,255,255,.08);stroke-width:1}
.ax{fill:rgba(255,255,255,.55);font-size:13px}
.ln{fill:none;stroke-linecap:round;stroke-linejoin:round}
.pt{opacity:0}
.slide.active .pt{animation:fade .5s forwards;animation-delay:calc(var(--d,0) * 1ms)}
@keyframes fade{to{opacity:1}}
.legend{display:flex;gap:22px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:8px}
.legend i{display:inline-block;width:22px;height:4px;border-radius:3px}
.legend i.dash{background:repeating-linear-gradient(90deg,currentColor 0 6px,transparent 6px 10px)!important;height:3px}
.bar{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(0)}
.slide.active .bar{animation:growy 1.1s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 300ms)}
@keyframes growy{to{transform:scaleY(1)}}
.seg{transition:stroke-dasharray 1.5s cubic-bezier(.2,.8,.2,1)}

/* tables */
.tbl{width:100%;border-collapse:collapse}
.tbl th{font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--sky);font-weight:700;text-align:left;padding:0 10px 10px;border-bottom:1px solid rgba(143,190,220,.3);white-space:nowrap}
.tbl td{padding:0 10px;border-bottom:1px solid rgba(255,255,255,.055);font-size:15px;color:rgba(255,255,255,.9);white-space:nowrap}
.tbl .r{text-align:right;font-variant-numeric:tabular-nums}
.tbl .c{text-align:center}
.tbl tfoot td{border-bottom:none;border-top:1px solid rgba(143,190,220,.35);font-weight:900;font-size:16px;color:#fff;padding-top:10px}
.tbl tfoot td.o{color:var(--orange)}
.tbl tr.hl td{background:rgba(143,190,220,.09)}
.tbl tr.hl td:first-child{border-radius:8px 0 0 8px}
.tbl tr.hl td:last-child{border-radius:0 8px 8px 0}
.pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11.5px;font-weight:700;letter-spacing:.8px}
.mini{display:flex;align-items:center;gap:10px;justify-content:flex-end}
.mini .t{width:120px;height:7px;border-radius:5px;background:rgba(255,255,255,.07);overflow:hidden}
.mini .t div{height:100%;border-radius:5px;transform-origin:left;transform:scaleX(0)}
.slide.active .mini .t div{animation:growx 1.2s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 400ms)}
.badge{display:inline-block;min-width:46px;text-align:center;padding:3px 8px;border-radius:8px;border:1px solid rgba(143,190,220,.45);color:var(--sky);font-size:13px;font-weight:700}
.muted{color:var(--faint)}
.note{font-size:13.5px;color:var(--faint);line-height:1.5}

/* cover */
.cover{padding:0}
.cover .inner{position:absolute;left:96px;top:110px;right:96px;z-index:2}
.logo-chip{display:inline-flex;align-items:center;gap:12px;background:#004369;border:1px solid rgba(143,190,220,.35);border-radius:16px;padding:10px 18px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.logo-chip img{height:46px;display:block}
.logo-chip .t{font-weight:900;letter-spacing:4px;font-size:18px}
.cover h1{font-size:96px;font-weight:800;line-height:1.0;letter-spacing:-2.5px;margin-top:46px}
.cover h1 em{font-style:normal;background:linear-gradient(90deg,#FF4D6D,#A99CF0);-webkit-background-clip:text;background-clip:text;color:transparent}
.cover .date{font-size:26px;font-weight:300;font-style:italic;color:var(--muted);margin-top:22px}
.kstrip{display:flex;gap:18px;margin-top:46px}
.kstrip .k{padding:18px 26px;border-radius:18px;background:rgba(255,255,255,.05);border:1px solid var(--line);backdrop-filter:blur(6px)}
.kstrip .k .v{font-size:34px;font-weight:900}
.kstrip .k .v small{font-size:17px;font-weight:400;color:var(--muted);margin-right:6px}
.kstrip .k .l{font-size:12.5px;letter-spacing:2px;text-transform:uppercase;color:var(--sky);margin-top:6px}
.pat{position:absolute;left:0;right:0;bottom:0;pointer-events:none}
.pat g.pg{opacity:0}
.slide.active .pat g.pg{animation:pop .7s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms)}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:var(--o,.6);transform:scale(1)}}
.pat g.pg{transform-box:fill-box;transform-origin:center}
.orb{position:absolute;right:-220px;top:-160px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(0,67,105,.9),rgba(6,43,63,.2) 60%,transparent 70%);filter:blur(2px)}
.hero{background:linear-gradient(140deg,#004369 0%,#0B3556 55%,#062640 100%);border:1px solid rgba(143,190,220,.35);overflow:hidden}
.hero .big{font-size:110px;font-weight:900;line-height:1;letter-spacing:-3px;background:linear-gradient(90deg,#A99CF0,#FF4D6D);-webkit-background-clip:text;background-clip:text;color:transparent}
.spark{position:absolute;border-radius:2px;background:#fff;opacity:.7}
.slide.active .spark{animation:twinkle 3s ease-in-out infinite}
@keyframes twinkle{50%{opacity:.15;transform:rotate(45deg) scale(.6)}}

/* controls */
#bar{position:absolute;left:0;right:0;bottom:0;height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 18px;color:__BAR_INK__}
#bar .lbl{font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.8;min-width:260px}
#bar .mid{display:flex;align-items:center;gap:14px}
#bar .rt{display:flex;align-items:center;gap:12px;min-width:260px;justify-content:flex-end}
.btn{width:40px;height:40px;border-radius:50%;border:2px solid __BAR_INK__;background:__BAR_BG__;color:__BAR_INK__;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s}
.btn:hover{background:__BAR_INK__;color:__BAR_BG__;transform:scale(1.06)}
.btn.wide{width:auto;padding:0 16px;border-radius:20px;font-weight:700;font-size:13px;letter-spacing:1px;gap:8px}
#dots{display:flex;gap:8px}
#dots b{width:10px;height:10px;border-radius:10px;background:__BAR_DOT__;cursor:pointer;transition:all .3s}
#dots b.on{width:30px;background:#FF4D6D}
#count{font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}
#hint{font-size:12px;opacity:.6}
:fullscreen #bar{color:#cfe6f1}
:fullscreen .btn{background:transparent;border-color:#8FBEDC;color:#8FBEDC}
#prog{position:absolute;left:0;top:0;height:3px;background:linear-gradient(90deg,#FF4D6D,#A99CF0);z-index:20;transition:width .6s cubic-bezier(.2,.8,.2,1)}
</style></head>
<body>
<div id="viewport"><div id="stage"><div id="prog"></div></div></div>
<div id="bar">
  <div class="lbl">Treasury Committee · Q1 FY26-27</div>
  <div class="mid">
    <div class="btn" id="prev" title="Previous (←)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></div>
    <div id="dots"></div>
    <div class="btn" id="next" title="Next (→)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></div>
  </div>
  <div class="rt">
    <span id="hint">← → to navigate · F for full screen</span>
    <span id="count">01 / 10</span>
    <div class="btn wide" id="fs" title="Full screen (F)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>PRESENT</div>
  </div>
</div>
<script>
const D = __DECK_DATA__;
const LOGO = "__LOGO_B64__";
const COL = {orange:'#FF4D6D', sky:'#8FBEDC', gold:'#A99CF0', white:'#EAF4F8', teal:'#3E86B8', slate:'#9fb6c3'};
const BUCKET = {LR:COL.sky, OSR:COL.orange, Investment:COL.gold, RPA:COL.white, WV:COL.teal};
const f = (n,d=2)=> (n==null||isNaN(n)) ? '–' : Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const M = n => n/1e6;
const TOTAL = 10;

/* ---------- motif: Karandaaz circles & quarter-circles ---------- */
function rng(seed){return ()=>{seed=(seed*16807)%2147483647;return (seed-1)/2147483646}}
function pattern(cols,rows,cell,seed,empty,maxO){
  const r=rng(seed), s=cell*0.78, pad=(cell-s)/2; let out='';
  const cols_=['#8FBEDC','#3E86B8','#ffffff','#4E9BD1','#9fb6c3'];
  for(let y=0;y<rows;y++) for(let x=0;x<cols;x++){
    const v=r(); const k=Math.floor(r()*5); const c=cols_[Math.floor(r()*cols_.length)];
    // fewer shapes in the upper rows -> skyline effect
    const thr = empty + (rows-1-y)*0.16;
    if(v<thr) continue;
    const ox=x*cell+pad, oy=y*cell+pad, o=(0.25+r()*maxO).toFixed(2), d=Math.round((x*35)+(rows-y)*60+r()*200);
    let shape = k===0 ? `<circle cx="${s/2}" cy="${s/2}" r="${s/2-1}"/>`
      : `<path d="M0 ${s} L0 0 A${s} ${s} 0 0 1 ${s} ${s} Z" transform="rotate(${(k-1)*90} ${s/2} ${s/2})"/>`;
    out+=`<g transform="translate(${ox} ${oy})"><g class="pg" style="--d:${d};--o:${o}" fill="none" stroke="${c}" stroke-width="1.8">${shape}</g></g>`;
  }
  return out;
}
const rings = `<svg class="rings" viewBox="0 0 760 760"><circle cx="380" cy="380" r="370"/><circle cx="380" cy="380" r="300" stroke-dasharray="4 10"/><circle cx="380" cy="380" r="225"/><circle cx="380" cy="380" r="150" stroke-dasharray="2 8"/></svg>`;

function hd(n, eyebrow, title, sub, right=''){
  return `<div class="hd"><div><div class="eyebrow rvx" style="--d:0"><span class="no">${String(n).padStart(2,'0')}</span>${eyebrow}</div>
  <div class="title rv" style="--d:80">${title}</div>${sub?`<div class="sub rv" style="--d:160">${sub}</div>`:''}</div>${right}</div>`;
}
const ft = i => `<div class="ft"><span><b>Karandaaz Pakistan</b> &nbsp;·&nbsp; Treasury Committee</span><span>${D.period} &nbsp;·&nbsp; ${String(i+1).padStart(2,'0')}</span></div>`;

/* ---------- chart helpers ---------- */
function lineChart(o){
  const W=o.w,H=o.h,P={l:58,r:o.pr||28,t:20,b:44},iw=W-P.l-P.r,ih=H-P.t-P.b,n=o.labels.length;
  const x=i=>P.l+i*iw/(n-1), y=v=>P.t+ih-(v-o.min)/(o.max-o.min)*ih;
  let g='';
  for(let v=o.min; v<=o.max+1e-9; v+=o.step){
    g+=`<line class="gl" x1="${P.l}" x2="${W-P.r}" y1="${y(v)}" y2="${y(v)}"/><text class="ax" x="${P.l-12}" y="${y(v)+4.5}" text-anchor="end">${f(v,o.dec??0)}%</text>`;
  }
  o.labels.forEach((l,i)=>{ if(o.every && i%o.every) return; g+=`<text class="ax" x="${x(i)}" y="${H-P.b+26}" text-anchor="middle">${l}</text>`});
  if(o.vline!=null){ const vx=x(o.vline); g+=`<line x1="${vx}" x2="${vx}" y1="${P.t}" y2="${P.t+ih}" stroke="rgba(255,255,255,.35)" stroke-dasharray="5 6"/><text class="ax" x="${vx+10}" y="${P.t+14}" font-style="italic">${o.vlabel||''}</text>`;}
  if(o.band){ const [a,b]=o.band; g+=`<rect x="${P.l}" width="${iw}" y="${y(b)}" height="${y(a)-y(b)}" fill="rgba(143,190,220,.06)"/>`; }
  let s='';
  o.series.forEach((se,si)=>{
    const pts=se.values.map((v,i)=>v==null?null:[x(i),y(v)]).filter(Boolean);
    if(!pts.length) return;
    let d=''; pts.forEach((p,i)=>{ d+= (i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)+' '; });
    if(se.area){ const a=d+`L${pts[pts.length-1][0]} ${P.t+ih} L${pts[0][0]} ${P.t+ih} Z`;
      s+=`<path d="${a}" fill="url(#ga${o.id}${si})" class="pt" style="--d:${900+si*200}"/>`;
      s+=`<defs><linearGradient id="ga${o.id}${si}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${se.color}" stop-opacity=".28"/><stop offset="1" stop-color="${se.color}" stop-opacity="0"/></linearGradient></defs>`; }
    s+=`<path class="ln anim" d="${d}" stroke="${se.color}" stroke-width="${se.w||3.5}" ${se.dash?'data-dash="'+se.dash+'"':''} style="filter:drop-shadow(0 0 6px ${se.color}55)" data-delay="${si*250}"/>`;
    pts.forEach((p,i)=>{ s+=`<circle class="pt" style="--d:${500+si*250+i*110}" cx="${p[0]}" cy="${p[1]}" r="${se.r||5}" fill="#0A2A44" stroke="${se.color}" stroke-width="2.5"/>`; });
    if(se.endLabel){ const p=pts[pts.length-1]; const v=se.values.filter(v=>v!=null).slice(-1)[0];
      s+=`<g class="pt" style="--d:${1500+si*250}"><rect x="${p[0]+10}" y="${p[1]-13+(se.lo||0)}" rx="7" width="62" height="26" fill="${se.color}"/><text x="${p[0]+41}" y="${p[1]+5+(se.lo||0)}" text-anchor="middle" font-size="14" font-weight="900" fill="#03111E">${f(v,2)}%</text></g>`; }
  });
  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}${s}</svg>`;
}
function donut(o){
  const S=o.size,T=o.thick,r=(S-T)/2,C=2*Math.PI*r,tot=o.items.reduce((a,b)=>a+b.value,0); let acc=0,s='';
  s+=`<circle cx="${S/2}" cy="${S/2}" r="${r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="${T}"/>`;
  o.items.forEach((it,i)=>{ const len=it.value/tot*C, gap=o.items.length>1?Math.min(3,len*0.3):0;
    s+=`<circle class="seg" data-len="${Math.max(len-gap,0.01)}" data-c="${C}" cx="${S/2}" cy="${S/2}" r="${r}" fill="none" stroke="${it.color}" stroke-width="${T}" stroke-dasharray="0 ${C}" stroke-dashoffset="${-acc}" transform="rotate(-90 ${S/2} ${S/2})" style="transition-delay:${300+i*140}ms"/>`;
    acc+=len; });
  return `<div style="position:relative;width:${S}px;height:${S}px;flex:none">
    <svg width="${S}" height="${S}" style="filter:drop-shadow(0 10px 30px rgba(0,0,0,.35))">${s}</svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">${o.center}</div></div>`;
}
function legendRows(items, unit='M', dec=2){
  const tot=items.reduce((a,b)=>a+b.value,0);
  return items.map((it,i)=>`<div class="rv" style="--d:${400+i*90};display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.06)">
    <span style="width:12px;height:12px;border-radius:50%;background:${it.color};box-shadow:0 0 10px ${it.color}"></span>
    <span style="flex:1;font-size:16px">${it.label}</span>
    <span class="num" style="font-size:16px;font-weight:700">${f(it.value,dec)}${unit?' '+unit:''}</span>
    <span class="num" style="width:62px;text-align:right;font-size:15px;color:${it.color};font-weight:700">${f(it.value/tot*100,1)}%</span></div>`).join('');
}

/* ---------- slides ---------- */
function sCover(){
  const logo = LOGO ? `<div class="logo-chip"><img src="data:image/jpeg;base64,${LOGO}"></div>` : `<div class="logo-chip"><span class="t">KARANDAAZ</span></div>`;
  const p=D.pool, inc=D.income;
  return `<div class="orb"></div>${rings}
  <svg class="pat" width="1600" height="300" viewBox="0 0 1600 300">${pattern(32,6,50,7,0.48,0.45)}</svg>
  <div class="inner">
    <div class="rv" style="--d:0">${logo}</div>
    <div class="eyebrow rvx" style="--d:150;margin-top:56px"><span class="no">Q1</span>${D.period} &nbsp;·&nbsp; Board Presentation</div>
    <h1 class="rv" style="--d:250">Treasury Committee<br><em>Meeting</em></h1>
    <div class="date rv" style="--d:400">${D.meeting_date}</div>
    <div class="kstrip">
      <div class="k rv" style="--d:600"><div class="v num"><small>PKR</small><span data-count="${p.total}" data-dec="2"></span><small style="margin-left:6px">M</small></div><div class="l">Treasury Investment Pool</div></div>
      <div class="k rv" style="--d:720"><div class="v num"><small>PKR</small><span data-count="${M(inc.income_total)}" data-dec="1"></span><small style="margin-left:6px">M</small></div><div class="l">Q1 Treasury Income</div></div>
      <div class="k rv" style="--d:840"><div class="v num"><span data-count="${p.weighted_rate}" data-dec="2" data-suffix="%"></span></div><div class="l">Weighted Pool Rate</div></div>
    </div>
  </div>`;
}
function sEconomy(i){
  const e=D.economy;
  const stats=e.stats.map((s,k)=>`<div class="card stat rv" style="--d:${200+k*110}"><div class="glow"></div>
    <div class="v num" style="color:${[COL.orange,'#fff',COL.gold,COL.sky][k]}"><span data-count="${s.value}" data-dec="${s.dec}" data-prefix="${s.prefix}" data-suffix="${s.suffix}"></span></div>
    <div class="l">${s.label}</div><div class="s">${s.sub}</div></div>`).join('');
  const max=Math.max(...e.bars.map(b=>b.value))*1.08;
  const bars=e.bars.map((b,k)=>`<div class="hb rv" style="--d:${700+k*150}"><div class="top"><span>${b.label}</span><b class="num" style="color:${b.color}">${f(b.value,1)}%</b></div>
    <div class="track"><div class="fill" style="--d:${700+k*150};width:${b.value/max*100}%;background:linear-gradient(90deg,${b.color}66,${b.color})"></div></div></div>`).join('');
  return `${rings}${hd(i+1,'Macro Snapshot',e.title,e.subtitle)}
  <div class="grid" style="grid-template-columns:repeat(4,1fr)">${stats}</div>
  <div class="grid" style="grid-template-columns:1.25fr 1fr;margin-top:24px">
    <div class="card rv" style="--d:600;height:410px"><div class="ct"><span class="dot"></span>Investor Confidence & Capital Markets</div>
      <ul class="bl">${e.markets.map((m,k)=>`<li class="rv" style="--d:${750+k*120}">${m}</li>`).join('')}</ul></div>
    <div class="card rv" style="--d:680;height:410px"><div class="ct"><span class="dot"></span>Inflation & Monetary Policy</div>
      <div style="margin-top:14px">${bars}</div>
      <div class="callout rv" style="--d:1100">${e.mpc_note}</div></div>
  </div>${ft(i)}`;
}
function sPolicy(i){
  const p=D.policy;
  const chips=`<div class="chips">${p.chips.map((c,k)=>`<div class="chip rv ${k==2?'hot':''}" style="--d:${200+k*100}"><div class="v num">${c.value}</div><div class="l">${c.label}</div></div>`).join('')}</div>`;
  const chart=lineChart({id:'pol',w:900,h:500,labels:p.labels,min:8,max:22,step:2,vline:6,vlabel:'FY2027 (illustrative)',pr:40,
    series:[{values:p.actual,color:COL.sky,area:true,w:4},{values:p.hold,color:COL.slate,dash:'2 9',w:3.5},{values:p.ease,color:COL.orange,dash:'2 9',w:3.5}]});
  return `${rings}${hd(i+1,'Monetary Policy','SBP Policy Rate — Trend & Outlook','Policy rate path since June 2024, with an illustrative outlook for FY2027',chips)}
  <div class="grid" style="grid-template-columns:960px 1fr">
    <div class="card rv" style="--d:300;padding:22px 24px 18px">
      <div class="legend" style="margin:0 0 6px 58px"><span><i style="background:${COL.sky}"></i>Policy Rate (Actual)</span><span style="color:${COL.slate}"><i class="dash"></i>${p.hold_name}</span><span style="color:${COL.orange}"><i class="dash"></i>${p.ease_name}</span></div>
      ${chart}
      <div class="note" style="margin:4px 0 0 58px">${p.source}</div></div>
    <div class="card rv" style="--d:450;display:flex;flex-direction:column"><div class="ct"><span class="dot"></span>FY2027 Outlook — What Analysts Are Watching</div>
      <ul class="bl sky sm" style="flex:1">${p.outlook.map((m,k)=>`<li class="rv" style="--d:${600+k*110}">${m}</li>`).join('')}</ul>
      <div class="note rv" style="--d:1200;font-style:italic;padding:12px 16px;border-radius:12px;background:rgba(255,255,255,.04);border:1px dashed rgba(255,255,255,.18)">${p.disclaimer}</div></div>
  </div>${ft(i)}`;
}
function sPkrv(i){
  const k=D.pkrv;
  const tiles=[['1M',k.m1,0,COL.orange],['3M',k.m3,0,'#ffffff'],['6M',k.m6,1,COL.sky],['12M',k.m12,1,COL.gold],['2Y',k.y2,1,COL.teal]].map((t,j)=>{
    const last=t[1][t[1].length-1], base=t[1][t[2]], bps=Math.round((last-base)*100);
    return `<div class="card rv" style="--d:${200+j*90};padding:18px 22px;flex:1">
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:14px;font-weight:900;letter-spacing:2px;color:${t[3]}">${t[0]} PKRV</span>
      <span class="num" style="font-size:12.5px;font-weight:700;padding:3px 9px;border-radius:12px;background:${bps>=0?'rgba(255,77,109,.16)':'rgba(143,190,220,.16)'};color:${bps>=0?COL.orange:COL.sky}">${bps>=0?'▲':'▼'} ${Math.abs(bps)} bps</span></div>
      <div class="num" style="font-size:38px;font-weight:900;margin-top:8px"><span data-count="${last}" data-dec="2" data-suffix="%"></span></div>
      <div class="note" style="margin-top:2px">since Jan '26</div></div>`; }).join('');
  const c1=lineChart({id:'st',w:672,h:400,labels:k.short_labels,min:10,max:12.5,step:0.5,dec:1,pr:84,
      series:[{values:k.m1,color:COL.orange,endLabel:true,lo:-10},{values:k.m3,color:'#ffffff',endLabel:true,lo:-24}]});
  const c2=lineChart({id:'lt',w:672,h:400,labels:k.long_labels,min:10,max:13,step:0.5,dec:1,pr:84,every:1,
      series:[{values:k.m6,color:COL.sky,endLabel:true,lo:26},{values:k.m12,color:COL.gold,endLabel:true,lo:-4},{values:k.y2,color:COL.teal,endLabel:true,lo:-32}]});
  return `${rings}${hd(i+1,'Secondary Market Yields','Short & Long-Term Trend Analysis of PKRVs','Month-end PKRV rates · latest as at '+k.as_of)}
  <div style="display:flex;gap:18px">${tiles}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr;margin-top:20px">
    <div class="card rv" style="--d:500;padding:20px 22px 10px"><div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Short-Term Trend</div>
      <div class="legend"><span><i style="background:${COL.orange}"></i>1M</span><span><i style="background:#fff"></i>3M</span></div></div>${c1}</div>
    <div class="card rv" style="--d:600;padding:20px 22px 10px"><div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Long-Term Trend</div>
      <div class="legend"><span><i style="background:${COL.sky}"></i>6M</span><span><i style="background:${COL.gold}"></i>12M</span><span><i style="background:${COL.teal}"></i>2Y</span></div></div>${c2}</div>
  </div>${ft(i)}`;
}
function sPool(i){
  const p=D.pool, mx=Math.max(...p.accounts.map(a=>a[3]));
  const items=p.buckets.map(b=>({label:b.name,value:b.value,color:BUCKET[b.key]}));
  const rows=p.accounts.map((a,k)=>`<tr class="rv ${p.highlight.includes(a[0])?'hl':''}" style="--d:${300+k*35};height:21.6px">
    <td>${a[0]}</td><td><span class="pill" style="background:${BUCKET[a[2]]}22;color:${BUCKET[a[2]]};border:1px solid ${BUCKET[a[2]]}66">${a[2]}</span></td>
    <td class="r">${f(a[1],2)}%</td><td class="r"><div class="mini"><span class="num">${f(a[3],2)}</span><div class="t"><div style="--d:${300+k*35};width:${Math.max(a[3]/mx*100,0.8)}%;background:${BUCKET[a[2]]}"></div></div></div></td></tr>`).join('');
  return `${rings}${hd(i+1,'Investment Pool','Investment Pool as of '+p.as_of,'Treasury Investment Pool (excluding grants) · PKR in Million')}
  <div class="grid" style="grid-template-columns:520px 1fr">
    <div class="card rv" style="--d:200;display:flex;flex-direction:column;align-items:center;height:606px">
      <div class="ct" style="align-self:flex-start"><span class="dot"></span>Pool by Bucket</div>
      ${donut({size:256,thick:32,items,center:`<div style="font-size:12px;letter-spacing:2.5px;color:var(--sky);text-transform:uppercase">Grand Total</div><div class="num" style="font-size:34px;font-weight:900;margin-top:4px"><span data-count="${p.total}" data-dec="2"></span></div><div style="font-size:14px;color:var(--faint)">PKR Million</div>`})}
      <div style="width:100%;margin-top:10px">${legendRows(items)}</div>
      <div class="chip hot rv" style="--d:900;margin-top:auto;width:100%;display:flex;justify-content:space-between;align-items:center;text-align:left;padding:12px 20px"><div class="l" style="margin:0">Weighted average rate</div><div class="v num" style="font-size:28px">${f(p.weighted_rate,2)}%</div></div>
    </div>
    <div class="card rv" style="--d:300;padding:20px 26px;height:606px">
      <table class="tbl"><thead><tr><th>Account</th><th>Bucket</th><th class="r">Rate</th><th class="r">PKR Mn</th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Grand Total</td><td></td><td class="r o">${f(p.weighted_rate,2)}%</td><td class="r o" style="padding-right:140px">${f(p.total,2)}</td></tr></tfoot></table>
    </div>
  </div>${ft(i)}`;
}
function sGrants(i){
  const g=D.grants;
  const items=[{label:'Grant Funds (GF)',value:g.gf,color:COL.sky},{label:'FIP',value:g.fip,color:COL.orange}];
  const usd=g.accounts[0][1];
  const rows=g.accounts.map((a,k)=>`<tr class="rv" style="--d:${300+k*60};height:38px"><td>${a[0]}</td>
    <td class="r">${a[1]==null?'<span class="muted">–</span>':f(a[1],2)}</td><td class="r">${a[2]==null?'<span class="muted">–</span>':f(a[2],2)}</td>
    <td class="r" style="font-weight:700">${f((a[1]||0)+(a[2]||0),2)}</td></tr>`).join('');
  return `${rings}${hd(i+1,'Grant Funds','Grants Position as of '+g.as_of,'Grant funds including GF & FIP · PKR in Million')}
  <div class="grid" style="grid-template-columns:1fr 560px">
    <div class="card rv" style="--d:200;padding:24px 30px;height:606px;display:flex;flex-direction:column">
      <table class="tbl"><thead><tr><th>Accounts</th><th class="r">GF</th><th class="r">FIP</th><th class="r">Grand Total</th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Grand Total</td><td class="r">${f(g.gf,2)}</td><td class="r">${f(g.fip,2)}</td><td class="r o">${f(g.total,2)}</td></tr></tfoot></table>
      <div class="note rv" style="--d:1000;margin-top:auto">${g.note}</div>
    </div>
    <div class="card rv" style="--d:300;display:flex;flex-direction:column;align-items:center;height:606px">
      <div class="ct" style="align-self:flex-start"><span class="dot"></span>Grant Funds Mix</div>
      ${donut({size:270,thick:36,items,center:`<div style="font-size:12px;letter-spacing:2.5px;color:var(--sky);text-transform:uppercase">Total Grants</div><div class="num" style="font-size:36px;font-weight:900;margin-top:4px"><span data-count="${g.total}" data-dec="2"></span></div><div style="font-size:14px;color:var(--faint)">PKR Million</div>`})}
      <div style="width:100%;margin-top:18px">${legendRows(items)}</div>
      <div class="callout rv" style="--d:900;width:100%;margin-top:auto">The <b>BAFL USD account</b> holds <b>PKR ${f(usd,2)} M</b> — <b>${f(usd/g.total*100,1)}%</b> of all grant funds.</div>
    </div>
  </div>${ft(i)}`;
}
function sBanks(i){
  const b=D.banks, segCols=[COL.sky,'#3E86B8',COL.gold,'#ffffff','#9fb6c3','#C98AA0','#5d7a8a',COL.teal,COL.orange];
  const rows=b.rows.map((r,k)=>{ const u=r[5]; const warn=u!=null&&u>=90;
    return `<tr class="rv" style="--d:${250+k*60};height:37px">
    <td class="c muted">${k+1}</td><td style="font-weight:700"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${segCols[k]};margin-right:10px"></span>${r[0]}</td>
    <td class="c">${r[1]?`<span class="badge">${r[1]}</span>`:'<span class="muted">–</span>'}</td>
    <td class="r">${f(r[2],0)}</td><td class="r">${f(r[3],2)}%</td><td class="r">${r[4]==null?'<span class="muted">–</span>':f(r[4],2)+'%'}</td>
    <td>${u==null?'<span class="muted" style="padding-left:6px">–</span>':`<div class="mini" style="justify-content:flex-start"><div class="t" style="width:110px"><div style="--d:${250+k*60};width:${u}%;background:${warn?COL.orange:COL.sky}"></div></div><span class="num" style="font-weight:700;color:${warn?COL.orange:'#fff'}">${u}%</span></div>`}</td>
    <td class="r">${r[6]==null?'<span class="muted">–</span>':f(r[6],0)}</td><td class="r" style="${warn?'color:'+COL.orange+';font-weight:700':''}">${r[7]==null?'<span class="muted">–</span>':f(r[7],0)}</td></tr>`;}).join('');
  const tot=b.rows.reduce((a,r)=>a+r[2],0); let acc=0;
  const segs=b.rows.map((r,k)=>{ const w=r[2]/tot*100; const html=`<rect class="bar" style="--d:${600+k*80};transform-origin:left center" x="${acc}%" y="0" width="${w}%" height="44" fill="${segCols[k]}" stroke="#0A2A44" stroke-width="2"/>${(w/100*900)>(String(r[0]).length+4)*8.4+14?`<text x="${acc+w/2}%" y="28" text-anchor="middle" font-size="13" font-weight="900" fill="#03111E">${r[0]} ${f(r[3],0)}%</text>`:''}`; acc+=w; return html; }).join('');
  const hot=b.rows.filter(r=>r[5]!=null&&r[5]>=90);
  return `${rings}${hd(i+1,'Counterparty Exposure','Bank-wise KRN Treasury Portfolio Analysis','As of '+b.as_of+' · PKR in Million')}
  <div class="card rv" style="--d:200;padding:22px 28px 16px">
    <table class="tbl"><thead><tr><th class="c">#</th><th>Bank</th><th class="c">LT Rating</th><th class="r">Balance</th><th class="r">KRN Portfolio %</th><th class="r">Rate Offered</th><th>Utilization of Limit</th><th class="r">Institutional Limit</th><th class="r">Under / (Over)</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td></td><td>Total</td><td></td><td class="r o">${f(b.total,0)}</td><td class="r">100%</td><td></td><td></td><td></td><td></td></tr></tfoot></table>
  </div>
  <div class="grid" style="grid-template-columns:1fr 470px;margin-top:20px">
    <div class="card rv" style="--d:500;padding:20px 26px"><div class="ct"><span class="dot"></span>Portfolio Composition</div>
      <svg width="100%" height="44" style="border-radius:10px;overflow:hidden;display:block"><g>${segs}</g></svg>
      <div class="note" style="margin-top:12px">${b.notes.map(n=>'• '+n).join('<br>')}</div></div>
    <div class="card rv" style="--d:600;padding:20px 26px;background:linear-gradient(140deg,rgba(255,77,109,.16),rgba(255,77,109,.04));border-color:rgba(255,77,109,.4)">
      <div class="ct" style="color:var(--orange)"><span class="dot"></span>Limit Watch</div>
      ${hot.length?hot.map(r=>`<div style="font-size:17px;line-height:1.5"><b style="font-size:30px;font-weight:900;color:var(--orange)">${r[5]}%</b>&nbsp; of the <b>${r[0]}</b> institutional limit is utilised — headroom of only <b>PKR ${f(r[7],0)} M</b>.</div>`).join(''):'<div style="font-size:17px">All banks are comfortably within institutional limits.</div>'}
    </div>
  </div>${ft(i)}`;
}
function sIncome(i){
  const n=D.income, cols=[COL.sky,COL.gold,COL.orange];
  const items=n.rows.map((r,k)=>({label:r[0],value:M(r[2]),color:cols[k]}));
  const rows=n.rows.map((r,k)=>`<tr class="rv" style="--d:${700+k*100};height:44px"><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cols[k]};margin-right:12px"></span>${r[0]}</td><td class="r">${f(M(r[1]),2)}</td><td class="r" style="font-weight:700">${f(M(r[2]),2)}</td><td class="r" style="color:${cols[k]};font-weight:700">${f(r[2]/n.income_total*100,1)}%</td></tr>`).join('');
  const spark=[[70,40,8,COL.gold],[118,96,9,'#fff'],[150,30,7,'#fff'],[220,120,6,COL.orange],[86,170,8,'#fff'],[190,190,10,COL.gold]].map(s=>`<div class="spark" style="right:${s[0]}px;top:${s[1]}px;width:${s[2]}px;height:${s[2]}px;background:${s[3]};transform:rotate(45deg)"></div>`).join('');
  return `${rings}${hd(i+1,'Performance','Treasury Income — FY 26-27',n.headline)}
  <div class="grid" style="grid-template-columns:600px 1fr">
    <div class="card hero rv" style="--d:200;height:320px;padding:38px 40px">${spark}
      <div style="font-size:15px;letter-spacing:5px;color:var(--sky);font-weight:700">PKR</div>
      <div class="big num" style="margin-top:6px"><span data-count="${M(n.income_total)}" data-dec="1" data-suffix="M"></span></div>
      <div style="font-size:22px;font-weight:900;letter-spacing:3px;margin-top:10px">TREASURY INCOME · Q1</div>
      <div style="font-size:14px;color:var(--muted);margin-top:16px;letter-spacing:.5px">Strategic contribution &nbsp;·&nbsp; Revenue generation &nbsp;·&nbsp; Capital preservation</div></div>
    <div class="card rv" style="--d:320;height:320px;display:flex;gap:34px;align-items:center;padding:22px 34px">
      ${donut({size:240,thick:30,items,center:`<div style="font-size:11.5px;letter-spacing:2px;color:var(--sky);text-transform:uppercase">Q1 Income</div><div class="num" style="font-size:28px;font-weight:900;margin-top:4px">${f(M(n.income_total),2)}</div><div style="font-size:13px;color:var(--faint)">PKR Million</div>`})}
      <div style="flex:1"><div class="ct"><span class="dot"></span>Income Mix · Q1</div>${legendRows(items)}</div></div>
  </div>
  <div class="card rv" style="--d:550;margin-top:24px;padding:22px 30px">
    <table class="tbl"><thead><tr><th>Type</th><th class="r">Opening Balance (PKR Mn)</th><th class="r">Q1 Income (PKR Mn)</th><th class="r">Share of Income</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td>Total</td><td class="r">${f(M(n.opening_total),2)}</td><td class="r o">${f(M(n.income_total),2)}</td><td class="r">100%</td></tr></tfoot></table>
  </div>${ft(i)}`;
}
function sForecast(i){
  const F=D.forecast, cols=[COL.sky,COL.gold,COL.orange];
  const W=944,H=330,P={l:56,r:16,t:34,b:44},iw=W-P.l-P.r,ih=H-P.t-P.b,max=500,y=v=>P.t+ih-v/max*ih,bw=118,gap=iw/4;
  let g=''; for(let v=0;v<=max;v+=100) g+=`<line class="gl" x1="${P.l}" x2="${W-P.r}" y1="${y(v)}" y2="${y(v)}"/><text class="ax" x="${P.l-12}" y="${y(v)+4.5}" text-anchor="end">${v}</text>`;
  ['Q1','Q2','Q3','Q4'].forEach((q,k)=>{ const cx=P.l+gap*k+gap/2, x0=cx-bw/2; let base=0; const actual=k===0;
    F.rows.forEach((r,j)=>{ const v=M(r[2+k]); const y1=y(base+v), h=y(base)-y1;
      g+=`<rect class="bar" style="--d:${k*160+j*90}" x="${x0}" y="${y1}" width="${bw}" height="${Math.max(h,1)}" fill="${cols[j]}" fill-opacity="${actual?1:.42}" ${actual?'':`stroke="${cols[j]}" stroke-width="1.5" stroke-dasharray="4 4"`}/>`; base+=v; });
    g+=`<text class="pt" style="--d:${900+k*160}" x="${cx}" y="${y(base)-12}" text-anchor="middle" font-size="19" font-weight="900" fill="#fff">${f(M(F.q_totals[k]),2)}</text>`;
    g+=`<text x="${cx}" y="${H-P.b+24}" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">${q}</text><text x="${cx}" y="${H-P.b+41}" text-anchor="middle" font-size="11.5" letter-spacing="2" fill="${actual?COL.orange:'rgba(255,255,255,.5)'}">${actual?'ACTUAL':'FORECAST'}</text>`;
  });
  const rows=F.rows.map((r,j)=>`<tr class="rv" style="--d:${800+j*90};height:34px"><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cols[j]};margin-right:12px"></span>${r[0]}</td><td class="r">${f(M(r[1]),2)}</td>
    ${[2,3,4,5].map(c=>`<td class="r" ${c==2?'style="color:'+COL.orange+'"':''}>${f(M(r[c]),2)}</td>`).join('')}<td class="r" style="font-weight:900">${f(M(r[2]+r[3]+r[4]+r[5]),2)}</td></tr>`).join('');
  const fcst=F.q_totals.slice(1).reduce((a,b)=>a+b,0);
  return `${rings}${hd(i+1,'Outlook','Treasury Income Forecast — FY 2026-27','Q1 actual with Q2–Q4 forecast by income bucket · PKR in Million')}
  <div class="grid" style="grid-template-columns:1fr 430px">
    <div class="card rv" style="--d:200;padding:18px 24px 6px">
      <div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Quarterly Income Build-up</div>
      <div class="legend">${F.rows.map((r,j)=>`<span><i style="background:${cols[j]}"></i>${r[0].replace(' - EAGR','')}</span>`).join('')}</div></div>
      <svg width="${W}" height="${H}">${g}</svg></div>
    <div class="card hero rv" style="--d:320;display:flex;flex-direction:column;justify-content:center;padding:30px 34px">
      <div style="font-size:13px;letter-spacing:3px;color:var(--sky);font-weight:700;text-transform:uppercase">Projected FY 26-27 Income</div>
      <div class="big num" style="font-size:76px;margin-top:10px"><span data-count="${M(F.grand_total)}" data-dec="1"></span></div>
      <div style="font-size:16px;color:var(--muted)">PKR Million</div>
      <div style="display:flex;gap:14px;margin-top:26px">
        <div style="flex:1;padding:14px 16px;border-radius:14px;background:rgba(0,0,0,.2)"><div class="num" style="font-size:24px;font-weight:900;color:var(--orange)">${f(M(F.q_totals[0]),1)}</div><div class="note">Q1 actual</div></div>
        <div style="flex:1;padding:14px 16px;border-radius:14px;background:rgba(0,0,0,.2)"><div class="num" style="font-size:24px;font-weight:900">${f(M(fcst),1)}</div><div class="note">Q2–Q4 forecast</div></div></div>
      <div class="note" style="margin-top:18px">Average balance for the year: <b style="color:#fff">PKR ${f(M(F.avg_total),2)} M</b></div>
    </div>
  </div>
  <div class="card rv" style="--d:600;margin-top:20px;padding:18px 28px">
    <table class="tbl"><thead><tr><th>Income Bucket</th><th class="r">Avg Balance (Year)</th><th class="r" style="color:var(--orange)">Q1 · Actual</th><th class="r">Q2 · Fcst</th><th class="r">Q3 · Fcst</th><th class="r">Q4 · Fcst</th><th class="r">Grand Total</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td>Total</td><td class="r">${f(M(F.avg_total),2)}</td>${F.q_totals.map((q,k)=>`<td class="r ${k==0?'o':''}">${f(M(q),2)}</td>`).join('')}<td class="r o">${f(M(F.grand_total),2)}</td></tr></tfoot></table>
  </div>${ft(i)}`;
}
function sClose(){
  return `<div class="orb" style="left:-240px;right:auto;top:auto;bottom:-300px"></div>${rings}
  <svg class="pat" width="1600" height="300" viewBox="0 0 1600 300">${pattern(32,6,50,23,0.5,0.45)}</svg>
  <div class="inner" style="position:absolute;left:96px;right:96px;top:230px;text-align:center;z-index:2">
    <div class="eyebrow rv" style="--d:0;justify-content:center">Treasury Committee &nbsp;·&nbsp; ${D.period}</div>
    <h1 class="rv close-h" style="--d:150;font-size:112px;font-weight:800;letter-spacing:-3px;margin-top:22px;line-height:1">Thank <em style="font-style:normal;background:linear-gradient(90deg,#FF4D6D,#A99CF0);-webkit-background-clip:text;background-clip:text;color:transparent">you</em></h1>
    <div class="date rv" style="--d:300;font-size:26px;font-weight:300;font-style:italic;color:var(--muted);margin-top:22px">Questions &amp; discussion</div>
  </div>`;
}

/* ---------- build ---------- */
const stage=document.getElementById('stage');
const builders=[sCover,sEconomy,sPolicy,sPkrv,sPool,sGrants,sBanks,sIncome,sForecast,sClose];
stage.insertAdjacentHTML('beforeend', builders.map((b,i)=>`<section class="slide ${i==0||i==TOTAL-1?'cover':''}">${b(i)}</section>`).join(''));
const slides=[...stage.querySelectorAll('.slide')];
const dots=document.getElementById('dots');
dots.innerHTML=slides.map((_,i)=>`<b data-i="${i}" title="Slide ${i+1}"></b>`).join('');
let cur=0;

function countUp(el){
  const to=parseFloat(el.dataset.count), dec=parseInt(el.dataset.dec||0), pre=el.dataset.prefix||'', suf=el.dataset.suffix||'', t0=performance.now(), dur=1500;
  (function step(t){ const p=Math.min((t-t0)/dur,1), e=1-Math.pow(1-p,4);
    el.textContent=pre+f(to*e,dec)+suf; if(p<1) requestAnimationFrame(step); })(t0);
}
function animate(s){
  s.querySelectorAll('[data-count]').forEach(el=>{ el.textContent=(el.dataset.prefix||'')+f(0,parseInt(el.dataset.dec||0))+(el.dataset.suffix||''); setTimeout(()=>countUp(el),350); });
  s.querySelectorAll('path.anim').forEach(p=>{ const L=p.getTotalLength(); if(!L) return; const dash=p.dataset.dash;
    p.style.transition='none'; p.style.strokeDasharray=L+' '+L; p.style.strokeDashoffset=L; p.getBoundingClientRect();
    p.style.transition=`stroke-dashoffset 1.8s cubic-bezier(.3,.7,.2,1) ${(+p.dataset.delay||0)+350}ms`; p.style.strokeDashoffset=0;
    if(dash){ setTimeout(()=>{ p.style.transition='none'; p.style.strokeDasharray=dash; p.style.strokeDashoffset=0; }, 2300+(+p.dataset.delay||0)); }
  });
  s.querySelectorAll('circle.seg').forEach(c=>{ const C=c.dataset.c; c.style.transition='none'; c.setAttribute('stroke-dasharray','0 '+C); c.getBoundingClientRect(); c.style.transition='';
    requestAnimationFrame(()=>requestAnimationFrame(()=>c.setAttribute('stroke-dasharray',c.dataset.len+' '+C))); });
}
function go(n, force){
  n=Math.max(0,Math.min(TOTAL-1,n)); if(n===cur && !force) return;
  slides.forEach((s,i)=>{ s.classList.remove('active'); s.classList.toggle('before', i<n); });
  void stage.offsetWidth;
  slides[n].classList.add('active'); cur=n; animate(slides[n]);
  [...dots.children].forEach((d,i)=>d.classList.toggle('on',i===n));
  document.getElementById('count').textContent=String(n+1).padStart(2,'0')+' / '+String(TOTAL).padStart(2,'0');
  document.getElementById('prog').style.width=((n+1)/TOTAL*100)+'%';
}
let lastW=-1;
function fit(){
  const vp=document.getElementById('viewport'), w=vp.clientWidth||window.innerWidth, h=vp.clientHeight||(window.innerHeight-60);
  if(w<20||h<20){ lastW=0; return; }   // tab hidden: keep last scale, replay when shown
  const s=Math.min(w/1600,h/900)*0.985; stage.style.transform=`translate(-50%,-50%) scale(${s})`;
  if(lastW===0) go(cur,true);          // replay when the tab becomes visible
  lastW=w;
}
document.getElementById('prev').onclick=()=>go(cur-1);
document.getElementById('next').onclick=()=>go(cur+1);
dots.onclick=e=>{ if(e.target.dataset.i!=null) go(+e.target.dataset.i); };
function toggleFS(){ const d=document; if(!d.fullscreenElement){ (d.documentElement.requestFullscreen||d.documentElement.webkitRequestFullscreen).call(d.documentElement); } else { (d.exitFullscreen||d.webkitExitFullscreen).call(d); } }
document.getElementById('fs').onclick=toggleFS;
document.addEventListener('keydown',e=>{
  if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();go(cur+1);}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();go(cur-1);}
  else if(e.key==='Home') go(0); else if(e.key==='End') go(TOTAL-1);
  else if(e.key==='f'||e.key==='F') toggleFS();
});
let tx=null; stage.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
stage.addEventListener('touchend',e=>{ if(tx==null) return; const dx=e.changedTouches[0].clientX-tx; if(Math.abs(dx)>50) go(cur+(dx<0?1:-1)); tx=null; });
stage.addEventListener('click',()=>window.focus());
window.addEventListener('resize',fit);
document.addEventListener('fullscreenchange',fit);
fit(); go(0,true);
if(window.ResizeObserver) new ResizeObserver(fit).observe(document.getElementById('viewport'));
setInterval(fit,600);
</script>
</body></html>'''


def build_tc_deck_html(logo_b64_str="", dark=False):
    """Injects slide data, logo and the app's light / night palette into the presentation template."""
    return (TC_DECK_TEMPLATE
            .replace("__DECK_DATA__", json.dumps(TC_DECK_DATA))
            .replace("__LOGO_B64__", logo_b64_str or "")
            .replace("__BAR_INK__", "#8FBEDC" if dark else "#004369")
            .replace("__BAR_BG__", "#0F2233" if dark else "#FFFFFF")
            .replace("__BAR_DOT__", "rgba(143,190,220,.3)" if dark else "rgba(0,67,105,.22)"))


# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_over, tab_bank, tab_pool, tab_mkt, tab_data, tab_deck = st.tabs(
    ["Overview", "Bank profits", "Pool and investments", "Market rates", "Data", "Committee presentation"]
)

# ── Overview ────────────────────────────────────────────────────────────────
with tab_over:
    section("Where this year's income comes from", "The quarterly summary split by fund and source, and how each month is building up against last year.")
    c1, c2 = st.columns([1, 1.45], gap="medium")
    with c1:
        with panel():
            panel_head("Q1 income mix", "Quarterly sheet, all funds")
            if not quarterly.empty:
                qd = quarterly.copy()
                qd["label"] = np.where(qd.fund == "OSR", qd.line, qd.fund.replace({"GF": "GF (BMGF)"}) + " savings")
                qd = qd[qd.Q1 > 0].sort_values("Q1", ascending=False)
                colors = [GREEN, BRASS, SLATE, SAGE, PLUM, "#9AA9A4", RUST][: len(qd)]
                fig = go.Figure(go.Pie(
                    labels=qd.label, values=qd.Q1, hole=0.66, sort=False, direction="clockwise",
                    marker=dict(colors=colors, line=dict(color=SURFACE, width=3)),
                    text=[f"{v / qd.Q1.sum() * 100:.0f}%" if v / qd.Q1.sum() >= 0.05 else "" for v in qd.Q1],
                    textinfo="text", textposition="inside", textfont=dict(color="white", size=12),
                    hovertemplate="%{label}<br>PKR %{value:,.0f}<br>%{percent}<extra></extra>",
                ))
                fig.update_layout(height=360, showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5, yanchor="middle"),
                                  margin=dict(l=0, r=0, t=10, b=10),
                                  annotations=[dict(text=f"<b style='font-size:22px;font-family:Sora,sans-serif'>{money(qd.Q1.sum())}</b><br><span style='color:{MUTED}'>Q1 total</span>",
                                                    showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper", font=dict(size=13))])
                show_chart(fig, "mix")
    with c2:
        with panel():
            panel_head("Monthly income against last year", f"Bars: {FY_LABEL} by source. Line: {PY_LABEL} bank savings plus T-bills.")
            fig = go.Figure()
            cat_m = income_cy.groupby(["month_idx", "category"])["amount"].sum().unstack(fill_value=0).reindex(range(12), fill_value=0)
            for cat in [c for c in CATEGORY_COLORS if c in cat_m.columns]:
                fig.add_bar(x=MONTHS, y=cat_m[cat] / 1e6, name=cat, marker_color=CATEGORY_COLORS[cat],
                            hovertemplate=f"{cat}<br>%{{x}}: PKR %{{y:,.1f}}M<extra></extra>")
            if monthly_py.notna().any():
                fig.add_scatter(x=MONTHS, y=monthly_py / 1e6, name=f"{PY_LABEL} (savings + T-bills)", mode="lines+markers", connectgaps=False,
                                line=dict(color=INK, width=2, dash="dot", shape="spline"), marker=dict(size=7, color=SURFACE, line=dict(color=INK, width=2)),
                                hovertemplate=f"{PY_LABEL}<br>%{{x}}: PKR %{{y:,.1f}}M<extra></extra>")
            fig.update_layout(barmode="stack", height=360, bargap=0.35, yaxis_title="PKR million", hovermode="x unified")
            show_chart(fig, "monthly")

    with panel():
        panel_head("Quarterly view by fund", "OSR, FIP and GF income across the four quarters. Later quarters fill in as the year progresses.")
        if not quarterly.empty:
            qf = quarterly.groupby("fund")[["Q1", "Q2", "Q3", "Q4"]].sum()
            fig = go.Figure()
            for fund, colr in zip(qf.index, [BRASS, SLATE, GREEN]):
                fig.add_bar(x=["Q1 Jul–Sep", "Q2 Oct–Dec", "Q3 Jan–Mar", "Q4 Apr–Jun"], y=qf.loc[fund] / 1e6,
                            name={"GF": "GF (BMGF)"}.get(fund, fund), marker_color=PROGRAM_COLORS.get({"GF": "GF (BMGF)"}.get(fund, fund), colr),
                            text=[f"{v / 1e6:,.1f}" if v else "" for v in qf.loc[fund]], textposition="outside",
                            hovertemplate=f"{fund}<br>%{{x}}: PKR %{{y:,.2f}}M<extra></extra>")
            fig.update_layout(barmode="group", height=300, yaxis_title="PKR million", bargap=0.3)
            show_chart(fig, "qfund")

# ── Bank profits ────────────────────────────────────────────────────────────
with tab_bank:
    section("Profit on bank balances", "Savings profit by bank across the months reported so far this fiscal year.")
    bc = bank_cy[bank_cy.program.isin(sel_programs)]
    avail = sorted(bc.month_idx.unique())
    if not avail:
        st.info("No bank profit rows found for the selected programs.")
    else:
        if len(avail) > 1:
            pick = st.select_slider("Months to include", options=[MONTHS[i] for i in avail],
                                    value=(MONTHS[avail[0]], MONTHS[avail[-1]]), key="bank_months")
            lo, hi = MONTHS.index(pick[0]), MONTHS.index(pick[1])
            span = f"{pick[0]}–{pick[1]}"
        else:
            lo = hi = avail[0]
            span = MONTHS[avail[0]]
        bc_s = bc[(bc.month_idx >= lo) & (bc.month_idx <= hi)]

        tot_c = bc_s.amount.sum()
        top_bank = bc_s.groupby("bank").amount.sum().sort_values(ascending=False)
        share_top = top_bank.iloc[0] / tot_c if tot_c else np.nan
        n_acc = bc_s.loc[bc_s.amount != 0, ["account", "account_no", "bank"]].drop_duplicates().shape[0]
        st.markdown(
            f'<div class="stats">'
            f'<div class="stat"><div class="l">Savings profit, {span}</div><div class="v">PKR {money(tot_c)}</div></div>'
            f'<div class="stat" style="border-color:{BRASS}"><div class="l">Largest bank</div><div class="v">{top_bank.index[0]} {share_top * 100:.0f}%</div></div>'
            f'<div class="stat" style="border-color:{SLATE}"><div class="l">Banks holding balances</div><div class="v">{top_bank.index.size}</div></div>'
            f'<div class="stat"><div class="l">Accounts earning</div><div class="v">{n_acc}</div></div></div>',
            unsafe_allow_html=True,
        )

        with panel():
            panel_head(f"Bank league table, {FY_LABEL}", "Press play to watch cumulative savings profit build month by month")
            race_src = bc_s.groupby(["bank", "month_idx"]).amount.sum().unstack(fill_value=0)
            if not race_src.empty:
                cum = race_src.cumsum(axis=1)
                months_idx = list(cum.columns)
                top = cum[months_idx[-1]].sort_values(ascending=False).head(10).index
                cum = cum.loc[top]
                xmax = cum.values.max() / 1e6 * 1.15

                def race_frame(k):
                    srt = cum[k].sort_values()
                    return go.Bar(x=srt / 1e6, y=srt.index, orientation="h",
                                  marker_color=[BRASS if b == srt.index[-1] else GREEN for b in srt.index],
                                  text=[f"{v / 1e6:,.1f}M" for v in srt], textposition="outside", cliponaxis=False,
                                  hovertemplate="%{y}: PKR %{x:,.2f}M<extra></extra>")

                frames = [go.Frame(data=[race_frame(k)], name=MONTHS[k],
                                   layout=dict(yaxis=dict(categoryorder="array", categoryarray=list(cum[k].sort_values().index))))
                          for k in months_idx]
                fig = go.Figure(data=[race_frame(months_idx[-1])], frames=frames)
                fig.update_yaxes(categoryorder="array", categoryarray=list(cum[months_idx[-1]].sort_values().index))
                fig.update_layout(
                    height=420, xaxis=dict(range=[0, xmax], title="Cumulative PKR million"), margin=dict(l=8, r=8, t=10, b=70),
                    updatemenus=[dict(type="buttons", showactive=False, x=0, y=-0.2, xanchor="left", direction="left",
                                      bgcolor=SURFACE, bordercolor=LINE, font=dict(color=INK),
                                      buttons=[dict(label="▶ Play", method="animate", args=[[MONTHS[k] for k in months_idx], dict(frame=dict(duration=900, redraw=True), transition=dict(duration=600, easing="cubic-in-out"), mode="immediate")]),
                                               dict(label="❚❚ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
                    sliders=[dict(active=len(months_idx) - 1, x=0.18, y=-0.12, len=0.82, currentvalue=dict(prefix="Through ", font=dict(color=MUTED)),
                                  pad=dict(t=20), bgcolor=GRID, activebgcolor=GREEN, bordercolor=LINE, font=dict(color=MUTED),
                                  steps=[dict(label=MONTHS[k], method="animate", args=[[MONTHS[k]], dict(frame=dict(duration=600, redraw=True), mode="immediate", transition=dict(duration=400))]) for k in months_idx])],
                )
                show_chart(fig, "race")

        rates = M["profit_rates"]
        if not rates.empty:
            with panel():
                panel_head("Best savings rates offered", "From the profit rates sheet")
                piv = rates.pivot_table(index="rank", columns="month", values="rate", aggfunc="first")
                names = rates.pivot_table(index="rank", columns="month", values="bank", aggfunc="first")
                cols = [m for m in MONTHS if m in piv.columns]
                tbl = pd.DataFrame({m: [f"{names.loc[r, m]} {piv.loc[r, m] * 100:.2f}%" for r in piv.index] for m in cols},
                                   index=[f"#{r}" for r in piv.index])
                show_table(tbl.reset_index().rename(columns={"index": "Rank"}))

# ── Pool and investments ────────────────────────────────────────────────────
with tab_pool:
    section("The treasury pool", "What the pool holds and what it earned, followed by the fixed income book.")
    if pool.empty:
        st.info("The Treasury Pool sheet has no figures yet.")
    else:
        pv = pool.pivot_table(index="month_idx", columns="fund", values="amount", aggfunc="sum").sort_index()
        order = pv.iloc[-1].sort_values(ascending=False).index
        fund_cols = dict(zip(order, [GREEN, BRASS, SLATE, SAGE, PLUM, "#9AA9A4", RUST]))
        c1, c2 = st.columns([1, 1.25], gap="medium")
        with c1:
            with panel():
                last = pv.index[-1]
                panel_head(f"Share of the pool, {MONTHS[last]}", "Latest month reported")
                fig = go.Figure(go.Pie(labels=order, values=pv.loc[last, order], hole=0.6, sort=False,
                                       marker=dict(colors=[fund_cols[f] for f in order], line=dict(color=SURFACE, width=2)),
                                       text=[f"{v / pv.loc[last, order].sum() * 100:.0f}%" if v / pv.loc[last, order].sum() >= 0.04 else "" for v in pv.loc[last, order]],
                                       textinfo="text", textposition="inside", textfont=dict(color="white"),
                                       hovertemplate="%{label}<br>PKR %{value:,.0f}<br>%{percent}<extra></extra>"))
                fig.update_layout(height=360, legend=dict(orientation="v", x=1.0, y=0.5, yanchor="middle", font=dict(size=11)),
                                  margin=dict(l=0, r=0, t=10, b=10),
                                  annotations=[dict(text=f"<b style='font-size:20px;font-family:Sora,sans-serif'>{money(pv.loc[last].sum(), 'B', 2)}</b>", showarrow=False, x=0.5, y=0.5)])
                show_chart(fig, "pooldonut")
        with c2:
            with panel():
                panel_head("Annualised yield on the pool", "Monthly income ÷ pool balance × 12, against policy rate and the month's average 3M PKRV")
                if len(yield_by_month):
                    xs = [MONTHS[int(i)] for i in yield_by_month.index]
                    fig = go.Figure()
                    fig.add_bar(x=xs, y=yield_by_month * 100, name="Yield on pool", marker_color=GREEN, width=0.45,
                                texttemplate="%{y:.2f}%", textposition="outside")
                    if not pkrv.empty:
                        avg3 = [pkrv.loc[(pkrv.index >= FY_START + pd.DateOffset(months=int(i))) & (pkrv.index < FY_START + pd.DateOffset(months=int(i) + 1)), "3M"].mean() * 100 for i in yield_by_month.index]
                        fig.add_scatter(x=xs, y=avg3, name="3M PKRV, month average", mode="lines+markers", line=dict(color=BRASS, width=2.5), marker=dict(size=9))
                    if pd.notna(current_policy):
                        fig.add_hline(y=current_policy * 100, line=dict(color=RUST, dash="dot", width=1.5),
                                      annotation_text=f"Policy {current_policy * 100:.2f}%", annotation_position="top left")
                    fig.update_layout(height=360, yaxis_title="%")
                    fig.update_yaxes(range=[0, max(13, (yield_by_month.max() * 100) + 2)])
                    show_chart(fig, "poolyield")
                else:
                    st.caption("Yield appears once a month has both bank profit and pool figures.")

    section("Fixed income book", "T-bills, term deposits and buy/sell transactions placed out of the pool.")
    if inst.empty:
        st.info("No instrument rows were found in the TDR, Buy/Sell or T-bill sheets.")
    else:
        tb = inst[inst.type == "T-bill"]
        bs = inst[inst.type == "Buy/Sell"]
        td = inst[inst.type == "TDR"]

        def wavg(d):
            return (d.rate * d.principal).sum() / d.principal.sum() if len(d) and d.principal.sum() else np.nan

        st.markdown(
            f'<div class="stats">'
            f'<div class="stat" style="border-color:{PLUM}"><div class="l">T-bills held</div><div class="v">{len(tb)} bills, PKR {money(tb.principal.sum())}</div></div>'
            f'<div class="stat" style="border-color:{PLUM}"><div class="l">T-bill weighted rate</div><div class="v">{pct(wavg(tb))}</div></div>'
            f'<div class="stat" style="border-color:{BRASS}"><div class="l">TDR book</div><div class="v">PKR {money(td.principal.sum())} at {pct(wavg(td))}</div></div>'
            f'<div class="stat" style="border-color:{SLATE}"><div class="l">Buy/sell placed</div><div class="v">{len(bs)} deals, PKR {money(bs.principal.sum())}</div></div>'
            f'<div class="stat" style="border-color:{SLATE}"><div class="l">Buy/sell weighted rate</div><div class="v">{pct(wavg(bs))}</div></div>'
            f'<div class="stat" style="border-color:{GREEN}"><div class="l">Average pick-up over PKRV</div><div class="v">{inst.spread_bps.mean():+.0f} bps</div></div></div>',
            unsafe_allow_html=True,
        )

        with st.expander("Pick-up in basis points, deal by deal"):
            st.caption("Each deal's booked rate against the PKRV for the same tenor on the day it was booked. Positive means the deal beat the market curve.")
            d2 = inst.dropna(subset=["spread_bps"]).sort_values("spread_bps")
            fig = go.Figure(go.Bar(x=d2.spread_bps, y=d2.label, orientation="h",
                                   marker_color=[GREEN if v >= 0 else RUST for v in d2.spread_bps],
                                   texttemplate="%{x:+.0f}", textposition="outside", cliponaxis=False,
                                   hovertemplate="%{y}<br>%{x:+.1f} bps<extra></extra>"))
            pad = max(12, (d2.spread_bps.max() - d2.spread_bps.min()) * 0.3)
            fig.update_xaxes(range=[min(0, d2.spread_bps.min()) - pad, max(0, d2.spread_bps.max()) + pad])
            fig.add_vline(x=0, line=dict(color=INK, width=1))
            fig.update_layout(height=max(320, 30 * len(d2) + 90), xaxis_title="bps", showlegend=False)
            show_chart(fig, "spread")

# ── Market rates ────────────────────────────────────────────────────────────
with tab_mkt:
    section("Market rates", "PKRV yields, KIBOR and the SBP policy rate from the rates workbook.")
    if pkrv.empty:
        st.info("Add the PKRV workbook to see market rates.")
    else:
        pr = policy_rate_series(mps, pkrv.index)
        latest = pkrv.dropna(how="all").iloc[-1]
        tenors = list(pkrv.columns)

        with panel():
                panel_head("How the curve has moved", "Month-end PKRV curve with the policy rate. Press play.")
                start_year = st.select_slider("Start from", options=list(range(pkrv.index.min().year, pkrv.index.max().year + 1)),
                                              value=max(pkrv.index.min().year, pkrv.index.max().year - 3), key="anim_start")
                me = pkrv[pkrv.index.year >= start_year].resample("ME").last().dropna(how="all")
                pr_me = policy_rate_series(mps, me.index)
                ymin = float(np.nanmin(me.values)) * 100 - 0.5
                ymax = float(np.nanmax(np.r_[me.values.ravel(), pr_me.dropna().values])) * 100 + 0.5

                def curve_traces(ts):
                    row = me.loc[ts]
                    p = pr_me.loc[ts]
                    return [
                        go.Scatter(x=tenors, y=row * 100, mode="lines+markers", line=dict(color=GREEN, width=4, shape="spline"),
                                   marker=dict(size=12, color=BRASS, line=dict(color=SURFACE, width=2)), fill="tozeroy", fillcolor="rgba(11,93,82,.07)",
                                   name="PKRV", hovertemplate="%{x}: %{y:.2f}%<extra></extra>"),
                        go.Scatter(x=tenors, y=[p * 100] * len(tenors), mode="lines", line=dict(color=RUST, width=1.5, dash="dot"),
                                   name="Policy rate", hovertemplate="Policy %{y:.2f}%<extra></extra>"),
                    ]

                frames = [go.Frame(data=curve_traces(ts), name=f"{ts:%b %Y}") for ts in me.index]
                fig = go.Figure(data=curve_traces(me.index[-1]), frames=frames)
                step_every = max(1, len(me) // 24)
                fig.update_layout(
                    height=380, yaxis=dict(range=[max(0, ymin), ymax], title="%"), margin=dict(l=8, r=8, t=10, b=80),
                    updatemenus=[dict(type="buttons", showactive=False, x=0, y=-0.22, xanchor="left", direction="left", bgcolor=SURFACE, bordercolor=LINE, font=dict(color=INK),
                                      buttons=[dict(label="▶ Play", method="animate", args=[[f.name for f in frames], dict(frame=dict(duration=160, redraw=False), transition=dict(duration=140, easing="linear"), fromcurrent=False, mode="immediate")]),
                                               dict(label="❚❚ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
                    sliders=[dict(active=len(frames) - 1, x=0.2, y=-0.12, len=0.8, currentvalue=dict(prefix="", font=dict(family="Sora, Manrope, sans-serif", size=14, color=GREEN)),
                                  pad=dict(t=24), bgcolor=GRID, activebgcolor=GREEN, bordercolor=LINE, font=dict(color=MUTED, size=10), minorticklen=0,
                                  steps=[dict(label=f.name if i % step_every == 0 else "", method="animate",
                                              args=[[f.name], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=200))]) for i, f in enumerate(frames)])],
                )
                show_chart(fig, "curveanim")

        with panel():
            panel_head("PKRV history with the policy rate", "Use the range buttons or drag the slider underneath")
            show_tenors = st.multiselect("Tenors", tenors, default=[t for t in ["1M", "3M", "6M", "12M"] if t in tenors], key="tenors")
            fig = go.Figure()
            for t in show_tenors:
                fig.add_scatter(x=pkrv.index, y=pkrv[t] * 100, name=f"PKRV {t}", mode="lines", line=dict(color=TENOR_COLORS.get(t, GREEN), width=1.6),
                                hovertemplate=f"{t}: %{{y:.2f}}%<extra></extra>")
            fig.add_scatter(x=pr.index, y=pr * 100, name="Policy rate", mode="lines", line=dict(color=RUST, width=2, shape="hv"),
                            hovertemplate="Policy: %{y:.2f}%<extra></extra>")
            if not kibor.empty and "6MK" in kibor:
                fig.add_scatter(x=kibor.index, y=kibor["6MK"] * 100, name="KIBOR 6M", mode="lines", line=dict(color=INK, width=1, dash="dot"),
                                visible="legendonly", hovertemplate="KIBOR 6M: %{y:.2f}%<extra></extra>")
            for d in mpr.date:
                if d > pk_latest_date:
                    fig.add_vline(x=d.timestamp() * 1000, line=dict(color=BRASS, width=1, dash="dot"))
            fig.update_layout(
                height=440, hovermode="x unified", yaxis_title="%",
                xaxis=dict(rangeslider=dict(visible=True, thickness=0.06, bgcolor=GRID), type="date",
                           range=[pk_latest_date - pd.DateOffset(years=3), pk_latest_date + pd.Timedelta(days=100)],
                           rangeselector=dict(buttons=[dict(count=6, label="6M", step="month", stepmode="backward"),
                                                       dict(count=1, label="1Y", step="year", stepmode="backward"),
                                                       dict(count=3, label="3Y", step="year", stepmode="backward"),
                                                       dict(count=5, label="5Y", step="year", stepmode="backward"),
                                                       dict(step="all", label="All")],
                                              bgcolor=SURFACE, activecolor="#DDEBE6", bordercolor=LINE, borderwidth=1, x=0, y=1.08)),
                legend=dict(x=1, xanchor="right", y=1.08),
            )
            show_chart(fig, "history")
            if pd.notna(next_mpc):
                st.caption(f"Dotted brass lines mark upcoming MPC meetings from the MPR sheet. Next: {next_mpc:%A %d %B %Y}.")

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            with panel():
                panel_head("3M PKRV against the policy rate", "Spread in basis points. Below zero, the market prices in cuts.")
                sp = ((pkrv["3M"] - pr) * 10000).dropna()
                sp = sp[sp.index >= pk_latest_date - pd.DateOffset(years=3)]
                wk = sp.resample("W").mean()
                fig = go.Figure(go.Bar(x=wk.index, y=wk, marker_color=[GREEN if v >= 0 else RUST for v in wk], marker_line_width=0,
                                       hovertemplate="Week of %{x|%d %b %Y}<br>%{y:+.0f} bps<extra></extra>"))
                fig.add_hline(y=0, line=dict(color=INK, width=1))
                fig.update_layout(height=320, yaxis_title="bps", bargap=0.1, showlegend=False)
                show_chart(fig, "polspread")
        with c4:
            with panel():
                panel_head("Curve slope and KIBOR premium", "12M minus 1M PKRV, and 6M KIBOR minus 6M PKRV")
                fig = go.Figure()
                if "12M" in pkrv and "1M" in pkrv:
                    slope = ((pkrv["12M"] - pkrv["1M"]) * 10000).dropna()
                    slope = slope[slope.index >= pk_latest_date - pd.DateOffset(years=3)]
                    fig.add_scatter(x=slope.index, y=slope, name="Slope 12M−1M", mode="lines", line=dict(color=GREEN, width=1.8),
                                    fill="tozeroy", fillcolor="rgba(11,93,82,.08)", hovertemplate="Slope %{y:+.0f} bps<extra></extra>")
                if not kibor.empty and "6MK" in kibor and "6M" in pkrv:
                    kj = kibor[["6MK"]].join(pkrv[["6M"]], how="inner").dropna()
                    prem = (kj["6MK"] - kj["6M"]) * 10000
                    prem = prem[prem.index >= pk_latest_date - pd.DateOffset(years=3)]
                    fig.add_scatter(x=prem.index, y=prem, name="KIBOR 6M − PKRV 6M", mode="lines", line=dict(color=BRASS, width=1.8),
                                    hovertemplate="KIBOR premium %{y:+.0f} bps<extra></extra>")
                fig.add_hline(y=0, line=dict(color=INK, width=1))
                fig.update_layout(height=320, yaxis_title="bps", hovermode="x unified")
                show_chart(fig, "slope")

        with panel():
            panel_head("3M PKRV trend and outlook", "30-day moving average, centred average, and a damped-trend smoothing projection. The projection is statistical, not a view on SBP policy.")
            f1, f2 = st.columns([1, 3])
            with f1:
                horizon = st.slider("Business days ahead", 20, 180, 60, step=10, key="horizon")
                lookback = st.slider("History shown, months", 6, 60, 18, step=6, key="lookback")
            s3 = pkrv["3M"].dropna()
            ma30 = s3.rolling(30).mean()
            cma = s3.rolling(30, center=True).mean()
            fit_src = s3[s3.index >= s3.index.max() - pd.DateOffset(years=3)].values
            fc, band, a_, b_ = holt_damped(fit_src, horizon)
            fidx = pd.bdate_range(s3.index.max() + pd.Timedelta(days=1), periods=horizon)
            view = s3.index >= s3.index.max() - pd.DateOffset(months=lookback)
            with f1:
                st.markdown(
                    f'<div class="stats" style="grid-template-columns:1fr"><div class="stat"><div class="l">Latest 3M PKRV</div><div class="v">{s3.iloc[-1] * 100:.2f}%</div></div>'
                    f'<div class="stat" style="border-color:{BRASS}"><div class="l">Projected in {horizon} business days</div><div class="v">{fc[-1] * 100:.2f}%</div></div>'
                    f'<div class="stat" style="border-color:{SLATE}"><div class="l">80% range</div><div class="v">{(fc[-1] - 1.28 * band[-1]) * 100:.2f}–{(fc[-1] + 1.28 * band[-1]) * 100:.2f}%</div></div></div>',
                    unsafe_allow_html=True,
                )
            with f2:
                fig = go.Figure()
                fig.add_scatter(x=np.r_[fidx, fidx[::-1]], y=np.r_[fc + 1.96 * band, (fc - 1.96 * band)[::-1]] * 100, fill="toself",
                                fillcolor="rgba(181,139,42,.10)", line=dict(width=0), name="95% range", hoverinfo="skip")
                fig.add_scatter(x=np.r_[fidx, fidx[::-1]], y=np.r_[fc + 1.28 * band, (fc - 1.28 * band)[::-1]] * 100, fill="toself",
                                fillcolor="rgba(181,139,42,.22)", line=dict(width=0), name="80% range", hoverinfo="skip")
                fig.add_scatter(x=s3.index[view], y=s3[view] * 100, name="3M PKRV", mode="lines", line=dict(color=GREEN, width=1.6),
                                hovertemplate="%{x|%d %b %Y}: %{y:.2f}%<extra></extra>")
                fig.add_scatter(x=ma30.index[view], y=ma30[view] * 100, name="30-day average", mode="lines", line=dict(color=SLATE, width=2, dash="dash"))
                fig.add_scatter(x=cma.index[view], y=cma[view] * 100, name="Centred average", mode="lines", line=dict(color=SAGE, width=2), visible="legendonly")
                fig.add_scatter(x=fidx, y=fc * 100, name="Projection", mode="lines", line=dict(color=BRASS, width=3),
                                hovertemplate="%{x|%d %b %Y}: %{y:.2f}%<extra></extra>")
                prv = pr[pr.index >= s3.index.max() - pd.DateOffset(months=lookback)]
                fig.add_scatter(x=prv.index, y=prv * 100, name="Policy rate", mode="lines", line=dict(color=RUST, width=1.5, shape="hv"))
                fig.update_layout(height=400, yaxis_title="%", hovermode="x unified")
                show_chart(fig, "forecast")

        if not mps.empty:
            with panel():
                panel_head("Policy rate decisions", "Each monetary policy statement since 2017. Marker colour shows the direction of the change.")
                mc = {"Rise": RUST, "Fall": GREEN, "Cut": GREEN, "Static": MUTED}
                fig = go.Figure()
                fig.add_scatter(x=mps.date, y=mps.rate * 100, mode="lines", line=dict(color=LINE, width=2, shape="hv"), showlegend=False, hoverinfo="skip")
                for attr, g in mps.groupby("attribute"):
                    fig.add_scatter(x=g.date, y=g.rate * 100, mode="markers", name=attr or "Starting rate",
                                    marker=dict(size=np.clip(np.abs(g.delta_bps.fillna(0)) / 25 + 8, 8, 30), color=mc.get(attr, SLATE), line=dict(color=SURFACE, width=1.5)),
                                    customdata=np.stack([g.label, g.delta_bps.fillna(0)], axis=-1),
                                    hovertemplate="%{customdata[0]}<br>%{y:.2f}% (%{customdata[1]:+.0f} bps)<extra></extra>")
                fig.update_layout(height=320, yaxis_title="%")
                show_chart(fig, "mps")

# ── Data ────────────────────────────────────────────────────────────────────
with tab_data:
    section("Source tables", "The parsed tables behind every chart. Download any of them as CSV.")

    def data_block(title, df, fname):
        with st.expander(f"{title}  ({len(df):,} rows)"):
            show_table(df.head(2000), height=320)
            st.download_button("Download CSV", df.to_csv(index=True if isinstance(df.index, pd.DatetimeIndex) else False).encode(),
                               file_name=fname, mime="text/csv", key=f"dl_{fname}")

    data_block(f"Bank profits, {FY_LABEL}", bank_cy, "bank_profits_fy27.csv")
    data_block(f"Bank profits, {PY_LABEL}", bank_py, "bank_profits_fy26.csv")
    data_block("Quarterly summary", quarterly, "quarterly.csv")
    data_block(f"Monthly income by source, {FY_LABEL}", income_cy, "income_by_month_fy27.csv")
    data_block("Instruments with PKRV benchmark", inst, "instruments.csv")
    data_block("Treasury pool", pool, "treasury_pool.csv")
    data_block("MPC meeting calendar", mpr, "mpc_calendar.csv")
    if not pkrv.empty:
        data_block("PKRV daily", pkrv, "pkrv.csv")
    if not kibor.empty:
        data_block("KIBOR daily", kibor, "kibor.csv")
    if not mps.empty:
        data_block("Policy rate history", mps, "mps.csv")

# ── Committee presentation ──────────────────────────────────────────────────
with tab_deck:
    section("Treasury Committee presentation", "Q1 FY 2026-27 board deck. Use ← → or the arrows to move between slides; Present opens it full screen.")
    tc_deck_html = build_tc_deck_html("", DARK_MODE)
    try:
        components.html(tc_deck_html, height=780, scrolling=False)
    except Exception:
        st.iframe(tc_deck_html, height=780)

boot_animations(reduce_motion)

st.markdown(
    f'<div style="margin-top:28px;color:{MUTED};font-size:.78rem">Built from the treasury working file and the PKRV rates workbook. '
    f"The 3M PKRV projection is a simple statistical model for discussion, not a forecast.</div>",
    unsafe_allow_html=True,
)

import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Portfolio Summary", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS for exact 1-to-1 styling
st.markdown("""
    <style>
    /* Global Settings */
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; }
    .stApp { background-color: #FFFFFF !important; }
    
    /* Hide default Streamlit elements for a cleaner look */
    header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 95%; }

    /* Top Glowing Header */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        margin-top: 1rem;
    }
    .glow-line {
        height: 2px;
        flex-grow: 1;
        max-width: 300px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }
    .header-card {
        background: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 8px;
        padding: 15px 40px;
        margin: 0 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        font-weight: 900;
        font-size: 24px;
        color: #000000;
        letter-spacing: 1px;
    }

    /* Staging Title Cards (Grey Boxes) */
    .staging-title {
        background: #E6ECF2;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        font-weight: 900;
        font-size: 18px;
        color: #000000;
        letter-spacing: 1.5px;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }

    /* Center Main Card */
    .center-card {
        background: #FFFFFF;
        border: 2px solid #2563EB; /* Blue Border */
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15);
        margin-top: 20px;
    }
    .center-title { font-size: 16px; font-weight: 700; color: #333333; letter-spacing: 1px; margin-bottom: 10px; }
    .center-value { font-size: 42px; font-weight: 900; color: #000000; margin-bottom: 10px; }
    .center-sub { font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Small Stage Cards */
    .stage-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 12px 20px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stage-card-title { font-size: 12px; font-weight: 800; color: #000000; margin-bottom: 8px; }
    .stage-card-value { font-size: 18px; font-weight: 900; color: #000000; }
    .stage-card-pct { font-size: 12px; font-weight: 600; color: #64748B; }
    
    /* Specific Border Colors for Stages */
    .stage-1 { border: 1px solid #10B981; } /* Green */
    .stage-1 hr { border-top: 1px solid #D1FAE5; margin: 8px 0; }
    
    .stage-2 { border: 1px solid #F59E0B; } /* Orange */
    .stage-2 hr { border-top: 1px solid #FEF3C7; margin: 8px 0; }
    
    .stage-3 { border: 1px solid #EF4444; } /* Red */
    .stage-3 hr { border-top: 1px solid #FEE2E2; margin: 8px 0; }

    /* Dropdown alignment */
    .stSelectbox { max-width: 200px; margin: 0 auto; }
    div[data-baseweb="select"] > div { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 3. Top Glowing Header
st.markdown("""
    <div class="header-container">
        <div class="glow-line"></div>
        <div class="header-card">KARANDAAZ PORTFOLIO SUMMARY</div>
        <div class="glow-line"></div>
    </div>
""", unsafe_allow_html=True)

# 4. Date Dropdown (Centered)
col_empty1, col_date, col_empty2 = st.columns([1, 0.3, 1])
with col_date:
    st.selectbox("", ["Jun 26", "Jul 26", "Aug 26"], label_visibility="collapsed")

st.write("") # Spacing
st.write("")

# 5. Main 3-Column Layout
left_col, center_col, right_col = st.columns([1, 1.2, 1], gap="large")

# --- LEFT COLUMN (CIC STAGING) ---
with left_col:
    st.markdown("<div class='staging-title'>CIC STAGING</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='stage-card stage-1'>
            <div class='stage-card-title'>CIC STAGE 1</div><hr>
            <div class='stage-card-value'>12,106 M <span class='stage-card-pct'>(73.8%)</span></div>
        </div>
        <div class='stage-card stage-2'>
            <div class='stage-card-title'>CIC STAGE 2</div><hr>
            <div class='stage-card-value'>2,436 M <span class='stage-card-pct'>(14.8%)</span></div>
        </div>
        <div class='stage-card stage-3'>
            <div class='stage-card-title'>CIC STAGE 3</div><hr>
            <div class='stage-card-value'>1,858 M <span class='stage-card-pct'>(11.4%)</span></div>
        </div>
    """, unsafe_allow_html=True)


# --- CENTER COLUMN (MAIN PORTFOLIO) ---
with center_col:
    st.markdown("""
        <div class='center-card'>
            <div class='center-title'>KARANDAAZ PORTFOLIO</div>
            <hr style="border: none; border-top: 1px solid #E2E8F0; width: 60%; margin: 10px auto;">
            <div class='center-value'>37.7 B</div>
            <div class='center-sub'>CLICK TO EXPAND</div>
        </div>
    """, unsafe_allow_html=True)


# --- RIGHT COLUMN (I I STAGING) ---
with right_col:
    st.markdown("<div class='staging-title'>I I STAGING</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='stage-card stage-1'>
            <div class='stage-card-title'>I I STAGE 1</div><hr>
            <div class='stage-card-value'>475 M <span class='stage-card-pct'>(2.9%)</span></div>
        </div>
        <div class='stage-card stage-2'>
            <div class='stage-card-title'>I I STAGE 2</div><hr>
            <div class='stage-card-value'>66 M <span class='stage-card-pct'>(0.4%)</span></div>
        </div>
        <div class='stage-card stage-3'>
            <div class='stage-card-title'>I I STAGE 3</div><hr>
            <div class='stage-card-value'>85 M <span class='stage-card-pct'>(0.5%)</span></div>
        </div>
    """, unsafe_allow_html=True)

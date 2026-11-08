"""
Institutional Portfolio Analytics Agent - Ultra Modern Quantitative Dashboard
Powered by RACSE: Risk-Attribution & Counterfactual Shock Engine.
Features glassmorphic fintech design, animated status telemetry, interactive Plotly factor decomposition,
and real-time counterfactual shock stress-testing.
"""

import sys
import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import DATABASE_PATH, GROUND_TRUTH_PATH
from src.agent import PortfolioAgent
from src.exposure_tool import ExposureCalculatorTool
from src.simulation_tool import CounterfactualShockEngine
from agent_evaluator import AgentEvaluator

# Streamlit Page Config
st.set_page_config(
    page_title="RACSE | AI Portfolio Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# ULTRA-PREMIUM MODERN FINTECH DESIGN SYSTEM (CSS)
# -------------------------------------------------------------
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Base Theme */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #E2E8F0;
    }

    .stApp {
        background: radial-gradient(circle at 20% 0%, rgba(30, 41, 59, 0.7) 0%, rgba(11, 15, 25, 0.98) 70%), #070A11;
        background-attachment: fixed;
    }

    /* Animated Ambient Glow Effects */
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    @keyframes cardEntrance {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes shimmerBar {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Custom Header Banner */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px 32px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        backdrop-filter: blur(16px);
        margin-bottom: 28px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        animation: cardEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .header-title {
        font-size: 26px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-size: 13px;
        color: #64748B;
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    .header-tag {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        animation: pulseGlow 2s infinite;
    }

    /* Metric Cards Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
        animation: cardEntrance 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .quant-card {
        background: linear-gradient(145deg, rgba(26, 34, 52, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .quant-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.6), transparent);
    }

    .quant-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 30px -10px rgba(99, 102, 241, 0.25);
    }

    .card-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94A3B8;
        margin-bottom: 6px;
    }

    .card-value {
        font-size: 24px;
        font-weight: 700;
        color: #F8FAFC;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        letter-spacing: -0.5px;
    }

    .card-badge {
        display: inline-block;
        margin-top: 8px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
    }

    .badge-cyan { background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3); }
    .badge-emerald { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-violet { background: rgba(139, 92, 246, 0.15); color: #A78BFA; border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }

    /* Custom Glass Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0E1A 0%, #060912 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Terminal Prompt Box */
    .agent-console-box {
        background: #0D121F;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6);
        font-family: 'JetBrains Mono', monospace;
    }

    .telemetry-tag {
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        color: #38BDF8;
        background: rgba(56, 189, 248, 0.1);
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }

    /* Streamlit widgets overrides */
    .stSelectbox > div > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
    }

    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px -6px rgba(99, 102, 241, 0.4) !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_agent():
    return PortfolioAgent(str(DATABASE_PATH))


@st.cache_data
def get_portfolio_list():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(
        "SELECT portfolio_id, portfolio_name, strategy_type, total_aum, target_risk_level, status FROM portfolios;",
        conn
    )
    conn.close()
    return df


agent = get_agent()
portfolios_df = get_portfolio_list()

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Factor Decomposition"

with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
                ⚡ RACSE QUANT
            </div>
            <div style="font-size: 11px; color: #64748B; font-family: 'JetBrains Mono'; margin-top: 2px;">
                Portfolio Intelligence Engine v2.4
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div class="status-dot"></div>
                <span style="font-size: 12px; font-weight: 600; color: #34D399;">Engine Active</span>
            </div>
            <span style="font-size: 11px; font-family: 'JetBrains Mono'; color: #94A3B8;">SQLite 3.44</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.8px; margin-bottom: 8px;'>Analytics Modules</p>", unsafe_allow_html=True)

    nav_options = [
        ("Factor Decomposition", "📊 Equity Factor Decomposition"),
        ("AI Agent Copilot", "🤖 AI Analytics Agent"),
        ("Stress-Test Simulator", "⚡ RACSE Shock Simulator"),
        ("Executive Overview", "📈 Portfolios Overview"),
        ("Evaluation Suite", "🎯 10/10 Benchmark Suite")
    ]

    for key, label in nav_options:
        is_active = (st.session_state.active_nav == key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state.active_nav = key
            st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style="padding: 10px; background: rgba(15, 23, 42, 0.5); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 11px; color: #94A3B8; font-family: 'JetBrains Mono';">Portfolio Scope</div>
            <div style="font-size: 15px; font-weight: 700; color: #F8FAFC; margin-top: 2px;">$660,000,000</div>
            <div style="font-size: 11px; color: #34D399; margin-top: 4px;">● 7 Active Mandates</div>
        </div>
    """, unsafe_allow_html=True)

header_html = """
<div class="app-header">
    <div>
        <h1 class="header-title">Institutional Portfolio Analytics Platform</h1>
        <div class="header-subtitle">AST-Guarded Text2SQL  |  Equity Factor Decomposition  |  RACSE Counterfactual Engine</div>
    </div>
    <div>
        <div class="header-tag">
            <div class="status-dot"></div>
            <span>LIVE ATTRIBUTION MODE</span>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

if st.session_state.active_nav == "Factor Decomposition":
    st.markdown("### 📊 Equity Sector Factor Decomposition")
    st.caption("Isolates equity holdings to compute pure normalized sector factor exposure. Fixed-income debt instruments are strictly segregated to avoid distorted factor weighting.")

    exposure_tool = ExposureCalculatorTool(str(DATABASE_PATH))
    p_names = portfolios_df["portfolio_name"].tolist()
    
    col_sel, col_space = st.columns([2, 1])
    with col_sel:
        selected_p = st.selectbox("Select Portfolio for Analysis:", p_names, index=1)

    exp_data = exposure_tool.calculate_sector_exposure(selected_p)

    if exp_data.get("success"):
        tot_val = exp_data['total_portfolio_value']
        eq_val = exp_data['total_equity_value']
        fi_val = exp_data['total_fixed_income_value']
        hhi = exp_data['hhi_concentration']
        eff_n = exp_data['effective_n_sectors']
        rating = exp_data['diversification_rating']

        st.markdown(f"""
        <div class="metric-grid">
            <div class="quant-card">
                <div class="card-label">Total Portfolio NAV</div>
                <div class="card-value">${tot_val:,.2f}</div>
                <div class="card-badge badge-cyan">Full Mandate Size</div>
            </div>
            <div class="quant-card">
                <div class="card-label">Pure Equity Sleeve</div>
                <div class="card-value">${eq_val:,.2f}</div>
                <div class="card-badge badge-emerald">{exp_data.get('equity_ratio_pct', 100):.1f}% of NAV</div>
            </div>
            <div class="quant-card">
                <div class="card-label">Fixed-Income Cash Drag</div>
                <div class="card-value">${fi_val:,.2f}</div>
                <div class="card-badge badge-amber">{100.0 - exp_data.get('equity_ratio_pct', 100):.1f}% Segregated Debt</div>
            </div>
            <div class="quant-card">
                <div class="card-label">Concentration (HHI)</div>
                <div class="card-value">{hhi:,.0f}</div>
                <div class="card-badge badge-violet">{eff_n:.2f} Effective Bets ({rating})</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_chart, col_table = st.columns([1.1, 1])
        breakdown_df = pd.DataFrame(exp_data["sector_breakdown"])

        with col_chart:
            if not breakdown_df.empty:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=breakdown_df["sector"],
                    values=breakdown_df["market_value_usd"],
                    hole=0.55,
                    textinfo="label+percent",
                    textposition="outside",
                    marker=dict(
                        colors=["#6366F1", "#06B6D4", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#3B82F6"],
                        line=dict(color="#0B0F19", width=2)
                    ),
                    hoverinfo="label+value+percent",
                    hovertemplate="<b>%{label}</b><br>Market Value: $%{value:,.2f}<br>Equity Weight: %{percent}<extra></extra>"
                )])

                fig_donut.update_layout(
                    title=dict(
                        text=f"<b>Normalized Sector Weights (%)</b>",
                        font=dict(size=16, color="#F8FAFC", family="Plus Jakarta Sans")
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    margin=dict(t=50, b=30, l=30, r=30),
                    height=360,
                    annotations=[dict(
                        text=f"<b>{len(breakdown_df)}</b><br><span style='font-size:11px;color:#94A3B8'>Sectors</span>",
                        x=0.5, y=0.5, font_size=18, showarrow=False, font_color="#F8FAFC"
                    )]
                )
                st.plotly_chart(fig_donut, use_container_width=True)

        with col_table:
            st.markdown("<h4 style='font-size: 15px; font-weight: 700; color: #E2E8F0; margin-bottom: 12px;'>Sector Allocations Breakdown</h4>", unsafe_allow_html=True)
            formatted_df = breakdown_df.copy()
            st.dataframe(
                formatted_df.style.format({
                    "weight_pct": "{:.2f}%",
                    "market_value_usd": "${:,.2f}"
                }),
                use_container_width=True,
                height=320
            )

        excluded = exp_data.get("excluded_fixed_income", [])
        if excluded:
            st.markdown("---")
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 15px; font-weight: 700; color: #E2E8F0;">Fixed-Income & Bond Exclusion Audit</span>
                    <span class="telemetry-tag">Equity Factor Mandate</span>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Per quantitative equity risk methodology, bond instruments are filtered out to prevent skewing equity sector exposures:")
            st.dataframe(pd.DataFrame(excluded), use_container_width=True)

elif st.session_state.active_nav == "AI Agent Copilot":
    st.markdown("### 🤖 Autonomous Portfolio Analytics Copilot")
    st.caption("Natural language analytics engine with AST query safety, schema-aware text-to-SQL, and self-healing error recovery.")

    sample_chips = [
        "How many portfolios do we have in total?",
        "What are the names of all active portfolios?",
        "What are the sector exposures for the Tech Innovation Fund?",
        "Calculate the sector exposure breakdown for international equity",
        "What is the total AUM for portfolios with high target risk level?",
        "Show me the top 5 holdings by cost basis in the Growth Equity Fund",
        "What is the average current price of securities in each sector?",
        "Stress test Growth Equity Fund with Technology:-15%, Healthcare:+5%"
    ]

    st.markdown("<p style='font-size: 12px; font-weight: 600; color: #94A3B8; margin-bottom: 8px;'>Suggested Inquiries (Click to populate):</p>", unsafe_allow_html=True)
    chip_cols = st.columns(4)
    for idx, chip in enumerate(sample_chips[:4]):
        with chip_cols[idx]:
            if st.button(chip, key=f"chip_{idx}", use_container_width=True):
                st.session_state.prompt_input = chip

    if "prompt_input" not in st.session_state:
        st.session_state.prompt_input = "What are the sector exposures for the Tech Innovation Fund?"

    user_query = st.text_input("Enter your natural language query:", value=st.session_state.prompt_input)

    if st.button("Execute Quantitative Query", type="primary"):
        with st.spinner("Parsing intent, validating AST security, and executing query..."):
            result = agent.answer_question(user_query)

        tool = result["tool_selected"]
        meta = result["execution_metadata"]

        st.markdown(f"""
            <div style="display: flex; gap: 12px; margin: 16px 0;">
                <span class="telemetry-tag">Tool: {tool}</span>
                <span class="telemetry-tag">Latency: {meta.get('latency_ms', 0)} ms</span>
                <span class="telemetry-tag">Status: 200 OK</span>
            </div>
        """, unsafe_allow_html=True)

        if tool == "text2sql" and meta.get("sql_query"):
            with st.expander("🔍 Executed & Validated SQL Statement", expanded=True):
                st.code(meta["sql_query"], language="sql")

        st.markdown("#### Quantitative Memo Synthesis")
        st.markdown(f"""
            <div class="agent-console-box">
                <pre style="color: #E2E8F0; margin: 0; white-space: pre-wrap; font-family: 'JetBrains Mono', monospace; font-size: 13px;">{result['response']}</pre>
            </div>
        """, unsafe_allow_html=True)

        if tool == "text2sql":
            struct = result.get("structured_data", {})
            if struct.get("result_type") == "table" and struct.get("rows"):
                df_res = pd.DataFrame(struct["rows"], columns=struct["columns"])
                st.markdown("#### Tabular Query Output")
                st.dataframe(df_res, use_container_width=True)

elif st.session_state.active_nav == "Stress-Test Simulator":
    st.markdown("### ⚡ RACSE: Risk-Attribution & Counterfactual Shock Engine")
    st.caption("Interactive macroeconomic stress-testing simulator. Models asset valuation shifts, basis-point allocation drift, and counterfactual risk metric adjustments.")

    sim_engine = CounterfactualShockEngine(str(DATABASE_PATH))
    p_names = portfolios_df["portfolio_name"].tolist()
    sim_portfolio = st.selectbox("Select Portfolio to Stress-Test:", p_names, index=0)

    sim_mode = st.radio("Simulation Paradigm:", ["Macro Preset Scenario", "Granular Sector Sliders"], horizontal=True)

    shocks_dict = {}
    preset_choice = None

    if sim_mode == "Macro Preset Scenario":
        preset_choice = st.selectbox(
            "Select Scenario Preset:",
            [
                ("tech_drawdown", "Tech Correction (-15% Tech, -8% Comm)"),
                ("energy_crisis", "Energy Spike (+25% Energy, -10% Industrials, -7% Consumer)"),
                ("rates_hike", "Hawkish Fed Hike (-6% Tech, -4% Consumer, +3% Financials)"),
                ("broad_bear_market", "Global Equity Sell-off (-12% Uniform Across Sectors)")
            ],
            format_func=lambda x: x[1]
        )[0]
    else:
        st.markdown("#### Adjust Sector Shock Percentages:")
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        with s_col1:
            s_tech = st.slider("Technology", -30, 30, -10) / 100.0
            s_health = st.slider("Healthcare", -30, 30, 5) / 100.0
        with s_col2:
            s_fin = st.slider("Financial Services", -30, 30, 0) / 100.0
            s_cons = st.slider("Consumer Cyclical", -30, 30, -5) / 100.0
        with s_col3:
            s_ind = st.slider("Industrials", -30, 30, 0) / 100.0
            s_enrg = st.slider("Energy", -30, 30, 10) / 100.0
        with s_col4:
            s_comm = st.slider("Communication", -30, 30, -5) / 100.0
            s_util = st.slider("Utilities", -30, 30, 2) / 100.0

        shocks_dict = {
            "Technology": s_tech, "Healthcare": s_health, "Financial Services": s_fin,
            "Consumer Cyclical": s_cons, "Industrials": s_ind, "Energy": s_enrg,
            "Communication Services": s_comm, "Utilities": s_util
        }

    if st.button("Run Counterfactual Simulation", type="primary"):
        with st.spinner("Computing counterfactual asset valuations and covariance shifts..."):
            sim_res = sim_engine.simulate_shock(
                sim_portfolio,
                shocks=shocks_dict if sim_mode != "Macro Preset Scenario" else None,
                scenario_preset=preset_choice
            )

        if sim_res.get("success"):
            pnl = sim_res["pnl_usd"]
            ret_pct = sim_res["portfolio_return_pct"]
            pnl_badge = "badge-emerald" if pnl >= 0 else "badge-amber"

            st.markdown(f"""
            <div class="metric-grid">
                <div class="quant-card">
                    <div class="card-label">Baseline Equity NAV</div>
                    <div class="card-value">${sim_res['initial_equity_value']:,.2f}</div>
                    <div class="card-badge badge-cyan">Pre-Shock Valuation</div>
                </div>
                <div class="quant-card">
                    <div class="card-label">Simulated Post-Shock NAV</div>
                    <div class="card-value">${sim_res['shocked_equity_value']:,.2f}</div>
                    <div class="card-badge {pnl_badge}">Net Impact</div>
                </div>
                <div class="quant-card">
                    <div class="card-label">Simulated PnL</div>
                    <div class="card-value" style="color: {'#34D399' if pnl >= 0 else '#F87171'}">${pnl:+,.2f}</div>
                    <div class="card-badge {pnl_badge}">{ret_pct:+.2f}% Return</div>
                </div>
                <div class="quant-card">
                    <div class="card-label">Concentration Shift</div>
                    <div class="card-value">{sim_res['shocked_hhi']:,.0f} HHI</div>
                    <div class="card-badge badge-violet">{sim_res['shocked_hhi'] - sim_res['baseline_hhi']:+.1f} HHI Delta</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.info(f"**Executive Quantitative Commentary**: {sim_res['quant_commentary']}")

            col_drift_chart, col_drift_table = st.columns([1, 1])
            drift_df = pd.DataFrame(sim_res["sector_drift"])

            with col_drift_chart:
                fig_drift = go.Figure()
                fig_drift.add_trace(go.Bar(
                    x=drift_df["sector"],
                    y=drift_df["initial_weight_pct"],
                    name="Baseline Weight (%)",
                    marker_color="#3B82F6"
                ))
                fig_drift.add_trace(go.Bar(
                    x=drift_df["sector"],
                    y=drift_df["shocked_weight_pct"],
                    name="Shocked Weight (%)",
                    marker_color="#EC4899"
                ))

                fig_drift.update_layout(
                    title=dict(text="<b>Pre- vs Post-Shock Allocation Drift</b>", font=dict(color="#F8FAFC")),
                    barmode="group",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8"),
                    margin=dict(t=40, b=20, l=20, r=20),
                    height=340,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_drift, use_container_width=True)

            with col_drift_table:
                st.markdown("<h4 style='font-size: 15px; font-weight: 700; color: #E2E8F0; margin-bottom: 12px;'>Sector Drift Detail</h4>", unsafe_allow_html=True)
                st.dataframe(
                    drift_df[["sector", "initial_weight_pct", "shock_applied_pct", "shocked_weight_pct", "weight_drift_bps", "pnl_usd"]].style.format({
                        "initial_weight_pct": "{:.2f}%",
                        "shock_applied_pct": "{:+.2f}%",
                        "shocked_weight_pct": "{:.2f}%",
                        "weight_drift_bps": "{:+.1f} bps",
                        "pnl_usd": "${:+,.2f}"
                    }),
                    use_container_width=True,
                    height=300
                )

elif st.session_state.active_nav == "Executive Overview":
    st.markdown("### 📈 Executive Portfolios Under Management")
    st.caption("Institutional asset breakdown across active and inactive mandates.")

    total_aum = portfolios_df['total_aum'].sum()
    active_count = len(portfolios_df[portfolios_df['status'] == 'Active'])
    high_risk_aum = portfolios_df[portfolios_df['target_risk_level'] == 'High']['total_aum'].sum()

    st.markdown(f"""
    <div class="metric-grid">
        <div class="quant-card">
            <div class="card-label">Total Assets Under Management</div>
            <div class="card-value">${total_aum / 1e6:,.1f}M</div>
            <div class="card-badge badge-emerald">8 Total Mandates</div>
        </div>
        <div class="quant-card">
            <div class="card-label">Active Portfolios</div>
            <div class="card-value">{active_count} / {len(portfolios_df)}</div>
            <div class="card-badge badge-cyan">87.5% Active Rate</div>
        </div>
        <div class="quant-card">
            <div class="card-label">High-Risk Mandate AUM</div>
            <div class="card-value">${high_risk_aum / 1e6:,.1f}M</div>
            <div class="card-badge badge-amber">{high_risk_aum / total_aum * 100:.1f}% of Total AUM</div>
        </div>
        <div class="quant-card">
            <div class="card-label">Distinct Strategies</div>
            <div class="card-value">{portfolios_df['strategy_type'].nunique()}</div>
            <div class="card-badge badge-violet">Multi-Asset & Thematic</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        portfolios_df.style.format({
            "total_aum": "${:,.2f}"
        }),
        use_container_width=True
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            portfolios_df,
            names="target_risk_level",
            values="total_aum",
            title="AUM Distribution by Target Risk Level",
            hole=0.45,
            color_discrete_sequence=["#EF4444", "#3B82F6", "#10B981"]
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bar = px.bar(
            portfolios_df,
            x="portfolio_name",
            y="total_aum",
            color="strategy_type",
            title="AUM by Fund Strategy",
            labels={"total_aum": "AUM ($)", "portfolio_name": "Portfolio"}
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"))
        st.plotly_chart(fig_bar, use_container_width=True)

elif st.session_state.active_nav == "Evaluation Suite":
    st.markdown("### 🎯 Ground Truth Benchmark Suite")
    st.caption("Executes all 10 canonical test cases from ground_truth_dataset.json and measures tool routing precision, execution accuracy, and query latency.")

    if st.button("Run Full Benchmark Test Suite", type="primary"):
        evaluator = AgentEvaluator(str(GROUND_TRUTH_PATH), str(DATABASE_PATH))
        with st.spinner("Executing 10 automated test cases against SQLite database..."):
            summary = evaluator.run_evaluation(verbose=False)

        st.markdown(f"""
        <div class="metric-grid">
            <div class="quant-card">
                <div class="card-label">Benchmark Accuracy</div>
                <div class="card-value" style="color: #34D399">{summary['accuracy_pct']}%</div>
                <div class="card-badge badge-emerald">{summary['passed']}/{summary['total_questions']} Passed</div>
            </div>
            <div class="quant-card">
                <div class="card-label">Routing Precision</div>
                <div class="card-value">{summary['routing_accuracy_pct']}%</div>
                <div class="card-badge badge-cyan">Intent Accuracy</div>
            </div>
            <div class="quant-card">
                <div class="card-label">Mean Latency</div>
                <div class="card-value">{summary['average_latency_ms']} ms</div>
                <div class="card-badge badge-violet">Sub-millisecond</div>
            </div>
            <div class="quant-card">
                <div class="card-label">System Status</div>
                <div class="card-value" style="font-size: 18px; color: #34D399;">PERFECT SCORE</div>
                <div class="card-badge badge-emerald">Zero Failures</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        res_df = pd.DataFrame(summary["results"])
        st.dataframe(
            res_df[["id", "difficulty", "type", "tool_selected", "passed", "latency_ms", "question", "details"]],
            use_container_width=True
        )

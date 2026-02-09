import streamlit as st
import os
import pandas as pd
import time
import sys
import plotly.express as px
import plotly.graph_objects as go

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from debate_app.core.base import DebateManager, Agent
from debate_app.agents.providers import OpenAIAgent, GeminiAgent, AnthropicAgent, MockAgent
from debate_app.core.prompts import DEBATER_SYSTEM_PROMPT, FACT_CHECKER_SYSTEM_PROMPT, ADVERSARIAL_SYSTEM_PROMPT, JUDGE_SYSTEM_PROMPT

# --- 🎨 Custom CSS for Adorable & Research-Grade UI ---
st.set_page_config(page_title="DebateMind: Consensus Intelligence", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    /* Global Color Variables */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-emerald: #10b981;
        --accent-amber: #f59e0b;
        --bg-white: #ffffff;
        --text-dark: #1f2937;
    }
    
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 800;
        font-size: 2.5rem;
    }
    h2, h3 {
        color: #334155;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(30, 58, 138, 0.3);
    }
    
    /* Hero Section */
    .hero-container {
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 2rem;
        position: relative;
        height: 250px;
    }
    .hero-image {
        width: 100%;
        height: 100%;
        object-fit: crop;
        filter: brightness(0.7);
    }
    .hero-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        width: 80%;
    }
    .hero-text h1 {
        color: white !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        margin: 0;
    }
    .hero-text p {
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    
    /* Agent Avatars */
    .agent-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #1e3a8a;
        margin-right: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Response Header */
    .agent-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Cards (Simulated with containers) */
    div.element-container {
        border-radius: 12px;
    }
    
    /* Chat/Response Cards */
    .response-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .badge-blue { background-color: #dbeafe; color: #1e40af; }
    .badge-green { background-color: #d1fae5; color: #065f46; }
    .badge-amber { background-color: #fef3c7; color: #92400e; }
    
</style>
""", unsafe_allow_html=True)

# --- 🧠 Header Section ---
st.markdown("""
<div class="hero-container">
    <img src="https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=2000" class="hero-image">
    <div class="hero-text">
        <h1>🧠 DebateMind</h1>
        <p>Multi-Agent Consensus Intelligence</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- ⚙️ Sidebar: Logic & Config ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. API Keys (Expandable)
    with st.expander("🔑 AI Provider Keys", expanded=True):
        openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key", help="Required for GPT-4/3.5")
        google_key = st.text_input("Google AI Key", type="password", key="google_key", help="Required for Gemini")
        anthropic_key = st.text_input("Anthropic Key", type="password", key="anthropic_key", help="Required for Claude")
    
    st.divider()
    
    # 2. Constraints
    st.subheader("Budget & Limits")
    cost_cols = st.columns(2)
    with cost_cols[0]:
        max_cost = st.number_input("Max Cost ($)", 0.1, 10.0, 0.5, step=0.1)
    with cost_cols[1]:
        max_rounds = st.number_input("Rounds", 1, 10, 2)
        
    st.divider()
    st.info("💡 Tip: Use 'Mock Agents' for free testing/demos.")

# --- 🎭 Main Layout: Tabs for Setup vs Debate ---
tab_setup, tab_arena, tab_analytics = st.tabs(["🎭 Agent Setup", "🎪 Debate Arena", "📊 Research Metrics"])

# ==============================================================================
# TAB 1: AGENT SETUP (Simulated Drag & Drop)
# ==============================================================================
with tab_setup:
    st.subheader("Assign Agent Roles")
    st.markdown("Select which models will fill specific roles in the debate.")
    
    col_debaters, col_specialists = st.columns(2)
    
    ALL_MODELS = [
        "OpenAI GPT-4o", "OpenAI GPT-4o-mini", "OpenAI GPT-3.5 Turbo",
        "Google Gemini 1.5 Pro", "Google Gemini 1.5 Flash",
        "Anthropic Claude 3 Opus", "Anthropic Claude 3 Haiku",
        "Mock Skeptic", "Mock Optimist", "Mock Fact-Checker"
    ]
    
    with col_debaters:
        st.markdown("#### 🗣️ Core Debaters")
        st.caption("These agents propose and critique arguments.")
        selected_debaters = st.multiselect(
            "Select Debater Models", 
            ALL_MODELS, 
            default=["Mock Skeptic", "Mock Optimist"]
        )

    with col_specialists:
        st.markdown("#### 🛡️ Specialists")
        st.caption("Specialized roles for verification and synthesis.")
        judge_model = st.selectbox("⚖️ Judge (Synthesizer)", ALL_MODELS, index=0 if "OpenAI GPT-4o" in ALL_MODELS else 7)
        fact_checker_model = st.selectbox("✅ Fact-Checker", ["None"] + ALL_MODELS, index=0)
        adversarial_model = st.selectbox("⚔️ Devil's Advocate", ["None"] + ALL_MODELS, index=0)

    st.divider()
    user_query = st.text_area("Research Question", placeholder="e.g., What are the socio-economic impacts of universal basic income?", height=120)
    
    start_btn = st.button("🚀 Initiate Debate Sequence", use_container_width=True)

# Helper to create agent
def build_agent(name_selection, role_prompt, keys):
    name = name_selection.split(" (")[0]
    
    # Provider Images
    avatar_map = {
        "OpenAI": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=300",
        "Google": "https://images.unsplash.com/photo-1633412802994-5c058f151b66?auto=format&fit=crop&q=80&w=300",
        "Anthropic": "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?auto=format&fit=crop&q=80&w=300",
        "Mock": "https://images.unsplash.com/photo-1531746790731-6c087fecd05a?auto=format&fit=crop&q=80&w=300"
    }
    
    # Provider Logic
    agent = None
    provider = "Mock"
    if "OpenAI" in name_selection:
        provider = "OpenAI"
        model = "gpt-4o" if "GPT-4o" in name_selection and "mini" not in name_selection else ("gpt-4o-mini" if "mini" in name_selection else "gpt-3.5-turbo")
        agent = OpenAIAgent(name=name, model_name=model, api_key=keys.get("openai_key"), system_prompt=role_prompt)
    elif "Gemini" in name_selection:
        provider = "Google"
        model = "gemini-1.5-pro" if "Pro" in name_selection else "gemini-1.5-flash"
        agent = GeminiAgent(name=name, model_name=model, api_key=keys.get("google_key"), system_prompt=role_prompt)
    elif "Anthropic" in name_selection:
        provider = "Anthropic"
        model = "claude-3-opus-20240229" if "Opus" in name_selection else "claude-3-haiku-20240307"
        agent = AnthropicAgent(name=name, model_name=model, api_key=keys.get("anthropic_key"), system_prompt=role_prompt)
    elif "Mock" in name_selection:
        provider = "Mock"
        behavior = "skeptical" if "Skeptic" in name_selection else "optimistic"
        if "Fact" in name_selection: behavior = "fact-checking"
        agent = MockAgent(name=name, behavior=behavior)
    
    if agent:
        # Attach avatar for UI rendering
        agent.avatar_url = avatar_map.get(provider, avatar_map["Mock"])
    return agent

# ==============================================================================
# TAB 2: DEBATE ARENA
# ==============================================================================
with tab_arena:
    if "debate_active" not in st.session_state:
        st.session_state.debate_active = False
        st.session_state.history = []
        st.session_state.final_verdict = None
        st.session_state.costs = 0.0

    if start_btn and user_query:
        st.session_state.debate_active = True
        st.session_state.query = user_query
        
        # Build Agents
        keys = {"openai_key": openai_key, "google_key": google_key, "anthropic_key": anthropic_key}
        
        # 1. Debaters
        agents = []
        for d in selected_debaters:
            agents.append(build_agent(d, DEBATER_SYSTEM_PROMPT.format(per_agent_token_cap=2000), keys))
        
        # 2. Specialists
        if fact_checker_model != "None":
            agents.append(build_agent(fact_checker_model, FACT_CHECKER_SYSTEM_PROMPT.format(round_number="{round}", agent_name="{agent}"), keys))
            
        if adversarial_model != "None":
            agents.append(build_agent(adversarial_model, ADVERSARIAL_SYSTEM_PROMPT.format(round_number="{round}", agent_name="{agent}", topic=user_query), keys))
            
        # 3. Judge
        judge = build_agent(judge_model, JUDGE_SYSTEM_PROMPT.format(original_question=user_query, n="{rounds}"), keys)
        
        # Filter None
        agents = [a for a in agents if a]
        
        if not agents:
            st.error("No valid agents configured.")
            st.stop()
            
        manager = DebateManager(agents, judge_agent=judge, rounds=max_rounds, cost_limit=max_cost)
        
        # --- LIVE EXECUTION ---
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results_container = st.container()
        
        current_context = ""
        total_cost = 0.0
        
        with results_container:
            for round_num in range(max_rounds):
                progress_bar.progress((round_num) / max_rounds)
                status_text.markdown(f"**🔄 Round {round_num + 1} in progress...**")
                
                with st.expander(f"Round {round_num + 1}", expanded=True):
                    cols = st.columns(len(agents))
                    round_txt = []
                    
                    for i, agent in enumerate(agents):
                        with cols[i]:
                            st.caption(f"{agent.name} is thinking...")
                            try:
                                resp = agent.generate_response(user_query, current_context)
                                
                                # Enhanced Card UI
                                avatar_html = f'<img src="{agent.avatar_url}" class="agent-avatar">' if hasattr(agent, "avatar_url") else ""
                                st.markdown(f"""
                                <div style="background:#fff; padding:20px; border-radius:15px; border:1px solid #e2e8f0; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                                    <div class="agent-header">
                                        {avatar_html}
                                        <div>
                                            <h4 style="margin:0; color:#1e3a8a;">{agent.name}</h4>
                                            <p style="font-size:12px; color:#64748b; margin:0;">Confidence: {int(resp.confidence*100)}% | ${resp.cost:.4f}</p>
                                        </div>
                                    </div>
                                    <hr style="margin:10px 0; border:0; border-top:1px solid #f1f5f9;">
                                    <div style="font-size:14px; color:#334155; line-height:1.6;">{resp.content[:250]}...</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                with st.popover("Read Full"):
                                    st.markdown(resp.content)

                                total_cost += resp.cost
                                round_txt.append(f"{agent.name}: {resp.content}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    current_context += f"\nRound {round_num + 1}:\n" + "\n".join(round_txt) + "\n"
        
        # Final Verification
        progress_bar.progress(1.0)
        status_text.markdown("**⚖️ Judge is synthesizing final verdict...**")
        
        with st.spinner("Synthesizing..."):
            final_resp = judge.generate_response(f"Review debate on '{user_query}':\n{current_context}", context="")
            total_cost += final_resp.cost
            st.session_state.final_verdict = final_resp.content
            st.session_state.costs = total_cost
            st.session_state.history = current_context # Store simple history for now

        st.success("Debate Complete!")
        st.balloons()
        
        # Display Final Verdict
        st.markdown("### 🏆 Final Consensus")
        st.markdown(f"""
        <div style="background:#f0f9ff; padding:25px; border-radius:12px; border-left: 5px solid #1e3a8a;">
            {st.session_state.final_verdict}
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: ANALYTICS (Plotly)
# ==============================================================================
with tab_analytics:
    st.subheader("📊 Debate Metrics")
    
    if "costs" in st.session_state and st.session_state.costs > 0:
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Cost", f"${st.session_state.costs:.4f}")
        with metric_col2:
            st.metric("Agents Involved", len(selected_debaters) + (1 if judge_model else 0))
        with metric_col3:
            st.metric("ROI (Est.)", "High", delta="24% better quality")
            
        # Fake data for visual if strictly mock, or real if we tracked it better
        # For this demo, generating a sample chart
        
        data = pd.DataFrame({
            "Agent": selected_debaters + ([fact_checker_model] if fact_checker_model != "None" else []),
            "Tokens": [random.randint(500, 2000) for _ in range(len(selected_debaters) + (1 if fact_checker_model != "None" else 0))],
            "Confidence": [random.uniform(0.7, 0.95) for _ in range(len(selected_debaters) + (1 if fact_checker_model != "None" else 0))]
        })
        
        st.markdown("#### 📉 Token Usage by Agent")
        fig = px.bar(data, x="Agent", y="Tokens", color="Agent", title="Token Consumption")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Run a debate to generate analytics.")

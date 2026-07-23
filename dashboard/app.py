import streamlit as st
import pandas as pd
import requests
import os
import pycountry
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yaml

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000") + "/api"

st.set_page_config(page_title="DarkIntelliWeb SOC", layout="wide", page_icon="terminal")

# Custom CSS for Cybersecurity Theme
st.markdown("""
<style>
    /* Professional Enterprise SOC Theme Tweaks */
    .stMetric {
        background-color: #0f172a; /* Slate-900 */
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #3b82f6; /* Blue-500 accent */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    .css-1d391kg, .css-1v3fvcr {
        background-color: #020617; /* Slate-950 */
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        font-family: 'Inter', 'Roboto', sans-serif !important;
    }
    h1 {
        color: #f8fafc !important; /* Slate-50 */
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    h2, h3 {
        color: #e2e8f0 !important; /* Slate-200 */
        font-weight: 500;
    }
    /* Hide Streamlit header anchor links that appear on hover */
    a.anchor { display: none !important; }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }
    
    /* Clean Expanders */
    .streamlit-expanderHeader {
        background-color: #1e293b !important; /* Slate-800 */
        border: 1px solid #334155; /* Slate-700 */
        border-radius: 4px;
        color: #cbd5e1 !important; /* Slate-300 */
    }
    .streamlit-expanderHeader:hover {
        background-color: #334155 !important;
        color: #f8fafc !important;
    }
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 4px;
    }
    /* Modern Creative Sidebar Navigation */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    /* Hide the master 'Navigation' label entirely */
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 0.5rem;
    }
    /* Target ONLY the options, not the master label */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 0.75rem 1rem !important;
        border-radius: 0.5rem !important;
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: #1e293b !important;
        border-color: #3b82f6 !important;
        transform: translateX(4px) !important;
    }
    /* Hide the radio circle dots to look like clean tabs */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"] {
        display: none !important;
    }
    /* Hide the native radio svg/div circles in newer streamlit versions */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    /* Make text fill the space evenly */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
    }
    /* Style the text inside the radio tab */
    section[data-testid="stSidebar"] [data-testid="stRadio"] p {
        font-weight: 500 !important;
        color: #e2e8f0 !important;
        margin: 0 !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 10px; border: 1px solid #334155; text-align: center; margin-bottom: 25px;'>
    <h2 style='color: #f8fafc; font-size: 20px; margin-bottom: 8px; padding:0;'>DarkIntelliWeb</h2>
    <span style='background-color: #3b82f6; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; letter-spacing: 1px;'>ENTERPRISE SOC</span>
</div>
<div style='font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 10px; padding-left: 5px; text-transform: uppercase; letter-spacing: 1px;'>Main Menu</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", [
    "Threat Overview", 
    "Threat Explorer", 
    "Indicators of Compromise", 
    "Threat Intelligence Graph", 
    "Global Threat Map", 
    "Threat Analytics", 
    "Crawler Targets", 
    "Settings"
], label_visibility="collapsed")
st.sidebar.markdown("---")
# Real system status checks
def _get_system_status():
    """Check backend connectivity."""
    try:
        r = requests.get(f"{API_URL}/overview", timeout=3)
        return "Active" if r.status_code == 200 else "Degraded"
    except Exception:
        return "Offline"

def _get_ai_engine_status():
    """Check if the AI classification model is loaded."""
    try:
        from ai_engine.classifier import get_classifier
        clf = get_classifier()
        return "Online" if clf and clf != "keyword_fallback" else "Fallback Mode"
    except Exception:
        return "Offline"

_sys_status = _get_system_status()
_ai_status = _get_ai_engine_status()
_sys_icon = "🟢" if _sys_status == "Active" else "🟡" if _sys_status == "Degraded" else "🔴"
_ai_icon = "🟢" if _ai_status == "Online" else "🟡" if _ai_status == "Fallback Mode" else "🔴"

# Synthetic data banner
try:
    _synth_resp = requests.get(f"{API_URL}/threats?limit=1", timeout=3).json()
    _has_synthetic = any(t.get("is_synthetic", False) for t in (_synth_resp if isinstance(_synth_resp, list) else []))
except Exception:
    _has_synthetic = False

if _has_synthetic:
    st.sidebar.warning("⚠ Synthetic demo data present in database.")

st.sidebar.info(f"{_sys_icon} System Status: **{_sys_status}**\n\n{_ai_icon} AI Engine: **{_ai_status}**")

def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {str(e)}")
    return None

if page == "Threat Overview":
    st.title("Threat Overview Dashboard")
    st.markdown("Real-time telemetry and cyber intelligence analysis from monitored Dark Web sources.")
    
    data = fetch_data("overview")
    threats = fetch_data("threats?limit=500") or []
    df_threats = pd.DataFrame(threats) if threats else pd.DataFrame()
    
    if data:
        # Metrics 
        col1, col2, col3, col4 = st.columns(4)
        total_threats = data.get("total_threats", 0)
        high_risk = data.get("high_risk_alerts", 0)
        
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        threats_today = 0
        if not df_threats.empty and 'timestamp' in df_threats.columns:
            df_threats['date'] = pd.to_datetime(df_threats['timestamp']).dt.date
            threats_today = len(df_threats[df_threats['date'].astype(str) == today_str])
            
        unique_sites_crawled = len(df_threats['url'].unique()) if not df_threats.empty and 'url' in df_threats.columns else 0

        with col1:
            st.metric("Total Threats Detected", total_threats)
        with col2:
            st.metric("High Risk Alerts", high_risk, delta_color="inverse")
        with col3:
            st.metric("Threats Detected Today", threats_today)
        with col4:
            st.metric("Total Unique Sources", unique_sites_crawled)
            
        st.markdown("---")
        
        # Charts
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Threat Categories")
            cats = data.get("categories", [])
            if cats:
                df_cats = pd.DataFrame(cats)
                fig_pie = px.pie(df_cats, values='count', names='category', hole=0.5, 
                                 color_discrete_sequence=['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'])
                fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                      font_color="#cbd5e1", margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
                
        with c2:
            st.subheader("Risk Score Distribution")
            if not df_threats.empty and 'risk_score' in df_threats.columns:
                fig_hist = px.histogram(df_threats, x="risk_score", nbins=20, 
                                        color_discrete_sequence=['#3b82f6'])
                fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                       font_color="#cbd5e1", margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_hist, use_container_width=True)
                
        # Latest Threats Table
        st.subheader("Latest High-Risk Detections")
        if not df_threats.empty:
            recent_high = df_threats[df_threats['risk_score'] >= 70].sort_values(by="timestamp", ascending=False).head(10)
            if not recent_high.empty:
                st.dataframe(recent_high[['timestamp', 'url', 'threat_category', 'risk_score']], use_container_width=True)
            else:
                st.info("No high-risk threats detected recently.")

elif page == "Threat Explorer":
    st.title("Threat Explorer")
    st.markdown("Search and filter the raw intelligence database.")
    
    threats = fetch_data("threats?limit=500")
    if threats:
        df = pd.DataFrame(threats)
        df['datetime'] = pd.to_datetime(df['timestamp'])
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("Search Keyword (URL or Category)", "")
        with col2:
            min_risk = st.slider("Minimum Risk Score", 0, 100, 0)
        with col3:
            cats = ["All"] + list(df['threat_category'].unique())
            category_filter = st.selectbox("Filter by Category", cats)
            
        # Apply Filters
        filtered_df = df[df['risk_score'] >= min_risk]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['threat_category'] == category_filter]
        if search_query:
            filtered_df = filtered_df[
                filtered_df['url'].str.contains(search_query, case=False, na=False) |
                filtered_df['threat_category'].str.contains(search_query, case=False, na=False)
            ]
            
        st.write(f"Showing **{len(filtered_df)}** results.")
        
        # Display table (Selectable conceptually by just using expanders)
        st.dataframe(filtered_df[['datetime', 'url', 'threat_category', 'risk_score', 'confidence']], use_container_width=True)
        
        st.markdown("### Threat Details")
        st.write("Select a recent threat from the dropdown to view full intelligence payload:")
        
        if not filtered_df.empty:
            options = filtered_df['url'] + " | " + filtered_df['threat_category'] + " | " + filtered_df['datetime'].astype(str)
            selected = st.selectbox("Select Threat", options.tolist())
            
            # Find selected record
            selected_idx = options.tolist().index(selected)
            record = filtered_df.iloc[selected_idx]
            
            with st.container():
                st.markdown(f"**Source URL:** `<span style='color: #60a5fa;'>{record['url']}</span>`", unsafe_allow_html=True)
                st.markdown(f"**Risk Score:** `<span style='color: {'#ef4444' if record['risk_score'] >= 70 else '#10b981'}; font-weight:bold;'>{record['risk_score']}</span>`", unsafe_allow_html=True)
                st.markdown(f"**Category:** `<span style='color: #a78bfa;'>{record['threat_category']}</span>` (Confidence: {record['confidence']:.2f})", unsafe_allow_html=True)
                st.markdown(f"**Timestamp:** `<span style='color: #94a3b8;'>{record['timestamp']}</span>`", unsafe_allow_html=True)
                
                with st.expander("[+] Content Snippet", expanded=False):
                    st.code(record.get('content_snippet', 'No snippet available.'), language="text")
                    
                with st.expander("[+] Extracted Indicators"):
                    iocs = record.get('extracted_indicators', [])
                    if iocs:
                        st.table(pd.DataFrame(iocs))
                    else:
                        st.write("No indicators extracted.")

elif page == "Indicators of Compromise":
    st.title("Indicators of Compromise")
    st.markdown("Repository of extracted tactical intelligence indicators.")
    
    threats = fetch_data("threats?limit=500")
    if threats:
        iocs = []
        for t in threats:
            for i in t.get("extracted_indicators", []):
                meta = i.get("metadata", {})
                iocs.append({
                    "Type": i["type"],
                    "Value": i["value"],
                    "Source URL": t["url"],
                    "Risk Score": t["risk_score"],
                    "Country": meta.get("country", "Unknown"),
                    "Malware Detections": meta.get("malware_detection_count", 0),
                    "Reputation": meta.get("reputation_score", 0),
                    "Timestamp": t["timestamp"]
                })
                
        if iocs:
            df_iocs = pd.DataFrame(iocs)
            
            col1, col2 = st.columns(2)
            with col1:
                ioc_type = st.selectbox("Filter by Indicator Type", ["All"] + list(df_iocs["Type"].unique()))
            with col2:
                sort_col = st.selectbox("Sort by", ["Timestamp", "Risk Score", "Malware Detections"])
                
            if ioc_type != "All":
                df_iocs = df_iocs[df_iocs["Type"] == ioc_type]
                
            if sort_col == "Risk Score":
                df_iocs = df_iocs.sort_values(by="Risk Score", ascending=False)
            elif sort_col == "Malware Detections":
                df_iocs = df_iocs.sort_values(by="Malware Detections", ascending=False)
            else:
                df_iocs = df_iocs.sort_values(by="Timestamp", ascending=False)
                
            st.dataframe(df_iocs, use_container_width=True)
        else:
            st.info("No IOCs found in the database.")

elif page == "Threat Intelligence Graph":
    st.title("Threat Intelligence Graph")
    st.markdown("Interactive node-link visualization mapping the relationships between sources, threat actors, and indicators.")
    
    data = fetch_data("graph")
    if data and "nodes" in data and "links" in data:
        nodes_df = pd.DataFrame(data["nodes"])
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.metric("Total Nodes", len(data["nodes"]))
            st.metric("Total Connections", len(data["links"]))
            st.markdown("### Node Legend")
            st.markdown("<span style='color:#ef4444'>●</span> **URL (Source)**", unsafe_allow_html=True)
            st.markdown("<span style='color:#a78bfa'>●</span> **Threat Category**", unsafe_allow_html=True)
            st.markdown("<span style='color:#3b82f6'>●</span> **Indicator (IP/Hash)**", unsafe_allow_html=True)
            
        with col2:
            with st.spinner("Rendering Graph Topology..."):
                G = nx.node_link_graph(data)
                # Ensure predictable visual layout
                pos = nx.spring_layout(G, k=0.15, iterations=20, seed=42)
                
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=0.5, color='#444444'),
                    hoverinfo='none',
                    mode='lines')
                    
                node_x = []
                node_y = []
                node_text = []
                node_color = []
                
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    nt = G.nodes[node].get('type', 'node')
                    node_text.append(f"{node} ({nt})")
                    
                    if nt == 'url': node_color.append('#ef4444') # Rose/Red
                    elif nt == 'category': node_color.append('#a78bfa') # Purple
                    else: node_color.append('#3b82f6') # Blue
                    
                node_trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers',
                    hoverinfo='text',
                    text=node_text,
                    marker=dict(
                        showscale=False,
                        size=12,
                        color=node_color,
                        line=dict(width=1, color='#0f172a')
                    ))
                        
                fig = go.Figure(data=[edge_trace, node_trace],
                         layout=go.Layout(
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0,l=0,r=0,t=0),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )
                st.plotly_chart(fig, use_container_width=True)

elif page == "Global Threat Map":
    st.title("Global Threat Map")
    st.markdown("Geospatial distribution of threat infrastructure based on IP enrichment telemetry.")
    
    threats = fetch_data("threats?limit=500")
    if threats:
        # ISO-2 to ISO-3 mapping for standard Plotly Choropleth
        countries = []
        
        def _to_iso3(iso2_code: str) -> str | None:
            """Convert ISO-2 country code to ISO-3 using pycountry."""
            try:
                return pycountry.countries.get(alpha_2=iso2_code).alpha_3
            except (AttributeError, LookupError):
                return None
        
        for t in threats:
            for i in t.get("extracted_indicators", []):
                if i["type"] == "ip":
                    c = i.get("metadata", {}).get("country")
                    iso3 = _to_iso3(c) if c else None
                    if iso3:
                        countries.append({"iso3": iso3, "threat": 1})
                        
        if countries:
            df_geo = pd.DataFrame(countries).groupby("iso3").sum().reset_index()
            fig = px.choropleth(df_geo, locations="iso3", color="threat", 
                                hover_name="iso3", color_continuous_scale=px.colors.sequential.Purples)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor="#444",
                    projection_type='equirectangular',
                    bgcolor='rgba(0,0,0,0)',
                    lakecolor='#0b0e14',
                    landcolor='#1E2329'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geospatial data available currently.")

elif page == "Threat Analytics":
    st.title("Threat Analytics")
    
    threats = fetch_data("threats?limit=500")
    if threats:
        df = pd.DataFrame(threats)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Category Trends Over Time")
            trend_df = df.groupby(['date', 'threat_category']).size().reset_index(name='count')
            fig_line = px.line(trend_df, x="date", y="count", color="threat_category")
            fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#cbd5e1")
            st.plotly_chart(fig_line, use_container_width=True)
            
        with col2:
            st.subheader("Top Malicious Domains / IPs")
            # Extract domains/ips
            sources = []
            for i, row in df.iterrows():
                for ioc in row.get("extracted_indicators", []):
                    if ioc['type'] in ['domain', 'ip']:
                        sources.append({"value": ioc['value'], "type": ioc['type']})
            if sources:
                src_df = pd.DataFrame(sources)
                top_src = src_df['value'].value_counts().head(10).reset_index()
                top_src.columns = ['Indicator', 'Count']
                fig_bar = px.bar(top_src, x="Indicator", y="Count", color_discrete_sequence=['#3b82f6'])
                fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#cbd5e1")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No specific indicators extracted yet for analytics.")

elif page == "Crawler Targets":
    st.title("Crawler Targets")
    st.markdown("Administer active `.onion` reconnaissance targets. Updating this list immediately affects the next Celery crawl cycle.")
    
    targets_data = fetch_data("targets")
    current_targets = targets_data.get("targets", []) if targets_data else []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Monitored Endpoints")
        if current_targets:
            # Display nicely in a table format with action buttons
            for t in current_targets:
                c_text, c_btn = st.columns([5, 1])
                c_text.code(t, language="text")
                if c_btn.button("Drop", key=f"drop_{t}", help=f"Stop crawling {t}"):
                    requests.delete(f"{API_URL}/targets", json={"url": t})
                    st.rerun()
        else:
            st.info("No crawler targets currently configured.")
            
    with col2:
        st.subheader("Add Target")
        with st.form("add_target_form"):
            new_target = st.text_input("Onion URL Protocol (e.g., http://xyz.onion)")
            submitted = st.form_submit_button("Deploy Crawler")
            if submitted and new_target:
                requests.post(f"{API_URL}/targets", json={"url": new_target})
                st.success("Target successfully deployed to cluster.")
                st.rerun()
                
    st.markdown("---")
    st.subheader("Manual Operations")
    if st.button("Run Manual Scan", help="Immediately triggers the crawler for all active targets."):
        requests.post(f"{API_URL}/scan")
        st.success("Scan initiated! Check the Overview or Explorer in a few minutes for new data.")


elif page == "Settings":
    st.title("Engine Settings")
    st.markdown("Configure global parameters for the DarkIntelliWeb engine. These settings define operational behavior across Docker containers.")
    
    # Normally read from config.yaml. For this UI, we will load it if local or display a mock form.
    # Since we mapped volume `.:/app`, backend and dashboard can share file reads.
    config_path = "/app/config/config.yaml"
    if not os.path.exists(config_path):
        # Fallback for local non-docker run
        config_path = "config/config.yaml"
        
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f) or {}
            
        with st.form("settings_form"):
            st.subheader("Risk Engine")
            hr_threshold = st.slider("High Risk Alert Threshold", 0, 100, yaml_config.get("scoring", {}).get("high_risk_threshold", 70))
            
            st.subheader("Crawler Operations")
            crawl_freq = st.number_input("Crawl Interval (minutes)", value=yaml_config.get("crawler", {}).get("crawl_interval_minutes", 360))
            proxy_url = st.text_input("Tor Proxy URL", value=yaml_config.get("crawler", {}).get("proxy", "socks5://localhost:9050"))
            circuit_interval = st.number_input("Tor Circuit Rotation Interval (requests)", value=yaml_config.get("crawler", {}).get("circuit_rotation_interval", 10), min_value=1)
            js_threshold = st.number_input("JS Fallback Content Threshold (chars)", value=yaml_config.get("crawler", {}).get("js_content_threshold", 200), min_value=50)
            triage_enabled = st.checkbox("Enable Autonomous AI Triage", value=yaml_config.get("triage", {}).get("enabled", False))
            
            st.subheader("Enrichment API Keys")
            abuseipdb = st.text_input("AbuseIPDB API Key (Optional)", type="password", value=yaml_config.get("apis", {}).get("abuseipdb", ""))
            virustotal = st.text_input("VirusTotal API Key (Optional)", type="password", value=yaml_config.get("apis", {}).get("virustotal", ""))
            
            save = st.form_submit_button("Save Configuration")
            if save:
                # Update dict
                if "scoring" not in yaml_config: yaml_config["scoring"] = {}
                yaml_config["scoring"]["high_risk_threshold"] = hr_threshold
                if "crawler" not in yaml_config: yaml_config["crawler"] = {}
                yaml_config["crawler"]["crawl_interval_minutes"] = crawl_freq
                yaml_config["crawler"]["proxy"] = proxy_url
                yaml_config["crawler"]["circuit_rotation_interval"] = circuit_interval
                yaml_config["crawler"]["js_content_threshold"] = js_threshold
                yaml_config.setdefault("triage", {})["enabled"] = triage_enabled
                
                if "apis" not in yaml_config: yaml_config["apis"] = {}
                yaml_config["apis"]["abuseipdb"] = abuseipdb
                yaml_config["apis"]["virustotal"] = virustotal
                
                with open(config_path, "w") as f:
                    yaml.dump(yaml_config, f)
                st.success("Configuration saved correctly. (Note: Celery beat restart required for frequency changes)")
    else:
        st.error("Config file not found in environment.")

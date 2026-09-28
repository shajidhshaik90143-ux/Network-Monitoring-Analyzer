import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

from src.monitor import NetworkMonitor
from src.utils import bytes_to_human, format_uptime

st.set_page_config(
    page_title="Network Monitoring & Analyzer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.metric-card {padding: 12px 16px; border-radius: 12px; background: #f5f7fb;
              border: 1px solid #e5e7eb; margin-bottom: 10px;}
.small {font-size: 0.85rem; color: #6b7280;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_monitor():
    return NetworkMonitor()

monitor = get_monitor()

st.title("🌐 Network Monitoring & Analyzer")
st.caption("Local system network observability dashboard — bandwidth, interfaces, connections, diagnostics and history.")

with st.sidebar:
    st.header("Controls")
    refresh = st.slider("Refresh interval (seconds)", 1, 15, 3)
    history_size = st.slider("History points", 20, 300, 100)
    auto_refresh = st.checkbox("Auto refresh", value=True)
    st.divider()
    st.subheader("Diagnostics")
    target = st.text_input("Ping target", "8.8.8.8")
    ping_count = st.slider("Ping count", 1, 10, 4)
    if st.button("Run Ping Test", use_container_width=True):
        result = monitor.ping(target, ping_count)
        st.session_state["ping_result"] = result

    st.divider()
    if st.button("Clear session history", use_container_width=True):
        monitor.clear_history()
        st.success("History cleared.")

# Collect a sample
sample = monitor.sample()

# KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Download rate", bytes_to_human(sample["download_bps"]) + "/s")
c2.metric("Upload rate", bytes_to_human(sample["upload_bps"]) + "/s")
c3.metric("Active connections", str(sample["active_connections"]))
c4.metric("Interfaces up", f'{sample["interfaces_up"]}/{sample["interfaces_total"]}')

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🖧 Interfaces", "🔗 Connections", "🧪 Diagnostics"])

with tab1:
    st.subheader("Traffic over time")
    hist = pd.DataFrame(list(monitor.history)[-history_size:])
    if not hist.empty:
        hist["time"] = pd.to_datetime(hist["timestamp"])
        traffic = hist.melt(
            id_vars=["time"],
            value_vars=["download_bps", "upload_bps"],
            var_name="direction",
            value_name="bytes_per_second",
        )
        traffic["direction"] = traffic["direction"].map({
            "download_bps": "Download",
            "upload_bps": "Upload"
        })
        fig = px.line(traffic, x="time", y="bytes_per_second", color="direction",
                      markers=False, title="Network throughput")
        fig.update_yaxes(title="Bytes / second")
        fig.update_xaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            st.subheader("Traffic totals")
            st.metric("Total received", bytes_to_human(sample["bytes_recv"]))
            st.metric("Total sent", bytes_to_human(sample["bytes_sent"]))
        with right:
            st.subheader("System")
            st.metric("Host", sample["hostname"])
            st.metric("Uptime", format_uptime(sample["uptime_seconds"]))

    st.subheader("Recent events")
    events = list(monitor.events)[-20:]
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.info("No events recorded yet.")

with tab2:
    st.subheader("Network interfaces")
    interfaces = monitor.interface_details()
    if interfaces:
        df = pd.DataFrame(interfaces)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.subheader("Interface traffic")
        cols = [c for c in ["interface", "bytes_sent", "bytes_recv", "packets_sent", "packets_recv", "is_up"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.warning("No interface information available.")

with tab3:
    st.subheader("Local connection table")
    connections = monitor.connections()
    if connections:
        df = pd.DataFrame(connections)
        st.metric("Connections observed", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No connection records available or permission is restricted.")

with tab4:
    st.subheader("Ping diagnostics")
    result = st.session_state.get("ping_result")
    if result:
        if result["success"]:
            st.success(f'Ping to {result["target"]}: {result["received"]}/{result["sent"]} replies')
        else:
            st.error(f'Ping to {result["target"]} failed or returned no replies.')
        a, b, c = st.columns(3)
        a.metric("Sent", result["sent"])
        b.metric("Received", result["received"])
        c.metric("Packet loss", f'{result["loss_percent"]:.1f}%')
        st.json(result)
    else:
        st.info("Enter a target and click Run Ping Test.")

st.divider()
st.caption(f"Last sample: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if auto_refresh:
    time.sleep(refresh)
    st.rerun()

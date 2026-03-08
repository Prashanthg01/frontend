import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import warnings
import json
import time
import os

warnings.filterwarnings('ignore')

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Production Analytics Suite",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #333539; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #ffffff; }
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4;
                   text-align: center; margin-bottom: 0.5rem; }
    .sub-header  { font-size: 1.2rem; color: #666; text-align: center;
                   margin-bottom: 2rem; }
    .kpi-card    { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem;
                   border-left: 5px solid #1f77b4; }
    .kpi-value   { font-size: 2rem; font-weight: bold; color: #1f77b4; }
    .kpi-label   { font-size: 0.9rem; color: #666; margin-top: 0.5rem; }
    .metric-card        { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                          padding:20px; border-radius:15px;
                          box-shadow:0 4px 6px rgba(0,0,0,.3); margin-bottom:10px; }
    .metric-card-green  { background: linear-gradient(135deg,#11998e 0%,#38ef7d 100%); }
    .metric-card-orange { background: linear-gradient(135deg,#f093fb 0%,#f5576c 100%); }
    .metric-card-blue   { background: linear-gradient(135deg,#4facfe 0%,#00f2fe 100%); }
    .metric-title { color:white; font-size:14px; font-weight:500;
                    margin-bottom:8px; opacity:.9; }
    .metric-value { color:white; font-size:28px; font-weight:bold; margin-bottom:8px; }
    .section-header { color:#00ff9f; font-size:20px; font-weight:bold;
                      margin:20px 0 15px 0; padding-left:10px;
                      border-left:4px solid #00ff9f; }
    .progress-container { background:#2a4a3c; border-radius:10px;
                          padding:20px; margin:20px 0; }
    .task-status { padding:10px 20px; border-radius:8px; font-weight:bold;
                   text-align:center; margin:10px 0; }
    .status-processing { background:linear-gradient(135deg,#4facfe 0%,#00f2fe 100%);
                         color:white; }
    .status-success    { background:linear-gradient(135deg,#11998e 0%,#38ef7d 100%);
                         color:white; }
    .status-error      { background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);
                         color:white; }
    </style>
""", unsafe_allow_html=True)

# ── Session state initialisation ─────────────────────────────────────────────
_defaults = {
    'page':               'Production Analytics',
    'data':               None,
    'processed':          False,
    'filter_options':     None,
    'filters_loaded':     False,
    'async_task_id':      None,
    'task_status':        None,
    # Schedule Management
    'schedule_task_id':   None,
    'schedule_task_done': False,
    'gantt_data':         None,
    'kpi_data':           None,
    'batch_overrides':    [],
    'compare_current':    None,
    'compare_preview':    None,
    'tbl_page':           1,
    'tbl_loaded':         False,
    'timeline_data':      None,
    'init_data_task_id':  None,
    'init_data_task_done': True,
    'init_data_result':   None,
    # ── NEW: Batch Optimization ──────────────────────────────────────
    'batch_preview_result':  None,
    'batch_preview_task_id': None,
    'batch_save_result':     None,
    'batch_save_task_id':    None,
    # Auth
    'auth_token':         None,
    'username':           None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def get_auth_headers():
    """Return headers dict with token for authenticated API calls."""
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Token {token}"} if token else {}


def is_authenticated():
    return bool(st.session_state.get("auth_token"))


# ── Sidebar: API URL (and auth) ─────────────────────────────────────────────
API_BASE_URL = st.sidebar.text_input(
    "API Base URL",
    value="http://localhost:8000/api",
    help="Enter your Django API base URL",
    key="api_base_url_input",
)

if not is_authenticated():
    st.sidebar.info("👤 Sign in to use the app.")
    st.markdown("## 🔐 Sign in")
    st.markdown("Enter your credentials to access the Production Analytics Suite.")
    with st.form("login_form", clear_on_submit=False):
        login_user = st.text_input("Username", key="login_username")
        login_pass = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Sign in")
        if submitted:
            if login_user and login_pass:
                try:
                    r = requests.post(
                        f"{API_BASE_URL}/auth/login/",
                        json={"username": login_user, "password": login_pass},
                        timeout=10,
                    )
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state.auth_token = data["token"]
                        st.session_state.username = data["user"]["username"]
                        st.success("Welcome! Redirecting…")
                        st.rerun()
                    else:
                        err = r.json().get("error", "Login failed")
                        st.error(err)
                except Exception as e:
                    st.error(f"Connection error: {e}")
            else:
                st.warning("Enter username and password.")
    st.stop()

st.sidebar.success(f"Logged in as **{st.session_state.username}**")
if st.sidebar.button("Log out", key="logout_btn"):
    try:
        requests.post(
            f"{API_BASE_URL}/auth/logout/",
            headers=get_auth_headers(),
            timeout=5,
        )
    except Exception:
        pass
    st.session_state.auth_token = None
    st.session_state.username = None
    st.rerun()


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def fetch_data(endpoint, params=None):
    try:
        r = requests.get(
            f"{API_BASE_URL}/{endpoint}/",
            params=params,
            headers=get_auth_headers(),
            timeout=30,
        )
        if r.status_code == 401:
            st.session_state.auth_token = None
            st.session_state.username = None
            st.error("Session expired. Please log in again.")
            st.rerun()
        return r.json() if r.status_code == 200 else (st.error(f"Error {r.status_code}"), None)[1]
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def post_data(endpoint, data=None):
    try:
        r = requests.post(
            f"{API_BASE_URL}/{endpoint}/",
            json=data,
            headers=get_auth_headers(),
            timeout=60,
        )
        if r.status_code == 401:
            st.session_state.auth_token = None
            st.session_state.username = None
            st.error("Session expired. Please log in again.")
            st.rerun()
        if r.status_code in (200, 201, 202):
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def post_files(endpoint, files_dict, data_dict=None):
    try:
        r = requests.post(
            f"{API_BASE_URL}/{endpoint}/",
            files=files_dict,
            data=data_dict,
            headers=get_auth_headers(),
            timeout=120,
        )
        if r.status_code == 401:
            st.session_state.auth_token = None
            st.session_state.username = None
            st.error("Session expired. Please log in again.")
            st.rerun()
        if r.status_code in (200, 201, 202):
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def check_task_status(task_id):
    try:
        r = requests.get(
            f"{API_BASE_URL}/task-status/{task_id}/",
            headers=get_auth_headers(),
            timeout=10,
        )
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        st.error(f"Error checking task: {e}")
        return None


def poll_task_until_complete(task_id, progress_bar, status_text, max_wait_seconds=300):
    start = time.time()
    while time.time() - start < max_wait_seconds:
        data = check_task_status(task_id)
        if data:
            state    = data.get('state')
            progress = data.get('progress', 0)
            msg      = data.get('status', 'Processing...')
            progress_bar.progress(progress / 100.0)
            status_text.text(f"📊 {msg} ({progress}%)")
            if state == 'SUCCESS':
                return data.get('result')
            if state == 'FAILURE':
                st.error(f"❌ Task failed: {data.get('error', 'Unknown error')}")
                return None
        time.sleep(2)
    st.warning("⏱️ Task taking longer than expected. Check back later.")
    return None


def display_async_progress(task_id, operation_name="Operation"):
    st.markdown(f"""
        <div class="progress-container">
            <h4>⏳ {operation_name} in Progress</h4>
            <p>Task ID: <code>{task_id}</code></p>
        </div>""", unsafe_allow_html=True)
    pb  = st.progress(0)
    txt = st.empty()
    result = poll_task_until_complete(task_id, pb, txt)
    if result:
        st.success(f"✅ {operation_name} completed successfully!")
    return result


# ===========================================================================
# GANTT HELPER
# ===========================================================================

_PALETTE = px.colors.qualitative.Plotly + px.colors.qualitative.D3


def _product_color(color_key: int) -> str:
    return _PALETTE[color_key % len(_PALETTE)]


def _to_naive_utc(dt: datetime) -> datetime:
    """Strip timezone info, converting to UTC first if tz-aware."""
    if dt.tzinfo is not None:
        dt = dt.utctimetuple()
        dt = datetime(*dt[:6])
    return dt


def _parse_iso(s: str) -> datetime:
    """Parse ISO string and return naive UTC datetime."""
    dt = datetime.fromisoformat(s)
    return _to_naive_utc(dt)


def _compute_gaps_from_bars(bars: list) -> dict:
    from collections import defaultdict as _dd
    machine_ops = _dd(list)
    for b in bars:
        machine_ops[b['machine']].append(b)

    gap_list, machine_stats = [], []
    causes = {'precedence': 0, 'interleave': 0, 'spt': 0}

    for machine, mops in machine_ops.items():
        mops_s = sorted(mops, key=lambda o: _parse_iso(o['start']))
        idle_hours, gap_count = 0.0, 0

        for i in range(1, len(mops_s)):
            prev = mops_s[i - 1]
            curr = mops_s[i]
            gap_secs = (_parse_iso(curr['start']) - _parse_iso(prev['end'])).total_seconds()

            if gap_secs > 60:
                idle_h = gap_secs / 3600
                idle_hours += idle_h
                gap_count  += 1

                if str(curr.get('product','')) != str(prev.get('product','')):
                    cause = 'interleave'; causes['interleave'] += 1
                elif curr.get('step', 1) > 1:
                    cause = 'precedence'; causes['precedence'] += 1
                else:
                    cause = 'spt'; causes['spt'] += 1

                gap_list.append({
                    'machine':    machine,
                    'gap_start':  prev['end'],
                    'gap_end':    curr['start'],
                    'idle_hours': round(idle_h, 3),
                    'cause':      cause,
                    'before_op':  f"P{prev.get('product')} Step {prev.get('step')}",
                    'after_op':   f"P{curr.get('product')} Step {curr.get('step')}",
                })

        machine_stats.append({'machine': machine,
                               'idle_hours': round(idle_hours, 3),
                               'gap_count': gap_count})

    worst = max(machine_stats, key=lambda r: r['idle_hours'])['machine'] if machine_stats else '—'
    clean = sum(1 for r in machine_stats if r['gap_count'] == 0)
    return {
        'total_gaps':       len(gap_list),
        'total_idle_hours': round(sum(g['idle_hours'] for g in gap_list), 2),
        'worst_machine':    worst,
        'clean_machines':   clean,
        'machine_stats':    machine_stats,
        'gap_list':         gap_list,
        'causes':           causes,
    }


def build_gantt_figure(gantt_data: dict, height: int = 600) -> go.Figure:
    bars     = gantt_data.get('gantt_bars', [])
    machines = gantt_data.get('machines', [])

    if not bars:
        fig = go.Figure()
        fig.update_layout(title="No schedule data available",
                          template='plotly_dark', height=height)
        return fig

    fig           = go.Figure()
    seen_products = set()
    _epoch        = datetime(1970, 1, 1)

    for bar in bars:
        product  = bar['product']
        color    = _product_color(bar['color_key'])
        start_dt = _parse_iso(bar['start'])
        end_dt   = _parse_iso(bar['end'])
        dur_h    = bar['duration_h']

        show_legend = product not in seen_products
        seen_products.add(product)

        hover = (
            f"<b>Product:</b> {product}<br>"
            f"<b>Machine:</b> {bar['machine']}<br>"
            f"<b>Batch:</b> {bar['batch_id']} (#{bar['batch_num']})<br>"
            f"<b>Step:</b> {bar['step']} – {bar['step_name']}<br>"
            f"<b>Start:</b> {start_dt.strftime('%Y-%m-%d %H:%M')}<br>"
            f"<b>End:</b>   {end_dt.strftime('%Y-%m-%d %H:%M')}<br>"
            f"<b>Duration:</b> {dur_h:.2f} h"
        )

        fig.add_trace(go.Bar(
            name          = str(product),
            x             = [dur_h],
            y             = [bar['machine']],
            orientation   = 'h',
            base          = [(start_dt - _epoch).total_seconds() / 3600],
            marker_color  = color,
            opacity       = 0.85,
            hovertemplate = hover + "<extra></extra>",
            showlegend    = show_legend,
            legendgroup   = str(product),
        ))

    dr      = gantt_data.get('date_range', {})
    x_start = _parse_iso(dr['start']) if dr.get('start') else None
    x_end   = _parse_iso(dr['end'])   if dr.get('end')   else None
    x0_hrs  = (x_start - _epoch).total_seconds() / 3600 if x_start else 0
    x1_hrs  = (x_end   - _epoch).total_seconds() / 3600 if x_end   else x0_hrs + 24

    span_days = (x1_hrs - x0_hrs) / 24
    tick_step = 24 if span_days <= 7 else (7 * 24 if span_days <= 30 else 14 * 24)
    tick_vals = list(range(int(x0_hrs), int(x1_hrs) + 1, tick_step))
    tick_text = [
        (_epoch + pd.Timedelta(hours=h)).strftime('%b %d') for h in tick_vals
    ]

    fig.update_layout(
        template  = 'plotly_dark',
        height    = max(height, 60 * len(machines) + 150),
        barmode   = 'overlay',
        title     = "Production Schedule – Gantt Chart",
        xaxis     = dict(title='Date', tickvals=tick_vals, ticktext=tick_text,
                         range=[x0_hrs, x1_hrs], showgrid=True, gridcolor='#444'),
        yaxis     = dict(title='Machine', autorange='reversed',
                         showgrid=True, gridcolor='#333'),
        legend    = dict(title='Product', orientation='v', x=1.01, y=1),
        margin    = dict(l=160, r=160, t=60, b=60),
    )
    return fig


# ===========================================================================
# SCHEDULE PROGRESS WIDGET
# ===========================================================================

def _render_task_progress(task_id: str, api_url: str):
    placeholder  = st.empty()
    progress_bar = st.progress(0)
    status_text  = st.empty()

    for _ in range(150):
        try:
            resp = requests.get(f"{api_url}/task-status/{task_id}/", headers=get_auth_headers(), timeout=10)
            if not resp.ok:
                status_text.warning("Could not reach task status endpoint.")
                break

            d     = resp.json()
            state = d.get('state', 'PENDING')
            pct   = d.get('progress', 0)
            msg   = d.get('status', 'Processing…')

            progress_bar.progress(min(pct / 100.0, 1.0))
            status_text.markdown(f"**{msg}** ({pct}%)")

            if state == 'SUCCESS':
                result = d.get('result', {})
                kpis   = result.get('kpis', {})
                placeholder.markdown(f"""
                <div style='background:#1a3a2a;border-left:4px solid #10b981;
                            padding:14px 18px;border-radius:6px;'>
                <b style='color:#10b981'>✅ Schedule Generated Successfully!</b><br>
                <span style='color:#ccc'>
                Operations saved: <b>{result.get('total_operations', '—'):,}</b><br>
                Makespan: <b>{kpis.get('makespan_hours','—')} h</b> &nbsp;/&nbsp;
                <b>{kpis.get('makespan_days','—')} days</b><br>
                Bottleneck: <b>{kpis.get('bottleneck_machine','—')}</b>
                ({kpis.get('bottleneck_util','—')}% utilisation)
                </span></div>
                """, unsafe_allow_html=True)
                st.session_state.kpi_data           = kpis
                st.session_state.schedule_task_done = True
                break

            elif state == 'FAILURE':
                placeholder.error(f"❌ Task failed: {d.get('error','Unknown error')}")
                st.session_state.schedule_task_done = True
                break

        except Exception as e:
            status_text.warning(f"Polling error: {e}")
            break

        time.sleep(2)

    progress_bar.empty()
    status_text.empty()


# ===========================================================================
# NAVIGATION
# ===========================================================================

st.sidebar.title("🏭 Production Suite")
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Production Analytics",
        "📅 Schedule Management",
        "📦 Batch Optimization",
        "📋 Filter Data",
        "📊 Buffer Optimization",
        "🔍 Bottleneck Analysis",
    ],
    key="navigation"
)
st.sidebar.markdown("---")


# ===========================================================================
# PAGE 1 – Production Analytics
# ===========================================================================

if page == "📊 Production Analytics":
    st.title("📊 Production Analytics Dashboard")

    with st.sidebar:
        st.header("⚙️ Configuration")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
            if not st.session_state.filters_loaded:
                with st.spinner("Loading filter options..."):
                    uploaded_file.seek(0)
                    try:
                        r = requests.post(f"{API_BASE_URL}/csv-filter-options/",
                                          files={"file": uploaded_file},
                                          headers=get_auth_headers())
                        if r.status_code == 200:
                            st.session_state.filter_options = r.json()
                            st.session_state.filters_loaded = True
                    except Exception as e:
                        st.error(f"Error loading filters: {e}")

        num_shifts = st.number_input("Number of shifts", min_value=1,
                                     max_value=200, value=28,
                                     help="Total number of shifts to analyse")

        if st.session_state.filters_loaded and st.session_state.filter_options:
            st.markdown("---")
            st.subheader("🔍 Data Filters")
            st.markdown("*Filter data by specific criteria*")
            fo = st.session_state.filter_options
            selected_pps_tn      = st.selectbox("PPS TN",      ["All"] + fo.get('PPS TN', []))
            selected_project     = st.selectbox("Project",     ["All"] + fo.get('Project', []))
            selected_sub_project = st.selectbox("Sub-Project", ["All"] + fo.get('Sub-Project', []))
            selected_machine     = st.selectbox("Machine",     ["All"] + fo.get('Machine', []))
            selected_tool_no     = st.selectbox("Tool No.",    ["All"] + fo.get('Tool No.', []))
            selected_area        = st.selectbox("Area",        ["All"] + fo.get('Area', []))
        else:
            selected_pps_tn = selected_project = selected_sub_project = "All"
            selected_machine = selected_tool_no = selected_area = "All"

    if st.sidebar.button("🚀 Process & Analyze", type="primary", use_container_width=True):
        if uploaded_file:
            with st.spinner("🔄 Processing data..."):
                uploaded_file.seek(0)
                try:
                    r = requests.post(
                        f"{API_BASE_URL}/process-csv/",
                        data={
                            "num_shifts":   num_shifts,
                            "pps_tn":       selected_pps_tn,
                            "project":      selected_project,
                            "sub_project":  selected_sub_project,
                            "machine":      selected_machine,
                            "tool_no":      selected_tool_no,
                            "area":         selected_area,
                        },
                        files={"file": uploaded_file},
                        headers=get_auth_headers(),
                    )
                    if r.status_code == 200:
                        st.session_state.data      = r.json()
                        st.session_state.processed = True
                        st.sidebar.success("✅ Analysis complete!")
                        active = [
                            f"{label}: {val}"
                            for label, val in [
                                ("PPS TN", selected_pps_tn),
                                ("Project", selected_project),
                                ("Sub-Project", selected_sub_project),
                                ("Machine", selected_machine),
                                ("Tool No.", selected_tool_no),
                                ("Area", selected_area),
                            ]
                            if val != "All"
                        ]
                        if active:
                            st.sidebar.info("**Active Filters:**\n" +
                                            "\n".join(f"- {f}" for f in active))
                    else:
                        st.error(f"❌ Error: {r.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
        else:
            st.warning("⚠️ Please upload a file first.")

    if st.session_state.processed and st.session_state.data:
        data        = st.session_state.data
        shift_data  = data["ShiftWise"]
        summary_data = data["Summary"]
        df_shift    = pd.DataFrame(shift_data).T
        df_summary  = pd.DataFrame(summary_data)

        with st.sidebar:
            st.markdown("---")
            st.subheader("📊 Display Options")
            metrics          = list(shift_data.keys())
            selected_metrics = st.multiselect("Select Metrics to Display",
                                              metrics, default=metrics)
            all_shifts  = list(shift_data[metrics[0]].keys())
            shift_range = st.select_slider("Select Shift Range",
                                           options=all_shifts,
                                           value=(all_shifts[0], all_shifts[-1]))
            chart_type  = st.selectbox("Primary Chart Type",
                                       ["Line Chart", "Bar Chart", "Area Chart", "Combined"])

        start_idx      = all_shifts.index(shift_range[0])
        end_idx        = all_shifts.index(shift_range[1]) + 1
        filtered_shifts = all_shifts[start_idx:end_idx]

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Production Charts", "⚡ Efficiency Analysis",
            "📋 Data Tables", "📥 Downloads"
        ])

        with tab1:
            st.subheader("Production Output Analysis")
            sm        = df_summary['Metric'].tolist()
            fg_str    = df_summary['Finished Goods'].tolist()
            conn_str  = df_summary['Connectors'].tolist()
            fg_vals   = [float(v.replace(',','')) for v in fg_str]
            conn_vals = [float(v.replace(',','')) for v in conn_str]

            st.markdown('<div class="section-header">🎯 Finished Goods</div>',
                        unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            for col, cls, icon, idx in [
                (c1, "metric-card-blue",   "📋", 0),
                (c2, "metric-card-green",  "✅", 1),
                (c3, "metric-card-orange", "⏳", 2),
                (c4, "metric-card",        "📂", 3),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card {cls}">
                        <div class="metric-title">{icon} {sm[idx]}</div>
                        <div class="metric-value">{fg_str[idx]}</div>
                    </div>""", unsafe_allow_html=True)

            if fg_vals[0] > 0:
                pct = fg_vals[1] / fg_vals[0] * 100
                st.markdown("**Production Progress**")
                st.progress(min(pct / 100, 1.0))
                st.markdown(
                    f"<p style='text-align:center;color:#00ff9f;font-weight:bold;'>"
                    f"{pct:.1f}% Complete ({fg_str[1]} / {fg_str[0]})</p>",
                    unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="section-header">🔌 Connectors</div>',
                        unsafe_allow_html=True)
            c5, c6, c7, c8 = st.columns(4)
            for col, cls, icon, idx in [
                (c5, "metric-card-blue",   "📋", 0),
                (c6, "metric-card-green",  "✅", 1),
                (c7, "metric-card-orange", "⏳", 2),
                (c8, "metric-card",        "📂", 3),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card {cls}">
                        <div class="metric-title">{icon} {sm[idx]}</div>
                        <div class="metric-value">{conn_str[idx]}</div>
                    </div>""", unsafe_allow_html=True)

            if conn_vals[0] > 0:
                pct = conn_vals[1] / conn_vals[0] * 100
                st.markdown("**Production Progress**")
                st.progress(min(pct / 100, 1.0))
                st.markdown(
                    f"<p style='text-align:center;color:#ff6b9d;font-weight:bold;'>"
                    f"{pct:.1f}% Complete ({conn_str[1]} / {conn_str[0]})</p>",
                    unsafe_allow_html=True)

            st.markdown("---")

            fg_v     = [float(shift_data['Production Output Finished Goods'][s].replace(',','')) for s in filtered_shifts]
            conn_v   = [float(shift_data['Production Output Connectors'][s].replace(',',''))     for s in filtered_shifts]
            backlog_v= [float(shift_data['Total Backlog Finished Goods'][s].replace(',',''))     for s in filtered_shifts]

            if chart_type == "Line Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_v, name='Finished Goods',
                                             mode='lines+markers', line=dict(color='#00ff9f', width=3)))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_v, name='Connectors',
                                             mode='lines+markers', line=dict(color='#ff6b9d', width=3)))
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_v, name='Backlog',
                                             mode='lines+markers', line=dict(color='#ffa500', width=3)))

            elif chart_type == "Bar Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=fg_v,
                                         name='Finished Goods', marker_color='#00ff9f'))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=conn_v,
                                         name='Connectors', marker_color='#ff6b9d'))
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=backlog_v,
                                         name='Backlog', marker_color='#ffa500'))
                fig.update_layout(barmode='group')

            elif chart_type == "Area Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_v, name='Finished Goods',
                                             fill='tozeroy', line=dict(color='#00ff9f')))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_v, name='Connectors',
                                             fill='tozeroy', line=dict(color='#ff6b9d')))

            else:  # Combined
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=fg_v,
                                         name='Finished Goods', marker_color='#00ff9f'),
                                  secondary_y=False)
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=conn_v,
                                         name='Connectors', marker_color='#ff6b9d'),
                                  secondary_y=False)
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_v, name='Backlog',
                                             mode='lines+markers',
                                             line=dict(color='#ffa500', width=3)),
                                  secondary_y=True)

            fig.update_layout(template='plotly_dark', height=500,
                              xaxis_title="Shifts", yaxis_title="Quantity",
                              hovermode='x unified',
                              legend=dict(orientation="h", yanchor="bottom",
                                          y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)

            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown("#### 🎯 Production by Category")
                pie = go.Figure(data=[go.Pie(
                    labels=['Finished Goods', 'Connectors'],
                    values=[sum(fg_v), sum(conn_v)],
                    hole=0.4, marker_colors=['#00ff9f','#ff6b9d']
                )])
                pie.update_layout(template='plotly_dark', height=350)
                st.plotly_chart(pie, use_container_width=True)
            with ch2:
                st.markdown("#### 📊 Cumulative Production")
                cum_fig = go.Figure()
                cum_fig.add_trace(go.Scatter(
                    x=filtered_shifts,
                    y=[sum(fg_v[:i+1]) for i in range(len(fg_v))],
                    name='Finished Goods', fill='tozeroy', line=dict(color='#00ff9f')))
                cum_fig.add_trace(go.Scatter(
                    x=filtered_shifts,
                    y=[sum(conn_v[:i+1]) for i in range(len(conn_v))],
                    name='Connectors', fill='tozeroy', line=dict(color='#ff6b9d')))
                cum_fig.update_layout(template='plotly_dark', height=350)
                st.plotly_chart(cum_fig, use_container_width=True)

        with tab2:
            st.subheader("⚡ Overall Efficiency Analysis")
            eff_vals   = []
            eff_labels = []
            for s in filtered_shifts:
                v = shift_data['Overall Efficiency'][s]
                if v != '-':
                    eff_vals.append(float(v.replace('%','')))
                    eff_labels.append(s)

            eff_fig = go.Figure()
            eff_fig.add_trace(go.Scatter(
                x=eff_labels, y=eff_vals, mode='lines+markers',
                name='Efficiency %',
                line=dict(color='#00d4ff', width=4),
                marker=dict(size=10, symbol='diamond'),
                fill='tozeroy', fillcolor='rgba(0,212,255,0.2)'
            ))
            eff_fig.add_hline(y=100, line_dash="dash", line_color="green",
                              annotation_text="Target: 100%")
            eff_fig.update_layout(template='plotly_dark', height=400,
                                   xaxis_title="Shifts", yaxis_title="Efficiency %",
                                   hovermode='x unified')
            st.plotly_chart(eff_fig, use_container_width=True)

            if eff_vals:
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Average Efficiency", f"{sum(eff_vals)/len(eff_vals):.2f}%")
                e2.metric("Maximum Efficiency", f"{max(eff_vals):.2f}%")
                e3.metric("Minimum Efficiency", f"{min(eff_vals):.2f}%")
                e4.metric("Shifts ≥100%",
                           f"{sum(1 for e in eff_vals if e>=100)}/{len(eff_vals)}")

            st.markdown("#### 📊 Efficiency Distribution")
            hist = go.Figure(data=[go.Histogram(x=eff_vals, nbinsx=10,
                                                 marker_color='#00d4ff', opacity=0.75)])
            hist.update_layout(template='plotly_dark', height=300,
                                xaxis_title="Efficiency %", yaxis_title="Frequency")
            st.plotly_chart(hist, use_container_width=True)

        with tab3:
            st.subheader("📋 Detailed Data Tables")
            filtered_df = df_shift[filtered_shifts].copy()
            if selected_metrics:
                avail = [m for m in selected_metrics if m in filtered_df.index]
                if avail:
                    filtered_df = filtered_df.loc[avail]
            st.dataframe(filtered_df, use_container_width=True, height=400)

        with tab4:
            st.subheader("📥 Download Options")
            d1, d2 = st.columns(2)
            with d1:
                st.markdown("#### Full Shift-wise Data")
                st.download_button("📥 Download Full Dataset (CSV)",
                                   data=df_shift.to_csv(index=True),
                                   file_name="shiftwise_production_data.csv",
                                   mime="text/csv", use_container_width=True)
            with d2:
                st.markdown("#### Summary Report")
                st.download_button("📥 Download Summary (CSV)",
                                   data=df_summary.to_csv(index=False),
                                   file_name="production_summary.csv",
                                   mime="text/csv", use_container_width=True)
            st.markdown("---")
            st.markdown("#### Filtered Data")
            st.download_button("📥 Download Filtered Data (CSV)",
                               data=filtered_df.to_csv(index=True),
                               file_name="filtered_production_data.csv",
                               mime="text/csv", use_container_width=True)
    else:
        st.markdown("""
        ### 👋 Welcome to Production Analytics Dashboard
        Upload your CSV file and configure the analysis parameters in the sidebar to get started.

        **Features:**
        - 📊 Production output tracking for Finished Goods and Connectors
        - ⚡ Efficiency analysis across shifts
        - 🔍 Advanced filtering by multiple criteria
        - 📈 Interactive charts and visualizations
        - 📥 Export capabilities for reports
        """)


# ===========================================================================
# PAGE 2 – Schedule Management
# ===========================================================================

elif page == "📅 Schedule Management":
    st.title("📅 Schedule Management")

    tab_gen, tab_gantt, tab_timeline, tab_table, tab_kpi, tab_compare, tab_optimize = st.tabs([
        "⚙️ Generate Schedule",
        "📊 Gantt Chart",
        "🕐 Timeline View",
        "📋 Schedule Table",
        "📈 KPIs",
        "🔄 Comparison",
        "🎯 Gap Optimizer",
    ])

    # ── TAB 1 – Generate ──────────────────────────────────────────────
    with tab_gen:
        st.subheader("⚙️ Generate Production Schedule")
        st.markdown("""
        <div style='background:#1a2a3a;border-left:4px solid #4facfe;
                    padding:14px 18px;border-radius:6px;margin-bottom:18px;'>
        <b style='color:#4facfe'>ℹ️ How it works</b><br>
        <span style='color:#ccc'>
        The scheduler uses a <b>Hybrid Heuristic + PuLP MILP</b> approach:<br>
        &nbsp; 1. <b>Phase 1</b> — Greedy SPT dispatcher builds a full feasible
                schedule in seconds.<br>
        &nbsp; 2. <b>Phase 2</b> — PuLP re-optimises the most loaded bottleneck
                machines to minimise makespan. Runs async via Celery.
        </span></div>""", unsafe_allow_html=True)

        # ── Data source toggle ────────────────────────────────────────────────
        st.markdown("### 📥 Initialize Data")

        data_source = st.radio(
            "Select data source",
            ["📂 Real CSV files", "🧪 Synthetic Dataset"],
            horizontal=True,
            key="schedule_data_source_radio",
            help=(
                "Real CSV — upload your Frontpage.csv and Process.csv as usual.\n\n"
                "Synthetic — generate realistic test data automatically (no files needed). "
                "All results are reproducible via the seed parameter."
            ),
        )

        # =====================================================================
        # BRANCH A — Real CSV (original UI, completely unchanged)
        # =====================================================================

        if data_source == "📂 Real CSV files":

            st.caption("Upload Frontpage and Process CSV files to refresh products, machines, and routing data.")

            init_c1, init_c2 = st.columns(2)
            with init_c1:
                frontpage_file = st.file_uploader(
                    "Frontpage CSV",
                    type=["csv"],
                    key="schedule_frontpage_csv",
                )
            with init_c2:
                process_file = st.file_uploader(
                    "Process CSV",
                    type=["csv"],
                    key="schedule_process_csv",
                )

            init_async_mode = st.checkbox(
                "Run initialization in background",
                value=True,
                key="schedule_init_async_mode",
            )
            init_clicked = st.button(
                "Initialize Data",
                use_container_width=True,
                key="schedule_initialize_data_btn",
            )

            if init_clicked:
                if not frontpage_file or not process_file:
                    st.warning("Please upload both Frontpage CSV and Process CSV files.")
                else:
                    with st.spinner("Uploading files and initializing data..."):
                        try:
                            frontpage_file.seek(0)
                            process_file.seek(0)
                            r = requests.post(
                                f"{API_BASE_URL}/initialize-data/",
                                files={
                                    "frontpage": (frontpage_file.name, frontpage_file, "text/csv"),
                                    "process":   (process_file.name,  process_file,  "text/csv"),
                                },
                                data={"async_mode": str(init_async_mode).lower()},
                                headers=get_auth_headers(),
                                timeout=120,
                            )
                            if r.status_code == 401:
                                st.session_state.auth_token = None
                                st.session_state.username   = None
                                st.error("Session expired. Please log in again.")
                                st.rerun()

                            if r.status_code in (200, 201, 202):
                                payload = r.json()
                                if r.status_code == 202 and payload.get("task_id"):
                                    st.session_state.init_data_task_id   = payload["task_id"]
                                    st.session_state.init_data_task_done = False
                                    st.session_state.init_data_result    = None
                                    st.success(f"Initialization started. Task ID: `{payload['task_id']}`")
                                else:
                                    st.session_state.init_data_task_id   = None
                                    st.session_state.init_data_task_done = True
                                    st.session_state.init_data_result    = payload
                                    st.success(payload.get("message", "Database initialized successfully."))
                            else:
                                st.error(f"Error {r.status_code}: {r.text}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

        # =====================================================================
        # BRANCH B — Synthetic dataset
        # =====================================================================

        else:  # "🧪 Synthetic Dataset"

            st.markdown("""
            <div style='background:#0d200d;border-left:3px solid #38ef7d;
                        padding:8px 14px;border-radius:4px;font-size:12px;
                        color:#86efac;margin-bottom:14px;'>
            🧪 <b>Synthetic Mode</b> — generates a realistic in-memory dataset and loads it
            directly into the database. No file upload needed.
            All algorithms (scheduler, batch ILP, buffer LP, gap analysis) work identically
            on synthetic and real data because both produce the same DB schema.
            </div>
            """, unsafe_allow_html=True)

            # ── Parameter controls ────────────────────────────────────────────

            syn_c1, syn_c2, syn_c3 = st.columns(3)

            with syn_c1:
                syn_num_products = st.number_input(
                    "Number of products",
                    min_value=1, max_value=200, value=10,
                    help="How many synthetic products to generate (1–200)",
                    key="syn_num_products",
                )
                syn_seed = st.number_input(
                    "Random seed",
                    min_value=0, max_value=999_999, value=42,
                    help="Fix the seed for reproducible results. Same seed → identical dataset.",
                    key="syn_seed",
                )

            with syn_c2:
                syn_num_machines = st.number_input(
                    "Number of machines",
                    min_value=2, max_value=15, value=2,
                    help="Machines to include in the synthetic dataset (2–15).",
                    key="syn_num_machines",
                )
                syn_demand_min = st.number_input(
                    "Min annual demand",
                    min_value=1, max_value=1_000_000, value=500,
                    key="syn_demand_min",
                )

            with syn_c3:
                syn_steps = st.number_input(
                    "Steps per product",
                    min_value=0, max_value=15, value=0,
                    help="Routing depth per product (0 = random 3-8)",
                    key="syn_steps_per_product",
                )
                syn_demand_max = st.number_input(
                    "Max annual demand",
                    min_value=1, max_value=10_000_000, value=50_000,
                    key="syn_demand_max",
                )

            syn_async = st.checkbox(
                "Run initialization in background (Celery)",
                value=True,
                key="syn_async_mode",
            )
            syn_clear = st.checkbox(
                "Clear existing data before loading",
                value=True,
                key="syn_clear_existing",
            )

            # ── Reproducibility notice ────────────────────────────────────────

            st.markdown(
                f"<div style='background:#111;border:1px solid #222;border-radius:4px;"
                f"padding:6px 12px;font-size:11px;color:#9ca3af;margin:4px 0 8px 0;'>"
                f"🔑 <b>Reproducibility key:</b> "
                f"seed=<b>{syn_seed}</b>, products=<b>{syn_num_products}</b>, "
                f"machines=<b>{'auto' if syn_num_machines == 0 else syn_num_machines}</b>, "
                f"steps=<b>{'random 3-8' if syn_steps == 0 else syn_steps}</b>, "
                f"demand=[<b>{syn_demand_min:,}</b>–<b>{syn_demand_max:,}</b>]"
                f"</div>",
                unsafe_allow_html=True,
            )

            syn_init_clicked = st.button(
                "🧪 Generate & Load Synthetic Dataset",
                type="primary",
                use_container_width=True,
                key="syn_initialize_btn",
            )

            if syn_init_clicked:
                if syn_demand_min >= syn_demand_max:
                    st.error("Min demand must be less than Max demand.")
                else:
                    payload = {
                        "num_products":   int(syn_num_products),
                        "seed":           int(syn_seed),
                        "demand_min":     int(syn_demand_min),
                        "demand_max":     int(syn_demand_max),
                        "clear_existing": str(syn_clear).lower(),
                        "async_mode":     str(syn_async).lower(),
                    }
                    if syn_num_machines > 0:
                        payload["num_machines"] = int(syn_num_machines)
                    if syn_steps > 0:
                        payload["steps_per_product"] = int(syn_steps)

                    with st.spinner("Generating synthetic dataset…"):
                        try:
                            r = requests.post(
                                f"{API_BASE_URL}/initialize-synthetic/",
                                json=payload,
                                headers=get_auth_headers(),
                                timeout=120,
                            )
                            if r.status_code == 401:
                                st.session_state.auth_token = None
                                st.session_state.username   = None
                                st.error("Session expired. Please log in again.")
                                st.rerun()

                            if r.status_code in (200, 201, 202):
                                resp = r.json()

                                if r.status_code == 202 and resp.get("task_id"):
                                    # Async: hand off to the existing progress poller
                                    st.session_state.init_data_task_id   = resp["task_id"]
                                    st.session_state.init_data_task_done = False
                                    st.session_state.init_data_result    = None
                                    meta = resp.get("metadata", {})
                                    st.success(
                                        f"Synthetic generation started — "
                                        f"Task ID: `{resp['task_id']}`"
                                    )
                                    if meta:
                                        st.json(meta)
                                else:
                                    # Sync result
                                    st.session_state.init_data_task_id   = None
                                    st.session_state.init_data_task_done = True
                                    st.session_state.init_data_result    = resp
                                    st.success(resp.get("message", "Synthetic data loaded."))
                            else:
                                st.error(f"Error {r.status_code}: {r.text}")

                        except Exception as e:
                            st.error(f"Connection error: {e}")

        # ── Shared progress poller (works for both real and synthetic async tasks) ──

        init_task_id = st.session_state.get("init_data_task_id")
        if init_task_id and not st.session_state.get("init_data_task_done", True):
            st.markdown("#### ⏳ Data Initialization Progress")
            init_pb  = st.progress(0)
            init_txt = st.empty()
            init_result = poll_task_until_complete(
                init_task_id, init_pb, init_txt, max_wait_seconds=600,
            )
            if init_result:
                st.session_state.init_data_result    = init_result
                st.session_state.init_data_task_done = True

        # ── Display result metrics (same for real and synthetic) ──────────────

        init_result = st.session_state.get("init_data_result")
        if isinstance(init_result, dict):
            badge_color = "#38ef7d" if init_result.get("dataset_type") == "synthetic" else "#4facfe"
            badge_label = "🧪 Synthetic" if init_result.get("dataset_type") == "synthetic" else "📂 Real CSV"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Products",      init_result.get("products_created", "—"))
            m2.metric("Machines",      init_result.get("machines_created", "—"))
            m3.metric("Process Steps", init_result.get("process_steps_created", "—"))
            m4.markdown(
                f"<div style='padding:10px 0;'>"
                f"<span style='background:{badge_color};color:#000;padding:4px 10px;"
                f"border-radius:10px;font-size:11px;font-weight:700;'>{badge_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if init_result.get("message"):
                st.success(init_result["message"])

            # Show reproducibility metadata for synthetic runs
            meta = init_result.get("metadata", {})
            if meta and meta.get("dataset_type") == "synthetic":
                with st.expander("🔬 Dataset Metadata (reproducibility record)", expanded=False):
                    st.json(meta)

        st.markdown("---")

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            start_date = st.date_input("📅 Schedule Start Date", value=date.today(),
                                        help="All operations are anchored from this date.")
        with g2:
            local_opt = st.slider("🔧 Bottleneck Machines to Re-optimise",
                                   min_value=0, max_value=15, value=5,
                                   help="Higher = better quality, slower solve.")
        with g3:
            clear_existing = st.checkbox("🗑️ Clear existing schedule before saving",
                                          value=True)
        with g4:
            enable_compaction = st.checkbox(
                "🔀 Enable Gap Elimination",
                value=True,
                help=(
                    "Runs Left-Shift Compaction after greedy dispatch. "
                    "Slides every operation as early as possible (respecting "
                    "precedence + no overlap) to eliminate idle gaps. "
                    "Recommended: ✅ ON"
                )
            )

        if enable_compaction:
            st.markdown(
                "<div style='background:#0d2a0d;border-left:3px solid #22c55e;"
                "padding:8px 14px;border-radius:4px;font-size:12px;color:#86efac;'>"
                "✅ <b>Gap Elimination ON</b> — Left-Shift Compaction will run after "
                "greedy dispatch, sliding every operation left to fill idle gaps "
                "without breaking precedence constraints."
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='background:#2a1a0d;border-left:3px solid #f59e0b;"
                "padding:8px 14px;border-radius:4px;font-size:12px;color:#fcd34d;'>"
                "⚠️ <b>Gap Elimination OFF</b> — Greedy-only schedule will have idle "
                "gaps. Enable this for continuous machine utilisation."
                "</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        with st.expander("🔬 Advanced Options — Per-product batch override"):
            st.markdown("Leave empty to use batch sizes already stored in the database.")
            try:
                pr = requests.get(f"{API_BASE_URL}/get-filter-options/", headers=get_auth_headers(), timeout=10)
                products_list = pr.json().get('products', []) if pr.ok else []
            except Exception:
                products_list = []

            if products_list:
                ov_prod = st.selectbox(
                    "Select product to override",
                    ["— none —"] + [f"{p['item']} – {p['description'][:40]}"
                                    for p in products_list]
                )
                if ov_prod != "— none —":
                    ov1, ov2 = st.columns(2)
                    ov_bs = ov1.number_input("Batch size",   min_value=1, value=100)
                    ov_nb = ov2.number_input("Num batches",  min_value=1, value=12)
                    if st.button("➕ Add Override"):
                        item_no = int(ov_prod.split(" – ")[0])
                        pk = next((p['item'] for p in products_list
                                   if p['item'] == item_no), None)
                        if pk:
                            st.session_state.batch_overrides.append([pk, ov_bs, ov_nb])
                            st.success(f"Override added for product {item_no}.")

            if st.session_state.batch_overrides:
                st.markdown(f"**Active overrides:** {len(st.session_state.batch_overrides)}")
                if st.button("🗑 Clear all overrides"):
                    st.session_state.batch_overrides = []

        st.markdown("---")
        btn1, btn2 = st.columns([2, 1])

        with btn1:
            gen_clicked = st.button("🚀 Generate Schedule (Async)",
                                     type="primary", use_container_width=True)
        with btn2:
            try:
                ex = requests.get(f"{API_BASE_URL}/get-schedule/?page_size=1", headers=get_auth_headers(), timeout=5)
                if ex.ok and ex.json().get('count', 0) > 0:
                    st.metric("Current schedule ops", ex.json()['count'])
            except Exception:
                pass

        if gen_clicked:
            payload = {
                'start_date':         start_date.isoformat(),
                'local_opt_machines': local_opt,
                'clear_existing':     clear_existing,
                'enable_compaction':  enable_compaction,
                'batch_overrides':    st.session_state.batch_overrides,
                'async_mode':         True,
            }
            with st.spinner("Submitting job to Celery…"):
                try:
                    r = requests.post(f"{API_BASE_URL}/generate-schedule/",
                                      json=payload, headers=get_auth_headers(), timeout=30)
                    if r.status_code in (200, 201, 202):
                        task_id = r.json().get('task_id')
                        if task_id:
                            st.session_state.schedule_task_id   = task_id
                            st.session_state.schedule_task_done = False
                            st.success(f"✅ Task submitted — ID: `{task_id}`")
                        else:
                            st.success("Schedule generated (sync).")
                    else:
                        st.error(f"Error {r.status_code}: {r.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        task_id = st.session_state.get('schedule_task_id')
        if task_id and not st.session_state.get('schedule_task_done', False):
            st.markdown("---")
            st.markdown("### ⏳ Schedule Generation Progress")
            _render_task_progress(task_id, API_BASE_URL)

    # ── TAB 2 – Gantt ─────────────────────────────────────────────────
    with tab_gantt:
        st.subheader("📊 Gantt Chart")

        gc1, gc2, gc3 = st.columns([2, 1, 1])
        with gc1:
            try:
                mr = requests.get(f"{API_BASE_URL}/get-filter-options/", headers=get_auth_headers(), timeout=10)
                all_machines = mr.json().get('machines', []) if mr.ok else []
            except Exception:
                all_machines = []
            sel_machines = st.multiselect("Filter Machines", options=all_machines,
                                           default=[], placeholder="All machines")
        with gc2:
            max_bars = st.number_input("Max bars to render",
                                        min_value=50, max_value=2000, value=500, step=50)
        with gc3:
            chart_h = st.number_input("Chart height (px)",
                                       min_value=400, max_value=2000, value=700, step=50)

        if st.button("🔄 Load / Refresh Gantt", type="primary"):
            params = {'max_bars': max_bars}
            if sel_machines:
                params['machines'] = ','.join(sel_machines)
            with st.spinner("Fetching Gantt data…"):
                try:
                    r = requests.get(f"{API_BASE_URL}/schedule-gantt/",
                                     params=params, headers=get_auth_headers(), timeout=30)
                    if r.ok:
                        st.session_state.gantt_data = r.json()
                    else:
                        st.error(f"Error {r.status_code}: {r.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        gd = st.session_state.get('gantt_data')
        if gd:
            total = gd.get('total_bars', 0)
            shown = len(gd.get('gantt_bars', []))
            if gd.get('truncated'):
                st.warning(f"⚠️ Showing {shown:,} of {total:,} operations. "
                           "Filter by machine to see more detail.")

            dr = gd.get('date_range', {})
            if dr.get('start') and dr.get('end'):
                d0 = _parse_iso(dr['start'])
                d1 = _parse_iso(dr['end'])
                m1, m2, m3 = st.columns(3)
                m1.metric("Makespan", f"{(d1-d0).total_seconds()/3600:.1f} h")
                m2.metric("Machines", len(gd.get('machines', [])))
                m3.metric("Operations shown", f"{shown:,}")

            st.plotly_chart(build_gantt_figure(gd, height=chart_h),
                            use_container_width=True)

            st.markdown("#### 🏭 Machine Load Summary")
            bars_df = pd.DataFrame(gd['gantt_bars'])
            if not bars_df.empty:
                load_df = (bars_df.groupby('machine')['duration_h'].sum()
                           .reindex(gd.get('machines', [])).reset_index()
                           .rename(columns={'duration_h': 'Total Load (h)'}))
                lf = px.bar(load_df, x='machine', y='Total Load (h)',
                             color='Total Load (h)', color_continuous_scale='Blues',
                             title="Total Machine Load (hours)", template='plotly_dark')
                lf.update_layout(height=350, showlegend=False)
                st.plotly_chart(lf, use_container_width=True)
        else:
            st.info("Click **Load / Refresh Gantt** to fetch schedule data.")

    # ── TAB 3 – Timeline View ──────────────────────────────────────────
    with tab_timeline:
        st.subheader("🕐 Timeline View")
        st.markdown("Visual step-by-step schedule per machine — mirrors the Production Schedule Dashboard layout.")

        tl1, tl2, tl3, tl4 = st.columns([2, 1, 1, 1])
        with tl1:
            try:
                mr2 = requests.get(f"{API_BASE_URL}/get-filter-options/", headers=get_auth_headers(), timeout=10)
                tl_machines = mr2.json().get('machines', []) if mr2.ok else []
            except Exception:
                tl_machines = []
            sel_tl_machines = st.multiselect(
                "Select Machine(s)", options=tl_machines,
                default=tl_machines[:6] if tl_machines else [],
                placeholder="Pick machines to display"
            )
        with tl2:
            tl_time_start = st.text_input("Time range start (HH:MM)", value="08:00")
        with tl3:
            tl_time_end   = st.text_input("Time range end  (HH:MM)", value="20:00")
        with tl4:
            time_interval_minutes = st.selectbox(
                "⏱️ Time interval",
                options=[1, 5, 15, 30, 60, 120],
                index=1,
                format_func=lambda x: f"{x} min",
                help="Timeline tick interval (default 5 min).",
            )
            tl_opt_goal = st.radio("Optimisation Goal",
                                   ["Minimize Makespan", "Maximize Throughput"],
                                   index=0)

        if st.button("🔄 Load Timeline", type="primary"):
            params = {'max_bars': 2000, 'page_size': 2000, 'format': 'gantt'}
            if sel_tl_machines:
                params['machines'] = ','.join(sel_tl_machines)
            with st.spinner("Loading timeline data…"):
                loaded = False
                try:
                    r = requests.get(f"{API_BASE_URL}/schedule-gantt/",
                                     params=params, headers=get_auth_headers(), timeout=30)
                    if r.ok:
                        st.session_state.timeline_data = r.json()
                        loaded = True
                except Exception:
                    pass

                if not loaded:
                    try:
                        r2 = requests.get(f"{API_BASE_URL}/get-schedule/",
                                          params={'page_size': 2000, 'format': 'gantt'},
                                          headers=get_auth_headers(), timeout=30)
                        if r2.ok:
                            raw   = r2.json()
                            rows  = raw.get('results', [])
                            prods = sorted(set(row['product'] for row in rows))
                            cmap  = {p: i for i, p in enumerate(prods)}
                            for row in rows:
                                row['color_key'] = cmap.get(row['product'], 0)
                                row['batch_num'] = row.get('batch_num', 1)
                                row['batch_id']  = row.get('batch_id', '')
                            starts = [row['start'] for row in rows if row.get('start')]
                            ends   = [row['end']   for row in rows if row.get('end')]
                            st.session_state.timeline_data = {
                                'gantt_bars':  rows,
                                'machines':    [r2.get('machine','') for r2 in rows],
                                'date_range':  {
                                    'start': min(starts) if starts else None,
                                    'end':   max(ends)   if ends   else None,
                                },
                                'total_bars': len(rows),
                                'truncated':  False,
                            }
                            seen_m = set()
                            machine_list = []
                            for row in rows:
                                m = row.get('machine', '')
                                if m and m not in seen_m:
                                    seen_m.add(m)
                                    machine_list.append(m)
                            st.session_state.timeline_data['machines'] = machine_list
                            loaded = True
                        else:
                            st.error(f"Error {r2.status_code}: {r2.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        td = st.session_state.get('timeline_data') or st.session_state.get('gantt_data')

        if td and td.get('gantt_bars'):
            bars_all  = td['gantt_bars']
            machines  = sel_tl_machines if sel_tl_machines else td.get('machines', [])
            bars_all = [b for b in bars_all if not sel_tl_machines or b['machine'] in sel_tl_machines]

            if not bars_all:
                st.info("No operations found for selected machines.")
            else:
                all_starts = [_parse_iso(b['start']) for b in bars_all]
                all_ends   = [_parse_iso(b['end'])   for b in bars_all]
                t_min      = min(all_starts)
                t_max      = max(all_ends)
                span_hrs   = max((t_max - t_min).total_seconds() / 3600, 1)

                try:
                    h_start = int(tl_time_start.split(':')[0])
                    h_end   = int(tl_time_end.split(':')[0])
                except Exception:
                    h_start, h_end = 8, 20

                products_uniq = sorted(set(b['product'] for b in bars_all))
                clr = ['#4facfe','#00f2fe','#11998e','#38ef7d','#f093fb',
                       '#f5576c','#fda085','#f6d365','#a18cd1','#fbc2eb',
                       '#84fab0','#8fd3f4','#ff9a9e','#fecfef','#667eea',
                       '#764ba2','#ff6b6b','#feca57','#48dbfb','#ff9ff3']
                prod_color = {p: clr[i % len(clr)] for i, p in enumerate(products_uniq)}

                machine_bars = {m: [] for m in machines}
                for b in bars_all:
                    if b['machine'] in machine_bars:
                        machine_bars[b['machine']].append(b)

                total_ops   = len(bars_all)
                total_dur   = sum(b['duration_h'] for b in bars_all)
                kpi_data_tl = st.session_state.get('kpi_data') or {}
                makespan_h  = kpi_data_tl.get('total_makespan_hours', round(span_hrs, 1))
                util_rows   = kpi_data_tl.get('machine_utilization', []) or []
                n_setups    = len(set(b['batch_id'] for b in bars_all))
                throughput  = kpi_data_tl.get('throughput_units_per_day', 0) or 0

                LABEL_W    = 140
                ROW_H      = 44
                TRACK_PAD  = 4
                BAR_H      = ROW_H - TRACK_PAD * 2
                TICK_SPACING_PX = 40
                n_ticks = int(span_hrs * 60 / time_interval_minutes) + 1
                n_ticks = min(max(n_ticks, 2), 500)
                CANVAS_W = (n_ticks - 1) * TICK_SPACING_PX
                CANVAS_W = max(CANVAS_W, 400)
                PX_PER_HR = CANVAS_W / span_hrs

                kpi_items = [
                    ("Total Makespan",   f"{makespan_h:.1f} h"),
                    ("Total Operations", f"{total_ops:,}"),
                    ("Batches / Setups", f"{n_setups:,}"),
                    ("Throughput",       f"{throughput:.0f} units/day"),
                    ("Opt. Goal",        tl_opt_goal.split()[1]),
                ]
                kpi_rows_html = "".join(f"""
                  <div class='kpi-row'>
                    <span class='kpi-lbl'>{lbl}</span>
                    <span class='kpi-val'>{val}</span>
                  </div>""" for lbl, val in kpi_items)

                util_bars_html = ""
                for m in machines:
                    util_pct  = next((u['utilization'] for u in util_rows
                                      if u['machine'] == m), 0)
                    bar_color = ('#ef4444' if util_pct >= 85 else
                                 '#f59e0b' if util_pct >= 70 else '#10b981')
                    safe_m = m.replace("'", "&#39;").replace('"', '&quot;')
                    util_bars_html += f"""
                  <div class='util-item'>
                    <div class='util-name' title='{safe_m}'>{safe_m}</div>
                    <div class='util-track'>
                      <div class='util-fill' style='width:{min(util_pct,100):.1f}%;
                           background:{bar_color};'></div>
                    </div>
                    <div class='util-pct'>{util_pct:.1f}%</div>
                  </div>"""

                tick_items = []
                for i in range(n_ticks):
                    tick_hrs = i * (time_interval_minutes / 60)
                    tick_dt  = t_min + timedelta(hours=tick_hrs)
                    tick_lbl = tick_dt.strftime('%H:%M' if span_hrs <= 48 else '%b %d')
                    tick_px  = i * TICK_SPACING_PX
                    tick_items.append((tick_px, tick_lbl))

                tick_header_html = "".join(
                    f"<div style='position:absolute;left:{px:.1f}px;"
                    f"transform:translateX(-50%);color:#9ca3af;font-size:11px;"
                    f"white-space:nowrap;top:4px;'>{lbl}</div>"
                    for px, lbl in tick_items
                )
                grid_lines_html = "".join(
                    f"<div style='position:absolute;left:{px:.1f}px;top:0;bottom:0;"
                    f"width:1px;background:rgba(255,255,255,0.06);'></div>"
                    for px, _ in tick_items
                )

                rows_html = ""
                for ri, machine in enumerate(machines):
                    mbars    = machine_bars.get(machine, [])
                    safe_m   = machine.replace("'", "&#39;").replace('"', '&quot;')
                    row_bg   = '#111a11' if ri % 2 == 0 else '#0e1a0e'
                    bar_blocks = grid_lines_html

                    if not mbars:
                        bar_blocks += (f"<div style='position:absolute;left:50%;top:50%;"
                                       f"transform:translate(-50%,-50%);color:#374151;"
                                       f"font-size:13px;'>— no operations —</div>")
                    else:
                        for b in sorted(mbars, key=lambda x: x['start']):
                            bs_dt  = _parse_iso(b['start'])
                            be_dt  = _parse_iso(b['end'])
                            offset = (bs_dt - t_min).total_seconds() / 3600
                            dur_b  = b['duration_h']
                            left_px  = max(0.0, offset * PX_PER_HR)
                            width_px = max(4.0, dur_b * PX_PER_HR)
                            color    = prod_color.get(b['product'], '#4facfe')
                            step_no  = b['step']
                            step_nm  = b.get('step_name', '')
                            batch_id = b.get('batch_id', '')
                            tip = (f"Step {step_no}: {step_nm} | "
                                   f"Product {b['product']} | Batch {batch_id} | "
                                   f"{bs_dt.strftime('%H:%M')} – "
                                   f"{be_dt.strftime('%H:%M')} ({dur_b:.2f} h)"
                                   ).replace("'", "&#39;")
                            opacity  = 1.0 if b.get('batch_num', 1) % 2 == 1 else 0.75
                            inner_label = (f"<div class='bar-step'>Step {step_no}</div>"
                                           f"<div class='bar-name'>{step_nm[:18]}</div>"
                                           if width_px > 60 else
                                           f"<div class='bar-step'>{step_no}</div>")
                            bar_blocks += f"""
                            <div class='bar' title='{tip}'
                                 style='left:{left_px:.1f}px;width:{width_px:.1f}px;
                                        background:{color};opacity:{opacity};
                                        top:{TRACK_PAD}px;height:{BAR_H}px;'>
                              {inner_label}
                            </div>"""

                    rows_html += f"""
                    <div class='gantt-row' style='background:{row_bg};'>
                      <div class='row-label' title='{safe_m}'>{safe_m}</div>
                      <div class='row-track' style='width:{CANVAS_W}px;height:{ROW_H}px;
                                                    position:relative;'>
                        {bar_blocks}
                      </div>
                    </div>"""

                legend_html = "".join(
                    f"<div class='legend-item'>"
                    f"<div class='legend-dot' style='background:{col};'></div>"
                    f"<span>Product {prod}</span></div>"
                    for prod, col in list(prod_color.items())[:20]
                )

                def _step_in_slot(mbars, slot_idx, total_slots):
                    slot_s = slot_idx * (span_hrs / total_slots)
                    slot_e = (slot_idx + 1) * (span_hrs / total_slots)
                    steps  = sorted(set(
                        f"Step {b['step']}" for b in mbars
                        if slot_s <= (_parse_iso(b['start']) - t_min
                                      ).total_seconds() / 3600 < slot_e
                    ))
                    return "<br>".join(steps) if steps else "—"

                n_slots   = min(len(tick_items) - 1, 6)
                hdr_cells = "".join(
                    f"<th>{tick_items[i][1]}</th>" for i in range(n_slots)
                )
                table_rows_html = ""
                for ri, machine in enumerate(machines):
                    mbars    = machine_bars.get(machine, [])
                    row_cls  = 'tr-even' if ri % 2 == 0 else 'tr-odd'
                    cells    = "".join(
                        f"<td>{_step_in_slot(mbars, i, n_slots)}</td>"
                        for i in range(n_slots)
                    )
                    table_rows_html += (
                        f"<tr class='{row_cls}'>"
                        f"<td class='td-machine'>{machine}</td>{cells}</tr>"
                    )

                gantt_scroll_h = min(420, max(180, len(machines) * ROW_H + 24))
                total_iframe_h = gantt_scroll_h + len(machines) * 40 + 380

                full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  background:#0e1117;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  color:#e5e7eb;
  padding:8px 10px;
  font-size:12px;
}}
.page-title  {{ font-size:16px;font-weight:700;color:#fff;margin-bottom:1px; }}
.page-sub    {{ font-size:11px;color:#6b7280;margin-bottom:10px; }}
.outer       {{ display:flex;gap:10px;align-items:flex-start; }}
.left-panel  {{ flex:1;min-width:0; }}
.kpi-panel   {{
  width:200px;min-width:200px;flex-shrink:0;
  background:#0d1f0d;border:1px solid #1a3a1a;
  border-radius:6px;padding:10px 12px;
}}
.kpi-title   {{ color:#00ff9f;font-size:12px;font-weight:700;
               margin-bottom:8px;letter-spacing:.3px; }}
.kpi-row     {{ display:flex;justify-content:space-between;align-items:center;
               padding:5px 0;border-bottom:1px solid #1a2a1a; }}
.kpi-lbl     {{ color:#9ca3af;font-size:11px; }}
.kpi-val     {{ color:#fff;font-weight:700;font-size:12px; }}
.sec-title   {{ color:#00ff9f;font-size:10px;font-weight:700;
               text-transform:uppercase;letter-spacing:.8px;
               margin:10px 0 6px 0; }}
.util-item   {{ margin:5px 0; }}
.util-name   {{ color:#d1d5db;font-size:10px;margin-bottom:2px;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }}
.util-track  {{ background:#1f2f1f;border-radius:3px;height:6px;
               overflow:hidden; }}
.util-fill   {{ height:6px;border-radius:3px;transition:width .3s; }}
.util-pct    {{ color:#6b7280;font-size:9px;text-align:right;margin-top:1px; }}
.gantt-wrap  {{
  border:1px solid #1f2f1f;border-radius:6px;overflow:hidden;
}}
.gantt-header {{
  display:flex;background:#0a140a;border-bottom:1px solid #1a3a1a;
  position:sticky;top:0;z-index:10;
}}
.header-label {{
  width:{LABEL_W}px;min-width:{LABEL_W}px;flex-shrink:0;
  padding:4px 8px;font-size:10px;color:#6b7280;font-weight:600;
  text-transform:uppercase;letter-spacing:.5px;
  border-right:1px solid #1a3a1a;
}}
.header-ticks {{
  flex:1;overflow:hidden;
}}
.header-ticks-inner {{
  position:relative;height:22px;
  width:{CANVAS_W}px;
}}
.gantt-scroll {{
  overflow:auto;
  max-height:{gantt_scroll_h}px;
}}
.gantt-row {{
  display:flex;align-items:stretch;
  border-bottom:1px solid #1a2a1a;
  transition:background .15s;
}}
.gantt-row:hover {{ filter:brightness(1.12); }}
.row-label {{
  width:{LABEL_W}px;min-width:{LABEL_W}px;flex-shrink:0;
  padding:0 6px 0 8px;font-size:11px;font-weight:600;color:#d1d5db;
  display:flex;align-items:center;
  border-right:1px solid #1a3a1a;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  cursor:default;
}}
.row-track {{ flex:1;overflow:visible;position:relative; }}
.bar {{
  position:absolute;border-radius:4px;
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;overflow:hidden;cursor:default;
  border:1px solid rgba(255,255,255,0.18);
  transition:filter .15s;
  padding:0 3px;
}}
.bar:hover {{ filter:brightness(1.25);z-index:5; }}
.bar-step {{ font-size:9px;font-weight:700;color:#fff;
  text-shadow:0 1px 2px rgba(0,0,0,.9);
  white-space:nowrap;line-height:1.1; }}
.bar-name {{ font-size:8px;color:rgba(255,255,255,.8);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  max-width:100%;line-height:1.1; }}
.legend      {{ display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;
               padding-top:8px;border-top:1px solid #1a2a1a; }}
.legend-item {{ display:flex;align-items:center;gap:4px;font-size:10px;
               color:#9ca3af; }}
.legend-dot  {{ width:10px;height:10px;border-radius:2px;flex-shrink:0; }}
.tab-section {{ margin-top:12px; }}
.tab-title   {{ color:#00ff9f;font-size:11px;font-weight:700;
               text-transform:uppercase;letter-spacing:.8px;
               margin-bottom:6px; }}
.tab-scroll  {{ overflow-x:auto;border:1px solid #1a2a1a;border-radius:6px; }}
table        {{ border-collapse:collapse;min-width:500px; }}
th           {{
  padding:5px 10px;background:#0a1a2a;color:#4facfe;
  font-size:10px;font-weight:600;border:1px solid #1e3a4a;
  white-space:nowrap;text-align:left;position:sticky;top:0;
}}
td           {{
  padding:4px 10px;border:1px solid #1a2a1a;
  font-size:10px;color:#d1d5db;vertical-align:top;
  line-height:1.4;
}}
.td-machine  {{
  font-weight:600;color:#9ca3af;white-space:nowrap;
  background:#0d1a0d;position:sticky;left:0;
  border-right:1px solid #1a3a1a;
}}
.tr-even td  {{ background:#0d1a0d; }}
.tr-odd  td  {{ background:#0a140a; }}
.tr-even .td-machine, .tr-odd .td-machine {{ background:#0a180a; }}
tr:hover td  {{ background:#111e11 !important; }}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  var scroll = document.getElementById('gantt-scroll');
  var hticks = document.getElementById('header-ticks');
  if (scroll && hticks) {{
    scroll.addEventListener('scroll', function() {{
      hticks.scrollLeft = scroll.scrollLeft;
    }});
  }}
}});
</script>
</head>
<body>
<div class='page-title'>Production Schedule Dashboard</div>
<div class='page-sub'>Optimized Machine Time Allocation</div>
<div class='outer'>
  <div class='left-panel'>
    <div class='gantt-wrap'>
      <div class='gantt-header'>
        <div class='header-label'>Machine</div>
        <div class='header-ticks' id='header-ticks' style='overflow:hidden;'>
          <div class='header-ticks-inner'>
            {tick_header_html}
          </div>
        </div>
      </div>
      <div class='gantt-scroll' id='gantt-scroll'>
        {rows_html}
      </div>
    </div>
    <div class='legend'>
      {legend_html}
    </div>
    <div class='tab-section'>
      <div class='tab-title'>📋 Tabular View</div>
      <div class='tab-scroll'>
        <table>
          <thead>
            <tr>
              <th style='position:sticky;left:0;z-index:2;
                         background:#0a1a2a;border-right:1px solid #1e3a4a;'>Machine</th>
              {hdr_cells}
            </tr>
          </thead>
          <tbody>
            {table_rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <div class='kpi-panel'>
    <div class='kpi-title'>📊 KPIs</div>
    {kpi_rows_html}
    <div class='sec-title'>Machine Util.</div>
    {util_bars_html}
  </div>
</div>
</body>
</html>"""

                components.html(full_html, height=total_iframe_h, scrolling=False)

        else:
            st.info("Generate a schedule first, then click **Load Timeline**.")

    # ── TAB 4 – Schedule Table ─────────────────────────────────────────
    with tab_table:
        st.subheader("📋 Schedule Table")

        tf1, tf2, tf3 = st.columns([2, 2, 1])
        with tf1:
            tbl_machine = st.text_input("Filter by machine (partial match)", value="")
        with tf2:
            tbl_product = st.text_input("Filter by product item number", value="")
        with tf3:
            tbl_ps = st.selectbox("Rows per page", [100, 200, 500, 1000], index=1)

        if st.button("🔄 Load Table", type="primary"):
            st.session_state.tbl_page   = 1
            st.session_state.tbl_loaded = True

        if st.session_state.get('tbl_loaded', False):
            params = {'page': st.session_state.tbl_page, 'page_size': tbl_ps}
            if tbl_machine: params['machine'] = tbl_machine
            if tbl_product: params['product'] = tbl_product

            try:
                r = requests.get(f"{API_BASE_URL}/get-schedule/",
                                  params=params, headers=get_auth_headers(), timeout=30)
                if r.ok:
                    d         = r.json()
                    results   = d.get('results', [])
                    total_cnt = d.get('count', 0)
                    total_pg  = d.get('total_pages', 1)

                    st.markdown(f"**{total_cnt:,} operations** — "
                                f"Page {st.session_state.tbl_page} of {total_pg}")

                    if results:
                        df_t = pd.DataFrame(results)
                        df_t['start']      = pd.to_datetime(df_t['start'], format='ISO8601', utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M')
                        df_t['end']        = pd.to_datetime(df_t['end'],   format='ISO8601', utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M')
                        df_t['duration_h'] = df_t['duration_h'].round(2)
                        st.dataframe(df_t, use_container_width=True, height=500)

                        pc1, _, pc3 = st.columns([1, 2, 1])
                        with pc1:
                            if st.button("◀ Prev") and st.session_state.tbl_page > 1:
                                st.session_state.tbl_page -= 1
                                st.rerun()
                        with pc3:
                            if st.button("Next ▶") and st.session_state.tbl_page < total_pg:
                                st.session_state.tbl_page += 1
                                st.rerun()

                        st.download_button("📥 Download this page (CSV)",
                                           data=pd.DataFrame(results).to_csv(index=False),
                                           file_name=f"schedule_p{st.session_state.tbl_page}.csv",
                                           mime="text/csv")
                    else:
                        st.info("No records match the current filter.")
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    # ── TAB 5 – KPIs ──────────────────────────────────────────────────
    with tab_kpi:
        st.subheader("📈 Schedule KPIs")

        if st.button("🔄 Refresh KPIs", type="primary"):
            try:
                r = requests.get(f"{API_BASE_URL}/kpis/", headers=get_auth_headers(), timeout=30)
                if r.ok:
                    st.session_state.kpi_data = r.json()
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

        kpi = st.session_state.get('kpi_data')
        if kpi:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Makespan",   f"{kpi.get('total_makespan_hours',0):.1f} h")
            k2.metric("Makespan (days)",  f"{kpi.get('total_makespan_days',0):.1f} d")
            k3.metric("Total Operations", f"{kpi.get('total_operations',0):,}")
            k4.metric("Units Scheduled",  f"{kpi.get('total_units_scheduled',0):,}")

            st.markdown("---")
            k5, k6 = st.columns(2)
            k5.metric("Throughput / day",  f"{kpi.get('throughput_units_per_day',0):.1f} units")
            k6.metric("Throughput / hour", f"{kpi.get('throughput_units_per_hour',0):.2f} units")

            bn = kpi.get('bottleneck')
            if bn:
                st.markdown(f"""
                <div style='background:#3a1a1a;border-left:4px solid #ef4444;
                            padding:14px 18px;border-radius:6px;margin:18px 0;'>
                <b style='color:#ef4444'>🚨 Bottleneck Machine</b><br>
                <span style='color:#fff;font-size:1.2rem'><b>{bn['machine']}</b></span>
                &nbsp;&nbsp;
                <span style='color:#fca5a5'>{bn['utilization']:.1f}% utilisation
                ({bn['used_hours']:.1f} h)</span>
                </div>""", unsafe_allow_html=True)

            util_rows = kpi.get('machine_utilization', [])
            if util_rows:
                st.markdown("#### 🏭 Machine Utilisation")
                df_util   = pd.DataFrame(util_rows)
                col_vals  = df_util['utilization'].tolist()
                util_fig  = go.Figure(go.Bar(
                    x=df_util['utilization'], y=df_util['machine'],
                    orientation='h',
                    marker=dict(
                        color=col_vals,
                        colorscale=[[0.0,'#10b981'],[0.6,'#f59e0b'],
                                    [0.85,'#ef4444'],[1.0,'#7f1d1d']],
                        cmin=0, cmax=100,
                        colorbar=dict(title='%'),
                    ),
                    text=[f"{v:.1f}%" for v in col_vals],
                    textposition='auto',
                ))
                util_fig.add_vline(x=85, line_dash='dash', line_color='red',
                                    annotation_text='Critical 85%',
                                    annotation_position='top right')
                util_fig.add_vline(x=70, line_dash='dot', line_color='orange',
                                    annotation_text='Watch 70%',
                                    annotation_position='top right')
                util_fig.update_layout(
                    template='plotly_dark',
                    height=max(400, 30 * len(util_rows) + 100),
                    xaxis_title="Utilisation (%)",
                    yaxis=dict(autorange='reversed'),
                    margin=dict(l=180),
                )
                st.plotly_chart(util_fig, use_container_width=True)

                st.markdown("#### 📊 Utilisation Distribution")
                hf = px.histogram(df_util, x='utilization', nbins=15,
                                   color_discrete_sequence=['#4facfe'],
                                   template='plotly_dark',
                                   title="Machine Utilisation Distribution",
                                   labels={'utilization': 'Utilisation (%)'})
                hf.update_layout(height=300)
                st.plotly_chart(hf, use_container_width=True)

                st.download_button("📥 Download KPI Data (CSV)",
                                   data=df_util.to_csv(index=False),
                                   file_name="schedule_kpis.csv", mime="text/csv")
        else:
            st.info("Click **Refresh KPIs** to load schedule performance metrics.")

    # ── TAB 6 – Comparison ────────────────────────────────────────────
    with tab_compare:
        st.subheader("🔄 Schedule Comparison")
        st.markdown(
            "Compare the current saved schedule's KPIs against a re-generated preview "
            "(no DB write) to evaluate different optimisation settings."
        )

        cmp1, cmp2 = st.columns(2)
        with cmp1:
            prev_opt = st.slider("Preview: bottleneck machines to optimise",
                                  0, 15, 5)
        with cmp2:
            if st.button("▶️ Run Comparison", type="primary"):
                with st.spinner("Fetching comparison data…"):
                    try:
                        cr = requests.get(f"{API_BASE_URL}/schedule-comparison/", headers=get_auth_headers(), timeout=30)
                        pr = requests.get(f"{API_BASE_URL}/optimize-schedule-preview/",
                                          params={'local_opt_machines': prev_opt},
                                          headers=get_auth_headers(), timeout=120)
                        if cr.ok and pr.ok:
                            st.session_state.compare_current = cr.json().get('current_schedule', {})
                            st.session_state.compare_preview = pr.json().get('preview_kpis', {})
                        else:
                            st.error("Error fetching comparison data.")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        cur  = st.session_state.get('compare_current')
        prev = st.session_state.get('compare_preview')

        if cur and prev:
            st.markdown("---")
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("#### 📌 Current Schedule")
                st.metric("Makespan",        f"{cur.get('makespan_hours',0):.1f} h")
                st.metric("Operations",      f"{cur.get('total_operations',0):,}")
                st.metric("Avg Utilisation", f"{cur.get('avg_utilization',0):.1f}%")
            with cc2:
                st.markdown("#### 🔮 Preview (not saved)")
                cur_mk  = cur.get('makespan_hours', 0)
                prev_mk = prev.get('makespan_hours', 0)
                st.metric("Makespan", f"{prev_mk:.1f} h",
                           delta=f"{prev_mk - cur_mk:+.1f} h", delta_color="inverse")
                st.metric("Operations", f"{prev.get('total_operations',0):,}")
                st.metric("Bottleneck", f"{prev.get('bottleneck_machine','—')}")

            cur_stats  = cur.get('machine_stats', [])
            prev_utils = prev.get('utilisation', {})
            if cur_stats and prev_utils:
                df_cur  = pd.DataFrame(cur_stats).rename(
                    columns={'utilization':'Current %','machine':'Machine'})
                df_prev = pd.DataFrame([{'Machine':m,'Preview %':v}
                                         for m,v in prev_utils.items()])
                df_cmp  = (pd.merge(df_cur[['Machine','Current %']],
                                     df_prev, on='Machine', how='outer')
                             .fillna(0)
                             .sort_values('Current %', ascending=False))
                cf = go.Figure()
                cf.add_trace(go.Bar(name='Current',  x=df_cmp['Machine'],
                                    y=df_cmp['Current %'],  marker_color='#4facfe'))
                cf.add_trace(go.Bar(name='Preview',  x=df_cmp['Machine'],
                                    y=df_cmp['Preview %'],  marker_color='#00f2fe'))
                cf.update_layout(barmode='group', template='plotly_dark',
                                  title='Machine Utilisation: Current vs Preview',
                                  xaxis_title='Machine', yaxis_title='Utilisation (%)',
                                  height=400)
                st.plotly_chart(cf, use_container_width=True)

    # ── TAB 7 – Gap Optimizer ─────────────────────────────────────────
    with tab_optimize:
        st.subheader("🎯 Gap Analysis & Elimination")

        with st.expander("📖 Why do gaps appear? (click to learn)", expanded=False):
            st.markdown("""
**Three root causes create the idle gaps you see on machines like Cutting Automation and SKM Seal:**

**① Precedence-induced starvation** — A machine finishes its current job and is free,
but the *next operation waiting for it* belongs to a batch whose upstream step (on a
different machine) has not finished yet.

**② Batch-interleaving gaps** — Different products share a machine. When Product A's
last batch finishes, Product B's next batch isn't ready yet.

**③ SPT ordering mismatches** — The greedy dispatcher sorts all operations by shortest
processing time globally, creating "arrival gaps".

**The fix — Left-Shift Compaction:** Enable **Gap Elimination** in the Generate tab.
            """)

        st.markdown("#### 📊 Load Schedule Data for Analysis")
        ga_src = st.radio(
            "Data source",
            ["Use already-loaded Gantt data (fast)",
             "Fetch fresh from API (up to 5000 ops)"],
            horizontal=True,
        )

        btn_analyze, btn_clear = st.columns([2, 1])
        with btn_analyze:
            do_analyze = st.button("🔍 Analyze Gaps Now",
                                   type="primary", use_container_width=True)
        with btn_clear:
            if st.button("🗑 Clear Results", use_container_width=True):
                st.session_state.gap_analysis = None
                st.rerun()

        if do_analyze:
            bars = []
            if "already-loaded" in ga_src:
                gd = st.session_state.get('gantt_data') or st.session_state.get('timeline_data')
                if gd:
                    bars = gd.get('gantt_bars', [])
                    if bars:
                        st.success(f"Using {len(bars):,} bars from loaded Gantt data.")
                    else:
                        st.warning("No gantt bars in loaded data.")
                else:
                    st.warning("No Gantt data loaded. Switch to Gantt Chart tab first.")
            else:
                with st.spinner("Fetching schedule from API…"):
                    try:
                        r2 = requests.get(f"{API_BASE_URL}/get-schedule/",
                                          params={'page_size': 5000}, headers=get_auth_headers(), timeout=30)
                        if r2.ok:
                            raw_rows = r2.json().get('results', [])
                            prods = sorted(set(row.get('product','') for row in raw_rows))
                            cmap  = {p: i for i, p in enumerate(prods)}
                            bars  = [{
                                'machine':   row.get('machine', ''),
                                'product':   row.get('product', ''),
                                'step':      row.get('step', 0),
                                'step_name': row.get('step_name', ''),
                                'batch_id':  row.get('batch_id', ''),
                                'batch_num': row.get('batch_num', 1),
                                'start':     row.get('start', ''),
                                'end':       row.get('end', ''),
                                'duration_h': row.get('duration_h', 0),
                                'color_key': cmap.get(row.get('product',''), 0),
                            } for row in raw_rows if row.get('start') and row.get('end')]
                            st.success(f"Fetched {len(bars):,} operations from API.")
                        else:
                            st.error(f"API error {r2.status_code}: {r2.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

            if bars:
                st.session_state.gap_analysis = _compute_gaps_from_bars(bars)
                st.session_state['_gap_bars']  = bars

        ga = st.session_state.get('gap_analysis')
        if not ga:
            st.markdown("""
            <div style='text-align:center;padding:50px 20px;color:#4b5563;'>
              <div style='font-size:52px;'>🔍</div>
              <div style='font-size:15px;font-weight:600;color:#6b7280;margin:10px 0;'>
                No gap analysis loaded yet
              </div>
              <div style='font-size:12px;'>
                Load Gantt data first, then click <b>Analyze Gaps Now</b>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("---")
            gm1, gm2, gm3, gm4 = st.columns(4)
            gm1.metric("Total Idle Gaps",  ga['total_gaps'])
            gm2.metric("Total Idle Time",  f"{ga['total_idle_hours']:.1f} h")
            gm3.metric("Worst Machine",    ga['worst_machine'])
            gm4.metric("Gap-Free Machines", ga['clean_machines'])

            causes = ga['causes']
            total_c = sum(causes.values()) or 1
            st.markdown("#### 🔬 Gap Cause Breakdown")
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("① Precedence-induced",
                       f"{causes['precedence']} gaps",
                       f"{causes['precedence']/total_c*100:.0f}% of gaps")
            cc2.metric("② Batch-interleaving",
                       f"{causes['interleave']} gaps",
                       f"{causes['interleave']/total_c*100:.0f}% of gaps")
            cc3.metric("③ SPT ordering",
                       f"{causes['spt']} gaps",
                       f"{causes['spt']/total_c*100:.0f}% of gaps")

            st.markdown("#### 📊 Idle Time by Machine")
            df_ms = pd.DataFrame(ga['machine_stats'])
            if not df_ms.empty:
                df_ms = df_ms.sort_values('idle_hours', ascending=False)
                bar_colors = [
                    '#ef4444' if v > 4 else '#f59e0b' if v > 1 else '#22c55e'
                    for v in df_ms['idle_hours']
                ]
                idle_fig = go.Figure()
                idle_fig.add_trace(go.Bar(
                    x=df_ms['machine'], y=df_ms['idle_hours'],
                    name='Idle Hours', marker_color=bar_colors,
                    text=[f"{v:.2f}h" for v in df_ms['idle_hours']],
                    textposition='auto',
                ))
                idle_fig.add_trace(go.Scatter(
                    x=df_ms['machine'], y=df_ms['gap_count'],
                    name='Gap Count', yaxis='y2',
                    mode='markers+lines',
                    marker=dict(color='#a78bfa', size=9, symbol='diamond'),
                    line=dict(color='#a78bfa', width=2, dash='dot'),
                ))
                idle_fig.update_layout(
                    template='plotly_dark', height=380,
                    title='Machine Idle Time and Gap Count',
                    xaxis_title='Machine',
                    yaxis=dict(title='Idle Hours'),
                    yaxis2=dict(title='Gap Count', overlaying='y', side='right'),
                    legend=dict(orientation='h', y=1.08),
                    margin=dict(b=120),
                )
                idle_fig.update_xaxes(tickangle=30)
                st.plotly_chart(idle_fig, use_container_width=True)

            with st.expander(f"📋 Full Gap List ({ga['total_gaps']} gaps)"):
                df_gl = pd.DataFrame(ga['gap_list'])
                if not df_gl.empty:
                    df_gl = df_gl.sort_values('idle_hours', ascending=False)
                    for col in ['gap_start', 'gap_end']:
                        df_gl[col] = (pd.to_datetime(df_gl[col], format='ISO8601', utc=True)
                                      .dt.tz_localize(None)
                                      .dt.strftime('%Y-%m-%d %H:%M'))
                    st.dataframe(
                        df_gl[['machine','gap_start','gap_end',
                               'idle_hours','cause','before_op','after_op']],
                        use_container_width=True, height=320
                    )
                    st.download_button(
                        "📥 Download Gap Report (CSV)",
                        data=df_gl.to_csv(index=False),
                        file_name="gap_analysis.csv", mime="text/csv",
                    )

            st.markdown("---")
            st.markdown("### 🔧 Fix These Gaps")
            fc1, fc2 = st.columns([3, 1])
            with fc1:
                fix_date = st.date_input("Start date for re-schedule",
                                          value=date.today(), key="gap_fix_date")
            with fc2:
                fix_opt = st.number_input("Bottleneck machines (MILP)",
                                           min_value=0, max_value=15, value=5,
                                           key="gap_fix_opt")

            if st.button("🚀 Re-Generate with Gap Elimination",
                         type="primary", use_container_width=True):
                payload = {
                    'start_date':         fix_date.isoformat(),
                    'local_opt_machines': fix_opt,
                    'clear_existing':     True,
                    'enable_compaction':  True,
                    'batch_overrides':    st.session_state.get('batch_overrides', []),
                    'async_mode':         True,
                }
                try:
                    r = requests.post(f"{API_BASE_URL}/generate-schedule/",
                                      json=payload, headers=get_auth_headers(), timeout=30)
                    if r.status_code in (200, 201, 202):
                        task_id = r.json().get('task_id')
                        if task_id:
                            st.session_state.schedule_task_id   = task_id
                            st.session_state.schedule_task_done = False
                            st.session_state.gap_analysis       = None
                            st.success(f"✅ Gap-elimination schedule submitted — Task `{task_id}`")
                            st.info("Switch to **⚙️ Generate Schedule** tab to watch progress.")
                    else:
                        st.error(f"Error {r.status_code}: {r.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")


# ===========================================================================
# PAGE 3 – Batch Optimization
# ===========================================================================

elif page == "📦 Batch Optimization":
    st.title("📦 Batch Size Optimization")

    # ── Info banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#1a2a3a;border-left:4px solid #4facfe;
                padding:14px 18px;border-radius:6px;margin-bottom:18px;'>
    <b style='color:#4facfe'>ℹ️ Two Optimization Modes</b><br>
    <span style='color:#ccc'>
    <b style='color:#00f2fe'>Individual ILP</b> — optimises each product independently,
    minimising the number of batches subject to size constraints.<br>
    <b style='color:#38ef7d'>Joint ILP (new)</b> — optimises ALL products simultaneously,
    minimising the <i>worst machine load</i> (makespan proxy) to balance utilisation
    across all machines and avoid bottlenecks.
    </span></div>
    """, unsafe_allow_html=True)

    # ── Adaptive bounds explanation (the bug fix) ──────────────────────────────
    with st.expander("⚠️ Why min/max batch size is applied adaptively (important)", expanded=False):
        st.markdown("""
**Problem with fixed global bounds:**

Your products span a very wide demand range — from **100 units** to **319,908 units**.
A fixed `min_batch=50, max_batch=500` causes two failure modes:

| Demand | Issue | What happened before fix |
|--------|-------|--------------------------|
| 121 | `max_batch=500 > demand=121` → ILP was forced to pick batch=500 for 1 batch, ignoring that only 121 units are needed | `new_batch_size=500, new_num_batches=1` ❌ |
| 319,908 | `ceil(319908/n) > 500` for **every** n ∈ [1..25] → ILP had no feasible solution at all | Fell back to naive heuristic ❌ |

**The fix — adaptive bounds per product:**
```
true_min = ceil(demand / max_num_batches)   # smallest batch using all slots
true_max = demand                            # one big batch (N=1)

effective_min = max(user_min, true_min)
effective_max = min(user_max, true_max)

if effective_min > effective_max:            # user bounds incompatible with demand
    use (true_min, true_max) instead
```
Your `min_batch_size` and `max_batch_size` parameters are now treated as **preferences**.
The ILP clamps them to what is actually achievable for each product's demand level.
        """)

    st.markdown("---")

    # ── Parameters ─────────────────────────────────────────────────────────────
    st.markdown("### ⚙️ Optimization Parameters")
    bp1, bp2, bp3, bp4 = st.columns(4)
    with bp1:
        max_num_batches = st.number_input(
            "Max number of batches", min_value=1, max_value=100, value=25,
            help="Upper bound for N in the ILP"
        )
    with bp2:
        min_batch_size = st.number_input(
            "Min batch size (preferred)", min_value=1, max_value=100000, value=50,
            help="Preferred minimum units per batch. Applied where feasible for the product's demand."
        )
    with bp3:
        max_batch_size = st.number_input(
            "Max batch size (preferred)", min_value=1, max_value=1000000, value=500,
            help="Preferred maximum units per batch. Clamped to demand when demand < this value."
        )
    with bp4:
        batch_async = st.checkbox(
            "Run async (Celery)", value=False,
            help="Use background task for large product catalogs"
        )

    params = {
        "max_num_batches": int(max_num_batches),
        "min_batch_size":  int(min_batch_size),
        "max_batch_size":  int(max_batch_size),
    }

    st.markdown("---")

    # ── Page tabs ──────────────────────────────────────────────────────────────
    tab_indiv, tab_joint = st.tabs([
        "🔢 Individual Optimization",
        "🤝 Joint Optimization (balance machine loads)",
    ])

    # ==========================================================================
    # TAB 1 — Individual ILP (existing, with adaptive bounds fix)
    # ==========================================================================
    with tab_indiv:
        st.markdown("""
        <div style='background:#0d1a2d;border-left:3px solid #4facfe;
                    padding:8px 14px;border-radius:4px;font-size:12px;
                    color:#93c5fd;margin-bottom:14px;'>
        Optimises each product independently. Objective: minimise number of batches N
        while keeping batch size within adaptive bounds. Fast — runs product-by-product.
        </div>
        """, unsafe_allow_html=True)

        ia1, ia2 = st.columns(2)
        with ia1:
            indiv_preview = st.button(
                "🔍 Preview (no DB write)",
                type="primary", use_container_width=True
            )
        with ia2:
            indiv_save = st.button(
                "💾 Save to Database",
                type="secondary", use_container_width=True
            )

        # ── Preview ───────────────────────────────────────────────────────────
        if indiv_preview:
            _params_async = {**params, "async_mode": "true" if batch_async else "false"}
            if batch_async:
                with st.spinner("Submitting preview task…"):
                    try:
                        r = requests.get(
                            f"{API_BASE_URL}/batch-optimization-preview/",
                            params=_params_async, headers=get_auth_headers(), timeout=30
                        )
                        if r.status_code == 202:
                            st.session_state.batch_preview_task_id = r.json().get("task_id")
                            st.session_state.batch_preview_result  = None
                            st.success(f"Task submitted: `{st.session_state.batch_preview_task_id}`")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
            else:
                with st.spinner("Running ILP for all products…"):
                    try:
                        r = requests.get(
                            f"{API_BASE_URL}/batch-optimization-preview/",
                            params=params, headers=get_auth_headers(), timeout=300
                        )
                        if r.status_code == 200:
                            st.session_state.batch_preview_result  = r.json()
                            st.session_state.batch_preview_task_id = None
                            st.success("✅ Preview complete!")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        btask = st.session_state.get("batch_preview_task_id")
        if btask:
            st.markdown("#### ⏳ Preview Task")
            pb  = st.progress(0)
            txt = st.empty()
            res = poll_task_until_complete(btask, pb, txt, max_wait_seconds=600)
            if res:
                st.session_state.batch_preview_result  = res
                st.session_state.batch_preview_task_id = None
                st.rerun()

        # ── Save ──────────────────────────────────────────────────────────────
        if indiv_save:
            if batch_async:
                with st.spinner("Submitting save task…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/batch-optimization-save/",
                            json={**params, "async_mode": "true"},
                            headers=get_auth_headers(), timeout=30
                        )
                        if r.status_code == 202:
                            st.session_state.batch_save_task_id = r.json().get("task_id")
                            st.session_state.batch_save_result  = None
                            st.success(f"Save task: `{st.session_state.batch_save_task_id}`")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
            else:
                with st.spinner("Applying to database…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/batch-optimization-save/",
                            json=params, headers=get_auth_headers(), timeout=300
                        )
                        if r.status_code == 200:
                            st.session_state.batch_save_result  = r.json()
                            st.session_state.batch_save_task_id = None
                            st.success("✅ Saved!")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        stask = st.session_state.get("batch_save_task_id")
        if stask:
            st.markdown("#### ⏳ Save Task")
            pb2  = st.progress(0)
            txt2 = st.empty()
            res2 = poll_task_until_complete(stask, pb2, txt2, max_wait_seconds=600)
            if res2:
                st.session_state.batch_save_result  = res2
                st.session_state.batch_save_task_id = None
                st.rerun()

        # ── Save result banner ────────────────────────────────────────────────
        save_result = st.session_state.get("batch_save_result")
        if isinstance(save_result, dict) and save_result.get("status") != "error":
            upd  = save_result.get("total_updated", 0)
            skip = save_result.get("total_skipped", 0)
            st.markdown(f"""
            <div style='background:#0a2a0a;border-left:4px solid #22c55e;
                        padding:14px 18px;border-radius:6px;margin:12px 0;'>
            <b style='color:#22c55e'>✅ Database Updated</b><br>
            <span style='color:#ccc'>
            <b style='color:#86efac'>{upd}</b> products updated &nbsp;|&nbsp;
            <b style='color:#fca5a5'>{skip}</b> skipped
            </span></div>
            """, unsafe_allow_html=True)
            updated_list = save_result.get("updated_products", [])
            if updated_list:
                with st.expander(f"📋 {len(updated_list)} updated products"):
                    df_upd = pd.DataFrame(updated_list)
                    df_upd["Batch Size Δ"]   = df_upd["new_batch_size"]  - df_upd["old_batch_size"]
                    df_upd["Num Batches Δ"]  = df_upd["new_num_batches"] - df_upd["old_num_batches"]
                    st.dataframe(df_upd, use_container_width=True, height=300)
                    st.download_button("📥 CSV", data=df_upd.to_csv(index=False),
                                       file_name="indiv_batch_updates.csv", mime="text/csv")

        # ── Preview results ───────────────────────────────────────────────────
        preview = st.session_state.get("batch_preview_result")
        if not preview:
            st.info("Click **🔍 Preview** to run the individual ILP and see results.")
        else:
            summary  = preview.get("summary", {})
            analysis = preview.get("batch_analysis", [])

            st.markdown("---")
            st.markdown("### 📊 Individual Optimization Results")

            sm1, sm2, sm3, sm4, sm5 = st.columns(5)
            sm1.metric("Products",       summary.get("total_products", 0))
            sm2.metric("Total Demand",   f"{summary.get('total_demand', 0):,}")
            sm3.metric("Total Batches",  summary.get("total_batches", 0))
            sm4.metric("Avg Batch Size", summary.get("avg_batch_size", 0))
            sm5.metric("Std Dev",        summary.get("std_batch_size", 0))

            # Adaptive bounds note
            if summary.get("note"):
                st.info(f"ℹ️ {summary['note']}")

            if analysis:
                df_a = pd.DataFrame(analysis)
                df_a["improvement_pct"] = (
                    df_a["improvement"]
                    .str.replace("%", "", regex=False)
                    .astype(float)
                )
                df_a["batch_reduction"]   = df_a["old_num_batches"] - df_a["new_num_batches"]
                df_a["batch_size_change"] = df_a["new_batch_size"]  - df_a["old_batch_size"]

                ptab1, ptab2, ptab3, ptab4 = st.tabs([
                    "📈 Charts", "📋 Full Table", "🏆 Top Improvements", "🔬 ILP Detail"
                ])

                with ptab1:
                    df_top20 = df_a.nlargest(20, "demand")

                    st.markdown("#### Batch Count: Old (12) vs New — top 20 by demand")
                    fig_bc = go.Figure()
                    fig_bc.add_trace(go.Bar(name="Old (12)", x=df_top20["item"].astype(str),
                                            y=df_top20["old_num_batches"], marker_color="#4facfe"))
                    fig_bc.add_trace(go.Bar(name="New (ILP)", x=df_top20["item"].astype(str),
                                            y=df_top20["new_num_batches"], marker_color="#00f2fe"))
                    fig_bc.update_layout(barmode="group", template="plotly_dark", height=380,
                                          xaxis_title="Item", yaxis_title="# Batches",
                                          legend=dict(orientation="h", y=1.1))
                    st.plotly_chart(fig_bc, use_container_width=True)

                    st.markdown("#### Batch Size: Old vs New vs Ideal")
                    fig_bs = go.Figure()
                    fig_bs.add_trace(go.Scatter(name="Old", x=df_top20["item"].astype(str),
                                                y=df_top20["old_batch_size"],
                                                mode="lines+markers", line=dict(color="#f59e0b")))
                    fig_bs.add_trace(go.Scatter(name="New", x=df_top20["item"].astype(str),
                                                y=df_top20["new_batch_size"],
                                                mode="lines+markers", line=dict(color="#22c55e")))
                    fig_bs.add_trace(go.Scatter(name="Ideal", x=df_top20["item"].astype(str),
                                                y=df_top20["ideal_batch_size"],
                                                mode="lines", line=dict(color="#a78bfa", dash="dot")))
                    fig_bs.update_layout(template="plotly_dark", height=360,
                                          xaxis_title="Item", yaxis_title="Batch Size",
                                          legend=dict(orientation="h", y=1.1))
                    st.plotly_chart(fig_bs, use_container_width=True)

                    # Effective bounds annotation
                    if "effective_min_batch" in df_a.columns:
                        st.markdown("#### Adaptive Bounds Applied")
                        bounds_fig = go.Figure()
                        bounds_fig.add_trace(go.Bar(
                            name="Eff. Min Batch", x=df_a["item"].astype(str),
                            y=df_a["effective_min_batch"], marker_color="rgba(239,68,68,0.5)"
                        ))
                        bounds_fig.add_trace(go.Bar(
                            name="New Batch Size", x=df_a["item"].astype(str),
                            y=df_a["new_batch_size"], marker_color="#22c55e"
                        ))
                        bounds_fig.add_trace(go.Bar(
                            name="Eff. Max Batch", x=df_a["item"].astype(str),
                            y=df_a["effective_max_batch"], marker_color="rgba(59,130,246,0.4)"
                        ))
                        bounds_fig.update_layout(
                            barmode="overlay", template="plotly_dark", height=340,
                            title="Adaptive Bounds vs Chosen Batch Size (each product)",
                            xaxis_title="Item", yaxis_title="Units",
                            legend=dict(orientation="h", y=1.1),
                        )
                        st.plotly_chart(bounds_fig, use_container_width=True)

                    c_l, c_r = st.columns(2)
                    with c_l:
                        fig_hist = px.histogram(df_a, x="improvement_pct", nbins=20,
                                                 color_discrete_sequence=["#4facfe"],
                                                 template="plotly_dark",
                                                 title="Improvement Distribution (%)")
                        fig_hist.update_layout(height=280)
                        st.plotly_chart(fig_hist, use_container_width=True)
                    with c_r:
                        fig_sc = px.scatter(df_a, x="demand", y="batch_reduction",
                                             color="improvement_pct",
                                             color_continuous_scale="Viridis",
                                             template="plotly_dark",
                                             hover_data=["item", "new_batch_size"],
                                             title="Demand vs Batch Reduction")
                        fig_sc.update_layout(height=280)
                        st.plotly_chart(fig_sc, use_container_width=True)

                with ptab2:
                    display_cols = [
                        "item", "description", "demand",
                        "old_batch_size", "old_num_batches",
                        "new_batch_size", "new_num_batches",
                        "ideal_batch_size", "improvement",
                        "batch_reduction", "batch_size_change",
                    ]
                    if "effective_min_batch" in df_a.columns:
                        display_cols += ["effective_min_batch", "effective_max_batch"]

                    df_display = df_a[display_cols].copy()

                    def _color_impr(val):
                        try:
                            v = float(str(val).replace("%", ""))
                            if v > 30: return "background:#14532d;color:#86efac"
                            if v > 10: return "background:#1a3a0a;color:#bef264"
                            if v > 0:  return "background:#1a2a0a;color:#d9f99d"
                        except Exception:
                            pass
                        return ""

                    st.dataframe(
                        df_display.style.applymap(_color_impr, subset=["improvement"]),
                        use_container_width=True, height=500
                    )
                    st.download_button("📥 Download CSV",
                                       data=df_display.to_csv(index=False),
                                       file_name="indiv_preview.csv", mime="text/csv")

                with ptab3:
                    df_top10 = df_a.nlargest(10, "improvement_pct")
                    for _, row in df_top10.iterrows():
                        impr  = row["improvement_pct"]
                        color = "#22c55e" if impr > 30 else "#f59e0b" if impr > 10 else "#6b7280"
                        st.markdown(f"""
                        <div style='background:#0d1a0d;border-left:4px solid {color};
                                    border-radius:6px;padding:10px 16px;margin-bottom:8px;
                                    display:flex;justify-content:space-between;'>
                          <div>
                            <b style='color:#d1d5db'>Item {int(row["item"])}</b>
                            <span style='color:#6b7280;font-size:12px;margin-left:8px;'>
                              {str(row["description"])[:45]}
                            </span><br>
                            <span style='color:#9ca3af;font-size:11px;'>
                              Demand: {int(row["demand"]):,}
                            </span>
                          </div>
                          <div style='text-align:right;'>
                            <b style='color:{color};font-size:16px;'>{impr:.1f}%</b><br>
                            <span style='color:#9ca3af;font-size:11px;'>
                              {int(row["old_num_batches"])}→{int(row["new_num_batches"])} batches &nbsp;|&nbsp;
                              {int(row["old_batch_size"])}→{int(row["new_batch_size"])} units/batch
                            </span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                    df_zero = df_a[df_a["improvement_pct"] == 0]
                    if not df_zero.empty:
                        st.markdown(f"#### ⚪ {len(df_zero)} products unchanged")
                        st.dataframe(df_zero[["item", "description", "demand",
                                              "old_batch_size", "new_batch_size"]],
                                     use_container_width=True, height=200)

                with ptab4:
                    st.markdown("#### ILP Formulation")
                    st.json({
                        "solver": "PuLP (CBC)",
                        "objective": "Minimize N (number of batches per product)",
                        "adaptive_bounds": {
                            "effective_min": "max(user_min, ceil(demand/max_num_batches))",
                            "effective_max": "min(user_max, demand)",
                            "fallback": "use (ceil(demand/max_N), demand) if intersection empty"
                        },
                        "variables": {
                            "B": "batch_size ∈ [eff_min, eff_max] integer",
                            "N": f"num_batches ∈ [1, {int(max_num_batches)}] integer",
                            "y_n": f"binary selector n ∈ [1..{int(max_num_batches)}]"
                        },
                        "key_constraints": [
                            "sum(y_n) == 1",
                            "N == sum(n*y_n)",
                            "B >= ceil(demand/n) - M*(1-y_n)  ∀n",
                            "y_n == 0 if ceil(demand/n) > eff_max"
                        ],
                        "parameters_used": params
                    })

    # ==========================================================================
    # TAB 2 — Joint Multi-Product ILP (NEW)
    # ==========================================================================
    with tab_joint:
        st.markdown("""
        <div style='background:#0d200d;border-left:3px solid #38ef7d;
                    padding:8px 14px;border-radius:4px;font-size:12px;
                    color:#86efac;margin-bottom:14px;'>
        Optimises ALL products simultaneously in a single MILP.
        Objective: <b>minimise C</b> (the worst machine load hours — the bottleneck).
        Machine-load constraints link batch decisions across products,
        producing a balanced schedule rather than per-product greedy choices.
        </div>
        """, unsafe_allow_html=True)

        # ── Why joint matters visual ───────────────────────────────────────────
        with st.expander("📖 Why Joint Optimization? (visual explanation)", expanded=False):
            st.markdown("""
**Before (Individual, independent optimization):**
```
Machine 1: ████████████████████████ 95%  ← BOTTLENECK
Machine 2: ████                      20%  ← IDLE
Machine 3: ██████                    30%
```
Each product's ILP ignores other products' machine use.
Product A and B both independently decide to use Machine 1 heavily.

**After (Joint optimization):**
```
Machine 1: ██████████████  65%
Machine 2: █████████████   60%
Machine 3: ████████████    55%
```
The joint MILP sees all machine constraints at once. It shifts some products
to use different batch counts so no single machine becomes overloaded.

**Result:** Lower makespan → faster total production → better schedule quality.

**MILP Formulation:**
```
Minimize  C                                    ← worst machine load (hours)

For each product i:
  Σ_n  y_{i,n}  =  1                          ← exactly one batch count chosen
  y_{i,n}  ∈  {0,1}

For each machine m:
  Σ_{i,n}  load_{i,m,n} × y_{i,n}  ≤  C      ← all machine loads ≤ C

where  load_{i,m,n}  =  cycle_time_{i,m} × ceil(demand_i/n) × n  /  3600
```
            """)

        # ── Solver time limit control ──────────────────────────────────────────
        jt1, jt2 = st.columns(2)
        with jt1:
            time_limit = st.number_input(
                "Solver time limit (seconds)", min_value=10,
                max_value=600, value=120,
                help="CBC will stop and return best solution found within this time"
            )
        with jt2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                f"Joint ILP size: ~{int(max_num_batches)} × products binary vars. "
                "For 39 products this is ~975 binaries — typically solved in <30s."
            )

        ja1, ja2 = st.columns(2)
        with ja1:
            joint_preview_btn = st.button(
                "🔍 Joint Preview (no DB write)",
                type="primary", use_container_width=True
            )
        with ja2:
            joint_save_btn = st.button(
                "💾 Joint Save to Database",
                type="secondary", use_container_width=True
            )

        # ── Joint Preview ──────────────────────────────────────────────────────
        if joint_preview_btn:
            if batch_async:
                with st.spinner("Submitting joint preview task…"):
                    try:
                        r = requests.get(
                            f"{API_BASE_URL}/batch-optimization-joint-preview/",
                            params={**params, "async_mode": "true"},
                            headers=get_auth_headers(), timeout=30
                        )
                        if r.status_code == 202:
                            st.session_state.joint_preview_task_id = r.json().get("task_id")
                            st.session_state.joint_preview_result  = None
                            st.success(f"Task: `{st.session_state.joint_preview_task_id}`")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
            else:
                with st.spinner(f"Running joint MILP (up to {time_limit}s)…"):
                    try:
                        r = requests.get(
                            f"{API_BASE_URL}/batch-optimization-joint-preview/",
                            params=params, headers=get_auth_headers(),
                            timeout=time_limit + 60
                        )
                        if r.status_code == 200:
                            st.session_state.joint_preview_result  = r.json()
                            st.session_state.joint_preview_task_id = None
                            st.success("✅ Joint preview complete!")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        jptask = st.session_state.get("joint_preview_task_id")
        if jptask:
            st.markdown("#### ⏳ Joint Preview Task")
            jpb  = st.progress(0)
            jtxt = st.empty()
            jres = poll_task_until_complete(jptask, jpb, jtxt, max_wait_seconds=600)
            if jres:
                st.session_state.joint_preview_result  = jres
                st.session_state.joint_preview_task_id = None
                st.rerun()

        # ── Joint Save ─────────────────────────────────────────────────────────
        if joint_save_btn:
            if batch_async:
                with st.spinner("Submitting joint save task…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/batch-optimization-joint/",
                            json={**params, "async_mode": "true"},
                            headers=get_auth_headers(), timeout=30
                        )
                        if r.status_code == 202:
                            st.session_state.joint_save_task_id = r.json().get("task_id")
                            st.session_state.joint_save_result  = None
                            st.success(f"Task: `{st.session_state.joint_save_task_id}`")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
            else:
                with st.spinner(f"Running joint MILP and saving (up to {time_limit}s)…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/batch-optimization-joint/",
                            json=params, headers=get_auth_headers(),
                            timeout=time_limit + 60
                        )
                        if r.status_code == 200:
                            st.session_state.joint_save_result  = r.json()
                            st.session_state.joint_save_task_id = None
                            st.success("✅ Joint optimization saved to database!")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        jstask = st.session_state.get("joint_save_task_id")
        if jstask:
            st.markdown("#### ⏳ Joint Save Task")
            jsb  = st.progress(0)
            jst  = st.empty()
            jsr  = poll_task_until_complete(jstask, jsb, jst, max_wait_seconds=600)
            if jsr:
                st.session_state.joint_save_result  = jsr
                st.session_state.joint_save_task_id = None
                st.rerun()

        # ── Joint Save result banner ───────────────────────────────────────────
        j_save = st.session_state.get("joint_save_result")
        if isinstance(j_save, dict) and j_save.get("status") != "error":
            upd = j_save.get("products_updated", 0)
            st.markdown(f"""
            <div style='background:#0a2a0a;border-left:4px solid #22c55e;
                        padding:14px 18px;border-radius:6px;margin:12px 0;'>
            <b style='color:#22c55e'>✅ Joint Optimization Applied to Database</b><br>
            <span style='color:#ccc'>
            <b style='color:#86efac'>{upd}</b> products updated &nbsp;|&nbsp;
            Makespan proxy: <b style='color:#38ef7d'>{j_save.get("makespan_proxy", 0):.1f}h</b> &nbsp;|&nbsp;
            Solver: <b>{j_save.get("status", "—")}</b>
            </span></div>
            """, unsafe_allow_html=True)

        # ── Joint results display ──────────────────────────────────────────────
        j_preview = (
            st.session_state.get("joint_preview_result") or
            st.session_state.get("joint_save_result")
        )

        if not j_preview:
            st.markdown("""
            <div style='text-align:center;padding:50px 20px;color:#4b5563;'>
              <div style='font-size:52px;'>🤝</div>
              <div style='font-size:15px;font-weight:600;color:#6b7280;margin:10px 0;'>
                No joint optimization loaded yet
              </div>
              <div style='font-size:12px;'>
                Click <b>🔍 Joint Preview</b> to run the multi-product MILP
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            analysis      = j_preview.get("batch_analysis", [])
            machine_loads = j_preview.get("machine_loads", {})
            summary       = j_preview.get("summary", {})
            solver_status = j_preview.get("status", "unknown")

            st.markdown("---")

            # Solver status badge
            badge_color = "#22c55e" if solver_status == "optimal" else "#f59e0b"
            st.markdown(
                f"<span style='background:{badge_color};color:#000;padding:4px 12px;"
                f"border-radius:12px;font-size:12px;font-weight:700;'>"
                f"Solver: {solver_status.upper()}</span>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # ── Summary KPIs ───────────────────────────────────────────────────
            st.markdown("### 📊 Joint Optimization Summary")
            jk1, jk2, jk3, jk4, jk5 = st.columns(5)
            jk1.metric("Products",      summary.get("total_products", len(analysis)))
            jk2.metric("Total Demand",  f"{summary.get('total_demand', 0):,}")
            jk3.metric("Total Batches", summary.get("total_batches", 0))
            jk4.metric("Makespan Proxy", f"{j_preview.get('makespan_proxy', 0):.1f}h",
                        help="Max machine load hours — lower = more balanced")
            jk5.metric("Avg Improvement", f"{summary.get('avg_improvement', 0):.1f}%")

            # ── Machine load chart — the KEY chart ─────────────────────────────
            if machine_loads:
                st.markdown("### 🏭 Machine Load Balance After Joint Optimization")

                ml_df = (
                    pd.DataFrame(list(machine_loads.items()), columns=["Machine", "Load (h)"])
                    .sort_values("Load (h)", ascending=False)
                )
                max_load = ml_df["Load (h)"].max()
                min_load = ml_df["Load (h)"].min()

                bar_colors = [
                    "#ef4444" if v == max_load else
                    "#22c55e" if v == min_load else "#4facfe"
                    for v in ml_df["Load (h)"]
                ]

                ml_fig = go.Figure()
                ml_fig.add_trace(go.Bar(
                    x=ml_df["Machine"], y=ml_df["Load (h)"],
                    marker_color=bar_colors,
                    text=[f"{v:.1f}h" for v in ml_df["Load (h)"]],
                    textposition="auto",
                    hovertemplate="<b>%{x}</b><br>Load: %{y:.2f}h<extra></extra>",
                ))
                # Makespan proxy reference line
                proxy = j_preview.get("makespan_proxy", 0)
                if proxy > 0:
                    ml_fig.add_hline(
                        y=proxy, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"Makespan proxy C={proxy:.1f}h",
                        annotation_position="top right"
                    )

                ml_fig.update_layout(
                    template="plotly_dark", height=400,
                    title="Machine Load Hours (joint optimization result)",
                    xaxis_title="Machine", yaxis_title="Load (hours)",
                    margin=dict(b=100),
                )
                ml_fig.update_xaxes(tickangle=30)
                st.plotly_chart(ml_fig, use_container_width=True)

                # Load balance score
                if max_load > 0:
                    balance_pct = (1 - (max_load - min_load) / max_load) * 100
                    st.markdown(f"""
                    <div style='background:#0d1a0d;border:1px solid #1a3a1a;border-radius:6px;
                                padding:10px 16px;margin:8px 0;font-size:13px;color:#9ca3af;'>
                    <b style='color:#38ef7d'>Load Balance Score: {balance_pct:.1f}%</b>
                    &nbsp; (100% = perfectly balanced, 0% = all load on one machine)<br>
                    Bottleneck: <b style='color:#ef4444'>{ml_df.iloc[0]["Machine"]}</b>
                    &nbsp;({ml_df.iloc[0]["Load (h)"]:.1f}h) &nbsp;|&nbsp;
                    Most idle: <b style='color:#22c55e'>{ml_df.iloc[-1]["Machine"]}</b>
                    &nbsp;({ml_df.iloc[-1]["Load (h)"]:.1f}h)
                    </div>
                    """, unsafe_allow_html=True)

            # ── Per-product results ────────────────────────────────────────────
            if analysis:
                df_j = pd.DataFrame(analysis)
                if "improvement" in df_j.columns:
                    df_j["improvement_pct"] = (
                        df_j["improvement"]
                        .str.replace("%", "", regex=False)
                        .astype(float)
                    )

                jt1, jt2, jt3 = st.tabs([
                    "📋 Product Results", "📈 Comparison Charts", "🔍 Source Breakdown"
                ])

                with jt1:
                    st.markdown("#### Per-Product Joint Optimization Results")

                    def _color_j(val):
                        try:
                            v = float(str(val).replace("%", ""))
                            if v > 30: return "background:#14532d;color:#86efac"
                            if v > 10: return "background:#1a3a0a;color:#bef264"
                            if v > 0:  return "background:#1a2a0a;color:#d9f99d"
                        except Exception:
                            pass
                        return ""

                    display_j = df_j[[
                        "item", "description", "demand",
                        "old_batch_size", "old_num_batches",
                        "new_batch_size", "new_num_batches",
                        "ideal_batch_size", "improvement",
                        "source",
                    ]].copy()
                    st.dataframe(
                        display_j.style.applymap(_color_j, subset=["improvement"]),
                        use_container_width=True, height=480
                    )
                    st.download_button("📥 Download CSV",
                                       data=display_j.to_csv(index=False),
                                       file_name="joint_batch_results.csv", mime="text/csv")

                with jt2:
                    df_top20j = df_j.nlargest(20, "demand")

                    # Side-by-side batch count comparison
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        fig_jbc = go.Figure()
                        fig_jbc.add_trace(go.Bar(name="Old", x=df_top20j["item"].astype(str),
                                                  y=df_top20j["old_num_batches"],
                                                  marker_color="#4facfe"))
                        fig_jbc.add_trace(go.Bar(name="Joint ILP", x=df_top20j["item"].astype(str),
                                                  y=df_top20j["new_num_batches"],
                                                  marker_color="#38ef7d"))
                        fig_jbc.update_layout(barmode="group", template="plotly_dark",
                                               height=320, title="Batch Count (top 20)",
                                               legend=dict(orientation="h", y=1.1))
                        st.plotly_chart(fig_jbc, use_container_width=True)

                    with fc2:
                        fig_jbs = go.Figure()
                        fig_jbs.add_trace(go.Scatter(name="Old", x=df_top20j["item"].astype(str),
                                                      y=df_top20j["old_batch_size"],
                                                      mode="lines+markers",
                                                      line=dict(color="#f59e0b")))
                        fig_jbs.add_trace(go.Scatter(name="Joint ILP", x=df_top20j["item"].astype(str),
                                                      y=df_top20j["new_batch_size"],
                                                      mode="lines+markers",
                                                      line=dict(color="#38ef7d")))
                        fig_jbs.update_layout(template="plotly_dark", height=320,
                                               title="Batch Size (top 20)",
                                               legend=dict(orientation="h", y=1.1))
                        st.plotly_chart(fig_jbs, use_container_width=True)

                    # Improvement histogram
                    if "improvement_pct" in df_j.columns:
                        fig_jimp = px.histogram(
                            df_j, x="improvement_pct", nbins=20,
                            color_discrete_sequence=["#38ef7d"],
                            template="plotly_dark",
                            title="Joint Improvement Distribution (%)",
                            labels={"improvement_pct": "Batch Reduction (%)"}
                        )
                        fig_jimp.update_layout(height=280)
                        st.plotly_chart(fig_jimp, use_container_width=True)

                with jt3:
                    if "source" in df_j.columns:
                        src_counts = df_j["source"].value_counts().reset_index()
                        src_counts.columns = ["Source", "Count"]

                        color_map = {
                            "joint_ilp": "#38ef7d",
                            "fallback":  "#f59e0b",
                            "skipped":   "#6b7280",
                        }
                        fig_src = px.pie(
                            src_counts, values="Count", names="Source",
                            color="Source", color_discrete_map=color_map,
                            template="plotly_dark",
                            title="Decision Source: How was each product's batch size chosen?"
                        )
                        fig_src.update_layout(height=320)
                        st.plotly_chart(fig_src, use_container_width=True)

                        st.markdown("""
                        | Source | Meaning |
                        |--------|---------|
                        | `joint_ilp` | Solved optimally by the joint MILP |
                        | `fallback` | ILP couldn't find optimal; used heuristic |
                        | `skipped` | Zero demand — not included in optimization |
                        """)

            # ── Machine load CSV download ──────────────────────────────────────
            if machine_loads:
                ml_csv = pd.DataFrame(
                    list(machine_loads.items()), columns=["machine", "load_hours"]
                ).sort_values("load_hours", ascending=False)
                st.download_button("📥 Download Machine Loads CSV",
                                   data=ml_csv.to_csv(index=False),
                                   file_name="joint_machine_loads.csv", mime="text/csv")


# ===========================================================================
# PAGE 4 – Filter Data
# ===========================================================================

elif page == "📋 Filter Data":
    st.title("📋 Filter Data")
    st.markdown("""
    <div style='background:#1a2a3a;border-left:4px solid #4facfe;padding:14px 18px;border-radius:6px;margin-bottom:18px;'>
    <b style='color:#4facfe'>Filter schedule and production data</b><br>
    <span style='color:#ccc'>
    Use the filters below to narrow down by <b>Machine(s)</b>, <b>Product(s)</b>, <b>Date range</b>,
    <b>Batch size</b>, <b>Duration</b>, <b>Process step</b>, and <b>DCC type</b>.
    </span></div>
    """, unsafe_allow_html=True)

    filter_options = fetch_data("get-filter-options")
    if not filter_options:
        st.warning("Could not load filter options. Ensure the backend is running and data is initialized.")
        st.stop()

    machines  = filter_options.get("machines", [])
    products  = filter_options.get("products", [])
    dcc_types = filter_options.get("dcc_types", [])
    date_range = filter_options.get("date_range", {})

    min_date = date_range.get("min")
    max_date = date_range.get("max")
    if min_date:
        min_date = pd.to_datetime(min_date).date()
    if max_date:
        max_date = pd.to_datetime(max_date).date()
    if not min_date:
        min_date = date.today()
    if not max_date:
        max_date = date.today()

    with st.expander("🔍 Filters", expanded=True):
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Schedule & machine")
            selected_machines = st.multiselect("Machines", options=machines, default=[])
            start_date = st.date_input("Start date", value=min_date,
                                        min_value=min_date, max_value=max_date)
            end_date = st.date_input("End date", value=max_date,
                                      min_value=min_date, max_value=max_date)
            step_filter = st.selectbox(
                "Process step (exact)",
                options=["— Any —"] + [str(i) for i in range(1, 101)], index=0
            )

        with c2:
            st.subheader("Product & batch")
            product_options = ["All"] + [
                f"Item {p['item']}: {p['description'][:40]}{'…' if len(p.get('description','')) > 40 else ''}"
                for p in products
            ]
            selected_product_label = st.multiselect(
                "Products (Item : description)", options=product_options, default=[]
            )
            dcc_type_filter = st.selectbox(
                "DCC type", options=["— Any —"] + (dcc_types or []), index=0
            )
            batch_size_min = st.number_input("Batch size (min)", min_value=0, value=0, step=10)
            batch_size_max = st.number_input("Batch size (max)", min_value=0, value=0, step=10,
                                              help="0 = no max")
            duration_min = st.number_input("Duration hours (min)", min_value=0.0,
                                            value=0.0, step=0.5, format="%.2f")
            duration_max = st.number_input("Duration hours (max)", min_value=0.0,
                                            value=0.0, step=0.5, format="%.2f",
                                            help="0 = no max")

    if st.button("▶️ Apply filters & load data", type="primary", key="filter_data_apply"):
        params = {"page": 1, "page_size": 2000}
        if selected_machines:
            params["machines"] = ",".join(selected_machines)
        if selected_product_label and "All" not in selected_product_label:
            items = []
            for label in selected_product_label:
                try:
                    item = int(label.split(":")[0].replace("Item", "").strip())
                    items.append(item)
                except (ValueError, AttributeError):
                    continue
            if items:
                params["products"] = ",".join(map(str, items))
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = f"{end_date.isoformat()}T23:59:59.999999"
        if step_filter and step_filter != "— Any —":
            params["step"] = step_filter
        if dcc_type_filter and dcc_type_filter != "— Any —":
            params["dcc_type"] = dcc_type_filter
        if batch_size_min > 0:
            params["batch_size_min"] = batch_size_min
        if batch_size_max > 0:
            params["batch_size_max"] = batch_size_max
        if duration_min > 0:
            params["duration_min"] = duration_min
        if duration_max > 0:
            params["duration_max"] = duration_max

        r = requests.get(
            f"{API_BASE_URL}/get-schedule/",
            params=params, headers=get_auth_headers(), timeout=60,
        )
        if r.status_code == 200:
            data = r.json()
            st.session_state["filter_data_results"] = data
            st.session_state["filter_data_params"]  = params
            st.success(f"✅ Found **{data.get('count', 0):,}** operations.")
        else:
            st.error(f"Error {r.status_code}: {r.text}")

    if "filter_data_results" in st.session_state:
        data        = st.session_state["filter_data_results"]
        results     = data.get("results", [])
        total_count = data.get("count", 0)

        st.markdown("---")
        st.subheader(f"📊 Filtered results ({total_count:,} operations)")

        if results:
            df = pd.DataFrame(results)
            if "start" in df.columns and "end" in df.columns:
                df["start"] = pd.to_datetime(df["start"], format="ISO8601", utc=True).dt.tz_localize(None).dt.strftime("%Y-%m-%d %H:%M")
                df["end"]   = pd.to_datetime(df["end"],   format="ISO8601", utc=True).dt.tz_localize(None).dt.strftime("%Y-%m-%d %H:%M")
            if "duration_h" in df.columns:
                df["duration_h"] = df["duration_h"].round(4)
            st.dataframe(df, use_container_width=True, height=450)
            st.download_button(
                "📥 Download filtered data (CSV)",
                data=df.to_csv(index=False),
                file_name="filtered_schedule.csv",
                mime="text/csv",
                key="filter_download_csv",
            )
        else:
            st.info("No rows match the current filters.")


# ===========================================================================
# PAGE 5 – Buffer Optimization
# ===========================================================================

elif page == "📊 Buffer Optimization":
    st.header("Buffer Optimization Analysis")

    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        safety_factor = st.number_input("Safety Factor", min_value=1.0,
                                         max_value=3.0, value=1.5, step=0.1)
    with col2:
        total_budget = st.number_input("Total Buffer Budget (optional)",
                                        min_value=0.0, value=0.0, step=100.0)
    with col3:
        if st.button("🔄 Load Buffer Data", type="primary"):
            st.session_state.load_buffer = True

    if st.session_state.get('load_buffer', False):
        try:
            params = {'safety_factor': safety_factor}
            if total_budget > 0:
                params['total_budget'] = total_budget
            r = requests.get(f"{API_BASE_URL}/buffer-optimization/",
                             params=params, headers=get_auth_headers(), timeout=30)
            if r.status_code == 200:
                data = r.json()
                if 'buffer_recommendations' in data and data['buffer_recommendations']:
                    st.subheader("📈 Production Parameters")
                    pd_ = data['parameters']
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Throughput/Hour", f"{pd_['throughput_per_hour']:.2f} units")
                    c2.metric("Makespan",        f"{pd_['makespan_hours']:.2f} hours")
                    c3.metric("Safety Factor",   f"{pd_['safety_factor']}")
                    c4.metric("Total Units",     f"{pd_['total_units']}")
                    st.info(f"**Formula:** {data['formula']}")

                    if 'pulp_allocation' in data:
                        pa = data['pulp_allocation']
                        st.success(f"""
                        **🎯 PuLP Optimal Allocation Applied!**
                        - Budget Available: {pa['total_budget']:.2f} units
                        - Total Required:   {pa['total_required']:.2f} units
                        - Total Allocated:  {pa['total_allocated']:.2f} units
                        """)

                    df_buf = pd.DataFrame(data['buffer_recommendations'])
                    st.subheader("🎯 Buffer Recommendations by Machine")

                    bc1, bc2 = st.columns(2)
                    with bc1:
                        fig_b = px.bar(df_buf, x='machine', y='buffer_size_units',
                                        color='recommendation',
                                        title="Recommended Buffer Sizes by Machine",
                                        color_discrete_map={
                                            'HIGH PRIORITY':   '#ef4444',
                                            'MEDIUM PRIORITY': '#f59e0b',
                                            'LOW PRIORITY':    '#10b981'
                                        })
                        st.plotly_chart(fig_b, use_container_width=True)
                    with bc2:
                        fig_s = px.scatter(df_buf, x='utilization', y='buffer_size_units',
                                            size='total_operations', color='recommendation',
                                            hover_data=['machine','avg_operation_time_hours'],
                                            title="Utilization vs Buffer Requirements",
                                            color_discrete_map={
                                                'HIGH PRIORITY':   '#ef4444',
                                                'MEDIUM PRIORITY': '#f59e0b',
                                                'LOW PRIORITY':    '#10b981'
                                            })
                        st.plotly_chart(fig_s, use_container_width=True)

                    if 'allocated_buffer' in df_buf.columns:
                        st.subheader("💰 Budget Allocation (PuLP Optimised)")
                        fig_a = go.Figure()
                        fig_a.add_trace(go.Bar(name='Required', x=df_buf['machine'],
                                                y=df_buf['required_buffer'],
                                                marker_color='lightcoral'))
                        fig_a.add_trace(go.Bar(name='Allocated', x=df_buf['machine'],
                                                y=df_buf['allocated_buffer'],
                                                marker_color='lightgreen'))
                        fig_a.update_layout(barmode='group', height=400,
                                             title='Required vs Allocated Buffer')
                        st.plotly_chart(fig_a, use_container_width=True)

                    st.subheader("📋 Detailed Buffer Recommendations")
                    df_d = df_buf.copy()
                    df_d['buffer_size_units']        = df_d['buffer_size_units'].round(2)
                    df_d['utilization']              = df_d['utilization'].apply(lambda x: f"{x:.2f}%")
                    df_d['avg_operation_time_hours'] = df_d['avg_operation_time_hours'].round(4)
                    st.dataframe(df_d, use_container_width=True)
                    st.download_button("📥 Download Buffer Data (CSV)",
                                       data=df_buf.to_csv(index=False),
                                       file_name="buffer_recommendations.csv", mime="text/csv")
                else:
                    st.info("No schedule data available for buffer optimization.")
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Error loading buffer data: {e}")


# ===========================================================================
# PAGE 6 – Bottleneck Analysis
# ===========================================================================

elif page == "🔍 Bottleneck Analysis":
    st.header("Bottleneck Analysis")

    if st.button("🔄 Load Bottleneck Data", type="primary"):
        st.session_state.load_bottleneck = True

    if st.session_state.get('load_bottleneck', False):
        try:
            r = requests.get(f"{API_BASE_URL}/bottleneck-analysis/", headers=get_auth_headers(), timeout=30)
            if r.status_code == 200:
                data = r.json()
                if 'machine_analysis' in data and data['machine_analysis']:
                    st.subheader("📊 Overall Summary")
                    s = data['summary']
                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("Total Makespan",         f"{s['total_makespan_hours']:.2f} hrs")
                    s2.metric("Bottleneck Machine",     s['bottleneck_machine'])
                    s3.metric("Bottleneck Utilization", f"{s['bottleneck_utilization']:.2f}%")
                    s4.metric("Average Utilization",    f"{s['avg_utilization']:.2f}%")

                    df_bn = pd.DataFrame(data['machine_analysis'])
                    st.subheader("🎯 Machine Utilization Analysis")

                    bn1, bn2 = st.columns(2)
                    with bn1:
                        colors = ['#ef4444' if 'CRITICAL' in s else
                                  '#f59e0b' if 'POTENTIAL' in s else
                                  '#10b981' if 'WELL' in s else '#6b7280'
                                  for s in df_bn['status']]
                        fu = go.Figure()
                        fu.add_trace(go.Bar(
                            y=df_bn['machine'], x=df_bn['utilization'],
                            orientation='h', marker=dict(color=colors),
                            text=df_bn['utilization'].apply(lambda x: f"{x:.1f}%"),
                            textposition='auto'
                        ))
                        fu.update_layout(title="Machine Utilization (%)",
                                          xaxis_title="Utilization (%)",
                                          yaxis_title="Machine",
                                          showlegend=False, height=400)
                        st.plotly_chart(fu, use_container_width=True)

                    with bn2:
                        sc = df_bn['status'].value_counts()
                        fp = px.pie(values=sc.values, names=sc.index,
                                     title="Machine Status Distribution",
                                     color=sc.index,
                                     color_discrete_map={
                                         'CRITICAL BOTTLENECK':  '#ef4444',
                                         'POTENTIAL BOTTLENECK': '#f59e0b',
                                         'WELL UTILIZED':        '#10b981',
                                         'UNDERUTILIZED':        '#6b7280'
                                     })
                        st.plotly_chart(fp, use_container_width=True)

                    st.subheader("⏱️ Time Utilization Breakdown")
                    ft = go.Figure()
                    ft.add_trace(go.Bar(name='Used Hours', y=df_bn['machine'],
                                         x=df_bn['used_hours'], orientation='h',
                                         marker_color='#3b82f6'))
                    ft.add_trace(go.Bar(name='Idle Hours', y=df_bn['machine'],
                                         x=df_bn['idle_hours'], orientation='h',
                                         marker_color='#e5e7eb'))
                    ft.update_layout(barmode='stack', height=400,
                                      title="Used vs Idle Hours by Machine",
                                      xaxis_title="Hours", yaxis_title="Machine")
                    st.plotly_chart(ft, use_container_width=True)

                    st.subheader("📋 Detailed Machine Analysis")
                    for _, row in df_bn.iterrows():
                        with st.expander(f"**{row['machine']}** — {row['status']}"):
                            d1, d2, d3 = st.columns(3)
                            d1.metric("Utilization", f"{row['utilization']:.2f}%")
                            d1.metric("Used Hours",  f"{row['used_hours']:.2f}")
                            d2.metric("Idle Hours",  f"{row['idle_hours']:.2f}")
                            d2.metric("Idle %",      f"{row['idle_percentage']:.2f}%")
                            d3.metric("Operations",  row['num_operations'])
                            d3.metric("Avg Op Time", f"{row['avg_operation_time_hours']:.4f} hrs")
                            st.info(f"**Recommendation:** {row['recommendation']}")

                    st.download_button("📥 Download Bottleneck Analysis (CSV)",
                                       data=df_bn.to_csv(index=False),
                                       file_name="bottleneck_analysis.csv", mime="text/csv")
                else:
                    st.info("No schedule data available for bottleneck analysis.")
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Error loading bottleneck data: {e}")
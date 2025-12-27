import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import json

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Production Analytics Suite",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #333539;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-title {
        color: white;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    .metric-value {
        color: white;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .section-header {
        color: #00ff9f;
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 15px 0;
        padding-left: 10px;
        border-left: 4px solid #00ff9f;
    }
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Production Analytics'
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'filter_options' not in st.session_state:
    st.session_state.filter_options = None
if 'filters_loaded' not in st.session_state:
    st.session_state.filters_loaded = False

API_BASE_URL = st.sidebar.text_input(
    "API Base URL",
    value="http://localhost:8000/api",
    help="Enter your Django API base URL"
)

# Helper functions for Schedule Management
def fetch_data(endpoint, params=None):
    """Fetch data from Django API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def post_data(endpoint, data=None):
    """Post data to Django API"""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error posting data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def generate_timeline_html(df_schedule, start_time, end_time, time_interval_minutes=30):
    """Generate custom timeline HTML with times on Y-axis and machines on X-axis"""
    if df_schedule.empty:
        return "<html><body><p>No schedule data available</p></body></html>"
    
    # Convert times
    df = df_schedule.copy()
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    
    # Get unique machines
    machines = sorted(df['machine_name'].unique())
    num_machines = len(machines)
    
    # Calculate timeline range - ensure timezone consistency
    timeline_start = pd.to_datetime(start_time)
    timeline_end = pd.to_datetime(end_time)
    
    # Check if the dataframe times have timezone info
    if df['start_time'].dt.tz is not None:
        if timeline_start.tz is None:
            timeline_start = timeline_start.tz_localize(df['start_time'].dt.tz)
        if timeline_end.tz is None:
            timeline_end = timeline_end.tz_localize(df['start_time'].dt.tz)
    else:
        if timeline_start.tz is not None:
            timeline_start = timeline_start.tz_localize(None)
        if timeline_end.tz is not None:
            timeline_end = timeline_end.tz_localize(None)
    
    total_hours = (timeline_end - timeline_start).total_seconds() / 3600
    
    # Generate time slots
    time_slots = []
    current_time = timeline_start
    while current_time < timeline_end:
        time_slots.append(current_time)
        current_time += timedelta(minutes=time_interval_minutes)
    
    num_slots = len(time_slots)
    
    # Build complete HTML document with embedded styles
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                margin: 0;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                background: #ffffff;
            }
            
            .timeline-container {
                width: 100%;
                overflow-x: auto;
                overflow-y: auto;
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .timeline-grid {
                display: grid;
                grid-template-rows: auto 1fr;
                min-height: 600px;
                gap: 0;
            }
            
            .machine-header-row {
                display: grid;
                grid-template-columns: 120px repeat(""" + str(num_machines) + """, 200px);
                border-bottom: 2px solid #dee2e6;
                background: #f8f9fa;
                position: sticky;
                top: 0;
                z-index: 10;
            }
            
            .corner-cell {
                padding: 15px;
                background: #e9ecef;
                border-right: 2px solid #dee2e6;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #495057;
            }
            
            .machine-header {
                font-weight: bold;
                padding: 15px;
                text-align: center;
                border-right: 1px solid #e9ecef;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #495057;
                background: #f8f9fa;
            }
            
            .timeline-body {
                display: grid;
                grid-template-columns: 120px repeat(""" + str(num_machines) + """, 200px);
                grid-template-rows: repeat(""" + str(num_slots) + """, 60px);
            }
            
            .time-label {
                padding: 10px 15px;
                background: #f8f9fa;
                border-right: 2px solid #dee2e6;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                justify-content: center;
                font-size: 0.85rem;
                color: #6c757d;
                font-weight: 600;
                position: sticky;
                left: 0;
                z-index: 5;
            }
            
            .time-date {
                font-size: 0.75rem;
                color: #868e96;
            }
            
            .machine-cell {
                border-right: 1px solid #e9ecef;
                border-bottom: 1px solid #e9ecef;
                position: relative;
                background: white;
            }
            
            .schedule-card {
                position: absolute;
                left: 5px;
                right: 5px;
                border-radius: 6px;
                padding: 8px 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                justify-content: center;
                color: white;
                font-size: 0.85rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                overflow: hidden;
                z-index: 2;
            }
            
            .schedule-card:hover {
                transform: scale(1.02);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                z-index: 3;
            }
            
            .card-title {
                font-weight: 600;
                font-size: 0.9rem;
                margin-bottom: 2px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .card-subtitle {
                font-size: 0.75rem;
                opacity: 0.9;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            /* Color schemes for different items */
            .item-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .item-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .item-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .item-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
            .item-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
            .item-6 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
            .item-7 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
            .item-8 { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
            .item-9 { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }
            .item-10 { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); }
            .item-11 { background: linear-gradient(135deg, #fddb92 0%, #d1fdff 100%); }
            .item-12 { background: linear-gradient(135deg, #9890e3 0%, #b1f4cf 100%); }
            .item-13 { background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%); }
            .item-14 { background: linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%); }
            .item-15 { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
            .item-16 { background: linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%); }
            .item-17 { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }
            .item-18 { background: linear-gradient(135deg, #f8b500 0%, #fceabb 100%); }
            .item-19 { background: linear-gradient(135deg, #cfd9df 0%, #e2ebf0 100%); }
            .item-20 { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }
            .item-21 { background: linear-gradient(135deg, #ff8177 0%, #ff867a 100%); }
            .item-22 { background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); }
            .item-23 { background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); }
            .item-24 { background: linear-gradient(135deg, #b24592 0%, #f15f79 100%); }
            .item-25 { background: linear-gradient(135deg, #4568dc 0%, #b06ab3 100%); }
            .item-26 { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
            .item-27 { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); }
            .item-28 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
            .item-29 { background: linear-gradient(135deg, #f77062 0%, #fe5196 100%); }
            .item-30 { background: linear-gradient(135deg, #5ee7df 0%, #b490ca 100%); }
            .item-31 { background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%); }
            .item-32 { background: linear-gradient(135deg, #7f7fd5 0%, #86a8e7 100%); }
            .item-33 { background: linear-gradient(135deg, #e1eec3 0%, #f05053 100%); }
            .item-34 { background: linear-gradient(135deg, #c471ed 0%, #f64f59 100%); }
            .item-35 { background: linear-gradient(135deg, #12c2e9 0%, #c471ed 100%); }
            .item-36 { background: linear-gradient(135deg, #fbc7d4 0%, #9796f0 100%); }
            .item-37 { background: linear-gradient(135deg, #cfd9df 0%, #e2ebf0 100%); }
            .item-38 { background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%); }
            .item-39 { background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%); }
            .item-40 { background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%); }
            .item-41 { background: linear-gradient(135deg, #1fddff 0%, #ff4b1f 100%); }
            .item-42 { background: linear-gradient(135deg, #3a1c71 0%, #d76d77 100%); }
            .item-43 { background: linear-gradient(135deg, #0fd850 0%, #f9f047 100%); }
            .item-44 { background: linear-gradient(135deg, #74ebd5 0%, #acb6e5 100%); }
            .item-45 { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); }
            .item-46 { background: linear-gradient(135deg, #4ca1af 0%, #c4e0e5 100%); }
            .item-47 { background: linear-gradient(135deg, #ff5f6d 0%, #ffc371 100%); }
            .item-48 { background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%); }
            .item-49 { background: linear-gradient(135deg, #ee9ca7 0%, #ffdde1 100%); }
            .item-50 { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); }
            
            .legend {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
            }
            
            .legend-item {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.85rem;
            }
            
            .legend-color {
                width: 30px;
                height: 20px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
    """
    
    html += '<div class="timeline-container">'
    html += '<div class="timeline-grid">'
    
    # Machine header row
    html += '<div class="machine-header-row">'
    html += '<div class="corner-cell">Time / Machine</div>'
    
    for machine in machines:
        html += f'<div class="machine-header">{machine}</div>'
    
    html += '</div>'  # End machine header row
    
    # Timeline body - create grid with time slots as rows and machines as columns
    html += '<div class="timeline-body">'
    
    # Create a mapping of machine to column index for positioning
    machine_to_col = {machine: idx for idx, machine in enumerate(machines)}
    
    # For each time slot
    for slot_idx, time_slot in enumerate(time_slots):
        # Time label cell
        time_str = time_slot.strftime('%H:%M')
        date_str = time_slot.strftime('%m/%d')
        html += f'''
        <div class="time-label">
            <div>{time_str}</div>
            <div class="time-date">{date_str}</div>
        </div>
        '''
        
        # Machine cells for this time slot
        slot_start = time_slot
        slot_end = time_slot + timedelta(minutes=time_interval_minutes)
        
        for machine in machines:
            html += '<div class="machine-cell">'
            
            # Find schedules for this machine that overlap with this time slot
            machine_data = df[df['machine_name'] == machine]
            
            for _, row in machine_data.iterrows():
                sched_start = row['start_time']
                sched_end = row['end_time']
                
                # Check if schedule overlaps with this time slot
                if sched_start < slot_end and sched_end > slot_start:
                    # Calculate vertical position and height
                    # Determine where in this slot the schedule starts and ends
                    display_start = max(sched_start, slot_start)
                    display_end = min(sched_end, slot_end)
                    
                    # Calculate percentage within the slot
                    slot_duration = (slot_end - slot_start).total_seconds()
                    offset_seconds = (display_start - slot_start).total_seconds()
                    duration_seconds = (display_end - display_start).total_seconds()
                    
                    top_percent = (offset_seconds / slot_duration) * 100
                    height_percent = (duration_seconds / slot_duration) * 100
                    
                    # Only show if this is the first slot where this schedule appears
                    if slot_start <= sched_start < slot_end:
                        # Calculate total height across all slots
                        total_duration = (sched_end - sched_start).total_seconds()
                        num_slots_span = total_duration / (time_interval_minutes * 60)
                        total_height_percent = height_percent * num_slots_span
                        
                        item_class = f"item-{row['product_item']}"
                        batch_id = row['batch_id']
                        step_num = row['step_number']
                        step_name = str(row['step_name'])[:30]
                        
                        html += f'''
                        <div class="schedule-card {item_class}" 
                             style="top: {top_percent}%; height: {total_height_percent}%;"
                             title="{batch_id} - Step {step_num}: {step_name}">
                            <div class="card-title">Step {step_num}</div>
                            <div class="card-subtitle">{batch_id}</div>
                        </div>
                        '''
            
            html += '</div>'  # End machine cell
    
    html += '</div>'  # End timeline body
    html += '</div>'  # End timeline grid
    html += '</div>'  # End timeline container
    
    # Add legend
    html += '<div class="legend">'
    items = sorted(df['product_item'].unique())
    for item in items:
        item_desc = df[df['product_item'] == item]['product_description'].iloc[0]
        short_desc = item_desc[:40] + "..." if len(item_desc) > 40 else item_desc
        html += f'''
        <div class="legend-item">
            <div class="legend-color item-{item}"></div>
            <span><strong>Item {item}:</strong> {short_desc}</span>
        </div>
        '''
    html += '</div>'
    
    html += '</body></html>'
    
    return html

def create_gantt_chart(df_schedule):
    """Create Gantt chart for production schedule"""
    if df_schedule.empty:
        return None
    
    df_gantt = df_schedule.copy()
    df_gantt['Start'] = pd.to_datetime(df_gantt['start_time'])
    df_gantt['Finish'] = pd.to_datetime(df_gantt['end_time'])
    df_gantt['Task'] = df_gantt['machine_name']
    df_gantt['Resource'] = df_gantt['batch_id'] + ' - Step ' + df_gantt['step_number'].astype(str)
    
    fig = px.timeline(
        df_gantt,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='product_item',
        hover_data=['batch_id', 'step_name', 'duration_hours', 'product_description'],
        title='Production Schedule Gantt Chart',
        labels={'Task': 'Machine', 'product_item': 'Product Item'},
        color_continuous_scale='Viridis'
    )
    
    fig.update_yaxes(categoryorder='category ascending')
    fig.update_layout(
        height=600,
        xaxis_title='Time',
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

def create_machine_utilization_chart(machine_stats):
    """Create machine utilization bar chart"""
    if not machine_stats:
        return None
    
    machines = [stat['machine'] for stat in machine_stats]
    utilizations = [stat['utilization'] for stat in machine_stats]
    
    fig = go.Figure(data=[
        go.Bar(
            x=machines,
            y=utilizations,
            text=[f"{u:.1f}%" for u in utilizations],
            textposition='auto',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title='Machine Utilization',
        xaxis_title='Machine',
        yaxis_title='Utilization (%)',
        height=400,
        yaxis_range=[0, 100]
    )
    
    return fig


def create_batch_comparison_chart(batch_analysis):
    """Create comparison chart for batch optimization"""
    df = pd.DataFrame(batch_analysis)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Old Method (Fixed 12)',
        x=df['item'],
        y=df['old_num_batches'],
        marker_color='lightcoral',
        text=df['old_num_batches'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name='Optimized Method',
        x=df['item'],
        y=df['new_num_batches'],
        marker_color='lightgreen',
        text=df['new_num_batches'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Batch Count Comparison: Old vs Optimized',
        xaxis_title='Product Item',
        yaxis_title='Number of Batches',
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

# Main Navigation
st.sidebar.title("🏭 Production Suite")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Production Analytics", "📅 Schedule Management", "📊 Buffer Optimization", "🔍 Bottleneck Analysis"],
    key="navigation"
)

st.sidebar.markdown("---")

# PAGE 1: Production Analytics
if page == "📊 Production Analytics":
    st.title("📊 Production Analytics Dashboard")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
            
            if not st.session_state.filters_loaded:
                with st.spinner("Loading filter options..."):
                    uploaded_file.seek(0)
                    try:
                        response = requests.post(
                            "http://127.0.0.1:8000/api/get-filter-options/",
                            files={"file": uploaded_file}
                        )
                        if response.status_code == 200:
                            st.session_state.filter_options = response.json()
                            st.session_state.filters_loaded = True
                    except Exception as e:
                        st.error(f"Error loading filters: {str(e)}")
        
        num_shifts = st.number_input(
            "Number of shifts",
            min_value=1,
            max_value=200,
            value=28,
            help="Enter the total number of shifts to analyze"
        )
        
        # Data Filters Section
        if st.session_state.filters_loaded and st.session_state.filter_options:
            st.markdown("---")
            st.subheader("🔍 Data Filters")
            st.markdown("*Filter data by specific criteria*")
            
            filter_opts = st.session_state.filter_options
            
            selected_pps_tn = st.selectbox(
                "PPS TN",
                ["All"] + filter_opts.get('PPS TN', []),
                help="Filter by PPS TN"
            )
            
            selected_project = st.selectbox(
                "Project",
                ["All"] + filter_opts.get('Project', []),
                help="Filter by Project"
            )
            
            selected_sub_project = st.selectbox(
                "Sub-Project",
                ["All"] + filter_opts.get('Sub-Project', []),
                help="Filter by Sub-Project"
            )
            
            selected_machine = st.selectbox(
                "Machine",
                ["All"] + filter_opts.get('Machine', []),
                help="Filter by Machine"
            )
            
            selected_tool_no = st.selectbox(
                "Tool No.",
                ["All"] + filter_opts.get('Tool No.', []),
                help="Filter by Tool Number"
            )
            
            selected_area = st.selectbox(
                "Area",
                ["All"] + filter_opts.get('Area', []),
                help="Filter by Area"
            )
        else:
            selected_pps_tn = "All"
            selected_project = "All"
            selected_sub_project = "All"
            selected_machine = "All"
            selected_tool_no = "All"
            selected_area = "All"

    # Submit button
    if st.sidebar.button("🚀 Process & Analyze", type="primary", use_container_width=True):
        if uploaded_file:
            with st.spinner("🔄 Processing data with selected filters..."):
                uploaded_file.seek(0)
                try:
                    filter_data = {
                        "num_shifts": num_shifts,
                        "pps_tn": selected_pps_tn,
                        "project": selected_project,
                        "sub_project": selected_sub_project,
                        "machine": selected_machine,
                        "tool_no": selected_tool_no,
                        "area": selected_area
                    }
                    
                    response = requests.post(
                        "http://127.0.0.1:8000/api/process-csv/",
                        data=filter_data,
                        files={"file": uploaded_file}
                    )
                    
                    if response.status_code == 200:
                        st.session_state.data = response.json()
                        st.session_state.processed = True
                        st.sidebar.success("✅ Analysis complete!")
                        
                        active_filters = []
                        if selected_pps_tn != "All":
                            active_filters.append(f"PPS TN: {selected_pps_tn}")
                        if selected_project != "All":
                            active_filters.append(f"Project: {selected_project}")
                        if selected_sub_project != "All":
                            active_filters.append(f"Sub-Project: {selected_sub_project}")
                        if selected_machine != "All":
                            active_filters.append(f"Machine: {selected_machine}")
                        if selected_tool_no != "All":
                            active_filters.append(f"Tool No.: {selected_tool_no}")
                        if selected_area != "All":
                            active_filters.append(f"Area: {selected_area}")
                        
                        if active_filters:
                            st.sidebar.info("**Active Filters:**\n" + "\n".join([f"- {f}" for f in active_filters]))
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        else:
            st.warning("⚠️ Please upload a file first.")

    # Main content
    if st.session_state.processed and st.session_state.data:
        data = st.session_state.data
        shift_data = data["ShiftWise"]
        summary_data = data["Summary"]
        
        df_shift = pd.DataFrame(shift_data).T
        df_summary = pd.DataFrame(summary_data)
        
        # Additional sidebar filters for visualization
        with st.sidebar:
            st.markdown("---")
            st.subheader("📊 Display Options")
            
            metrics = list(shift_data.keys())
            selected_metrics = st.multiselect(
                "Select Metrics to Display",
                metrics,
                default=metrics
            )
            
            all_shifts = list(shift_data[metrics[0]].keys())
            shift_range = st.select_slider(
                "Select Shift Range",
                options=all_shifts,
                value=(all_shifts[0], all_shifts[-1])
            )
            
            chart_type = st.selectbox(
                "Primary Chart Type",
                ["Line Chart", "Bar Chart", "Area Chart", "Combined"]
            )
        
        start_idx = all_shifts.index(shift_range[0])
        end_idx = all_shifts.index(shift_range[1]) + 1
        filtered_shifts = all_shifts[start_idx:end_idx]
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Production Charts", "⚡ Efficiency Analysis", "📋 Data Tables", "📥 Downloads"])
        
        with tab1:
            st.subheader("Production Output Analysis")
            
            summary_metrics = df_summary['Metric'].tolist()
            fg_summary_str = df_summary['Finished Goods'].tolist()
            conn_summary_str = df_summary['Connectors'].tolist()
            
            fg_summary = [float(val.replace(',', '')) for val in fg_summary_str]
            conn_summary = [float(val.replace(',', '')) for val in conn_summary_str]
            
            # Finished Goods Section
            st.markdown('<div class="section-header">🎯 Finished Goods</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card metric-card-blue">
                    <div class="metric-title">📋 {summary_metrics[0]}</div>
                    <div class="metric-value">{fg_summary_str[0]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card metric-card-green">
                    <div class="metric-title">✅ {summary_metrics[1]}</div>
                    <div class="metric-value">{fg_summary_str[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="metric-card metric-card-orange">
                    <div class="metric-title">⏳ {summary_metrics[2]}</div>
                    <div class="metric-value">{fg_summary_str[2]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📂 {summary_metrics[3]}</div>
                    <div class="metric-value">{fg_summary_str[3]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if fg_summary[0] > 0:
                fg_progress = (fg_summary[1] / fg_summary[0]) * 100
                st.markdown("**Production Progress**")
                st.progress(min(fg_progress / 100, 1.0))
                st.markdown(f"<p style='text-align: center; color: #00ff9f; font-weight: bold;'>{fg_progress:.1f}% Complete ({fg_summary_str[1]} / {fg_summary_str[0]})</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Connectors Section
            st.markdown('<div class="section-header">🔌 Connectors</div>', unsafe_allow_html=True)
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.markdown(f"""
                <div class="metric-card metric-card-blue">
                    <div class="metric-title">📋 {summary_metrics[0]}</div>
                    <div class="metric-value">{conn_summary_str[0]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div class="metric-card metric-card-green">
                    <div class="metric-title">✅ {summary_metrics[1]}</div>
                    <div class="metric-value">{conn_summary_str[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col7:
                st.markdown(f"""
                <div class="metric-card metric-card-orange">
                    <div class="metric-title">⏳ {summary_metrics[2]}</div>
                    <div class="metric-value">{conn_summary_str[2]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col8:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📂 {summary_metrics[3]}</div>
                    <div class="metric-value">{conn_summary_str[3]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if conn_summary[0] > 0:
                conn_progress = (conn_summary[1] / conn_summary[0]) * 100
                st.markdown("**Production Progress**")
                st.progress(min(conn_progress / 100, 1.0))
                st.markdown(f"<p style='text-align: center; color: #ff6b9d; font-weight: bold;'>{conn_progress:.1f}% Complete ({conn_summary_str[1]} / {conn_summary_str[0]})</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Prepare data for charts
            fg_values = []
            conn_values = []
            backlog_values = []
            
            for shift in filtered_shifts:
                fg_val = shift_data['Production Output Finished Goods'][shift].replace(',', '')
                conn_val = shift_data['Production Output Connectors'][shift].replace(',', '')
                backlog_val = shift_data['Total Backlog Finished Goods'][shift].replace(',', '')
                
                fg_values.append(float(fg_val) if fg_val != '0' else 0)
                conn_values.append(float(conn_val) if conn_val != '0' else 0)
                backlog_values.append(float(backlog_val) if backlog_val != '0' else 0)
            
            # Create production chart based on selection
            if chart_type == "Line Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_values, name='Finished Goods',
                                            mode='lines+markers', line=dict(color='#00ff9f', width=3)))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_values, name='Connectors',
                                            mode='lines+markers', line=dict(color='#ff6b9d', width=3)))
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_values, name='Backlog',
                                            mode='lines+markers', line=dict(color='#ffa500', width=3)))
            
            elif chart_type == "Bar Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=fg_values, name='Finished Goods',
                                        marker_color='#00ff9f'))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=conn_values, name='Connectors',
                                        marker_color='#ff6b9d'))
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=backlog_values, name='Backlog',
                                        marker_color='#ffa500'))
                fig.update_layout(barmode='group')
            
            elif chart_type == "Area Chart":
                fig = go.Figure()
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_values, name='Finished Goods',
                                            fill='tozeroy', line=dict(color='#00ff9f')))
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_values, name='Connectors',
                                            fill='tozeroy', line=dict(color='#ff6b9d')))
            
            else:  # Combined
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                if 'Production Output Finished Goods' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=fg_values, name='Finished Goods',
                                        marker_color='#00ff9f'), secondary_y=False)
                if 'Production Output Connectors' in selected_metrics:
                    fig.add_trace(go.Bar(x=filtered_shifts, y=conn_values, name='Connectors',
                                        marker_color='#ff6b9d'), secondary_y=False)
                if 'Total Backlog Finished Goods' in selected_metrics:
                    fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_values, name='Backlog',
                                            mode='lines+markers', line=dict(color='#ffa500', width=3)),
                                secondary_y=True)
            
            fig.update_layout(
                template='plotly_dark',
                height=500,
                xaxis_title="Shifts",
                yaxis_title="Quantity",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Production by Category")
                total_fg_prod = sum(fg_values)
                total_conn_prod = sum(conn_values)
                
                pie_fig = go.Figure(data=[go.Pie(
                    labels=['Finished Goods', 'Connectors'],
                    values=[total_fg_prod, total_conn_prod],
                    hole=0.4,
                    marker_colors=['#00ff9f', '#ff6b9d']
                )])
                pie_fig.update_layout(template='plotly_dark', height=350)
                st.plotly_chart(pie_fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Cumulative Production")
                cumulative_fg = [sum(fg_values[:i+1]) for i in range(len(fg_values))]
                cumulative_conn = [sum(conn_values[:i+1]) for i in range(len(conn_values))]
                
                cum_fig = go.Figure()
                cum_fig.add_trace(go.Scatter(x=filtered_shifts, y=cumulative_fg, name='Finished Goods',
                                            fill='tozeroy', line=dict(color='#00ff9f')))
                cum_fig.add_trace(go.Scatter(x=filtered_shifts, y=cumulative_conn, name='Connectors',
                                            fill='tozeroy', line=dict(color='#ff6b9d')))
                cum_fig.update_layout(template='plotly_dark', height=350)
                st.plotly_chart(cum_fig, use_container_width=True)
        
        with tab2:
            st.subheader("⚡ Overall Efficiency Analysis")
            
            efficiency_values = []
            efficiency_labels = []
            
            for shift in filtered_shifts:
                eff_str = shift_data['Overall Efficiency'][shift]
                if eff_str != '-':
                    eff_val = float(eff_str.replace('%', ''))
                    efficiency_values.append(eff_val)
                    efficiency_labels.append(shift)
            
            eff_fig = go.Figure()
            eff_fig.add_trace(go.Scatter(
                x=efficiency_labels, 
                y=efficiency_values,
                mode='lines+markers',
                name='Efficiency %',
                line=dict(color='#00d4ff', width=4),
                marker=dict(size=10, symbol='diamond'),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 255, 0.2)'
            ))
            
            eff_fig.add_hline(y=100, line_dash="dash", line_color="green", 
                             annotation_text="Target: 100%")
            
            eff_fig.update_layout(
                template='plotly_dark',
                height=400,
                xaxis_title="Shifts",
                yaxis_title="Efficiency %",
                hovermode='x unified'
            )
            
            st.plotly_chart(eff_fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            if efficiency_values:
                with col1:
                    st.metric("Average Efficiency", f"{sum(efficiency_values)/len(efficiency_values):.2f}%")
                with col2:
                    st.metric("Maximum Efficiency", f"{max(efficiency_values):.2f}%")
                with col3:
                    st.metric("Minimum Efficiency", f"{min(efficiency_values):.2f}%")
                with col4:
                    above_target = sum(1 for e in efficiency_values if e >= 100)
                    st.metric("Shifts ≥100%", f"{above_target}/{len(efficiency_values)}")
            
            st.markdown("#### 📊 Efficiency Distribution")
            hist_fig = go.Figure(data=[go.Histogram(
                x=efficiency_values,
                nbinsx=10,
                marker_color='#00d4ff',
                opacity=0.75
            )])
            hist_fig.update_layout(
                template='plotly_dark',
                height=300,
                xaxis_title="Efficiency %",
                yaxis_title="Frequency"
            )
            st.plotly_chart(hist_fig, use_container_width=True)
        
        with tab3:
            st.subheader("📋 Detailed Data Tables")
            st.markdown("#### Shift-wise Production & Efficiency")
            
            filtered_df = df_shift[filtered_shifts].copy()
            
            if selected_metrics:
                available_metrics = [metric for metric in selected_metrics if metric in filtered_df.index]
                if available_metrics:
                    filtered_df = filtered_df.loc[available_metrics]
            
            st.dataframe(filtered_df, use_container_width=True, height=400)
        
        with tab4:
            st.subheader("📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Full Shift-wise Data")
                csv_data = df_shift.to_csv(index=True)
                st.download_button(
                    label="📥 Download Full Dataset (CSV)",
                    data=csv_data,
                    file_name="shiftwise_production_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("#### Summary Report")
                csv_summary = df_summary.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary (CSV)",
                    data=csv_summary,
                    file_name="production_summary.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("#### Filtered Data")
            filtered_csv = filtered_df.to_csv(index=True)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=filtered_csv,
                file_name="filtered_production_data.csv",
                mime="text/csv",
                use_container_width=True
            )

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

# PAGE 2: Schedule Management
elif page == "📅 Schedule Management":
    st.markdown('<div class="main-header">🏭 Production Schedule Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimized Machine Time Allocation</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Controls")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Init Data", use_container_width=True):
            with st.spinner("Initializing database..."):
                result = post_data("initialize-data")
                if result:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
    
    with col2:
        if st.button("📅 Generate Schedule", use_container_width=True):
            with st.spinner("Generating schedule..."):
                result = post_data("generate-schedule")
                if result:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
    
    st.sidebar.markdown("---")
    
    # Batch Size Optimization Section
    st.sidebar.subheader("📦 Batch Size Optimization")
    
    with st.sidebar.expander("⚙️ Configure Batch Parameters", expanded=False):
        st.markdown("**Adjust batch size constraints:**")
        
        max_num_batches = st.number_input(
            "Max Number of Batches",
            min_value=1,
            max_value=50,
            value=25,
            step=1,
            help="Maximum number of batches allowed per product"
        )
        
        min_batch_size = st.number_input(
            "Min Batch Size (units)",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="Minimum size per batch"
        )
        
        max_batch_size = st.number_input(
            "Max Batch Size (units)",
            min_value=100,
            max_value=1000,
            value=500,
            step=50,
            help="Maximum size per batch"
        )
        
        if st.button("🔍 Preview Optimization", use_container_width=True):
            with st.spinner("Calculating optimal batch sizes..."):
                params = {
                    'max_num_batches': max_num_batches,
                    'min_batch_size': min_batch_size,
                    'max_batch_size': max_batch_size
                }
                batch_preview = fetch_data("batch-optimization-preview", params)
                
                if batch_preview:
                    st.session_state['batch_preview'] = batch_preview
                    st.success("✅ Optimization preview ready!")
    

    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    filter_options = fetch_data("get-filter-options")
    
    if filter_options:
        machines = ['All'] + filter_options.get('machines', [])
        selected_machine_sched = st.sidebar.selectbox("Select Machine(s)", machines)
        
        products = filter_options.get('products', [])
        product_options = ['All'] + [f"Item {p['item']}: {p['description'][:30]}..." for p in products]
        selected_product_sched = st.sidebar.selectbox("Select Product", product_options)
        
        date_range = filter_options.get('date_range', {})
        if date_range.get('min') and date_range.get('max'):
            min_date = pd.to_datetime(date_range['min']).date()
            max_date = pd.to_datetime(date_range['max']).date()
            
            st.sidebar.subheader("📆 Time Range")
            start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
            end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        else:
            start_date = None
            end_date = None
    else:
        selected_machine_sched = 'All'
        selected_product_sched = 'All'
        start_date = None
        end_date = None
    
    st.sidebar.markdown("---")
    
    # Timeline settings
    st.sidebar.subheader("⏱️ Timeline View Settings")
    time_interval_minutes = st.sidebar.slider("Time Interval (minutes)", 1, 120, 5, step=1)
    
    # Display Batch Optimization Preview if available
    if 'batch_preview' in st.session_state:
        st.markdown("---")
        st.subheader("📦 Batch Size Optimization Preview")
        
        batch_data = st.session_state['batch_preview']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{batch_data['summary']['total_batches']}</div>
                    <div class="kpi-label">Total Batches</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{batch_data['summary']['avg_batch_size']:.0f}</div>
                    <div class="kpi-label">Avg Batch Size</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{batch_data['summary']['min_batch_size']}-{batch_data['summary']['max_batch_size']}</div>
                    <div class="kpi-label">Batch Size Range</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{batch_data['summary']['total_demand']:,}</div>
                    <div class="kpi-label">Total Demand</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Batch comparison chart
        st.subheader("📊 Batch Count Comparison")
        batch_chart = create_batch_comparison_chart(batch_data['batch_analysis'])
        if batch_chart:
            st.plotly_chart(batch_chart, use_container_width=True)
        
        # Detailed batch analysis table
        st.subheader("📋 Detailed Batch Analysis")
        
        df_batch = pd.DataFrame(batch_data['batch_analysis'])
        df_batch_display = df_batch[[
            'item', 'description', 'demand',
            'old_batch_size', 'old_num_batches',
            'new_batch_size', 'new_num_batches',
            'ideal_batch_size', 'improvement'
        ]].copy()
        
        df_batch_display.columns = [
            'Item', 'Description', 'Demand',
            'Old Batch Size', 'Old Batches',
            'New Batch Size', 'New Batches',
            'Ideal Size', 'Improvement'
        ]
        
        st.dataframe(df_batch_display, use_container_width=True, height=400)
        
        # Download batch analysis
        csv_batch = df_batch_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Batch Analysis CSV",
            data=csv_batch,
            file_name=f"batch_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Info box with parameters
        st.info(f"""
        **Current Parameters:**
        - Max Batches: {batch_data['parameters']['max_num_batches']}
        - Min Batch Size: {batch_data['parameters']['min_batch_size']} units
        - Max Batch Size: {batch_data['parameters']['max_batch_size']} units
        
        💡 The optimization algorithm calculates an **ideal batch size** based on demand and divides it by the max number of batches. 
        It then adjusts to stay within min/max constraints while minimizing total batches needed.
        """)
        
        st.markdown("---")
    
    # Fetch schedule data
    params = {}
    if selected_machine_sched != 'All':
        params['machine'] = selected_machine_sched
    if selected_product_sched != 'All':
        product_item = int(selected_product_sched.split(':')[0].replace('Item ', ''))
        params['product'] = product_item
    # if start_date:
    #     params['start_date'] = start_date.isoformat()
    # if end_date:
    #     params['end_date'] = end_date.isoformat()
    
    schedule_data = fetch_data("get-schedule", params)
    kpi_data = fetch_data("get-kpis")
    
    if not schedule_data or not schedule_data.get('schedules'):
        st.warning("⚠️ No schedule data available. Please initialize data and generate schedule.")
    else:
        df_schedule = pd.DataFrame(schedule_data['schedules'])
        
        # KPIs Section
        st.subheader("📊 Key Performance Indicators")
        
        if kpi_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value">{kpi_data.get('total_makespan_days', 0):.1f}</div>
                        <div class="kpi-label">Total Makespan (Days)</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_utilization = sum([m['utilization'] for m in kpi_data.get('machine_utilization', [])]) / max(len(kpi_data.get('machine_utilization', [])), 1)
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value">{avg_utilization:.1f}%</div>
                        <div class="kpi-label">Avg Machine Utilization</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value">{kpi_data.get('total_operations', 0)}</div>
                        <div class="kpi-label">Number of Operations</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value">{kpi_data.get('throughput_units_per_day', 0):.0f}</div>
                        <div class="kpi-label">Throughput (units/day)</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Timeline View", "📈 Gantt Chart", "📋 Table View", "🔧 Machine Details"])
        
        with tab1:
            st.subheader("Production Timeline Schedule")
            
            if start_date and end_date:
                timeline_start = datetime.combine(start_date, datetime.min.time())
                timeline_end = datetime.combine(end_date, datetime.max.time())
            else:
                timeline_start = pd.to_datetime(df_schedule['start_time']).min()
                timeline_end = pd.to_datetime(df_schedule['end_time']).max()
            
            timeline_html = generate_timeline_html(df_schedule, timeline_start, timeline_end, time_interval_minutes)
            components.html(timeline_html, height=800, scrolling=True)
            
            st.info("💡 Hover over cards to see full details. Scroll horizontally to view the entire timeline.")
        
        with tab2:
            st.subheader("Production Schedule Gantt Chart")
            gantt_fig = create_gantt_chart(df_schedule)
            if gantt_fig:
                st.plotly_chart(gantt_fig, use_container_width=True)
            else:
                st.info("No data available for Gantt chart")
        
        with tab3:
            st.subheader("Schedule Table View")
            
            display_cols = [
                'machine_name', 'product_item', 'product_sap_tn', 'product_dcc_type',
                'batch_id', 'step_number', 'step_name', 'workers_required',
                'start_time', 'end_time', 'duration_hours'
            ]
            
            df_display = df_schedule[display_cols].copy()
            df_display['start_time'] = pd.to_datetime(df_display['start_time']).dt.strftime('%Y-%m-%d %H:%M')
            df_display['end_time'] = pd.to_datetime(df_display['end_time']).dt.strftime('%Y-%m-%d %H:%M')
            
            df_display.columns = [
                'Machine', 'Item', 'SAP TN', 'DCC Type', 'Batch ID',
                'Step', 'Step Name', 'Workers', 'Start Time', 'End Time', 'Duration (h)'
            ]
            
            st.dataframe(df_display, use_container_width=True, height=600)
            
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Schedule CSV",
                data=csv,
                file_name=f"production_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tab4:
            st.subheader("Machine Utilization Details")
            
            if kpi_data and kpi_data.get('machine_utilization'):
                util_fig = create_machine_utilization_chart(kpi_data['machine_utilization'])
                if util_fig:
                    st.plotly_chart(util_fig, use_container_width=True)
                
                st.subheader("Machine Statistics")
                machine_stats_df = pd.DataFrame(kpi_data['machine_utilization'])
                machine_stats_df.columns = ['Machine', 'Used Hours', 'Utilization (%)', 'Num Operations']
                st.dataframe(machine_stats_df, use_container_width=True)
            else:
                st.info("No machine statistics available")
        
        # Footer
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total schedules: {len(df_schedule)}")

elif page == "📊 Buffer Optimization":
    st.header("Buffer Optimization Analysis")
    
    # Safety factor input
    col1, col2 = st.columns([1, 3])
    with col1:
        safety_factor = st.number_input(
            "Safety Factor",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Multiplier for buffer calculations (higher = more conservative)"
        )
    
    with col2:
        if st.button("🔄 Load Buffer Data", type="primary"):
            st.session_state.load_buffer = True
    
    # Fetch buffer optimization data
    if st.session_state.get('load_buffer', False):
        try:
            response = requests.get(
                f"{API_BASE_URL}/buffer-optimization/",
                params={'safety_factor': safety_factor},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'buffer_recommendations' in data and data['buffer_recommendations']:
                    # Display parameters
                    st.subheader("📈 Production Parameters")
                    params = data['parameters']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Throughput/Hour", f"{params['throughput_per_hour']:.2f} units")
                    col2.metric("Makespan", f"{params['makespan_hours']:.2f} hours")
                    col3.metric("Safety Factor", f"{params['safety_factor']}")
                    col4.metric("Total Units", f"{params['total_units']}")
                    
                    st.info(f"**Formula:** {data['formula']}")
                    
                    # Convert to DataFrame
                    df_buffer = pd.DataFrame(data['buffer_recommendations'])
                    
                    # Display metrics
                    st.subheader("🎯 Buffer Recommendations by Machine")
                    
                    # Create visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Bar chart: Buffer sizes
                        fig_buffer = px.bar(
                            df_buffer,
                            x='machine',
                            y='buffer_size_units',
                            color='recommendation',
                            title="Recommended Buffer Sizes by Machine",
                            labels={'buffer_size_units': 'Buffer Size (units)', 'machine': 'Machine'},
                            color_discrete_map={
                                'HIGH PRIORITY': '#ef4444',
                                'MEDIUM PRIORITY': '#f59e0b',
                                'LOW PRIORITY': '#10b981'
                            }
                        )
                        fig_buffer.update_layout(showlegend=True)
                        st.plotly_chart(fig_buffer, use_container_width=True)
                    
                    with col2:
                        # Scatter plot: Utilization vs Buffer Size
                        fig_scatter = px.scatter(
                            df_buffer,
                            x='utilization',
                            y='buffer_size_units',
                            size='total_operations',
                            color='recommendation',
                            hover_data=['machine', 'avg_operation_time_hours'],
                            title="Utilization vs Buffer Requirements",
                            labels={
                                'utilization': 'Utilization (%)',
                                'buffer_size_units': 'Buffer Size (units)'
                            },
                            color_discrete_map={
                                'HIGH PRIORITY': '#ef4444',
                                'MEDIUM PRIORITY': '#f59e0b',
                                'LOW PRIORITY': '#10b981'
                            }
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    # Detailed table
                    st.subheader("📋 Detailed Buffer Recommendations")
                    
                    # Format the dataframe for display
                    df_display = df_buffer.copy()
                    df_display['buffer_size_units'] = df_display['buffer_size_units'].round(2)
                    df_display['utilization'] = df_display['utilization'].apply(lambda x: f"{x:.2f}%")
                    df_display['avg_operation_time_hours'] = df_display['avg_operation_time_hours'].round(4)
                    
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        column_config={
                            "recommendation": st.column_config.TextColumn(
                                "Priority",
                                width="medium"
                            )
                        }
                    )
                    
                    # Download button
                    csv = df_buffer.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Buffer Data (CSV)",
                        data=csv,
                        file_name="buffer_recommendations.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No schedule data available for buffer optimization.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
        except Exception as e:
            st.error(f"Error loading buffer data: {str(e)}")

elif page == "🔍 Bottleneck Analysis":
    st.header("Bottleneck Analysis")
    
    if st.button("🔄 Load Bottleneck Data", type="primary"):
        st.session_state.load_bottleneck = True
    
    # Fetch bottleneck analysis data
    if st.session_state.get('load_bottleneck', False):
        try:
            response = requests.get(
                f"{API_BASE_URL}/bottleneck-analysis/",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'machine_analysis' in data and data['machine_analysis']:
                    # Display summary
                    st.subheader("📊 Overall Summary")
                    summary = data['summary']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Makespan", f"{summary['total_makespan_hours']:.2f} hrs")
                    col2.metric("Bottleneck Machine", summary['bottleneck_machine'])
                    col3.metric("Bottleneck Utilization", f"{summary['bottleneck_utilization']:.2f}%")
                    col4.metric("Average Utilization", f"{summary['avg_utilization']:.2f}%")
                    
                    # Convert to DataFrame
                    df_bottleneck = pd.DataFrame(data['machine_analysis'])
                    
                    # Visualizations
                    st.subheader("🎯 Machine Utilization Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Horizontal bar chart: Utilization by machine
                        fig_util = go.Figure()
                        
                        colors = []
                        for status in df_bottleneck['status']:
                            if 'CRITICAL' in status:
                                colors.append('#ef4444')
                            elif 'POTENTIAL' in status:
                                colors.append('#f59e0b')
                            elif 'WELL' in status:
                                colors.append('#10b981')
                            else:
                                colors.append('#6b7280')
                        
                        fig_util.add_trace(go.Bar(
                            y=df_bottleneck['machine'],
                            x=df_bottleneck['utilization'],
                            orientation='h',
                            marker=dict(color=colors),
                            text=df_bottleneck['utilization'].apply(lambda x: f"{x:.1f}%"),
                            textposition='auto'
                        ))
                        
                        fig_util.update_layout(
                            title="Machine Utilization (%)",
                            xaxis_title="Utilization (%)",
                            yaxis_title="Machine",
                            showlegend=False,
                            height=400
                        )
                        
                        st.plotly_chart(fig_util, use_container_width=True)
                    
                    with col2:
                        # Pie chart: Status distribution
                        status_counts = df_bottleneck['status'].value_counts()
                        fig_pie = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Machine Status Distribution",
                            color=status_counts.index,
                            color_discrete_map={
                                'CRITICAL BOTTLENECK': '#ef4444',
                                'POTENTIAL BOTTLENECK': '#f59e0b',
                                'WELL UTILIZED': '#10b981',
                                'UNDERUTILIZED': '#6b7280'
                            }
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Time utilization breakdown
                    st.subheader("⏱️ Time Utilization Breakdown")
                    
                    fig_time = go.Figure()
                    
                    fig_time.add_trace(go.Bar(
                        name='Used Hours',
                        y=df_bottleneck['machine'],
                        x=df_bottleneck['used_hours'],
                        orientation='h',
                        marker_color='#3b82f6'
                    ))
                    
                    fig_time.add_trace(go.Bar(
                        name='Idle Hours',
                        y=df_bottleneck['machine'],
                        x=df_bottleneck['idle_hours'],
                        orientation='h',
                        marker_color='#e5e7eb'
                    ))
                    
                    fig_time.update_layout(
                        barmode='stack',
                        title="Used vs Idle Hours by Machine",
                        xaxis_title="Hours",
                        yaxis_title="Machine",
                        height=400
                    )
                    
                    st.plotly_chart(fig_time, use_container_width=True)
                    
                    # Detailed machine analysis
                    st.subheader("📋 Detailed Machine Analysis")
                    
                    for _, row in df_bottleneck.iterrows():
                        with st.expander(f"**{row['machine']}** - {row['status']}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Utilization", f"{row['utilization']:.2f}%")
                                st.metric("Used Hours", f"{row['used_hours']:.2f}")
                            
                            with col2:
                                st.metric("Idle Hours", f"{row['idle_hours']:.2f}")
                                st.metric("Idle %", f"{row['idle_percentage']:.2f}%")
                            
                            with col3:
                                st.metric("Operations", row['num_operations'])
                                st.metric("Avg Op Time", f"{row['avg_operation_time_hours']:.4f} hrs")
                            
                            st.info(f"**Recommendation:** {row['recommendation']}")
                    
                    # Download button
                    csv = df_bottleneck.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Bottleneck Analysis (CSV)",
                        data=csv,
                        file_name="bottleneck_analysis.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No schedule data available for bottleneck analysis.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
        except Exception as e:
            st.error(f"Error loading bottleneck data: {str(e)}")
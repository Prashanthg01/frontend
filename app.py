import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="CSV Production Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Production Analytics Dashboard")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'filter_options' not in st.session_state:
    st.session_state.filter_options = None
if 'filters_loaded' not in st.session_state:
    st.session_state.filters_loaded = False

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")
        
        # Load filter options if not already loaded
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
        
        # PPS TN Filter
        pps_tn_options = ["All"] + filter_opts.get('PPS TN', [])
        selected_pps_tn = st.selectbox(
            "PPS TN",
            pps_tn_options,
            help="Filter by PPS TN"
        )
        
        # Project Filter
        project_options = ["All"] + filter_opts.get('Project', [])
        selected_project = st.selectbox(
            "Project",
            project_options,
            help="Filter by Project"
        )
        
        # Sub-Project Filter
        sub_project_options = ["All"] + filter_opts.get('Sub-Project', [])
        selected_sub_project = st.selectbox(
            "Sub-Project",
            sub_project_options,
            help="Filter by Sub-Project"
        )
        
        # Machine Filter
        machine_options = ["All"] + filter_opts.get('Machine', [])
        selected_machine = st.selectbox(
            "Machine",
            machine_options,
            help="Filter by Machine"
        )
        
        # Tool No. Filter
        tool_no_options = ["All"] + filter_opts.get('Tool No.', [])
        selected_tool_no = st.selectbox(
            "Tool No.",
            tool_no_options,
            help="Filter by Tool Number"
        )
        
        # Area Filter
        area_options = ["All"] + filter_opts.get('Area', [])
        selected_area = st.selectbox(
            "Area",
            area_options,
            help="Filter by Area"
        )
    else:
        # Default values when no file is uploaded
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
                # Prepare filter data
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
                    
                    # Show active filters
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
    
    # Create dataframes
    df_shift = pd.DataFrame(shift_data).T
    df_summary = pd.DataFrame(summary_data)
    
    # Additional sidebar filters for visualization
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 Display Options")
        
        # Metric selection
        metrics = list(shift_data.keys())
        selected_metrics = st.multiselect(
            "Select Metrics to Display",
            metrics,
            default=metrics
        )
        
        # Shift range filter
        all_shifts = list(shift_data[metrics[0]].keys())
        shift_range = st.select_slider(
            "Select Shift Range",
            options=all_shifts,
            value=(all_shifts[0], all_shifts[-1])
        )
        
        # Chart type selection
        chart_type = st.selectbox(
            "Primary Chart Type",
            ["Line Chart", "Bar Chart", "Area Chart", "Combined"]
        )
    
    # Filter data based on shift range
    start_idx = all_shifts.index(shift_range[0])
    end_idx = all_shifts.index(shift_range[1]) + 1
    filtered_shifts = all_shifts[start_idx:end_idx]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Production Charts", "⚡ Efficiency Analysis", "📋 Data Tables", "📥 Downloads"])
    
    with tab1:
        st.subheader("Production Output Analysis")
        
        # Extract summary values and convert to numeric
        summary_metrics = df_summary['Metric'].tolist()
        fg_summary_str = df_summary['Finished Goods'].tolist()
        conn_summary_str = df_summary['Connectors'].tolist()
        
        # Convert string values to numeric (remove commas)
        fg_summary = [float(val.replace(',', '')) for val in fg_summary_str]
        conn_summary = [float(val.replace(',', '')) for val in conn_summary_str]
        
        # Custom CSS for better card styling
        st.markdown("""
        <style>
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
        </style>
        """, unsafe_allow_html=True)
        
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
        
        # Progress bar for Finished Goods
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
        
        # Progress bar for Connectors
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
        
        # Extract efficiency data
        efficiency_values = []
        efficiency_labels = []
        
        for shift in filtered_shifts:
            eff_str = shift_data['Overall Efficiency'][shift]
            if eff_str != '-':
                eff_val = float(eff_str.replace('%', ''))
                efficiency_values.append(eff_val)
                efficiency_labels.append(shift)
        
        # Efficiency line chart
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
        
        # Add target line at 100%
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
        
        # Efficiency statistics
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
        
        # Efficiency distribution
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
        
        # Shift-wise data
        st.markdown("#### Shift-wise Production & Efficiency")
        
        filtered_df = df_shift[filtered_shifts].copy()
        
        if selected_metrics:
            available_metrics = [metric for metric in selected_metrics if metric in filtered_df.index]
            if available_metrics:
                filtered_df = filtered_df.loc[available_metrics]
        
        st.dataframe(filtered_df, use_container_width=True, height=200)
    
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
        
        # Filtered data download
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
    # Welcome screen
    st.markdown("""
    👋 Welcome to Production Analytics Dashboard
    """)
# import streamlit as st
# import requests
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from plotly.subplots import make_subplots
# import warnings

# # Suppress warnings
# warnings.filterwarnings('ignore')

# # Page configuration
# st.set_page_config(
#     page_title="CSV Production Analyzer",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .main {
#         background-color: #0e1117;
#     }
#     .stMetric {
#         background-color: #f0f2f6;
#         padding: 15px;
#         border-radius: 10px;
#     }
#     h1, h2, h3 {
#         color: #ffffff;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.title("📊 Production Analytics Dashboard")

# # Initialize session state
# if 'data' not in st.session_state:
#     st.session_state.data = None
# if 'processed' not in st.session_state:
#     st.session_state.processed = False
# if 'filter_options' not in st.session_state:
#     st.session_state.filter_options = None
# if 'filters_loaded' not in st.session_state:
#     st.session_state.filters_loaded = False

# # Sidebar
# with st.sidebar:
#     st.header("⚙️ Configuration")
#     uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
#     if uploaded_file is not None:
#         st.success("✅ File uploaded successfully!")
        
#         # Load filter options if not already loaded
#         if not st.session_state.filters_loaded:
#             with st.spinner("Loading filter options..."):
#                 uploaded_file.seek(0)
#                 try:
#                     response = requests.post(
#                         "http://127.0.0.1:8000/api/get-filter-options/",
#                         files={"file": uploaded_file}
#                     )
#                     if response.status_code == 200:
#                         st.session_state.filter_options = response.json()
#                         st.session_state.filters_loaded = True
#                 except Exception as e:
#                     st.error(f"Error loading filters: {str(e)}")
    
#     num_shifts = st.number_input(
#         "Number of shifts",
#         min_value=1,
#         max_value=200,
#         value=28,
#         help="Enter the total number of shifts to analyze"
#     )
    
#     # Data Filters Section
#     if st.session_state.filters_loaded and st.session_state.filter_options:
#         st.markdown("---")
#         st.subheader("🔍 Data Filters")
#         st.markdown("*Filter data by specific criteria*")
        
#         filter_opts = st.session_state.filter_options
        
#         # PPS TN Filter
#         pps_tn_options = ["All"] + filter_opts.get('PPS TN', [])
#         selected_pps_tn = st.selectbox(
#             "PPS TN",
#             pps_tn_options,
#             help="Filter by PPS TN"
#         )
        
#         # Project Filter
#         project_options = ["All"] + filter_opts.get('Project', [])
#         selected_project = st.selectbox(
#             "Project",
#             project_options,
#             help="Filter by Project"
#         )
        
#         # Sub-Project Filter
#         sub_project_options = ["All"] + filter_opts.get('Sub-Project', [])
#         selected_sub_project = st.selectbox(
#             "Sub-Project",
#             sub_project_options,
#             help="Filter by Sub-Project"
#         )
        
#         # Machine Filter
#         machine_options = ["All"] + filter_opts.get('Machine', [])
#         selected_machine = st.selectbox(
#             "Machine",
#             machine_options,
#             help="Filter by Machine"
#         )
        
#         # Tool No. Filter
#         tool_no_options = ["All"] + filter_opts.get('Tool No.', [])
#         selected_tool_no = st.selectbox(
#             "Tool No.",
#             tool_no_options,
#             help="Filter by Tool Number"
#         )
        
#         # Area Filter
#         area_options = ["All"] + filter_opts.get('Area', [])
#         selected_area = st.selectbox(
#             "Area",
#             area_options,
#             help="Filter by Area"
#         )
#     else:
#         # Default values when no file is uploaded
#         selected_pps_tn = "All"
#         selected_project = "All"
#         selected_sub_project = "All"
#         selected_machine = "All"
#         selected_tool_no = "All"
#         selected_area = "All"

# # Submit button
# if st.sidebar.button("🚀 Process & Analyze", type="primary", use_container_width=True):
#     if uploaded_file:
#         with st.spinner("🔄 Processing data with selected filters..."):
#             uploaded_file.seek(0)
#             try:
#                 # Prepare filter data
#                 filter_data = {
#                     "num_shifts": num_shifts,
#                     "pps_tn": selected_pps_tn,
#                     "project": selected_project,
#                     "sub_project": selected_sub_project,
#                     "machine": selected_machine,
#                     "tool_no": selected_tool_no,
#                     "area": selected_area
#                 }
                
#                 response = requests.post(
#                     "http://127.0.0.1:8000/api/process-csv/",
#                     data=filter_data,
#                     files={"file": uploaded_file}
#                 )
                
#                 if response.status_code == 200:
#                     st.session_state.data = response.json()
#                     st.session_state.processed = True
#                     st.sidebar.success("✅ Analysis complete!")
                    
#                     # Show active filters
#                     active_filters = []
#                     if selected_pps_tn != "All":
#                         active_filters.append(f"PPS TN: {selected_pps_tn}")
#                     if selected_project != "All":
#                         active_filters.append(f"Project: {selected_project}")
#                     if selected_sub_project != "All":
#                         active_filters.append(f"Sub-Project: {selected_sub_project}")
#                     if selected_machine != "All":
#                         active_filters.append(f"Machine: {selected_machine}")
#                     if selected_tool_no != "All":
#                         active_filters.append(f"Tool No.: {selected_tool_no}")
#                     if selected_area != "All":
#                         active_filters.append(f"Area: {selected_area}")
                    
#                     if active_filters:
#                         st.sidebar.info("**Active Filters:**\n" + "\n".join([f"- {f}" for f in active_filters]))
#                 else:
#                     st.error(f"❌ Error: {response.text}")
#             except Exception as e:
#                 st.error(f"❌ Connection error: {str(e)}")
#     else:
#         st.warning("⚠️ Please upload a file first.")

# # Main content
# if st.session_state.processed and st.session_state.data:
#     data = st.session_state.data
#     shift_data = data["ShiftWise"]
#     summary_data = data["Summary"]
    
#     # Create dataframes
#     df_shift = pd.DataFrame(shift_data).T
#     df_summary = pd.DataFrame(summary_data)
    
#     # Additional sidebar filters for visualization
#     with st.sidebar:
#         st.markdown("---")
#         st.subheader("📊 Display Options")
        
#         # Metric selection
#         metrics = list(shift_data.keys())
#         selected_metrics = st.multiselect(
#             "Select Metrics to Display",
#             metrics,
#             default=metrics
#         )
        
#         # Shift range filter
#         all_shifts = list(shift_data[metrics[0]].keys())
#         shift_range = st.select_slider(
#             "Select Shift Range",
#             options=all_shifts,
#             value=(all_shifts[0], all_shifts[-1])
#         )
        
#         # Chart type selection
#         chart_type = st.selectbox(
#             "Primary Chart Type",
#             ["Line Chart", "Bar Chart", "Area Chart", "Combined"]
#         )
    
#     # Filter data based on shift range
#     start_idx = all_shifts.index(shift_range[0])
#     end_idx = all_shifts.index(shift_range[1]) + 1
#     filtered_shifts = all_shifts[start_idx:end_idx]
    
#     tab1, tab2, tab3, tab4 = st.tabs(["📊 Production Charts", "⚡ Efficiency Analysis", "📋 Data Tables", "📥 Downloads"])
    
#     with tab1:
#         st.subheader("Production Output Analysis")
        
#         # Extract summary values and convert to numeric
#         summary_metrics = df_summary['Metric'].tolist()
#         fg_summary_str = df_summary['Finished Goods'].tolist()
#         conn_summary_str = df_summary['Connectors'].tolist()
        
#         # Convert string values to numeric (remove commas)
#         fg_summary = [float(val.replace(',', '')) for val in fg_summary_str]
#         conn_summary = [float(val.replace(',', '')) for val in conn_summary_str]
        
#         # Custom CSS for better card styling
#         st.markdown("""
#         <style>
#         .metric-card {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 20px;
#             border-radius: 15px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
#             margin-bottom: 10px;
#         }
#         .metric-card-green {
#             background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
#         }
#         .metric-card-orange {
#             background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#         }
#         .metric-card-blue {
#             background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#         }
#         .metric-title {
#             color: white;
#             font-size: 14px;
#             font-weight: 500;
#             margin-bottom: 8px;
#             opacity: 0.9;
#         }
#         .metric-value {
#             color: white;
#             font-size: 28px;
#             font-weight: bold;
#             margin-bottom: 8px;
#         }
#         .section-header {
#             color: #00ff9f;
#             font-size: 20px;
#             font-weight: bold;
#             margin: 20px 0 15px 0;
#             padding-left: 10px;
#             border-left: 4px solid #00ff9f;
#         }
#         </style>
#         """, unsafe_allow_html=True)
        
#         # Finished Goods Section
#         st.markdown('<div class="section-header">🎯 Finished Goods</div>', unsafe_allow_html=True)
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div class="metric-card metric-card-blue">
#                 <div class="metric-title">📋 {summary_metrics[0]}</div>
#                 <div class="metric-value">{fg_summary_str[0]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div class="metric-card metric-card-green">
#                 <div class="metric-title">✅ {summary_metrics[1]}</div>
#                 <div class="metric-value">{fg_summary_str[1]}</div>
#             </div>
#             """, unsafe_allow_html=True)
            
#         with col3:
#             st.markdown(f"""
#             <div class="metric-card metric-card-orange">
#                 <div class="metric-title">⏳ {summary_metrics[2]}</div>
#                 <div class="metric-value">{fg_summary_str[2]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-title">📂 {summary_metrics[3]}</div>
#                 <div class="metric-value">{fg_summary_str[3]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Progress bar for Finished Goods
#         if fg_summary[0] > 0:
#             fg_progress = (fg_summary[1] / fg_summary[0]) * 100
#             st.markdown("**Production Progress**")
#             st.progress(min(fg_progress / 100, 1.0))
#             st.markdown(f"<p style='text-align: center; color: #00ff9f; font-weight: bold;'>{fg_progress:.1f}% Complete ({fg_summary_str[1]} / {fg_summary_str[0]})</p>", unsafe_allow_html=True)
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # Connectors Section
#         st.markdown('<div class="section-header">🔌 Connectors</div>', unsafe_allow_html=True)
#         col5, col6, col7, col8 = st.columns(4)
        
#         with col5:
#             st.markdown(f"""
#             <div class="metric-card metric-card-blue">
#                 <div class="metric-title">📋 {summary_metrics[0]}</div>
#                 <div class="metric-value">{conn_summary_str[0]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col6:
#             st.markdown(f"""
#             <div class="metric-card metric-card-green">
#                 <div class="metric-title">✅ {summary_metrics[1]}</div>
#                 <div class="metric-value">{conn_summary_str[1]}</div>
#             </div>
#             """, unsafe_allow_html=True)
            
#         with col7:
#             st.markdown(f"""
#             <div class="metric-card metric-card-orange">
#                 <div class="metric-title">⏳ {summary_metrics[2]}</div>
#                 <div class="metric-value">{conn_summary_str[2]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col8:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-title">📂 {summary_metrics[3]}</div>
#                 <div class="metric-value">{conn_summary_str[3]}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Progress bar for Connectors
#         if conn_summary[0] > 0:
#             conn_progress = (conn_summary[1] / conn_summary[0]) * 100
#             st.markdown("**Production Progress**")
#             st.progress(min(conn_progress / 100, 1.0))
#             st.markdown(f"<p style='text-align: center; color: #ff6b9d; font-weight: bold;'>{conn_progress:.1f}% Complete ({conn_summary_str[1]} / {conn_summary_str[0]})</p>", unsafe_allow_html=True)
        
#         st.markdown("---")
        
#         # Prepare data for charts
#         fg_values = []
#         conn_values = []
#         backlog_values = []
        
#         for shift in filtered_shifts:
#             fg_val = shift_data['Production Output Finished Goods'][shift].replace(',', '')
#             conn_val = shift_data['Production Output Connectors'][shift].replace(',', '')
#             backlog_val = shift_data['Total Backlog Finished Goods'][shift].replace(',', '')
            
#             fg_values.append(float(fg_val) if fg_val != '0' else 0)
#             conn_values.append(float(conn_val) if conn_val != '0' else 0)
#             backlog_values.append(float(backlog_val) if backlog_val != '0' else 0)
        
#         # Create production chart based on selection
#         if chart_type == "Line Chart":
#             fig = go.Figure()
#             if 'Production Output Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_values, name='Finished Goods',
#                                         mode='lines+markers', line=dict(color='#00ff9f', width=3)))
#             if 'Production Output Connectors' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_values, name='Connectors',
#                                         mode='lines+markers', line=dict(color='#ff6b9d', width=3)))
#             if 'Total Backlog Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_values, name='Backlog',
#                                         mode='lines+markers', line=dict(color='#ffa500', width=3)))
        
#         elif chart_type == "Bar Chart":
#             fig = go.Figure()
#             if 'Production Output Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Bar(x=filtered_shifts, y=fg_values, name='Finished Goods',
#                                     marker_color='#00ff9f'))
#             if 'Production Output Connectors' in selected_metrics:
#                 fig.add_trace(go.Bar(x=filtered_shifts, y=conn_values, name='Connectors',
#                                     marker_color='#ff6b9d'))
#             if 'Total Backlog Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Bar(x=filtered_shifts, y=backlog_values, name='Backlog',
#                                     marker_color='#ffa500'))
#             fig.update_layout(barmode='group')
        
#         elif chart_type == "Area Chart":
#             fig = go.Figure()
#             if 'Production Output Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=fg_values, name='Finished Goods',
#                                         fill='tozeroy', line=dict(color='#00ff9f')))
#             if 'Production Output Connectors' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=conn_values, name='Connectors',
#                                         fill='tozeroy', line=dict(color='#ff6b9d')))
        
#         else:  # Combined
#             fig = make_subplots(specs=[[{"secondary_y": True}]])
#             if 'Production Output Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Bar(x=filtered_shifts, y=fg_values, name='Finished Goods',
#                                     marker_color='#00ff9f'), secondary_y=False)
#             if 'Production Output Connectors' in selected_metrics:
#                 fig.add_trace(go.Bar(x=filtered_shifts, y=conn_values, name='Connectors',
#                                     marker_color='#ff6b9d'), secondary_y=False)
#             if 'Total Backlog Finished Goods' in selected_metrics:
#                 fig.add_trace(go.Scatter(x=filtered_shifts, y=backlog_values, name='Backlog',
#                                         mode='lines+markers', line=dict(color='#ffa500', width=3)),
#                             secondary_y=True)
        
#         fig.update_layout(
#             template='plotly_dark',
#             height=500,
#             xaxis_title="Shifts",
#             yaxis_title="Quantity",
#             hovermode='x unified',
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Additional comparison charts
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("#### 🎯 Production by Category")
#             total_fg_prod = sum(fg_values)
#             total_conn_prod = sum(conn_values)
            
#             pie_fig = go.Figure(data=[go.Pie(
#                 labels=['Finished Goods', 'Connectors'],
#                 values=[total_fg_prod, total_conn_prod],
#                 hole=0.4,
#                 marker_colors=['#00ff9f', '#ff6b9d']
#             )])
#             pie_fig.update_layout(template='plotly_dark', height=350)
#             st.plotly_chart(pie_fig, use_container_width=True)
        
#         with col2:
#             st.markdown("#### 📊 Cumulative Production")
#             cumulative_fg = [sum(fg_values[:i+1]) for i in range(len(fg_values))]
#             cumulative_conn = [sum(conn_values[:i+1]) for i in range(len(conn_values))]
            
#             cum_fig = go.Figure()
#             cum_fig.add_trace(go.Scatter(x=filtered_shifts, y=cumulative_fg, name='Finished Goods',
#                                         fill='tozeroy', line=dict(color='#00ff9f')))
#             cum_fig.add_trace(go.Scatter(x=filtered_shifts, y=cumulative_conn, name='Connectors',
#                                         fill='tozeroy', line=dict(color='#ff6b9d')))
#             cum_fig.update_layout(template='plotly_dark', height=350)
#             st.plotly_chart(cum_fig, use_container_width=True)
    
#     with tab2:
#         st.subheader("⚡ Overall Efficiency Analysis")
        
#         # Extract efficiency data
#         efficiency_values = []
#         efficiency_labels = []
        
#         for shift in filtered_shifts:
#             eff_str = shift_data['Overall Efficiency'][shift]
#             if eff_str != '-':
#                 eff_val = float(eff_str.replace('%', ''))
#                 efficiency_values.append(eff_val)
#                 efficiency_labels.append(shift)
        
#         # Efficiency line chart
#         eff_fig = go.Figure()
#         eff_fig.add_trace(go.Scatter(
#             x=efficiency_labels, 
#             y=efficiency_values,
#             mode='lines+markers',
#             name='Efficiency %',
#             line=dict(color='#00d4ff', width=4),
#             marker=dict(size=10, symbol='diamond'),
#             fill='tozeroy',
#             fillcolor='rgba(0, 212, 255, 0.2)'
#         ))
        
#         # Add target line at 100%
#         eff_fig.add_hline(y=100, line_dash="dash", line_color="green", 
#                          annotation_text="Target: 100%")
        
#         eff_fig.update_layout(
#             template='plotly_dark',
#             height=400,
#             xaxis_title="Shifts",
#             yaxis_title="Efficiency %",
#             hovermode='x unified'
#         )
        
#         st.plotly_chart(eff_fig, use_container_width=True)
        
#         # Efficiency statistics
#         col1, col2, col3, col4 = st.columns(4)
        
#         if efficiency_values:
#             with col1:
#                 st.metric("Average Efficiency", f"{sum(efficiency_values)/len(efficiency_values):.2f}%")
#             with col2:
#                 st.metric("Maximum Efficiency", f"{max(efficiency_values):.2f}%")
#             with col3:
#                 st.metric("Minimum Efficiency", f"{min(efficiency_values):.2f}%")
#             with col4:
#                 above_target = sum(1 for e in efficiency_values if e >= 100)
#                 st.metric("Shifts ≥100%", f"{above_target}/{len(efficiency_values)}")
        
#         # Efficiency distribution
#         st.markdown("#### 📊 Efficiency Distribution")
#         hist_fig = go.Figure(data=[go.Histogram(
#             x=efficiency_values,
#             nbinsx=10,
#             marker_color='#00d4ff',
#             opacity=0.75
#         )])
#         hist_fig.update_layout(
#             template='plotly_dark',
#             height=300,
#             xaxis_title="Efficiency %",
#             yaxis_title="Frequency"
#         )
#         st.plotly_chart(hist_fig, use_container_width=True)
    
#     with tab3:
#         st.subheader("📋 Detailed Data Tables")
        
#         # Shift-wise data
#         st.markdown("#### Shift-wise Production & Efficiency")
        
#         filtered_df = df_shift[filtered_shifts].copy()
        
#         if selected_metrics:
#             available_metrics = [metric for metric in selected_metrics if metric in filtered_df.index]
#             if available_metrics:
#                 filtered_df = filtered_df.loc[available_metrics]
        
#         st.dataframe(filtered_df, use_container_width=True, height=200)
    
#     with tab4:
#         st.subheader("📥 Download Options")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("#### Full Shift-wise Data")
#             csv_data = df_shift.to_csv(index=True)
#             st.download_button(
#                 label="📥 Download Full Dataset (CSV)",
#                 data=csv_data,
#                 file_name="shiftwise_production_data.csv",
#                 mime="text/csv",
#                 use_container_width=True
#             )
        
#         with col2:
#             st.markdown("#### Summary Report")
#             csv_summary = df_summary.to_csv(index=False)
#             st.download_button(
#                 label="📥 Download Summary (CSV)",
#                 data=csv_summary,
#                 file_name="production_summary.csv",
#                 mime="text/csv",
#                 use_container_width=True
#             )
        
#         st.markdown("---")
        
#         # Filtered data download
#         st.markdown("#### Filtered Data")
#         filtered_csv = filtered_df.to_csv(index=True)
#         st.download_button(
#             label="📥 Download Filtered Data (CSV)",
#             data=filtered_csv,
#             file_name="filtered_production_data.csv",
#             mime="text/csv",
#             use_container_width=True
#         )

# else:
#     # Welcome screen
#     st.markdown("""
#     👋 Welcome to Production Analytics Dashboard
#     """)


# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import json

# # Configuration
# API_BASE_URL = "http://localhost:8000/api"  # Update with your Django API URL

# # Page config
# st.set_page_config(
#     page_title="Production Schedule Dashboard",
#     page_icon="🏭",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         font-size: 1.2rem;
#         color: #666;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .kpi-card {
#         background-color: #f0f2f6;
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         border-left: 5px solid #1f77b4;
#     }
#     .kpi-value {
#         font-size: 2rem;
#         font-weight: bold;
#         color: #1f77b4;
#     }
#     .kpi-label {
#         font-size: 0.9rem;
#         color: #666;
#         margin-top: 0.5rem;
#     }
    
#     /* Timeline Styles */
#     .timeline-container {
#         width: 100%;
#         overflow-x: auto;
#         overflow-y: visible;
#         background: white;
#         border-radius: 8px;
#         padding: 20px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
    
#     .timeline-grid {
#         display: grid;
#         grid-template-columns: 150px 1fr;
#         min-width: 1200px;
#         gap: 0;
#     }
    
#     .timeline-header {
#         display: contents;
#     }
    
#     .machine-label {
#         font-weight: bold;
#         padding: 15px;
#         background: #f8f9fa;
#         border-right: 2px solid #dee2e6;
#         border-bottom: 1px solid #dee2e6;
#         display: flex;
#         align-items: center;
#         color: #495057;
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }
    
#     .time-header {
#         display: flex;
#         border-bottom: 2px solid #dee2e6;
#         background: #f8f9fa;
#         position: sticky;
#         top: 0;
#         z-index: 5;
#     }
    
#     .time-slot-header {
#         flex: 1;
#         min-width: 100px;
#         padding: 10px;
#         text-align: center;
#         border-right: 1px solid #e9ecef;
#         font-size: 0.85rem;
#         color: #6c757d;
#         font-weight: 600;
#     }
    
#     .machine-row {
#         display: flex;
#         position: relative;
#         min-height: 80px;
#         border-bottom: 1px solid #dee2e6;
#         background: white;
#     }
    
#     .time-grid {
#         flex: 1;
#         display: flex;
#         position: relative;
#     }
    
#     .time-slot {
#         flex: 1;
#         min-width: 100px;
#         border-right: 1px solid #e9ecef;
#         position: relative;
#     }
    
#     .schedule-card {
#         position: absolute;
#         height: 60px;
#         border-radius: 6px;
#         padding: 8px 12px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.15);
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         color: white;
#         font-size: 0.85rem;
#         font-weight: 500;
#         cursor: pointer;
#         transition: all 0.2s;
#         overflow: hidden;
#         z-index: 2;
#         top: 10px;
#     }
    
#     .schedule-card:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 4px 8px rgba(0,0,0,0.2);
#         z-index: 3;
#     }
    
#     .card-title {
#         font-weight: 600;
#         font-size: 0.9rem;
#         margin-bottom: 2px;
#         white-space: nowrap;
#         overflow: hidden;
#         text-overflow: ellipsis;
#     }
    
#     .card-subtitle {
#         font-size: 0.75rem;
#         opacity: 0.9;
#         white-space: nowrap;
#         overflow: hidden;
#         text-overflow: ellipsis;
#     }
    
#     /* Color schemes for different items */
#     .item-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
#     .item-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
#     .item-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
#     .item-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
#     .item-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
#     .item-6 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
#     .item-7 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
#     .item-24 { background: linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%); }
#     .item-25 { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
#     .item-26 { background: linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%); }
#     .item-27 { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }
#     .item-28 { background: linear-gradient(135deg, #f8b500 0%, #fceabb 100%); }
    
#     .legend {
#         display: flex;
#         flex-wrap: wrap;
#         gap: 15px;
#         margin: 20px 0;
#         padding: 15px;
#         background: #f8f9fa;
#         border-radius: 6px;
#     }
    
#     .legend-item {
#         display: flex;
#         align-items: center;
#         gap: 8px;
#         font-size: 0.85rem;
#     }
    
#     .legend-color {
#         width: 30px;
#         height: 20px;
#         border-radius: 4px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
    
#     .empty-slot {
#         color: #adb5bd;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         height: 100%;
#         font-size: 0.75rem;
#     }
#     </style>
# """, unsafe_allow_html=True)


# # Helper functions
# def fetch_data(endpoint, params=None):
#     """Fetch data from Django API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/{endpoint}/", params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"Error fetching data: {response.status_code}")
#             return None
#     except Exception as e:
#         st.error(f"Connection error: {str(e)}")
#         return None


# def post_data(endpoint, data=None):
#     """Post data to Django API"""
#     try:
#         response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=data)
#         if response.status_code in [200, 201]:
#             return response.json()
#         else:
#             st.error(f"Error posting data: {response.status_code}")
#             return None
#     except Exception as e:
#         st.error(f"Connection error: {str(e)}")
#         return None


# def generate_timeline_html(df_schedule, start_time, end_time, time_interval_hours=2):
#     """Generate custom timeline HTML"""
#     if df_schedule.empty:
#         return "<p>No schedule data available</p>"
    
#     # Convert times
#     df = df_schedule.copy()
#     df['start_time'] = pd.to_datetime(df['start_time'])
#     df['end_time'] = pd.to_datetime(df['end_time'])
    
#     # Get unique machines
#     machines = sorted(df['machine_name'].unique())
    
#     # Calculate timeline range - ensure timezone consistency
#     timeline_start = pd.to_datetime(start_time)
#     timeline_end = pd.to_datetime(end_time)
    
#     # Check if the dataframe times have timezone info
#     if df['start_time'].dt.tz is not None:
#         # If dataframe has timezone, add timezone to timeline_start/end
#         if timeline_start.tz is None:
#             timeline_start = timeline_start.tz_localize(df['start_time'].dt.tz)
#         if timeline_end.tz is None:
#             timeline_end = timeline_end.tz_localize(df['start_time'].dt.tz)
#     else:
#         # If dataframe is timezone-naive, remove timezone from timeline_start/end
#         if timeline_start.tz is not None:
#             timeline_start = timeline_start.tz_localize(None)
#         if timeline_end.tz is not None:
#             timeline_end = timeline_end.tz_localize(None)
    
#     total_hours = (timeline_end - timeline_start).total_seconds() / 3600
    
#     # Generate time slots
#     time_slots = []
#     current_time = timeline_start
#     while current_time < timeline_end:
#         time_slots.append(current_time)
#         current_time += timedelta(hours=time_interval_hours)
    
#     num_slots = len(time_slots)
    
#     # Build HTML
#     html = '<div class="timeline-container">'
#     html += '<div class="timeline-grid">'
    
#     # Header row
#     html += '<div class="timeline-header">'
#     html += '<div class="machine-label" style="background: #e9ecef;">Machine</div>'
#     html += '<div class="time-header">'
    
#     for time_slot in time_slots:
#         time_str = time_slot.strftime('%H:%M')
#         date_str = time_slot.strftime('%m/%d')
#         html += f'<div class="time-slot-header">{date_str}<br>{time_str}</div>'
    
#     html += '</div></div>'
    
#     # Machine rows
#     for machine in machines:
#         machine_data = df[df['machine_name'] == machine]
        
#         html += f'<div class="machine-label">{machine}</div>'
#         html += '<div class="machine-row">'
#         html += '<div class="time-grid">'
        
#         # Add time slot dividers
#         for i in range(num_slots):
#             html += '<div class="time-slot"></div>'
        
#         # Add schedule cards
#         for _, row in machine_data.iterrows():
#             start = row['start_time']
#             end = row['end_time']
            
#             # Calculate position and width
#             start_offset = (start - timeline_start).total_seconds() / 3600
#             duration = (end - start).total_seconds() / 3600
            
#             left_percent = (start_offset / total_hours) * 100
#             width_percent = (duration / total_hours) * 100
            
#             # Ensure card stays within bounds
#             if left_percent < 0:
#                 width_percent += left_percent
#                 left_percent = 0
#             if left_percent + width_percent > 100:
#                 width_percent = 100 - left_percent
            
#             if width_percent > 0:
#                 item_class = f"item-{row['product_item']}"
#                 batch_id = row['batch_id']
#                 step_num = row['step_number']
#                 step_name = row['step_name'][:30]
                
#                 # Truncate step name for display
#                 display_name = step_name if len(step_name) <= 30 else step_name[:27] + "..."
                
#                 html += f'''
#                 <div class="schedule-card {item_class}" 
#                      style="left: {left_percent}%; width: {width_percent}%;"
#                      title="{batch_id} - Step {step_num}: {step_name}">
#                     <div class="card-title">Step {step_num}</div>
#                     <div class="card-subtitle">{batch_id}</div>
#                 </div>
#                 '''
        
#         html += '</div></div>'
    
#     html += '</div></div>'
    
#     # Add legend
#     html += '<div class="legend">'
#     items = sorted(df['product_item'].unique())
#     for item in items:
#         item_desc = df[df['product_item'] == item]['product_description'].iloc[0]
#         short_desc = item_desc[:40] + "..." if len(item_desc) > 40 else item_desc
#         html += f'''
#         <div class="legend-item">
#             <div class="legend-color item-{item}"></div>
#             <span><strong>Item {item}:</strong> {short_desc}</span>
#         </div>
#         '''
#     html += '</div>'
    
#     return html


# def create_gantt_chart(df_schedule):
#     """Create Gantt chart for production schedule"""
#     if df_schedule.empty:
#         return None
    
#     df_gantt = df_schedule.copy()
#     df_gantt['Start'] = pd.to_datetime(df_gantt['start_time'])
#     df_gantt['Finish'] = pd.to_datetime(df_gantt['end_time'])
#     df_gantt['Task'] = df_gantt['machine_name']
#     df_gantt['Resource'] = df_gantt['batch_id'] + ' - Step ' + df_gantt['step_number'].astype(str)
    
#     fig = px.timeline(
#         df_gantt,
#         x_start='Start',
#         x_end='Finish',
#         y='Task',
#         color='product_item',
#         hover_data=['batch_id', 'step_name', 'duration_hours', 'product_description'],
#         title='Production Schedule Gantt Chart',
#         labels={'Task': 'Machine', 'product_item': 'Product Item'},
#         color_continuous_scale='Viridis'
#     )
    
#     fig.update_yaxes(categoryorder='category ascending')
#     fig.update_layout(
#         height=600,
#         xaxis_title='Time',
#         showlegend=True,
#         hovermode='closest'
#     )
    
#     return fig


# def create_machine_utilization_chart(machine_stats):
#     """Create machine utilization bar chart"""
#     if not machine_stats:
#         return None
    
#     machines = [stat['machine'] for stat in machine_stats]
#     utilizations = [stat['utilization'] for stat in machine_stats]
    
#     fig = go.Figure(data=[
#         go.Bar(
#             x=machines,
#             y=utilizations,
#             text=[f"{u:.1f}%" for u in utilizations],
#             textposition='auto',
#             marker_color='lightblue'
#         )
#     ])
    
#     fig.update_layout(
#         title='Machine Utilization',
#         xaxis_title='Machine',
#         yaxis_title='Utilization (%)',
#         height=400,
#         yaxis_range=[0, 100]
#     )
    
#     return fig


# # Main app
# def main():
#     # Header
#     st.markdown('<div class="main-header">🏭 Production Schedule Dashboard</div>', unsafe_allow_html=True)
#     st.markdown('<div class="sub-header">Optimized Machine Time Allocation</div>', unsafe_allow_html=True)
    
#     # Sidebar
#     st.sidebar.title("⚙️ Controls")
    
#     # Initialize/Regenerate buttons
#     col1, col2 = st.sidebar.columns(2)
    
#     with col1:
#         if st.button("🔄 Init Data", use_container_width=True):
#             with st.spinner("Initializing database..."):
#                 result = post_data("initialize-data")
#                 if result:
#                     st.success(f"✅ {result['message']}")
#                     st.rerun()
    
#     with col2:
#         if st.button("📅 Generate Schedule", use_container_width=True):
#             with st.spinner("Generating schedule..."):
#                 result = post_data("generate-schedule")
#                 if result:
#                     st.success(f"✅ {result['message']}")
#                     st.rerun()
    
#     st.sidebar.markdown("---")
    
#     # Filters
#     st.sidebar.subheader("🔍 Filters")
    
#     # Get filter options
#     filter_options = fetch_data("get-filter-options")
    
#     if filter_options:
#         # Machine filter
#         machines = ['All'] + filter_options.get('machines', [])
#         selected_machine = st.sidebar.selectbox("Select Machine(s)", machines)
        
#         # Product filter
#         products = filter_options.get('products', [])
#         product_options = ['All'] + [f"Item {p['item']}: {p['description'][:30]}..." for p in products]
#         selected_product = st.sidebar.selectbox("Select Product", product_options)
        
#         # Time range
#         date_range = filter_options.get('date_range', {})
#         if date_range.get('min') and date_range.get('max'):
#             min_date = pd.to_datetime(date_range['min']).date()
#             max_date = pd.to_datetime(date_range['max']).date()
            
#             st.sidebar.subheader("📆 Time Range")
#             start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
#             end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
#         else:
#             start_date = None
#             end_date = None
#     else:
#         selected_machine = 'All'
#         selected_product = 'All'
#         start_date = None
#         end_date = None
    
#     st.sidebar.markdown("---")
    
#     # Timeline settings
#     st.sidebar.subheader("⏱️ Timeline View Settings")
#     time_interval = st.sidebar.slider("Time Interval (hours)", 1, 24, 2)
    
#     # Optimization goal (placeholder for future use)
#     st.sidebar.subheader("🎯 Optimization Goal")
#     optimization_goal = st.sidebar.radio(
#         "Select Goal",
#         ["Minimize Makespan", "Maximize Throughput"],
#         disabled=True
#     )
#     st.sidebar.caption("ℹ️ Feature coming soon")
    
#     # Main content
#     # Fetch schedule data
#     params = {}
#     if selected_machine != 'All':
#         params['machine'] = selected_machine
#     if selected_product != 'All':
#         product_item = int(selected_product.split(':')[0].replace('Item ', ''))
#         params['product'] = product_item
#     if start_date:
#         params['start_date'] = start_date.isoformat()
#     if end_date:
#         params['end_date'] = end_date.isoformat()
    
#     schedule_data = fetch_data("get-schedule", params)
#     kpi_data = fetch_data("get-kpis")
    
#     if not schedule_data or not schedule_data.get('schedules'):
#         st.warning("⚠️ No schedule data available. Please initialize data and generate schedule.")
#         return
    
#     # Convert to DataFrame
#     df_schedule = pd.DataFrame(schedule_data['schedules'])
    
#     # KPIs Section
#     st.subheader("📊 Key Performance Indicators")
    
#     if kpi_data:
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('total_makespan_days', 0):.1f}</div>
#                     <div class="kpi-label">Total Makespan (Days)</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             avg_utilization = sum([m['utilization'] for m in kpi_data.get('machine_utilization', [])]) / len(kpi_data.get('machine_utilization', [1]))
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{avg_utilization:.1f}%</div>
#                     <div class="kpi-label">Avg Machine Utilization</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('total_operations', 0)}</div>
#                     <div class="kpi-label">Number of Operations</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('throughput_units_per_day', 0):.0f}</div>
#                     <div class="kpi-label">Throughput (units/day)</div>
#                 </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # Tabs for different views
#     tab1, tab2, tab3, tab4 = st.tabs(["📅 Timeline View", "📈 Gantt Chart", "📋 Table View", "🔧 Machine Details"])
    
#     with tab1:
#         st.subheader("Production Timeline Schedule")
        
#         # Get time range for timeline
#         if start_date and end_date:
#             timeline_start = datetime.combine(start_date, datetime.min.time())
#             timeline_end = datetime.combine(end_date, datetime.max.time())
#         else:
#             timeline_start = pd.to_datetime(df_schedule['start_time']).min()
#             timeline_end = pd.to_datetime(df_schedule['end_time']).max()
        
#         # Generate and display custom timeline
#         timeline_html = generate_timeline_html(df_schedule, timeline_start, timeline_end, time_interval)
#         st.markdown(timeline_html, unsafe_allow_html=True)
        
#         st.info("💡 Hover over cards to see full details. Scroll horizontally to view the entire timeline.")
    
#     with tab2:
#         st.subheader("Production Schedule Gantt Chart")
#         gantt_fig = create_gantt_chart(df_schedule)
#         if gantt_fig:
#             st.plotly_chart(gantt_fig, use_container_width=True)
#         else:
#             st.info("No data available for Gantt chart")
    
#     with tab3:
#         st.subheader("Schedule Table View")
        
#         # Display options
#         display_cols = [
#             'machine_name', 'product_item', 'product_sap_tn', 'product_dcc_type',
#             'batch_id', 'step_number', 'step_name', 'workers_required',
#             'start_time', 'end_time', 'duration_hours'
#         ]
        
#         df_display = df_schedule[display_cols].copy()
#         df_display['start_time'] = pd.to_datetime(df_display['start_time']).dt.strftime('%Y-%m-%d %H:%M')
#         df_display['end_time'] = pd.to_datetime(df_display['end_time']).dt.strftime('%Y-%m-%d %H:%M')
        
#         # Rename columns for display
#         df_display.columns = [
#             'Machine', 'Item', 'SAP TN', 'DCC Type', 'Batch ID',
#             'Step', 'Step Name', 'Workers', 'Start Time', 'End Time', 'Duration (h)'
#         ]
        
#         st.dataframe(df_display, use_container_width=True, height=600)
        
#         # Download button
#         csv = df_display.to_csv(index=False)
#         st.download_button(
#             label="📥 Download Schedule CSV",
#             data=csv,
#             file_name=f"production_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#             mime="text/csv"
#         )
    
#     with tab4:
#         st.subheader("Machine Utilization Details")
        
#         if kpi_data and kpi_data.get('machine_utilization'):
#             # Utilization chart
#             util_fig = create_machine_utilization_chart(kpi_data['machine_utilization'])
#             if util_fig:
#                 st.plotly_chart(util_fig, use_container_width=True)
            
#             # Detailed table
#             st.subheader("Machine Statistics")
#             machine_stats_df = pd.DataFrame(kpi_data['machine_utilization'])
#             machine_stats_df.columns = ['Machine', 'Used Hours', 'Utilization (%)', 'Num Operations']
#             st.dataframe(machine_stats_df, use_container_width=True)
#         else:
#             st.info("No machine statistics available")
    
#     # Footer
#     st.markdown("---")
#     st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total schedules: {len(df_schedule)}")


# if __name__ == "__main__":
#     main()


# import streamlit as st
# import streamlit.components.v1 as components
# import requests
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import json

# # Configuration
# API_BASE_URL = "http://localhost:8000/api"  # Update with your Django API URL

# # Page config
# st.set_page_config(
#     page_title="Production Schedule Dashboard",
#     page_icon="🏭",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS (only for non-timeline elements)
# st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         font-size: 1.2rem;
#         color: #666;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .kpi-card {
#         background-color: #f0f2f6;
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         border-left: 5px solid #1f77b4;
#     }
#     .kpi-value {
#         font-size: 2rem;
#         font-weight: bold;
#         color: #1f77b4;
#     }
#     .kpi-label {
#         font-size: 0.9rem;
#         color: #666;
#         margin-top: 0.5rem;
#     }
#     </style>
# """, unsafe_allow_html=True)


# # Helper functions
# def fetch_data(endpoint, params=None):
#     """Fetch data from Django API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/{endpoint}/", params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"Error fetching data: {response.status_code}")
#             return None
#     except Exception as e:
#         st.error(f"Connection error: {str(e)}")
#         return None


# def post_data(endpoint, data=None):
#     """Post data to Django API"""
#     try:
#         response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=data)
#         if response.status_code in [200, 201]:
#             return response.json()
#         else:
#             st.error(f"Error posting data: {response.status_code}")
#             return None
#     except Exception as e:
#         st.error(f"Connection error: {str(e)}")
#         return None


# def generate_timeline_html(df_schedule, start_time, end_time, time_interval_hours=0.2):
#     """Generate custom timeline HTML - returns complete HTML document"""
#     if df_schedule.empty:
#         return "<html><body><p>No schedule data available</p></body></html>"
    
#     # Convert times
#     df = df_schedule.copy()
#     df['start_time'] = pd.to_datetime(df['start_time'])
#     df['end_time'] = pd.to_datetime(df['end_time'])
    
#     # Get unique machines
#     machines = sorted(df['machine_name'].unique())
    
#     # Calculate timeline range - ensure timezone consistency
#     timeline_start = pd.to_datetime(start_time)
#     timeline_end = pd.to_datetime(end_time)
    
#     # Check if the dataframe times have timezone info
#     if df['start_time'].dt.tz is not None:
#         if timeline_start.tz is None:
#             timeline_start = timeline_start.tz_localize(df['start_time'].dt.tz)
#         if timeline_end.tz is None:
#             timeline_end = timeline_end.tz_localize(df['start_time'].dt.tz)
#     else:
#         if timeline_start.tz is not None:
#             timeline_start = timeline_start.tz_localize(None)
#         if timeline_end.tz is not None:
#             timeline_end = timeline_end.tz_localize(None)
    
#     total_hours = (timeline_end - timeline_start).total_seconds() / 3600
    
#     # Generate time slots
#     time_slots = []
#     current_time = timeline_start
#     while current_time < timeline_end:
#         time_slots.append(current_time)
#         current_time += timedelta(hours=time_interval_hours)
    
#     num_slots = len(time_slots)
    
#     # Build complete HTML document with embedded styles
#     html = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <style>
#             body {
#                 margin: 0;
#                 padding: 20px;
#                 font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
#                 background: #ffffff;
#             }
            
#             .timeline-container {
#                 width: 100%;
#                 overflow-x: auto;
#                 overflow-y: visible;
#                 background: white;
#                 border-radius: 8px;
#                 padding: 20px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             }
            
#             .timeline-grid {
#                 display: grid;
#                 grid-template-columns: 150px 1fr;
#                 min-width: 1200px;
#                 gap: 0;
#             }
            
#             .timeline-header {
#                 display: contents;
#             }
            
#             .machine-label {
#                 font-weight: bold;
#                 padding: 15px;
#                 background: #f8f9fa;
#                 border-right: 2px solid #dee2e6;
#                 border-bottom: 1px solid #dee2e6;
#                 display: flex;
#                 align-items: center;
#                 color: #495057;
#                 position: sticky;
#                 left: 0;
#                 z-index: 10;
#             }
            
#             .time-header {
#                 display: flex;
#                 border-bottom: 2px solid #dee2e6;
#                 background: #f8f9fa;
#                 position: sticky;
#                 top: 0;
#                 z-index: 5;
#             }
            
#             .time-slot-header {
#                 flex: 1;
#                 min-width: 100px;
#                 padding: 10px;
#                 text-align: center;
#                 border-right: 1px solid #e9ecef;
#                 font-size: 0.85rem;
#                 color: #6c757d;
#                 font-weight: 600;
#             }
            
#             .machine-row {
#                 display: flex;
#                 position: relative;
#                 min-height: 80px;
#                 border-bottom: 1px solid #dee2e6;
#                 background: white;
#             }
            
#             .time-grid {
#                 flex: 1;
#                 display: flex;
#                 position: relative;
#             }
            
#             .time-slot {
#                 flex: 1;
#                 min-width: 100px;
#                 border-right: 1px solid #e9ecef;
#                 position: relative;
#             }
            
#             .schedule-card {
#                 position: absolute;
#                 height: 60px;
#                 border-radius: 6px;
#                 padding: 8px 12px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.15);
#                 display: flex;
#                 flex-direction: column;
#                 justify-content: center;
#                 color: white;
#                 font-size: 0.85rem;
#                 font-weight: 500;
#                 cursor: pointer;
#                 transition: all 0.2s;
#                 overflow: hidden;
#                 z-index: 2;
#                 top: 10px;
#             }
            
#             .schedule-card:hover {
#                 transform: translateY(-2px);
#                 box-shadow: 0 4px 8px rgba(0,0,0,0.2);
#                 z-index: 3;
#             }
            
#             .card-title {
#                 font-weight: 600;
#                 font-size: 0.9rem;
#                 margin-bottom: 2px;
#                 white-space: nowrap;
#                 overflow: hidden;
#                 text-overflow: ellipsis;
#             }
            
#             .card-subtitle {
#                 font-size: 0.75rem;
#                 opacity: 0.9;
#                 white-space: nowrap;
#                 overflow: hidden;
#                 text-overflow: ellipsis;
#             }
            
#             /* Color schemes for different items */
#             .item-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
#             .item-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
#             .item-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
#             .item-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
#             .item-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
#             .item-6 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
#             .item-7 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
#             .item-24 { background: linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%); }
#             .item-25 { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
#             .item-26 { background: linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%); }
#             .item-27 { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }
#             .item-28 { background: linear-gradient(135deg, #f8b500 0%, #fceabb 100%); }
            
#             .legend {
#                 display: flex;
#                 flex-wrap: wrap;
#                 gap: 15px;
#                 margin: 20px 0;
#                 padding: 15px;
#                 background: #f8f9fa;
#                 border-radius: 6px;
#             }
            
#             .legend-item {
#                 display: flex;
#                 align-items: center;
#                 gap: 8px;
#                 font-size: 0.85rem;
#             }
            
#             .legend-color {
#                 width: 30px;
#                 height: 20px;
#                 border-radius: 4px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             }
#         </style>
#     </head>
#     <body>
#     """
    
#     html += '<div class="timeline-container">'
#     html += '<div class="timeline-grid">'
    
#     # Header row
#     html += '<div class="timeline-header">'
#     html += '<div class="machine-label" style="background: #e9ecef;">Machine</div>'
#     html += '<div class="time-header">'
    
#     for time_slot in time_slots:
#         time_str = time_slot.strftime('%H:%M')
#         date_str = time_slot.strftime('%m/%d')
#         html += f'<div class="time-slot-header">{date_str}<br>{time_str}</div>'
    
#     html += '</div></div>'
    
#     # Machine rows
#     for machine in machines:
#         machine_data = df[df['machine_name'] == machine]
        
#         html += f'<div class="machine-label">{machine}</div>'
#         html += '<div class="machine-row">'
#         html += '<div class="time-grid">'
        
#         # Add time slot dividers
#         for i in range(num_slots):
#             html += '<div class="time-slot"></div>'
        
#         # Add schedule cards
#         for _, row in machine_data.iterrows():
#             start = row['start_time']
#             end = row['end_time']
            
#             # Calculate position and width
#             start_offset = (start - timeline_start).total_seconds() / 3600
#             duration = (end - start).total_seconds() / 3600
            
#             left_percent = (start_offset / total_hours) * 100
#             width_percent = (duration / total_hours) * 100
            
#             # Ensure card stays within bounds
#             if left_percent < 0:
#                 width_percent += left_percent
#                 left_percent = 0
#             if left_percent + width_percent > 100:
#                 width_percent = 100 - left_percent
            
#             if width_percent > 0:
#                 item_class = f"item-{row['product_item']}"
#                 batch_id = row['batch_id']
#                 step_num = row['step_number']
#                 step_name = str(row['step_name'])[:30]
                
#                 html += f'''
#                 <div class="schedule-card {item_class}" 
#                      style="left: {left_percent}%; width: {width_percent}%;"
#                      title="{batch_id} - Step {step_num}: {step_name}">
#                     <div class="card-title">Step {step_num}</div>
#                     <div class="card-subtitle">{batch_id}</div>
#                 </div>
#                 '''
        
#         html += '</div></div>'
    
#     html += '</div></div>'
    
#     # Add legend
#     html += '<div class="legend">'
#     items = sorted(df['product_item'].unique())
#     for item in items:
#         item_desc = df[df['product_item'] == item]['product_description'].iloc[0]
#         short_desc = item_desc[:40] + "..." if len(item_desc) > 40 else item_desc
#         html += f'''
#         <div class="legend-item">
#             <div class="legend-color item-{item}"></div>
#             <span><strong>Item {item}:</strong> {short_desc}</span>
#         </div>
#         '''
#     html += '</div>'
    
#     html += '</body></html>'
    
#     return html


# def create_gantt_chart(df_schedule):
#     """Create Gantt chart for production schedule"""
#     if df_schedule.empty:
#         return None
    
#     df_gantt = df_schedule.copy()
#     df_gantt['Start'] = pd.to_datetime(df_gantt['start_time'])
#     df_gantt['Finish'] = pd.to_datetime(df_gantt['end_time'])
#     df_gantt['Task'] = df_gantt['machine_name']
#     df_gantt['Resource'] = df_gantt['batch_id'] + ' - Step ' + df_gantt['step_number'].astype(str)
    
#     fig = px.timeline(
#         df_gantt,
#         x_start='Start',
#         x_end='Finish',
#         y='Task',
#         color='product_item',
#         hover_data=['batch_id', 'step_name', 'duration_hours', 'product_description'],
#         title='Production Schedule Gantt Chart',
#         labels={'Task': 'Machine', 'product_item': 'Product Item'},
#         color_continuous_scale='Viridis'
#     )
    
#     fig.update_yaxes(categoryorder='category ascending')
#     fig.update_layout(
#         height=600,
#         xaxis_title='Time',
#         showlegend=True,
#         hovermode='closest'
#     )
    
#     return fig


# def create_machine_utilization_chart(machine_stats):
#     """Create machine utilization bar chart"""
#     if not machine_stats:
#         return None
    
#     machines = [stat['machine'] for stat in machine_stats]
#     utilizations = [stat['utilization'] for stat in machine_stats]
    
#     fig = go.Figure(data=[
#         go.Bar(
#             x=machines,
#             y=utilizations,
#             text=[f"{u:.1f}%" for u in utilizations],
#             textposition='auto',
#             marker_color='lightblue'
#         )
#     ])
    
#     fig.update_layout(
#         title='Machine Utilization',
#         xaxis_title='Machine',
#         yaxis_title='Utilization (%)',
#         height=400,
#         yaxis_range=[0, 100]
#     )
    
#     return fig


# # Main app
# def main():
#     # Header
#     st.markdown('<div class="main-header">🏭 Production Schedule Dashboard</div>', unsafe_allow_html=True)
#     st.markdown('<div class="sub-header">Optimized Machine Time Allocation</div>', unsafe_allow_html=True)
    
#     # Sidebar
#     st.sidebar.title("⚙️ Controls")
    
#     # Initialize/Regenerate buttons
#     col1, col2 = st.sidebar.columns(2)
    
#     with col1:
#         if st.button("🔄 Init Data", use_container_width=True):
#             with st.spinner("Initializing database..."):
#                 result = post_data("initialize-data")
#                 if result:
#                     st.success(f"✅ {result['message']}")
#                     st.rerun()
    
#     with col2:
#         if st.button("📅 Generate Schedule", use_container_width=True):
#             with st.spinner("Generating schedule..."):
#                 result = post_data("generate-schedule")
#                 if result:
#                     st.success(f"✅ {result['message']}")
#                     st.rerun()
    
#     st.sidebar.markdown("---")
    
#     # Filters
#     st.sidebar.subheader("🔍 Filters")
    
#     # Get filter options
#     filter_options = fetch_data("get-filter-options")
    
#     if filter_options:
#         # Machine filter
#         machines = ['All'] + filter_options.get('machines', [])
#         selected_machine = st.sidebar.selectbox("Select Machine(s)", machines)
        
#         # Product filter
#         products = filter_options.get('products', [])
#         product_options = ['All'] + [f"Item {p['item']}: {p['description'][:30]}..." for p in products]
#         selected_product = st.sidebar.selectbox("Select Product", product_options)
        
#         # Time range
#         date_range = filter_options.get('date_range', {})
#         if date_range.get('min') and date_range.get('max'):
#             min_date = pd.to_datetime(date_range['min']).date()
#             max_date = pd.to_datetime(date_range['max']).date()
            
#             st.sidebar.subheader("📆 Time Range")
#             start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
#             end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
#         else:
#             start_date = None
#             end_date = None
#     else:
#         selected_machine = 'All'
#         selected_product = 'All'
#         start_date = None
#         end_date = None
    
#     st.sidebar.markdown("---")
    
#     # Timeline settings
#     st.sidebar.subheader("⏱️ Timeline View Settings")
#     time_interval = st.sidebar.slider("Time Interval (hours)", 1, 24, 2)
    
#     # Optimization goal (placeholder for future use)
#     st.sidebar.subheader("🎯 Optimization Goal")
#     optimization_goal = st.sidebar.radio(
#         "Select Goal",
#         ["Minimize Makespan", "Maximize Throughput"],
#         disabled=True
#     )
#     st.sidebar.caption("ℹ️ Feature coming soon")
    
#     # Main content
#     # Fetch schedule data
#     params = {}
#     if selected_machine != 'All':
#         params['machine'] = selected_machine
#     if selected_product != 'All':
#         product_item = int(selected_product.split(':')[0].replace('Item ', ''))
#         params['product'] = product_item
#     if start_date:
#         params['start_date'] = start_date.isoformat()
#     if end_date:
#         params['end_date'] = end_date.isoformat()
    
#     schedule_data = fetch_data("get-schedule", params)
#     kpi_data = fetch_data("get-kpis")
    
#     if not schedule_data or not schedule_data.get('schedules'):
#         st.warning("⚠️ No schedule data available. Please initialize data and generate schedule.")
#         return
    
#     # Convert to DataFrame
#     df_schedule = pd.DataFrame(schedule_data['schedules'])
    
#     # KPIs Section
#     st.subheader("📊 Key Performance Indicators")
    
#     if kpi_data:
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('total_makespan_days', 0):.1f}</div>
#                     <div class="kpi-label">Total Makespan (Days)</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             avg_utilization = sum([m['utilization'] for m in kpi_data.get('machine_utilization', [])]) / len(kpi_data.get('machine_utilization', [1]))
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{avg_utilization:.1f}%</div>
#                     <div class="kpi-label">Avg Machine Utilization</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('total_operations', 0)}</div>
#                     <div class="kpi-label">Number of Operations</div>
#                 </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-value">{kpi_data.get('throughput_units_per_day', 0):.0f}</div>
#                     <div class="kpi-label">Throughput (units/day)</div>
#                 </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # Tabs for different views
#     tab1, tab2, tab3, tab4 = st.tabs(["📅 Timeline View", "📈 Gantt Chart", "📋 Table View", "🔧 Machine Details"])
    
#     with tab1:
#         st.subheader("Production Timeline Schedule")
        
#         # Get time range for timeline
#         if start_date and end_date:
#             timeline_start = datetime.combine(start_date, datetime.min.time())
#             timeline_end = datetime.combine(end_date, datetime.max.time())
#         else:
#             timeline_start = pd.to_datetime(df_schedule['start_time']).min()
#             timeline_end = pd.to_datetime(df_schedule['end_time']).max()
        
#         # Generate and display custom timeline using components.html
#         timeline_html = generate_timeline_html(df_schedule, timeline_start, timeline_end, time_interval)
#         components.html(timeline_html, height=800, scrolling=True)
        
#         st.info("💡 Hover over cards to see full details. Scroll horizontally to view the entire timeline.")
    
#     with tab2:
#         st.subheader("Production Schedule Gantt Chart")
#         gantt_fig = create_gantt_chart(df_schedule)
#         if gantt_fig:
#             st.plotly_chart(gantt_fig, use_container_width=True)
#         else:
#             st.info("No data available for Gantt chart")
    
#     with tab3:
#         st.subheader("Schedule Table View")
        
#         # Display options
#         display_cols = [
#             'machine_name', 'product_item', 'product_sap_tn', 'product_dcc_type',
#             'batch_id', 'step_number', 'step_name', 'workers_required',
#             'start_time', 'end_time', 'duration_hours'
#         ]
        
#         df_display = df_schedule[display_cols].copy()
#         df_display['start_time'] = pd.to_datetime(df_display['start_time']).dt.strftime('%Y-%m-%d %H:%M')
#         df_display['end_time'] = pd.to_datetime(df_display['end_time']).dt.strftime('%Y-%m-%d %H:%M')
        
#         # Rename columns for display
#         df_display.columns = [
#             'Machine', 'Item', 'SAP TN', 'DCC Type', 'Batch ID',
#             'Step', 'Step Name', 'Workers', 'Start Time', 'End Time', 'Duration (h)'
#         ]
        
#         st.dataframe(df_display, use_container_width=True, height=600)
        
#         # Download button
#         csv = df_display.to_csv(index=False)
#         st.download_button(
#             label="📥 Download Schedule CSV",
#             data=csv,
#             file_name=f"production_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#             mime="text/csv"
#         )
    
#     with tab4:
#         st.subheader("Machine Utilization Details")
        
#         if kpi_data and kpi_data.get('machine_utilization'):
#             # Utilization chart
#             util_fig = create_machine_utilization_chart(kpi_data['machine_utilization'])
#             if util_fig:
#                 st.plotly_chart(util_fig, use_container_width=True)
            
#             # Detailed table
#             st.subheader("Machine Statistics")
#             machine_stats_df = pd.DataFrame(kpi_data['machine_utilization'])
#             machine_stats_df.columns = ['Machine', 'Used Hours', 'Utilization (%)', 'Num Operations']
#             st.dataframe(machine_stats_df, use_container_width=True)
#         else:
#             st.info("No machine statistics available")
    
#     # Footer
#     st.markdown("---")
#     st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total schedules: {len(df_schedule)}")


# if __name__ == "__main__":
#     main()








import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"  # Update with your Django API URL

# Page config
st.set_page_config(
    page_title="Production Schedule Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (only for non-timeline elements)
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)


# Helper functions
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

# def generate_timeline_html(df_schedule, start_time, end_time, time_interval_minutes=30):
#     """Generate custom timeline HTML - returns complete HTML document"""
#     if df_schedule.empty:
#         return "<html><body><p>No schedule data available</p></body></html>"
    
#     # Convert times
#     df = df_schedule.copy()
#     df['start_time'] = pd.to_datetime(df['start_time'])
#     df['end_time'] = pd.to_datetime(df['end_time'])
    
#     # Get unique machines
#     machines = sorted(df['machine_name'].unique())
    
#     # Calculate timeline range - ensure timezone consistency
#     timeline_start = pd.to_datetime(start_time)
#     timeline_end = pd.to_datetime(end_time)
    
#     # Check if the dataframe times have timezone info
#     if df['start_time'].dt.tz is not None:
#         if timeline_start.tz is None:
#             timeline_start = timeline_start.tz_localize(df['start_time'].dt.tz)
#         if timeline_end.tz is None:
#             timeline_end = timeline_end.tz_localize(df['start_time'].dt.tz)
#     else:
#         if timeline_start.tz is not None:
#             timeline_start = timeline_start.tz_localize(None)
#         if timeline_end.tz is not None:
#             timeline_end = timeline_end.tz_localize(None)
    
#     total_hours = (timeline_end - timeline_start).total_seconds() / 3600
    
#     # Generate time slots
#     time_slots = []
#     current_time = timeline_start
#     while current_time < timeline_end:
#         time_slots.append(current_time)
#         current_time += timedelta(seconds=time_interval_minutes)
    
#     num_slots = len(time_slots)
    
#     # Build complete HTML document with embedded styles
#     html = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <style>
#             body {
#                 margin: 0;
#                 padding: 20px;
#                 font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
#                 background: #ffffff;
#             }
            
#             .timeline-container {
#                 width: 100%;
#                 overflow-x: auto;
#                 overflow-y: visible;
#                 background: white;
#                 border-radius: 8px;
#                 padding: 20px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             }
            
#             .timeline-grid {
#                 display: grid;
#                 grid-template-columns: 150px 1fr;
#                 min-width: 120000px;
#                 gap: 0;
#             }
            
#             .timeline-header {
#                 display: contents;
#             }
            
#             .machine-label {
#                 font-weight: bold;
#                 padding: 15px;
#                 background: #f8f9fa;
#                 border-right: 2px solid #dee2e6;
#                 border-bottom: 1px solid #dee2e6;
#                 display: flex;
#                 align-items: center;
#                 color: #495057;
#                 position: sticky;
#                 left: 0;
#                 z-index: 10;
#             }
            
#             .time-header {
#                 display: flex;
#                 border-bottom: 2px solid #dee2e6;
#                 background: #f8f9fa;
#                 position: sticky;
#                 top: 0;
#                 z-index: 5;
#             }
            
#             .time-slot-header {
#                 flex: 1;
#                 min-width: 100px;
#                 padding: 10px;
#                 text-align: center;
#                 border-right: 1px solid #e9ecef;
#                 font-size: 0.85rem;
#                 color: #6c757d;
#                 font-weight: 600;
#             }
            
#             .machine-row {
#                 display: flex;
#                 position: relative;
#                 min-height: 80px;
#                 border-bottom: 1px solid #dee2e6;
#                 background: white;
#             }
            
#             .time-grid {
#                 flex: 1;
#                 display: flex;
#                 position: relative;
#             }
            
#             .time-slot {
#                 flex: 1;
#                 min-width: 100px;
#                 border-right: 1px solid #e9ecef;
#                 position: relative;
#             }
            
#             .schedule-card {
#                 position: absolute;
#                 height: 60px;
#                 border-radius: 6px;
#                 padding: 8px 12px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.15);
#                 display: flex;
#                 flex-direction: column;
#                 justify-content: center;
#                 color: white;
#                 font-size: 0.85rem;
#                 font-weight: 500;
#                 cursor: pointer;
#                 transition: all 0.2s;
#                 overflow: hidden;
#                 z-index: 2;
#                 top: 10px;
#             }
            
#             .schedule-card:hover {
#                 transform: translateY(-2px);
#                 box-shadow: 0 4px 8px rgba(0,0,0,0.2);
#                 z-index: 3;
#             }
            
#             .card-title {
#                 font-weight: 600;
#                 font-size: 0.9rem;
#                 margin-bottom: 2px;
#                 white-space: nowrap;
#                 overflow: hidden;
#                 text-overflow: ellipsis;
#             }
            
#             .card-subtitle {
#                 font-size: 0.75rem;
#                 opacity: 0.9;
#                 white-space: nowrap;
#                 overflow: hidden;
#                 text-overflow: ellipsis;
#             }
            
#             /* Color schemes for different items */
#             .item-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
#             .item-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
#             .item-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
#             .item-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
#             .item-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
#             .item-6 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
#             .item-7 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
#             .item-8 { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
#             .item-9 { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }
#             .item-10 { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); }

#             .item-11 { background: linear-gradient(135deg, #fddb92 0%, #d1fdff 100%); }
#             .item-12 { background: linear-gradient(135deg, #9890e3 0%, #b1f4cf 100%); }
#             .item-13 { background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%); }
#             .item-14 { background: linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%); }
#             .item-15 { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
#             .item-16 { background: linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%); }
#             .item-17 { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }
#             .item-18 { background: linear-gradient(135deg, #f8b500 0%, #fceabb 100%); }
#             .item-19 { background: linear-gradient(135deg, #cfd9df 0%, #e2ebf0 100%); }
#             .item-20 { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }

#             .item-21 { background: linear-gradient(135deg, #ff8177 0%, #ff867a 100%); }
#             .item-22 { background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); }
#             .item-23 { background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); }
#             .item-24 { background: linear-gradient(135deg, #b24592 0%, #f15f79 100%); }
#             .item-25 { background: linear-gradient(135deg, #4568dc 0%, #b06ab3 100%); }
#             .item-26 { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
#             .item-27 { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); }
#             .item-28 { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
#             .item-29 { background: linear-gradient(135deg, #f77062 0%, #fe5196 100%); }
#             .item-30 { background: linear-gradient(135deg, #5ee7df 0%, #b490ca 100%); }

#             .item-31 { background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%); }
#             .item-32 { background: linear-gradient(135deg, #7f7fd5 0%, #86a8e7 100%); }
#             .item-33 { background: linear-gradient(135deg, #e1eec3 0%, #f05053 100%); }
#             .item-34 { background: linear-gradient(135deg, #c471ed 0%, #f64f59 100%); }
#             .item-35 { background: linear-gradient(135deg, #12c2e9 0%, #c471ed 100%); }
#             .item-36 { background: linear-gradient(135deg, #fbc7d4 0%, #9796f0 100%); }
#             .item-37 { background: linear-gradient(135deg, #cfd9df 0%, #e2ebf0 100%); }
#             .item-38 { background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%); }
#             .item-39 { background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%); }
#             .item-40 { background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%); }

#             .item-41 { background: linear-gradient(135deg, #1fddff 0%, #ff4b1f 100%); }
#             .item-42 { background: linear-gradient(135deg, #3a1c71 0%, #d76d77 100%); }
#             .item-43 { background: linear-gradient(135deg, #0fd850 0%, #f9f047 100%); }
#             .item-44 { background: linear-gradient(135deg, #74ebd5 0%, #acb6e5 100%); }
#             .item-45 { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); }
#             .item-46 { background: linear-gradient(135deg, #4ca1af 0%, #c4e0e5 100%); }
#             .item-47 { background: linear-gradient(135deg, #ff5f6d 0%, #ffc371 100%); }
#             .item-48 { background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%); }
#             .item-49 { background: linear-gradient(135deg, #ee9ca7 0%, #ffdde1 100%); }
#             .item-50 { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); }

            
#             .legend {
#                 display: flex;
#                 flex-wrap: wrap;
#                 gap: 15px;
#                 margin: 20px 0;
#                 padding: 15px;
#                 background: #f8f9fa;
#                 border-radius: 6px;
#             }
            
#             .legend-item {
#                 display: flex;
#                 align-items: center;
#                 gap: 8px;
#                 font-size: 0.85rem;
#             }
            
#             .legend-color {
#                 width: 30px;
#                 height: 20px;
#                 border-radius: 4px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             }
#         </style>
#     </head>
#     <body>
#     """
    
#     html += '<div class="timeline-container">'
#     html += '<div class="timeline-grid">'
    
#     # Header row
#     html += '<div class="timeline-header">'
#     html += '<div class="machine-label" style="background: #e9ecef;">Machine</div>'
#     html += '<div class="time-header">'
    
#     for time_slot in time_slots:
#         time_str = time_slot.strftime('%H:%M')
#         date_str = time_slot.strftime('%m/%d')
#         html += f'<div class="time-slot-header">{date_str}<br>{time_str}</div>'
    
#     html += '</div></div>'
    
#     # Machine rows
#     for machine in machines:
#         machine_data = df[df['machine_name'] == machine]
        
#         html += f'<div class="machine-label">{machine}</div>'
#         html += '<div class="machine-row">'
#         html += '<div class="time-grid">'
        
#         # Add time slot dividers
#         for i in range(num_slots):
#             html += '<div class="time-slot"></div>'
        
#         # Add schedule cards
#         for _, row in machine_data.iterrows():
#             start = row['start_time']
#             end = row['end_time']
            
#             # Calculate position and width
#             start_offset = (start - timeline_start).total_seconds() / 3600
#             duration = (end - start).total_seconds() / 3600
            
#             left_percent = (start_offset / total_hours) * 100
#             width_percent = (duration / total_hours) * 100
            
#             # Ensure card stays within bounds
#             if left_percent < 0:
#                 width_percent += left_percent
#                 left_percent = 0
#             if left_percent + width_percent > 100:
#                 width_percent = 100 - left_percent
            
#             if width_percent > 0:
#                 item_class = f"item-{row['product_item']}"
#                 batch_id = row['batch_id']
#                 step_num = row['step_number']
#                 step_name = str(row['step_name'])[:30]
                
#                 html += f'''
#                 <div class="schedule-card {item_class}" 
#                      style="left: {left_percent}%; width: {width_percent}%;"
#                      title="{batch_id} - Step {step_num}: {step_name}">
#                     <div class="card-title">Step {step_num}</div>
#                     <div class="card-subtitle">{batch_id}</div>
#                 </div>
#                 '''
        
#         html += '</div></div>'
    
#     html += '</div></div>'
    
#     # Add legend
#     html += '<div class="legend">'
#     items = sorted(df['product_item'].unique())
#     for item in items:
#         item_desc = df[df['product_item'] == item]['product_description'].iloc[0]
#         short_desc = item_desc[:40] + "..." if len(item_desc) > 40 else item_desc
#         html += f'''
#         <div class="legend-item">
#             <div class="legend-color item-{item}"></div>
#             <span><strong>Item {item}:</strong> {short_desc}</span>
#         </div>
#         '''
#     html += '</div>'
    
#     html += '</body></html>'
    
#     return html


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


# Main app
def main():
    # Header
    st.markdown('<div class="main-header">🏭 Production Schedule Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimized Machine Time Allocation</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Controls")
    
    # Initialize/Regenerate buttons
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
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    # Get filter options
    filter_options = fetch_data("get-filter-options")
    
    if filter_options:
        # Machine filter
        machines = ['All'] + filter_options.get('machines', [])
        selected_machine = st.sidebar.selectbox("Select Machine(s)", machines)
        
        # Product filter
        products = filter_options.get('products', [])
        product_options = ['All'] + [f"Item {p['item']}: {p['description'][:30]}..." for p in products]
        selected_product = st.sidebar.selectbox("Select Product", product_options)
        
        # Time range
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
        selected_machine = 'All'
        selected_product = 'All'
        start_date = None
        end_date = None
    
    st.sidebar.markdown("---")
    
    # Timeline settings
    st.sidebar.subheader("⏱️ Timeline View Settings")
    time_interval_minutes = st.sidebar.slider("Time Interval (minutes)", 5, 120, 30, step=5)
    time_interval = time_interval_minutes / 60  # Convert to hours for internal use
    
    # Optimization goal (placeholder for future use)
    st.sidebar.subheader("🎯 Optimization Goal")
    optimization_goal = st.sidebar.radio(
        "Select Goal",
        ["Minimize Makespan", "Maximize Throughput"],
        disabled=True
    )
    st.sidebar.caption("ℹ️ Feature coming soon")
    
    # Main content
    # Fetch schedule data
    params = {}
    if selected_machine != 'All':
        params['machine'] = selected_machine
    if selected_product != 'All':
        product_item = int(selected_product.split(':')[0].replace('Item ', ''))
        params['product'] = product_item
    if start_date:
        params['start_date'] = start_date.isoformat()
    if end_date:
        params['end_date'] = end_date.isoformat()
    
    schedule_data = fetch_data("get-schedule", params)
    kpi_data = fetch_data("get-kpis")
    
    if not schedule_data or not schedule_data.get('schedules'):
        st.warning("⚠️ No schedule data available. Please initialize data and generate schedule.")
        return
    
    # Convert to DataFrame
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
            avg_utilization = sum([m['utilization'] for m in kpi_data.get('machine_utilization', [])]) / len(kpi_data.get('machine_utilization', [1]))
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
        
        # Get time range for timeline
        if start_date and end_date:
            timeline_start = datetime.combine(start_date, datetime.min.time())
            timeline_end = datetime.combine(end_date, datetime.max.time())
        else:
            timeline_start = pd.to_datetime(df_schedule['start_time']).min()
            timeline_end = pd.to_datetime(df_schedule['end_time']).max()
        
        # Generate and display custom timeline using components.html
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
        
        # Display options
        display_cols = [
            'machine_name', 'product_item', 'product_sap_tn', 'product_dcc_type',
            'batch_id', 'step_number', 'step_name', 'workers_required',
            'start_time', 'end_time', 'duration_hours'
        ]
        
        df_display = df_schedule[display_cols].copy()
        df_display['start_time'] = pd.to_datetime(df_display['start_time']).dt.strftime('%Y-%m-%d %H:%M')
        df_display['end_time'] = pd.to_datetime(df_display['end_time']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns for display
        df_display.columns = [
            'Machine', 'Item', 'SAP TN', 'DCC Type', 'Batch ID',
            'Step', 'Step Name', 'Workers', 'Start Time', 'End Time', 'Duration (h)'
        ]
        
        st.dataframe(df_display, use_container_width=True, height=600)
        
        # Download button
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
            # Utilization chart
            util_fig = create_machine_utilization_chart(kpi_data['machine_utilization'])
            if util_fig:
                st.plotly_chart(util_fig, use_container_width=True)
            
            # Detailed table
            st.subheader("Machine Statistics")
            machine_stats_df = pd.DataFrame(kpi_data['machine_utilization'])
            machine_stats_df.columns = ['Machine', 'Used Hours', 'Utilization (%)', 'Num Operations']
            st.dataframe(machine_stats_df, use_container_width=True)
        else:
            st.info("No machine statistics available")
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total schedules: {len(df_schedule)}")


if __name__ == "__main__":
    main()
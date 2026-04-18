"""
Dashboard Module
Streamlit-based interactive dashboard for poll results visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_processor import DataProcessor
from analyzer import PollAnalyzer
from visualizer import PollVisualizer

# Set page configuration
st.set_page_config(
    page_title="Poll Results Visualizer",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path):
    """Load and cache data."""
    processor = DataProcessor()
    return processor.load_data(file_path)

@st.cache_data
def process_data(df):
    """Process and cache cleaned data."""
    processor = DataProcessor()
    return processor.clean_data(df)

@st.cache_data
def analyze_data(df):
    """Analyze and cache analysis results."""
    analyzer = PollAnalyzer()
    return analyzer.analyze_responses(df)

def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">:bar_chart: Poll Results Visualizer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for file upload and filters
    st.sidebar.header("Configuration")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Poll Data (CSV)",
        type=['csv'],
        help="Upload a CSV file containing poll responses"
    )
    
    # Option to use synthetic data
    use_synthetic = st.sidebar.checkbox(
        "Use Synthetic Data",
        help="Generate sample poll data for demonstration"
    )
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
        st.session_state.analysis_results = None
        st.session_state.processor = DataProcessor()
        st.session_state.analyzer = PollAnalyzer()
        st.session_state.visualizer = PollVisualizer()
    
    # Load data
    if use_synthetic:
        st.sidebar.info("Generating synthetic poll data...")
        with st.spinner("Generating synthetic data..."):
            synthetic_data = st.session_state.processor.generate_synthetic_data(num_responses=1000)
            st.session_state.data = process_data(synthetic_data)
            st.session_state.analysis_results = analyze_data(st.session_state.data)
        st.sidebar.success("Synthetic data loaded successfully!")
        
    elif uploaded_file is not None:
        st.sidebar.info("Loading uploaded data...")
        with st.spinner("Loading and processing data..."):
            raw_data = load_data(uploaded_file)
            st.session_state.data = process_data(raw_data)
            st.session_state.analysis_results = analyze_data(st.session_state.data)
        st.sidebar.success("Data loaded successfully!")
    
    # Check if data is available
    if st.session_state.data is None:
        st.warning("Please upload a CSV file or use synthetic data to begin.")
        st.info("""
        **Expected CSV Format:**
        - respondent_id: Unique identifier for each respondent
        - timestamp: Response timestamp
        - question: Poll question text
        - response: Selected option/answer
        - region: Geographic region (optional)
        - gender: Gender (optional)
        - age_group: Age group (optional)
        - satisfaction_score: Rating 1-5 (optional)
        - feedback: Text feedback (optional)
        """)
        return
    
    data = st.session_state.data
    analysis_results = st.session_state.analysis_results
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        min_date = data['timestamp'].min().date()
        max_date = data['timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            mask = (data['timestamp'].dt.date >= date_range[0]) & (data['timestamp'].dt.date <= date_range[1])
            data = data[mask]
    
    # Region filter
    if 'region' in data.columns:
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            options=data['region'].unique(),
            default=data['region'].unique()
        )
        data = data[data['region'].isin(selected_regions)]
    
    # Gender filter
    if 'gender' in data.columns:
        selected_genders = st.sidebar.multiselect(
            "Select Genders",
            options=data['gender'].unique(),
            default=data['gender'].unique()
        )
        data = data[data['gender'].isin(selected_genders)]
    
    # Age group filter
    if 'age_group' in data.columns:
        selected_age_groups = st.sidebar.multiselect(
            "Select Age Groups",
            options=data['age_group'].unique(),
            default=data['age_group'].unique()
        )
        data = data[data['age_group'].isin(selected_age_groups)]
    
    # Main content area
    st.header("Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_respondents = data['respondent_id'].nunique() if 'respondent_id' in data.columns else len(data)
        st.metric("Total Respondents", total_respondents)
    
    with col2:
        total_responses = len(data)
        st.metric("Total Responses", total_responses)
    
    with col3:
        avg_satisfaction = data['satisfaction_score'].mean() if 'satisfaction_score' in data.columns else 0
        st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}/5.0")
    
    with col4:
        date_range_days = (data['timestamp'].max() - data['timestamp'].min()).days if 'timestamp' in data.columns else 0
        st.metric("Date Range", f"{date_range_days} days")
    
    # Data preview
    st.subheader("Data Preview")
    with st.expander("View Raw Data"):
        st.dataframe(data, use_container_width=True)
    
    # Charts section
    st.header("Visualizations")
    
    # Create tabs for different chart types
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Response Analysis", "Demographics", "Trends", "Feedback"])
    
    with tab1:
        st.subheader("Overview Dashboard")
        
        # Response distribution
        if 'response' in data.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                response_counts = data['response'].value_counts()
                fig_response = px.bar(
                    x=response_counts.index,
                    y=response_counts.values,
                    title="Response Distribution",
                    labels={'x': 'Response', 'y': 'Count'}
                )
                st.plotly_chart(fig_response, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig_pie = px.pie(
                    names=response_counts.index,
                    values=response_counts.values,
                    title="Response Percentage"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Satisfaction distribution
        if 'satisfaction_score' in data.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_satisfaction = px.histogram(
                data,
                x='satisfaction_score',
                title="Satisfaction Score Distribution",
                nbins=5,
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig_satisfaction, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Response Analysis")
        
        if 'question' in data.columns and 'response' in data.columns:
            # Question-wise analysis
            questions = data['question'].unique()
            selected_question = st.selectbox("Select Question", questions)
            
            question_data = data[data['question'] == selected_question]
            response_counts = question_data['response'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_question_bar = px.bar(
                    x=response_counts.index,
                    y=response_counts.values,
                    title=f"Responses: {selected_question}",
                    labels={'x': 'Response', 'y': 'Count'}
                )
                st.plotly_chart(fig_question_bar, use_container_width=True)
            
            with col2:
                fig_question_pie = px.pie(
                    names=response_counts.index,
                    values=response_counts.values,
                    title=f"Response Percentages: {selected_question}"
                )
                st.plotly_chart(fig_question_pie, use_container_width=True)
    
    with tab3:
        st.subheader("Demographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'region' in data.columns:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                region_counts = data['region'].value_counts()
                fig_region = px.bar(
                    x=region_counts.index,
                    y=region_counts.values,
                    title="Responses by Region"
                )
                st.plotly_chart(fig_region, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if 'gender' in data.columns:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                gender_counts = data['gender'].value_counts()
                fig_gender = px.pie(
                    names=gender_counts.index,
                    values=gender_counts.values,
                    title="Gender Distribution"
                )
                st.plotly_chart(fig_gender, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Age group distribution
        if 'age_group' in data.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            age_counts = data['age_group'].value_counts()
            fig_age = px.bar(
                x=age_counts.index,
                y=age_counts.values,
                title="Age Group Distribution"
            )
            st.plotly_chart(fig_age, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cross-tabulation analysis
        if 'region' in data.columns and 'response' in data.columns:
            st.subheader("Regional Response Patterns")
            cross_tab = pd.crosstab(data['region'], data['response'])
            fig_cross = px.imshow(
                cross_tab,
                title="Regional Response Heatmap",
                labels=dict(x="Response", y="Region", color="Count")
            )
            st.plotly_chart(fig_cross, use_container_width=True)
    
    with tab4:
        st.subheader("Temporal Trends")
        
        if 'timestamp' in data.columns:
            # Daily response trends
            data['date'] = data['timestamp'].dt.date
            daily_counts = data.groupby('date').size().reset_index()
            daily_counts.columns = ['date', 'count']
            
            fig_daily = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Daily Response Trends",
                markers=True
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Hourly response patterns
            data['hour'] = data['timestamp'].dt.hour
            hourly_counts = data.groupby('hour').size().reset_index()
            hourly_counts.columns = ['hour', 'count']
            
            fig_hourly = px.bar(
                hourly_counts,
                x='hour',
                y='count',
                title="Hourly Response Patterns"
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Satisfaction over time
            if 'satisfaction_score' in data.columns:
                daily_satisfaction = data.groupby('date')['satisfaction_score'].mean().reset_index()
                daily_satisfaction.columns = ['date', 'avg_satisfaction']
                
                fig_sat_time = px.line(
                    daily_satisfaction,
                    x='date',
                    y='avg_satisfaction',
                    title="Average Satisfaction Over Time",
                    markers=True
                )
                st.plotly_chart(fig_sat_time, use_container_width=True)
    
    with tab5:
        st.subheader("Feedback Analysis")
        
        if 'feedback' in data.columns:
            # Feedback length analysis
            data['feedback_length'] = data['feedback'].astype(str).str.len()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_feedback_len = px.histogram(
                    data,
                    x='feedback_length',
                    title="Feedback Length Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_feedback_len, use_container_width=True)
            
            with col2:
                if 'satisfaction_score' in data.columns:
                    fig_feedback_sat = px.box(
                        data,
                        x='satisfaction_score',
                        y='feedback_length',
                        title="Feedback Length vs Satisfaction"
                    )
                    st.plotly_chart(fig_feedback_sat, use_container_width=True)
            
            # Sample feedback text
            st.subheader("Sample Feedback")
            sample_feedback = data[data['feedback'].str.len() > 10]['feedback'].dropna().head(10)
            
            for i, feedback in enumerate(sample_feedback, 1):
                st.write(f"{i}. {feedback}")
    
    # Insights section
    st.header("Key Insights")
    
    if analysis_results and 'key_insights' in analysis_results:
        insights = analysis_results['key_insights']
        
        for i, insight in enumerate(insights, 1):
            st.success(f"{i}. {insight}")
    
    # Export functionality
    st.header("Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Filtered Data (CSV)"):
            csv_data = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="filtered_poll_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export Summary Report"):
            # Create summary report
            summary = {
                'total_respondents': data['respondent_id'].nunique() if 'respondent_id' in data.columns else len(data),
                'total_responses': len(data),
                'date_range': f"{data['timestamp'].min().date()} to {data['timestamp'].max().date()}" if 'timestamp' in data.columns else "N/A",
                'avg_satisfaction': f"{data['satisfaction_score'].mean():.1f}/5.0" if 'satisfaction_score' in data.columns else "N/A",
                'top_response': data['response'].mode().iloc[0] if 'response' in data.columns else "N/A"
            }
            
            summary_text = "Poll Results Summary Report\n" + "="*50 + "\n"
            for key, value in summary.items():
                summary_text += f"{key.replace('_', ' ').title()}: {value}\n"
            
            st.download_button(
                label="Download Summary",
                data=summary_text,
                file_name="poll_summary.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("Generate Analysis Report"):
            st.info("Analysis report generation coming soon!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Poll Results Visualizer v1.0 | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

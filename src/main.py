"""
Main Streamlit Application for IntelliQuery
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import logging
import time

# Import internal modules
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Config
from src.connectors.monday_client import MondayClient
from src.processors.data_cleaner import DataCleaner
from src.processors.query_parser import QueryParser
from src.analytics.bi_engine import BIEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Config
st.set_page_config(
    page_title="IntelliQuery | AI Business Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E1E1E;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_system():
    """Initialize system components"""
    try:
        Config.validate()
        return {
            'monday': MondayClient(),
            'cleaner': DataCleaner(),
            'parser': QueryParser(),
            'bi': BIEngine()
        }
    except Exception as e:
        st.error(f"System Initialization Failed: {e}")
        return None


@st.cache_data(ttl=3600)
def load_data(_system):
    """Fetch and clean data from monday.com"""
    try:
        with st.spinner("Fetching data from monday.com..."):
            # Fetch raw data
            raw_deals = _system['monday'].fetch_deals()
            raw_orders = _system['monday'].fetch_work_orders()
            
            # Clean data
            deals_df = _system['cleaner'].normalize_deals(raw_deals)
            orders_df = _system['cleaner'].normalize_work_orders(raw_orders)
            
            # Join data
            combined_df = _system['cleaner'].join_deals_and_orders(deals_df, orders_df)
            
            # Get quality report
            quality_report = _system['cleaner'].get_quality_report()
            
            return {
                'deals': deals_df,
                'orders': orders_df,
                'combined': combined_df,
                'quality_report': quality_report,
                'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        st.error(f"Data Loading Failed: {e}")
        return None


def render_pipeline_dashboard(data: Dict, bi_engine: BIEngine, key_prefix: str = ""):
    """Render pipeline analysis dashboard"""
    st.subheader("📊 Pipeline Analysis")
    
    metrics = bi_engine.analyze_pipeline(data['deals'])
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Deals", metrics['total_deals'])
    c2.metric("Pipeline Value", f"₹{metrics['total_pipeline_value']:,.0f}")
    c3.metric("Weighted Value", f"₹{metrics['weighted_pipeline_value']:,.0f}")
    c4.metric("Avg Deal Size", f"₹{metrics['average_deal_size']:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Deals by Stage")
        stage_df = pd.DataFrame(list(metrics['deals_by_stage'].items()), columns=['Stage', 'Count'])
        fig = px.bar(stage_df, x='Count', y='Stage', orientation='h', color='Count')
        st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_pipeline_stage")
        
    with col2:
        st.markdown("##### Probability Distribution")
        prob_df = pd.DataFrame(list(metrics['deals_by_probability'].items()), columns=['Probability', 'Count'])
        fig = px.pie(prob_df, values='Count', names='Probability', hole=0.4)
        st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_pipeline_prob")


def render_revenue_dashboard(data: Dict, bi_engine: BIEngine, key_prefix: str = ""):
    """Render revenue analysis dashboard"""
    st.subheader("💰 Revenue & Collections")
    
    metrics = bi_engine.revenue_analysis(data['orders'])
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Billed", f"₹{metrics['total_billed']:,.0f}")
    c2.metric("Total Collected", f"₹{metrics['total_collected']:,.0f}")
    c3.metric("Collection Rate", f"{metrics['collection_rate']:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Revenue by Sector")
        sector_df = pd.DataFrame(list(metrics['revenue_by_sector'].items()), columns=['Sector', 'Revenue'])
        fig = px.pie(sector_df, values='Revenue', names='Sector')
        st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_rev_sector")
        
    with col2:
        st.markdown("##### Monthly Billing Trend")
        trend_df = pd.DataFrame(list(metrics['monthly_trend'].items()), columns=['Month', 'Billed'])
        fig = px.line(trend_df, x='Month', y='Billed', markers=True)
        st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_rev_trend")


def render_analysis_result(intent: Dict, metrics: Dict, system: Dict, data: Dict, key_prefix: str = "", user_query: str = ""):
    """Render the analysis result based on intent and metrics"""
    
    # Generate natural language insights
    if user_query and not metrics.get('error'):
        with st.spinner("Generating insights..."):
            try:
                insights = system['parser'].generate_insights(user_query, intent, metrics)
                
                # Check if insight is valid and complete
                if insights and len(insights) > 20 and "Analysis complete" not in insights:
                    st.info(f"💡 **Insights:** {insights}")
                elif insights and len(insights) <= 20:
                    # Truncated or incomplete response - show simple fallback
                    logger.warning(f"Insight generation returned truncated response: {insights}")
                    st.info(f"💡 Analysis complete. Review the metrics and charts below.")
                else:
                    st.info(f"💡 Analysis complete. Review the metrics and charts below.")
            except Exception as e:
                logger.error(f"Failed to display insights: {e}")
                st.info(f"💡 Analysis complete. Review the metrics and charts below.")
    
    # Handle Clarification
    if intent.get('clarification_needed') and intent.get('clarifying_questions'):
        st.warning("I need a bit more detail to be precise:")
        for q in intent['clarifying_questions']:
            st.write(f"- {q}")
        st.markdown("---")
        st.info(f"Showing **{intent['intent'].replace('_', ' ').title()}** based on my best guess:")

    if intent['intent'] == 'pipeline_analysis':
        st.write(f"### Pipeline Analysis")
        
        # Show data quality warnings if present
        if metrics.get('data_quality', {}).get('warnings'):
            with st.expander("⚠️ Data Quality Warnings", expanded=False):
                for warning in metrics['data_quality']['warnings']:
                    st.warning(warning)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Pipeline Value", f"₹{metrics.get('total_pipeline_value', 0):,.0f}")
        c2.metric("Deal Count", metrics.get('deal_count', 0))
        
        if metrics.get('monthly_trend'):
            st.subheader("Monthly Deal Trend")
            trend_df = pd.DataFrame(list(metrics['monthly_trend'].items()), columns=['Month', 'Count'])
            # Sort by date if possible (Month Year format is tricky to sort, but px usually handles it or we can sort by date)
            fig = px.line(trend_df, x='Month', y='Count', markers=True)
            st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_pipeline_trend")

        st.subheader("Top Deals")
        st.dataframe(pd.DataFrame(metrics.get('top_deals', [])), width='stretch')
        
    elif intent['intent'] == 'revenue_analysis':
        st.write(f"### Revenue Analysis")
        
        # Show data quality warnings if present
        if metrics.get('data_quality', {}).get('warnings'):
            with st.expander("⚠️ Data Quality Warnings", expanded=False):
                for warning in metrics['data_quality']['warnings']:
                    st.warning(warning)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Billed", f"₹{metrics.get('total_billed', 0):,.0f}")
        c2.metric("Total Collected", f"₹{metrics.get('total_collected', 0):,.0f}")
        
        st.subheader("Revenue by Sector")
        # Use Plotly for better control and unique keys
        sector_data = metrics.get('revenue_by_sector', {})
        if sector_data:
            sector_df = pd.DataFrame(list(sector_data.items()), columns=['Sector', 'Revenue'])
            fig = px.bar(sector_df, x='Sector', y='Revenue', color='Sector')
            st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_analysis_rev_sector")
        
    elif intent['intent'] == 'risk_assessment':
        st.write(f"### Risk Assessment")
        st.write(f"Found {metrics.get('total_risks', 0)} potential risks.")
        
        risk_df = pd.DataFrame(metrics.get('risk_list', []))
        if not risk_df.empty:
            st.dataframe(risk_df, width='stretch')
        else:
            st.success("No major risks found!")
    
    elif intent['intent'] == 'sector_performance':
        st.write(f"### Sector Performance Analysis")
        st.caption("📊 Cross-board analytics combining deals and work orders")
        
        sector_data = metrics.get('sector_performance', [])
        if sector_data:
            df = pd.DataFrame(sector_data)
            
            # Summary metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Sectors Analyzed", len(df))
            c2.metric("Total Pipeline", f"₹{df['pipeline_value'].sum():,.0f}")
            c3.metric("Total Revenue", f"₹{df['billed_revenue'].sum():,.0f}")
            
            # Detailed table
            st.subheader("Performance by Sector")
            st.dataframe(df, width='stretch')
            
            # Comparison chart
            st.subheader("Sector Comparison")
            fig = px.bar(df, x='sector', 
                        y=['pipeline_value', 'billed_revenue', 'collected_revenue'],
                        title="Pipeline vs Revenue by Sector",
                        barmode='group',
                        labels={'value': 'Amount (₹)', 'variable': 'Metric'})
            st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_sector_perf")
        else:
            st.warning("No sector data available for comparison.")
    
    elif intent['intent'] == 'resource_utilization':
        st.write(f"### Resource Utilization")
        
        owner_data = metrics.get('owner_performance', [])
        if owner_data:
            df = pd.DataFrame(owner_data)
            
            c1, c2 = st.columns(2)
            c1.metric("Total Owners/Resources", metrics.get('total_owners', 0))
            c2.metric("Avg Deals per Owner", f"{metrics.get('avg_deals_per_owner', 0):.1f}")
            
            st.subheader("Performance by Owner")
            st.dataframe(df, width='stretch')
            
            # Workload distribution chart
            fig = px.bar(df, x='owner', y='deal_count', 
                        title="Deal Distribution by Owner",
                        labels={'deal_count': 'Number of Deals', 'owner': 'Owner'})
            st.plotly_chart(fig, width='stretch', key=f"{key_prefix}_resource_dist")
        else:
            st.info("No owner assignment data available.")
    
    elif intent['intent'] == 'operational_metrics':
        st.write(f"### Operational Metrics")
        
        if metrics.get('conversion_rate') is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Conversion Rate", f"{metrics.get('conversion_rate', 0):.1f}%")
            c2.metric("Won Deals", metrics.get('won_deals', 0))
            c3.metric("Loss Rate", f"{metrics.get('loss_rate', 0):.1f}%")
        
        if metrics.get('avg_cycle_days'):
            st.subheader("Deal Cycle Time")
            c1, c2 = st.columns(2)
            c1.metric("Average Days", f"{metrics.get('avg_cycle_days', 0):.0f}")
            c2.metric("Median Days", f"{metrics.get('median_cycle_days', 0):.0f}")
            st.caption(f"Based on {metrics.get('deals_with_cycle_data', 0)} closed deals")
        else:
            st.info("Cycle time data not available (missing close dates).")
            
    else:
        st.write("I analyzed your data based on your query.")
        st.info("Showing general dashboard for context:")
        render_pipeline_dashboard(data, system['bi'], key_prefix=f"{key_prefix}_fallback")
    
    # Suggest follow-up questions
    if not metrics.get('error'):
        st.markdown("---")
        with st.expander("💡 You might also ask...", expanded=False):
            suggestions = []
            
            if intent['intent'] == 'pipeline_analysis':
                suggestions = [
                    "What are the high-risk deals?",
                    "Show me revenue for this sector",
                    "Which deals have been open the longest?",
                    "Compare pipeline across all sectors"
                ]
            elif intent['intent'] == 'revenue_analysis':
                suggestions = [
                    "Which clients haven't paid yet?",
                    "Show me the pipeline for this sector",
                    "What's our collection rate trend?",
                    "Compare revenue across sectors"
                ]
            elif intent['intent'] == 'risk_assessment':
                suggestions = [
                    "Show me the pipeline health",
                    "What's our total revenue?",
                    "Which sector has the most risks?",
                    "Show me high-value deals"
                ]
            
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")


def main():
    # Sidebar
    with st.sidebar:
        st.image("https://cdn.monday.com/images/logos/monday_logo_icon.png", width=50)
        st.title("IntelliQuery")
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
            
        st.markdown("### 🛠️ Settings")
        debug_mode = st.checkbox("Debug Mode", value=Config.DEBUG_MODE)
        
        st.markdown("---")
        st.markdown("### 💡 Sample Queries")
        st.code("How's our pipeline looking for mining sector?")
        st.code("What's our total revenue this quarter?")
        st.code("Which deals are at risk?")
    
    # Main Content
    st.markdown('<div class="main-header">🚀 Business Intelligence Agent</div>', unsafe_allow_html=True)
    
    # Initialize System
    system = init_system()
    if not system:
        st.stop()
        
    # Load Data
    data = load_data(system)
    if not data:
        st.stop()
        
    # Data Quality Warning
    with st.expander("⚠️ Data Quality Report"):
        st.markdown(data['quality_report'])
        
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display Chat History
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                # Render the stored analysis result with unique key
                render_analysis_result(
                    message["intent"], 
                    message["metrics"], 
                    system, 
                    data, 
                    key_prefix=f"hist_{idx}",
                    user_query=st.session_state.messages[idx-1]["content"] if idx > 0 else ""
                )
    
    # Query Interface
    query = st.chat_input("Ask a question about your business data...")
    
    # Default View (Dashboard) - Only show if no history and no current query
    if not query and not st.session_state.messages:
        tab1, tab2, tab3 = st.tabs(["Pipeline", "Revenue", "Risks"])
        
        with tab1:
            render_pipeline_dashboard(data, system['bi'], key_prefix="dash_pipeline")
            
        with tab2:
            render_revenue_dashboard(data, system['bi'], key_prefix="dash_revenue")
            
        with tab3:
            st.subheader("🚨 Risk Assessment")
            risks = system['bi'].risk_assessment(data['deals'], data['orders'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("High Risks", risks['risk_summary']['high'], delta_color="inverse")
            c2.metric("Medium Risks", risks['risk_summary']['medium'], delta_color="inverse")
            c3.metric("Total Issues", risks['total_risks'])
            
            for risk in risks['risk_list']:
                color = "red" if risk['severity'] == "High" else "orange"
                st.markdown(f":{color}[**{risk['type']}**] ({risk['id']}): {risk['message']}")
    
    # Query Processing
    if query:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display User Query (immediately)
        with st.chat_message("user"):
            st.write(query)
            
        # Process Query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # 1. Parse Query (pass history for context)
                intent = system['parser'].parse_query(query, history=st.session_state.messages[:-1])
                
                if debug_mode:
                    st.json(intent)
                
                # 2. Execute Analysis
                metrics = {}
                if intent['intent'] == 'pipeline_analysis':
                    metrics = system['bi'].analyze_pipeline(data['deals'], intent.get('filters'))
                elif intent['intent'] == 'revenue_analysis':
                    metrics = system['bi'].revenue_analysis(data['orders'], intent.get('filters'))
                elif intent['intent'] == 'risk_assessment':
                    metrics = system['bi'].risk_assessment(data['deals'], data['orders'])
                elif intent['intent'] == 'sector_performance':
                    metrics = system['bi'].sector_performance(data['combined'])
                elif intent['intent'] == 'resource_utilization':
                    metrics = system['bi'].resource_utilization(data['deals'])
                elif intent['intent'] == 'operational_metrics':
                    metrics = system['bi'].operational_metrics(data['deals'])
                
                # 3. Render Result
                render_analysis_result(intent, metrics, system, data, key_prefix="current", user_query=query)
                
                # 4. Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "intent": intent,
                    "metrics": metrics
                })


if __name__ == "__main__":
    main()

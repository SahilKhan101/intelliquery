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


def render_pipeline_dashboard(data: Dict, bi_engine: BIEngine):
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
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("##### Probability Distribution")
        prob_df = pd.DataFrame(list(metrics['deals_by_probability'].items()), columns=['Probability', 'Count'])
        fig = px.pie(prob_df, values='Count', names='Probability', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)


def render_revenue_dashboard(data: Dict, bi_engine: BIEngine):
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
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("##### Monthly Billing Trend")
        trend_df = pd.DataFrame(list(metrics['monthly_trend'].items()), columns=['Month', 'Billed'])
        fig = px.line(trend_df, x='Month', y='Billed', markers=True)
        st.plotly_chart(fig, use_container_width=True)


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
    
    # Query Interface
    query = st.chat_input("Ask a question about your business data...")
    
    # Default View (Dashboard)
    if not query:
        tab1, tab2, tab3 = st.tabs(["Pipeline", "Revenue", "Risks"])
        
        with tab1:
            render_pipeline_dashboard(data, system['bi'])
            
        with tab2:
            render_revenue_dashboard(data, system['bi'])
            
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
    else:
        # Display User Query
        with st.chat_message("user"):
            st.write(query)
            
        # Process Query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # 1. Parse Query
                intent = system['parser'].parse_query(query)
                
                if debug_mode:
                    st.json(intent)
                
                # 2. Handle Clarification
                if intent.get('clarification_needed') and intent.get('clarifying_questions'):
                    st.warning("I need a bit more detail to be precise:")
                    for q in intent['clarifying_questions']:
                        st.write(f"- {q}")
                    
                    # Continue anyway if we have a valid intent, but warn the user
                    st.markdown("---")
                    st.info(f"Showing **{intent['intent'].replace('_', ' ').title()}** based on my best guess:")

                # 3. Execute Analysis based on Intent
                if intent['intent'] == 'pipeline_analysis':
                    metrics = system['bi'].analyze_pipeline(data['deals'], intent.get('filters'))
                    st.write(f"### Pipeline Analysis")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Total Pipeline Value", f"₹{metrics.get('total_pipeline_value', 0):,.0f}")
                    c2.metric("Deal Count", metrics.get('deal_count', 0))
                    
                    st.subheader("Top Deals")
                    st.dataframe(pd.DataFrame(metrics.get('top_deals', [])), use_container_width=True)
                    
                elif intent['intent'] == 'revenue_analysis':
                    metrics = system['bi'].revenue_analysis(data['orders'], intent.get('filters'))
                    st.write(f"### Revenue Analysis")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Total Billed", f"₹{metrics.get('total_billed', 0):,.0f}")
                    c2.metric("Total Collected", f"₹{metrics.get('total_collected', 0):,.0f}")
                    
                    st.subheader("Revenue by Sector")
                    st.bar_chart(metrics.get('revenue_by_sector', {}))
                    
                elif intent['intent'] == 'risk_assessment':
                    risks = system['bi'].risk_assessment(data['deals'], data['orders'])
                    st.write(f"### Risk Assessment")
                    st.write(f"Found {risks['total_risks']} potential risks.")
                    
                    risk_df = pd.DataFrame(risks['risk_list'])
                    if not risk_df.empty:
                        st.dataframe(risk_df, use_container_width=True)
                    else:
                        st.success("No major risks found!")
                    
                else:
                    st.write("I analyzed your data based on your query.")
                    st.info("Showing general dashboard for context:")
                    render_pipeline_dashboard(data, system['bi'])


if __name__ == "__main__":
    main()

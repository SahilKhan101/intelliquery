"""
Business Intelligence Engine for calculating metrics and generating insights
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from src.utils.date_utils import get_quarter, get_month_year

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BIEngine:
    """Core business intelligence logic for analyzing deals and work orders"""
    
    def __init__(self):
        pass
    
    def _filter_dataframe(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        filtered_df = df.copy()
        
        # Sector filter
        if filters.get('sector'):
            sector = filters['sector'].lower()
            if 'sector' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sector'].str.lower().str.contains(sector, na=False)]
        
        # Status filter
        if filters.get('status'):
            status = filters['status'].lower()
            status_col = 'deal_status' if 'deal_status' in filtered_df.columns else 'execution_status'
            if status_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[status_col].str.lower().str.contains(status, na=False)]
        
        # Probability filter (deals only)
        if filters.get('probability') and 'closure_probability' in filtered_df.columns:
            prob = filters['probability'].lower()
            filtered_df = filtered_df[filtered_df['closure_probability'].str.lower() == prob]
        
        # Owner filter
        if filters.get('owner') and 'owner_code' in filtered_df.columns:
            owner = filters['owner'].lower()
            filtered_df = filtered_df[filtered_df['owner_code'].str.lower().str.contains(owner, na=False)]
            
        # Date filter
        date_col = None
        if 'close_date' in filtered_df.columns:
            date_col = 'close_date'
        elif 'po_date' in filtered_df.columns:
            date_col = 'po_date'
            
        if date_col:
            if filters.get('date_range_start'):
                try:
                    start_date = pd.to_datetime(filters['date_range_start'])
                    filtered_df = filtered_df[filtered_df[date_col] >= start_date]
                except: pass
                
            if filters.get('date_range_end'):
                try:
                    end_date = pd.to_datetime(filters['date_range_end'])
                    filtered_df = filtered_df[filtered_df[date_col] <= end_date]
                except: pass
                
        return filtered_df

    def analyze_pipeline(self, deals_df: pd.DataFrame, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze sales pipeline health
        """
        df = self._filter_dataframe(deals_df, filters or {})
        
        if df.empty:
            return {"error": "No data found matching filters", "data_quality": {"total_records": 0}}
        
        # Track data quality
        total_records = len(df)
        null_counts = {}
        warnings = []
        
        # Count nulls in critical fields
        critical_fields = ['deal_value', 'closure_probability', 'deal_stage', 'close_date']
        for field in critical_fields:
            if field in df.columns:
                null_count = df[field].isna().sum()
                if null_count > 0:
                    null_counts[field] = null_count
                    pct = (null_count / total_records) * 100
                    if pct > 10:
                        warnings.append(f"{field}: {pct:.1f}% missing ({null_count} records)")
        
        # Calculate key metrics (pandas automatically excludes NaN)
        total_deals = len(df)
        total_value = df['deal_value'].sum()
        avg_deal_value = df['deal_value'].mean()
        valid_values = df['deal_value'].notna().sum()
        
        # Log warnings
        if warnings:
            logger.warning(f"Data quality issues in pipeline analysis: {'; '.join(warnings)}")
        
        # Breakdown by stage
        stage_breakdown = df['deal_stage'].value_counts().to_dict()
        
        # Breakdown by probability
        prob_breakdown = df['closure_probability'].value_counts().to_dict()
        
        # Monthly trend for deals
        monthly_trend = {}
        if 'close_date' in df.columns:
            # Filter out NaT for trend
            trend_df = df[df['close_date'].notna()].copy()
            if not trend_df.empty:
                trend_df['month_year'] = trend_df['close_date'].apply(get_month_year)
                monthly_trend = trend_df.groupby('month_year').size().to_dict()

        # Weighted pipeline value
        weighted_value = 0
        prob_weights = {'High': 0.8, 'Medium': 0.5, 'Low': 0.2, 'Unknown': 0.1}
        
        for _, row in df.iterrows():
            prob = str(row.get('closure_probability', 'Unknown'))
            weight = prob_weights.get(prob, 0.1)
            val = row.get('deal_value', 0)
            if pd.notna(val):
                weighted_value += val * weight
                
        return {
            "total_deals": total_deals,
            "total_pipeline_value": total_value,
            "average_deal_size": avg_deal_value,
            "weighted_pipeline_value": weighted_value,
            "deals_by_stage": stage_breakdown,
            "deals_by_probability": prob_breakdown,
            "monthly_trend": monthly_trend,
            "top_deals": df.nlargest(5, 'deal_value')[['deal_code', 'client_code', 'deal_value', 'closure_probability']].to_dict('records'),
            "data_quality": {
                "total_records": total_records,
                "null_counts": null_counts,
                "warnings": warnings,
                "values_used_in_calculations": valid_values
            }
        }

    def revenue_analysis(self, orders_df: pd.DataFrame, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze revenue trends
        """
        df = self._filter_dataframe(orders_df, filters or {})
        
        if df.empty:
            return {"error": "No data found matching filters", "data_quality": {"total_records": 0}}
        
        # Track data quality
        total_records = len(df)
        null_counts = {}
        warnings = []
        
        # Count nulls in critical fields
        critical_fields = ['billed_value_excl_gst', 'collected_amount', 'po_date']
        for field in critical_fields:
            if field in df.columns:
                null_count = df[field].isna().sum()
                if null_count > 0:
                    null_counts[field] = null_count
                    pct = (null_count / total_records) * 100
                    if pct > 10:
                        warnings.append(f"{field}: {pct:.1f}% missing ({null_count} records)")
        
        if warnings:
            logger.warning(f"Data quality issues in revenue analysis: {'; '.join(warnings)}")
            
        # Key metrics
        total_billed = df['billed_value_excl_gst'].sum()
        total_collected = df['collected_amount'].sum()
        total_receivable = total_billed - total_collected
        collection_rate = (total_collected / total_billed * 100) if total_billed > 0 else 0
        
        valid_billed = df['billed_value_excl_gst'].notna().sum()
        valid_collected = df['collected_amount'].notna().sum()
        
        # Revenue by sector
        sector_revenue = df.groupby('sector')['billed_value_excl_gst'].sum().sort_values(ascending=False).to_dict()
        
        # Monthly trend
        monthly_trend = {}
        date_col = 'po_date' if 'po_date' in df.columns else None
        if date_col:
            trend_df = df[df[date_col].notna()].copy()
            if not trend_df.empty:
                trend_df['month_year'] = trend_df[date_col].apply(get_month_year)
                monthly_trend = trend_df.groupby('month_year')['billed_value_excl_gst'].sum().to_dict()
                
        return {
            "total_billed": total_billed,
            "total_collected": total_collected,
            "total_receivable": total_receivable,
            "collection_rate": collection_rate,
            "revenue_by_sector": sector_revenue,
            "monthly_trend": monthly_trend,
            "data_quality": {
                "total_records": total_records,
                "null_counts": null_counts,
                "warnings": warnings,
                "billed_values_used": valid_billed,
                "collected_values_used": valid_collected
            }
        }

    def risk_assessment(self, deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify at-risk deals and projects
        
        Returns:
            Dictionary of risk indicators
        """
        risks = []
        
        # 1. Stalled Deals (Open deals created > 90 days ago)
        today = datetime.now()
        open_deals = deals_df[deals_df['deal_status'].str.lower() == 'open'].copy()
        
        if 'created_date' in open_deals.columns:
            open_deals['days_open'] = open_deals['created_date'].apply(
                lambda x: (today - x).days if pd.notna(x) else 0
            )
            stalled = open_deals[open_deals['days_open'] > 90]
            
            for _, row in stalled.iterrows():
                risks.append({
                    "type": "Stalled Deal",
                    "id": row['deal_code'],
                    "severity": "Medium",
                    "message": f"Deal open for {row['days_open']} days in stage '{row['deal_stage']}'"
                })
        
        # 2. High Value, Low Probability Deals
        high_value_threshold = deals_df['deal_value'].quantile(0.75)
        risky_deals = deals_df[
            (deals_df['deal_value'] > high_value_threshold) & 
            (deals_df['closure_probability'] == 'Low')
        ]
        
        for _, row in risky_deals.iterrows():
            risks.append({
                "type": "High Value Risk",
                "id": row['deal_code'],
                "severity": "High",
                "message": f"High value deal ({row['deal_value']:,.0f}) with Low probability"
            })
            
        # 3. Collection Risks (Billed but not collected)
        if not orders_df.empty:
            unpaid = orders_df[
                (orders_df['billed_value_excl_gst'] > 0) & 
                (orders_df['collected_amount'] == 0)
            ]
            
            for _, row in unpaid.iterrows():
                risks.append({
                    "type": "Collection Risk",
                    "id": row['deal_code'],
                    "severity": "High",
                    "message": f"Billed {row['billed_value_excl_gst']:,.0f} but 0 collected"
                })
        
        return {
            "total_risks": len(risks),
            "risk_list": risks,
            "risk_summary": {
                "high": len([r for r in risks if r['severity'] == 'High']),
                "medium": len([r for r in risks if r['severity'] == 'Medium']),
                "low": len([r for r in risks if r['severity'] == 'Low'])
            }
        }

    def sector_performance(self, combined_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze performance by sector
        
        Args:
            combined_df: Joined deals and orders DataFrame
            
        Returns:
            Sector performance metrics
        """
        if combined_df.empty:
            return {}
            
        # Group by sector (using deal sector as primary)
        sector_col = 'sector_deal' if 'sector_deal' in combined_df.columns else 'sector'
        
        metrics = combined_df.groupby(sector_col).agg({
            'deal_value': 'sum',
            'deal_code': 'count',
            'billed_value_excl_gst': 'sum',
            'collected_amount': 'sum'
        }).reset_index()
        
        metrics.columns = ['sector', 'pipeline_value', 'deal_count', 'billed_revenue', 'collected_revenue']
        
        # Calculate conversion/efficiency metrics
        metrics['avg_deal_size'] = metrics['pipeline_value'] / metrics['deal_count']
        
        return metrics.to_dict('records')

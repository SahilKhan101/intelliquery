"""
Data cleaning and normalization module for handling messy business data
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import json
from src.utils.date_utils import parse_date_flexible, format_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and normalize messy business data from monday.com"""
    
    def __init__(self):
        self.data_quality_issues = []
    
    def _extract_column_value(self, column_values: List[Dict], column_id: str) -> Any:
        """
        Extract value from monday.com column_values array
        
        Args:
            column_values: List of column value objects from monday.com
            column_id: Column ID to extract
            
        Returns:
            Column value (text or parsed JSON value)
        """
        for col in column_values:
            if col.get('id') == column_id:
                text = col.get('text', '')
                value = col.get('value')
                
                # Try to parse JSON value if available
                if value:
                    try:
                        parsed = json.loads(value)
                        # For date columns, extract the 'date' field
                        if isinstance(parsed, dict) and 'date' in parsed:
                            return parsed['date']
                        return parsed
                    except json.JSONDecodeError:
                        pass
                
                return text if text else None
        return None
    
    def normalize_deals(self, raw_items: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert raw monday.com deal items to clean DataFrame
        
        Args:
            raw_items: Raw items from monday.com API
            
        Returns:
            Cleaned pandas DataFrame
        """
        logger.info(f"Normalizing {len(raw_items)} deal records...")
        
        deals = []
        for item in raw_items:
            column_values = item.get('column_values', [])
            
            deal = {
                'item_id': item.get('id'),
                'deal_code': item.get('name'),  # Item name is often the deal code
                'owner_code': self._extract_column_value(column_values, 'person'),
                'client_code': self._extract_column_value(column_values, 'text'),
                'deal_status': self._extract_column_value(column_values, 'status'),
                'close_date': self._extract_column_value(column_values, 'date'),
                'closure_probability': self._extract_column_value(column_values, 'dropdown'),
                'deal_value': self._extract_column_value(column_values, 'numbers'),
                'tentative_close_date': self._extract_column_value(column_values, 'date4'),
                'deal_stage': self._extract_column_value(column_values, 'status5'),
                'product_deal': self._extract_column_value(column_values, 'text7'),
                'sector': self._extract_column_value(column_values, 'text8'),
                'created_date': self._extract_column_value(column_values, 'date9'),
            }
            deals.append(deal)
        
        df = pd.DataFrame(deals)
        
        # Clean and normalize
        df = self._clean_deal_data(df)
        
        logger.info(f"Normalized {len(df)} deals successfully")
        return df
    
    def _clean_deal_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning rules to deal data"""
        
        # Convert dates
        date_columns = ['close_date', 'tentative_close_date', 'created_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(parse_date_flexible)
        
        # Convert deal value to numeric
        if 'deal_value' in df.columns:
            df['deal_value'] = pd.to_numeric(df['deal_value'], errors='coerce')
        
        # Clean text fields
        text_columns = ['owner_code', 'client_code', 'product_deal', 'sector']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and x != '' else None)
        
        # Standardize closure probability
        if 'closure_probability' in df.columns:
            prob_map = {
                'high': 'High',
                'medium': 'Medium',
                'med': 'Medium',
                'low': 'Low',
                '': 'Unknown'
            }
            df['closure_probability'] = df['closure_probability'].apply(
                lambda x: prob_map.get(str(x).lower().strip(), x) if pd.notna(x) else 'Unknown'
            )
        
        # Track data quality issues
        self._track_quality_issues(df, 'Deals')
        
        return df
    
    def normalize_work_orders(self, raw_items: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert raw monday.com work order items to clean DataFrame
        
        Args:
            raw_items: Raw items from monday.com API
            
        Returns:
            Cleaned pandas DataFrame
        """
        logger.info(f"Normalizing {len(raw_items)} work order records...")
        
        orders = []
        for item in raw_items:
            column_values = item.get('column_values', [])
            
            order = {
                'item_id': item.get('id'),
                'deal_code': self._extract_column_value(column_values, 'text'),
                'customer_code': self._extract_column_value(column_values, 'text0'),
                'serial_number': item.get('name'),  # Serial # as item name
                'nature_of_work': self._extract_column_value(column_values, 'dropdown'),
                'execution_status': self._extract_column_value(column_values, 'status'),
                'data_delivery_date': self._extract_column_value(column_values, 'date'),
                'po_date': self._extract_column_value(column_values, 'date4'),
                'document_type': self._extract_column_value(column_values, 'dropdown8'),
                'sector': self._extract_column_value(column_values, 'text6'),
                'type_of_work': self._extract_column_value(column_values, 'text7'),
                'amount_excl_gst': self._extract_column_value(column_values, 'numbers'),
                'amount_incl_gst': self._extract_column_value(column_values, 'numbers9'),
                'billed_value_excl_gst': self._extract_column_value(column_values, 'numbers0'),
                'collected_amount': self._extract_column_value(column_values, 'numbers4'),
                'project_stage': self._extract_column_value(column_values, 'status8'),
            }
            orders.append(order)
        
        df = pd.DataFrame(orders)
        
        # Clean and normalize
        df = self._clean_work_order_data(df)
        
        logger.info(f"Normalized {len(df)} work orders successfully")
        return df
    
    def _clean_work_order_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning rules to work order data"""
        
        # Convert dates
        date_columns = ['data_delivery_date', 'po_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(parse_date_flexible)
        
        # Convert numeric fields
        numeric_columns = ['amount_excl_gst', 'amount_incl_gst', 'billed_value_excl_gst', 'collected_amount']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean text fields
        text_columns = ['deal_code', 'customer_code', 'sector', 'type_of_work']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and x != '' else None)
        
        # Track data quality issues
        self._track_quality_issues(df, 'Work Orders')
        
        return df
    
    def join_deals_and_orders(self, deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Join deals with work orders on deal code
        
        Args:
            deals_df: Cleaned deals DataFrame
            orders_df: Cleaned work orders DataFrame
            
        Returns:
            Combined DataFrame
        """
        logger.info("Joining deals and work orders...")
        
        # Left join to keep all deals
        combined = deals_df.merge(
            orders_df,
            left_on='deal_code',
            right_on='deal_code',
            how='left',
            suffixes=('_deal', '_order')
        )
        
        logger.info(f"Combined dataset has {len(combined)} records")
        return combined
    
    def _track_quality_issues(self, df: pd.DataFrame, dataset_name: str):
        """Track data quality issues for reporting"""
        
        missing_summary = df.isnull().sum()
        total_rows = len(df)
        
        for col, missing_count in missing_summary.items():
            if missing_count > 0:
                pct = (missing_count / total_rows) * 100
                if pct > 5:  # Only track if >5% missing
                    self.data_quality_issues.append({
                        'dataset': dataset_name,
                        'column': col,
                        'missing_count': int(missing_count),
                        'missing_percentage': round(pct, 2)
                    })
    
    def get_quality_report(self) -> str:
        """
        Generate human-readable data quality report
        
        Returns:
            Formatted quality report string
        """
        if not self.data_quality_issues:
            return "✅ Data quality is excellent! No significant issues found."
        
        report = ["⚠️ **Data Quality Issues:**\n"]
        
        for issue in self.data_quality_issues:
            report.append(
                f"- {issue['dataset']} → `{issue['column']}`: "
                f"{issue['missing_percentage']}% missing ({issue['missing_count']} records)"
            )
        
        return "\n".join(report)
    
    def clear_quality_issues(self):
        """Clear tracked quality issues"""
        self.data_quality_issues = []

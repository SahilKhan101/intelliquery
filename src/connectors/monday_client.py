"""
Monday.com API client for fetching board data
"""
import os
import requests
from typing import List, Dict, Any, Optional
import logging
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MondayClient:
    """Handle all monday.com API interactions using GraphQL"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize monday.com client
        
        Args:
            api_key: monday.com API key (defaults to Config.MONDAY_API_KEY)
        """
        self.api_key = api_key or Config.MONDAY_API_KEY
        self.api_url = Config.MONDAY_API_URL
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
            'API-Version': '2024-01'
        }
    
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute GraphQL query against monday.com API
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            
        Returns:
            API response data
            
        Raises:
            Exception: If API request fails
        """
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [err.get('message', str(err)) for err in data['errors']]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
            
            return data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"monday.com API request failed: {e}")
            raise Exception(f"Failed to connect to monday.com: {str(e)}")
    
    def fetch_board_items(self, board_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Fetch all items from a monday.com board
        
        Args:
            board_id: Board ID to fetch from
            limit: Maximum number of items to fetch per page
            
        Returns:
            List of items with their column values
        """
        query = '''
        query ($boardId: [ID!], $limit: Int!) {
            boards(ids: $boardId) {
                items_page(limit: $limit) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                            type
                        }
                    }
                }
            }
        }
        '''
        
        variables = {
            'boardId': [int(board_id)],
            'limit': limit
        }
        
        try:
            logger.info(f"Fetching items from board {board_id}...")
            data = self._execute_query(query, variables)
            
            boards = data.get('boards', [])
            if not boards:
                logger.warning(f"No board found with ID {board_id}")
                return []
            
            items_page = boards[0].get('items_page', {})
            items = items_page.get('items', [])
            
            logger.info(f"Successfully fetched {len(items)} items from board {board_id}")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch board items: {e}")
            raise
    
    def fetch_deals(self) -> List[Dict[str, Any]]:
        """
        Fetch all deals from Deal Funnel board
        
        Returns:
            List of deal items
        """
        board_id = Config.DEAL_BOARD_ID
        if not board_id:
            raise ValueError("DEAL_BOARD_ID not configured in environment")
        
        logger.info("Fetching Deal Funnel data...")
        return self.fetch_board_items(board_id)
    
    def fetch_work_orders(self) -> List[Dict[str, Any]]:
        """
        Fetch all work orders from Work Order Tracker board
        
        Returns:
            List of work order items
        """
        board_id = Config.WORK_ORDER_BOARD_ID
        if not board_id:
            raise ValueError("WORK_ORDER_BOARD_ID not configured in environment")
        
        logger.info("Fetching Work Order Tracker data...")
        return self.fetch_board_items(board_id)
    
    def get_board_columns(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Get column definitions for a board
        
        Args:
            board_id: Board ID
            
        Returns:
            List of column definitions
        """
        query = '''
        query ($boardId: [ID!]) {
            boards(ids: $boardId) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        '''
        
        variables = {'boardId': [int(board_id)]}
        
        try:
            data = self._execute_query(query, variables)
            boards = data.get('boards', [])
            if boards:
                return boards[0].get('columns', [])
            return []
        except Exception as e:
            logger.error(f"Failed to fetch board columns: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to monday.com API
        
        Returns:
            True if connection successful, False otherwise
        """
        query = '''
        query {
            me {
                id
                name
            }
        }
        '''
        
        try:
            data = self._execute_query(query)
            user = data.get('me', {})
            if user:
                logger.info(f"Successfully connected to monday.com as: {user.get('name')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

"""
Query parser using Google Gemini for natural language understanding
"""
import logging
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryParser:
    """Interpret natural language business queries using Gemini SDK directly"""
    
    def __init__(self):
        """Initialize Gemini Client"""
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Use the model we confirmed exists
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini SDK with model: {self.model_name}")
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured format
        """
        prompt = f"""You are a business intelligence assistant parsing natural language queries about deals and work orders.

The user has access to two datasets:
1. **Deals**: Contains sales pipeline data with fields like deal_code, client_code, deal_status, closure_probability, deal_value, sector, deal_stage, owner_code
2. **Work Orders**: Contains project execution data with fields like deal_code, execution_status, amount, billed_value, collected_amount, sector, project_stage

Common sectors: Mining, Powerline, Energy
Common statuses: Open, Closed, Won, Lost
Common probabilities: High, Medium, Low

Parse the following query and extract the required fields into a JSON object.

Query: {user_query}

Required JSON Structure:
{{
    "intent": "primary intent (pipeline_analysis, revenue_analysis, risk_assessment, sector_performance, deal_details, general_query)",
    "filters": {{ "sector": "...", "status": "...", "probability": "...", "date_range_start": "...", "date_range_end": "...", "owner": "..." }},
    "metrics": ["list", "of", "metrics"],
    "aggregation": "sum/count/average/trend/comparison",
    "time_period": "today/this_week/this_month/this_quarter/this_year/last_6_months/custom",
    "clarification_needed": boolean,
    "clarifying_questions": ["question1", "question2"]
}}

Return ONLY valid JSON. Do not include markdown formatting like ```json.
"""
        
        try:
            logger.info(f"Parsing query: {user_query}")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    response_mime_type="application/json"
                )
            )
            
            # Clean response
            content = response.text.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            
            result = json.loads(content)
            logger.info(f"Parsed intent: {result.get('intent')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse query: {e}")
            return {
                'intent': 'general_query',
                'filters': {},
                'metrics': ['count'],
                'aggregation': 'sum',
                'time_period': 'all',
                'clarification_needed': True,
                'clarifying_questions': ["Could you please rephrase your question?"]
            }
    
    def generate_clarifying_questions(self, query: str, context: str = "") -> List[str]:
        """Generate clarifying questions"""
        prompt = f"""The user asked an ambiguous question: "{query}"

{context}

Generate 2-3 clarifying questions to help understand exactly what they want to know.
Return as a JSON array of strings.
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            content = response.text.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            
            questions = json.loads(content)
            return questions if isinstance(questions, list) else [str(questions)]
        except Exception as e:
            logger.error(f"Failed to generate clarifying questions: {e}")
            return ["Could you be more specific?"]

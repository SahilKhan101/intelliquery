"""
Query parser using Google Gemini for natural language understanding
"""
import logging
import json
from datetime import datetime
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
    
    def parse_query(self, user_query: str, history: List[Dict] = None) -> Dict[str, Any]:
        """
        Parse natural language query into structured format with conversation context
        """
        history_text = ""
        if history:
            history_text = "\nRecent Conversation History:\n"
            # Only take last 5 messages to keep prompt concise
            for msg in history[-5:]:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg.get('content', f"Intent: {msg.get('intent', {}).get('intent')}")
                history_text += f"{role}: {content}\n"

        today = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""You are a business intelligence assistant parsing natural language queries about deals and work orders.
Current Date: {today}

The user has access to two datasets:
1. **Deals**: Contains sales pipeline data with fields like deal_code, client_code, deal_status, closure_probability, deal_value, sector, deal_stage, owner_code, close_date, created_date
2. **Work Orders**: Contains project execution data with fields like deal_code, execution_status, amount, billed_value, collected_amount, sector, project_stage, po_date

Common sectors: Mining, Powerline, Energy
Common statuses: Open, Closed, Won, Lost
Common probabilities: High, Medium, Low

{history_text}

Parse the following query and extract the required fields into a JSON object. 
If the query is a follow-up, use the conversation history for context.
If the user specifies a year (e.g., "in 2025"), set date_range_start to "2025-01-01" and date_range_end to "2025-12-31".

**Common Query Patterns:**
- "revenue trend" or "monthly revenue" → revenue_analysis (will show monthly_trend chart)
- "pipeline" or "deals" → pipeline_analysis  
- "risks" or "at risk" → risk_assessment
- "sector performance" or "compare sectors" → sector_performance
- Revenue uses billed_value_excl_gst from Work Orders by default

Query: {user_query}

Required JSON Structure:
{{
    "intent": "primary intent (pipeline_analysis, revenue_analysis, risk_assessment, sector_performance, resource_utilization, operational_metrics, deal_details, general_query)",
    "filters": {{ "sector": "...", "status": "...", "probability": "...", "date_range_start": "YYYY-MM-DD", "date_range_end": "YYYY-MM-DD", "owner": "..." }},
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
    
    def generate_insights(self, query: str, intent: Dict, metrics: Dict) -> str:
        """
        Generate natural language insights from calculated metrics
        """
        # Format metrics into readable text
        metrics_summary = f"""
User Query: {query}
Intent: {intent.get('intent')}

Calculated Metrics:
{str(metrics)[:1000]}  # Truncate to avoid token limits
"""
        
        prompt = f"""You are a business analyst explaining data insights to a founder.

{metrics_summary}

Provide a concise 2-3 sentence natural language summary of these metrics. 
Focus on:
- Key takeaways (what stands out)
- Business implications (what this means)
- Actionable insights (what to do about it)

Write in a conversational, professional tone. Be specific about numbers.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500  # Increased for complete insights
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            # Fallback to simple summary
            if intent.get('intent') == 'pipeline_analysis':
                return f"Found {metrics.get('total_deals', 0)} deals with a total pipeline value of ₹{metrics.get('total_pipeline_value', 0):,.0f}."
            elif intent.get('intent') == 'revenue_analysis':
                return f"Total billed: ₹{metrics.get('total_billed', 0):,.0f}, Total collected: ₹{metrics.get('total_collected', 0):,.0f}."
            else:
                return "Analysis complete. Review the metrics below for details."

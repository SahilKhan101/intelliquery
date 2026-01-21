"""
Query parser using Google Gemini for natural language understanding
"""
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryParser:
    """Interpret natural language business queries using Gemini"""
    
    def __init__(self):
        """Initialize Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Define output schema
        self.response_schemas = [
            ResponseSchema(
                name="intent",
                description="Primary intent: 'pipeline_analysis', 'revenue_analysis', 'risk_assessment', 'sector_performance', 'deal_details', 'general_query'"
            ),
            ResponseSchema(
                name="filters",
                description="Filters as JSON object with keys: sector, status, probability, date_range_start, date_range_end, owner"
            ),
            ResponseSchema(
                name="metrics",
                description="List of metrics to calculate: ['deal_value', 'count', 'conversion_rate', 'revenue', 'billed', 'collected']"
            ),
            ResponseSchema(
                name="aggregation",
                description="Aggregation type: 'sum', 'count', 'average', 'trend', 'comparison'"
            ),
            ResponseSchema(
                name="time_period",
                description="Time period: 'today', 'this_week', 'this_month', 'this_quarter', 'this_year', 'last_6_months', 'custom'"
            ),
            ResponseSchema(
                name="clarification_needed",
                description="True if query is too ambiguous and needs clarification"
            ),
            ResponseSchema(
                name="clarifying_questions",
                description="List of clarifying questions to ask the user if needed"
            )
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured format
        
        Args:
            user_query: Natural language business question
            
        Returns:
            Structured query parameters
            
        Example:
            >>> parser.parse_query("How's our pipeline looking for mining sector this quarter?")
            {
                'intent': 'pipeline_analysis',
                'filters': {'sector': 'mining'},
                'time_period': 'this_quarter',
                'metrics': ['deal_value', 'count'],
                'aggregation': 'sum'
            }
        """
        format_instructions = self.output_parser.get_format_instructions()
        
        prompt = PromptTemplate(
            template="""You are a business intelligence assistant parsing natural language queries about deals and work orders.

The user has access to two datasets:
1. **Deals**: Contains sales pipeline data with fields like deal_code, client_code, deal_status, closure_probability, deal_value, sector, deal_stage, owner_code
2. **Work Orders**: Contains project execution data with fields like deal_code, execution_status, amount, billed_value, collected_amount, sector, project_stage

Common sectors: Mining, Powerline, Energy
Common statuses: Open, Closed, Won, Lost
Common probabilities: High, Medium, Low

Parse the following query and extract:
- Intent (what are they asking for?)
- Filters (which subset of data?)
- Metrics (what to measure?)
- Aggregation (how to summarize?)
- Time period (when?)

Query: {query}

{format_instructions}

Return valid JSON only.
""",
            input_variables=["query"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        try:
            logger.info(f"Parsing query: {user_query}")
            
            # Create chain
            chain = prompt | self.llm | self.output_parser
            
            # Execute
            result = chain.invoke({"query": user_query})
            
            # Parse filters JSON string to dict
            if isinstance(result.get('filters'), str):
                import json
                try:
                    result['filters'] = json.loads(result['filters'])
                except json.JSONDecodeError:
                    result['filters'] = {}
            
            logger.info(f"Parsed intent: {result.get('intent')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse query: {e}")
            # Return default structure
            return {
                'intent': 'general_query',
                'filters': {},
                'metrics': ['count'],
                'aggregation': 'sum',
                'time_period': 'all',
                'clarification_needed': True,
                'clarifying_questions': ["Could you please rephrase your question? I had trouble understanding it."]
            }
    
    def generate_clarifying_questions(self, query: str, context: str = "") -> List[str]:
        """
        Generate clarifying questions for ambiguous queries
        
        Args:
            query: User's query
            context: Additional context
            
        Returns:
            List of clarifying questions
        """
        prompt = f"""The user asked an ambiguous question: "{query}"

{context}

Generate 2-3 clarifying questions to help understand exactly what they want to know.
Focus on:
- Which specific metric or data they want
- Time period
- Specific filters (sector, status, etc.)

Return as a JSON array of question strings.
"""
        
        try:
            response = self.llm.invoke(prompt)
            import json
            questions = json.loads(response.content)
            return questions if isinstance(questions, list) else [str(questions)]
        except Exception as e:
            logger.error(f"Failed to generate clarifying questions: {e}")
            return [
                "Which specific metric would you like to see?",
                "For which time period?",
                "Any specific sector or status filter?"
            ]

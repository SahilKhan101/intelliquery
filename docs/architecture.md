# IntelliQuery Architecture Documentation

## System Overview

IntelliQuery is a conversational Business Intelligence agent that connects to monday.com boards to answer founder-level queries about deals and work orders. The system transforms messy real-world data into actionable insights through natural language processing and intelligent analytics.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│                       (src/main.py)                          │
│  - Chat interface                                            │
│  - Session state management                                  │
│  - Visualization rendering (Plotly charts)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Query Processing Layer                       │
│                 (src/processors/query_parser.py)             │
│  - Intent classification (LLM)                               │
│  - Filter extraction                                         │
│  - Conversation history management                           │
│  - Natural language insight generation                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Analytics Layer                            │
│                  (src/analytics/bi_engine.py)                │
│  - Pipeline analysis                                         │
│  - Revenue analysis                                          │
│  - Risk assessment                                           │
│  - Data quality tracking                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Data Processing Layer                         │
│              (src/processors/data_cleaner.py)                │
│  - Date normalization                                        │
│  - Text standardization                                      │
│  - Duplicate detection                                       │
│  - One-to-many join aggregation                             │
│  - Quality reporting                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Source Layer                           │
│            (src/connectors/monday_client.py)                 │
│  - monday.com GraphQL API integration                        │
│  - Authentication                                            │
│  - Board data fetching                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **MondayClient** (Data Source)
**File:** `src/connectors/monday_client.py`

**Responsibilities:**
- Connect to monday.com via GraphQL API
- Fetch data from Deal Funnel and Work Order Tracker boards
- Handle pagination and rate limiting
- Manage API authentication

**Key Methods:**
```python
fetch_deals() -> List[Dict]         # Get all deals from board
fetch_work_orders() -> List[Dict]   # Get all work orders from board
_fetch_board_items(board_id) -> List[Dict]  # Generic board fetcher
```

**Technology Choice:**
- **GraphQL over REST**: More efficient, single request for all fields
- **Requests library**: Simple, reliable HTTP client

---

### 2. **DataCleaner** (Normalization)
**File:** `src/processors/data_cleaner.py`

**Responsibilities:**
- Extract values from monday.com's nested JSON structure
- Normalize dates, text, and numeric fields
- Detect duplicates and conflicts
- Generate data quality reports

**Key Methods:**
```python
normalize_deals(raw_items) -> pd.DataFrame
normalize_work_orders(raw_items) -> pd.DataFrame
join_deals_and_orders(deals_df, orders_df) -> pd.DataFrame
get_quality_report() -> str
```

**Data Resilience Features:**
- **Duplicate Detection**: Finds duplicate `deal_code` entries
- **One-to-Many Aggregation**: Sums numeric fields when 1 deal has multiple orders
- **Flexible Date Parsing**: Handles DD/MM/YYYY, ISO, timestamps
- **Null Handling**: Tracks and reports missing data without discarding rows

---

### 3. **QueryParser** (NLU)
**File:** `src/processors/query_parser.py`

**Responsibilities:**
- Convert natural language to structured intent
- Extract filters (sector, status, date ranges)
- Generate clarifying questions
- Produce narrative insights from metrics

**Key Methods:**
```python
parse_query(query, history) -> Dict[intent, filters, metrics]
generate_insights(query, intent, metrics) -> str
```

**Technology Choice: Google Gemini (Native SDK)**

**Why not LangChain?**
- **Problem**: `langchain-google-genai` had API version conflicts (404 errors with `v1beta`)
- **Solution**: Direct `google.generativeai` SDK for reliability
- **Trade-off**: Manual JSON parsing vs. LangChain abstractions

**Intent Classification Schema:**
```json
{
  "intent": "pipeline_analysis | revenue_analysis | risk_assessment",
  "filters": {
    "sector": "Mining",
    "status": "Open",
    "date_range_start": "2025-01-01",
    "date_range_end": "2025-12-31"
  },
  "metrics": ["deal_value", "count"],
  "time_period": "this_quarter",
  "clarification_needed": false
}
```

---

### 4. **BIEngine** (Analytics)
**File:** `src/analytics/bi_engine.py`

**Responsibilities:**
- Calculate business metrics
- Apply filters to data
- Track data quality issues
- Generate insights

**Key Methods:**
```python
analyze_pipeline(deals_df, filters) -> Dict[metrics]
revenue_analysis(orders_df, filters) -> Dict[metrics]
risk_assessment(deals_df, orders_df) -> Dict[risks]
```

**Metrics Provided:**

**Pipeline Analysis:**
- Total deals, pipeline value, weighted value (by probability)
- Breakdown by stage, probability
- Monthly trend (based on `close_date`)
- Top 5 deals by value

**Revenue Analysis:**
- Total billed, collected, receivable
- Collection rate
- Revenue by sector
- Monthly billing trend

**Risk Assessment:**
- Stalled deals (open > 90 days)
- High-value + low-probability deals
- Uncollected invoices

**Data Quality Tracking:**
- Counts nulls in critical fields
- Logs warnings if >10% missing
- Returns transparency metrics (e.g., "165 values used, 181 excluded")

---

### 5. **Streamlit UI** (Presentation)
**File:** `src/main.py`

**Responsibilities:**
- Chat interface with history
- Render metrics and charts
- Display data quality warnings
- Manage session state

**Features:**
- **Persistent Chat**: Uses `st.session_state.messages`
- **Contextual Memory**: Passes last 5 messages to LLM
- **Unique Chart Keys**: Prevents duplicate element ID errors
- **Dynamic Dashboards**: Pipeline, Revenue, Risks tabs

---

## Data Flow

### Example Query: "Show me revenue for mining sector"

```
1. User Input
   └─> query = "Show me revenue for mining sector"

2. Query Parser (Gemini LLM)
   └─> intent = {
         "intent": "revenue_analysis",
         "filters": {"sector": "Mining"},
         "metrics": ["billed", "collected"]
       }

3. Data Layer
   └─> MondayClient.fetch_work_orders()
       └─> DataCleaner.normalize_work_orders()
           └─> orders_df (176 rows, cleaned)

4. Analytics Layer
   └─> BIEngine.revenue_analysis(orders_df, filters={"sector": "Mining"})
       └─> Filters to 45 rows with sector="Mining"
       └─> Calculates:
           - total_billed = ₹2,500,000
           - total_collected = ₹1,800,000
           - collection_rate = 72%

5. Insight Generation (Gemini LLM)
   └─> "Mining sector shows ₹2.5M billed with 72% collection rate. 
        This is strong performance, but ₹700K is still outstanding."

6. UI Rendering
   └─> Display:
       - Natural language insight
       - Metrics (billed, collected)
       - Chart (revenue breakdown)
       - Data quality warnings (if any)
```

---

## Technology Stack

### Backend
- **Python 3.12**: Core language
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for monday.com API

### LLM
- **Google Gemini 2.5 Flash**: Intent classification and insight generation
- **google.generativeai SDK**: Direct API access (not LangChain)

### Frontend
- **Streamlit**: Interactive UI framework
- **Plotly**: Interactive charts

### Data Source
- **monday.com GraphQL API**: Real-time board data

---

## Key Design Decisions

### 1. **Intent-Based vs. Text-to-SQL**

**Decision:** Intent-based classification with deterministic analytics

**Why:**
- ✅ **Safer**: No risk of SQL injection or bad queries
- ✅ **Deterministic**: Business logic in code, not prompts
- ✅ **Flexible**: Handles complex metrics (weighted pipeline value)
- ✅ **Faster**: Single LLM call for classification, then Python execution

**When Text-to-SQL would be better:**
- Large datasets (>1M rows) where Pandas is too slow
- Ad-hoc queries that aren't predefined
- SQL database already exists

---

### 2. **Pandas vs. SQL Database**

**Decision:** In-memory Pandas DataFrames

**Why:**
- ✅ **Small dataset**: 346 deals + 176 orders = manageable in RAM
- ✅ **Prototyping**: No DB setup, faster iteration
- ✅ **Flexibility**: Easy to add new metrics without schema changes
- ✅ **Simplicity**: No ETL pipeline needed

**When to migrate to SQL:**
- Dataset grows beyond 100K rows
- Need concurrent writes
- Multiple users with different permissions

---

### 3. **Native SDK vs. LangChain**

**Decision:** Use `google.generativeai` directly

**Why:**
- ✅ **Reliability**: LangChain had API version mismatches
- ✅ **Control**: Direct access to generation config
- ✅ **Transparency**: Easier to debug
- ✅ **Latest models**: Access to `gemini-2.5-flash`

**Trade-offs:**
- ❌ Lost: LangChain prompt templates
- ❌ Lost: Built-in output parsers
- ✅ Gained: Stability and control

---

### 4. **Session State for Chat History**

**Decision:** Store `intent` + `metrics` in session state

**Why:**
- ✅ **Performance**: Avoid re-calculating metrics on every render
- ✅ **Offline replay**: Can show full history without re-querying monday.com
- ✅ **Contextual queries**: Pass history to LLM for follow-ups

**Alternative (rejected):**
- Store only queries, re-run analysis on render
- ❌ Slower, wastes API calls

---

## Limitations & Known Issues

### Current Limitations

1. **No Write Capabilities**
   - Read-only access to monday.com
   - Cannot update statuses or add notes
   - **Marked as bonus feature in assignment**

2. **Limited Forecasting**
   - Shows trends, but no predictive analytics
   - Simple aggregations only (sum, count, average)

3. **Single User**
   - No authentication or multi-tenancy
   - All users see the same data

4. **No Caching**
   - Re-fetches from monday.com every hour (Streamlit cache)
   - Could add Redis for faster refresh

5. **Deprecated SDK Warning**
   - Using `google.generativeai` (will be EOL soon)
   - Should migrate to `google.genai` for production

### Data Quality Issues (from Real Data)

From the assignment CSVs:
- **52% of deals** have null `deal_value`
- **92% of deals** have null `close_date`
- **36% of orders** have null `billed_value_excl_gst`

**How we handle it:**
- Transparently report via data quality warnings
- Use available data for calculations (Pandas skips NaN)
- Provide context (e.g., "Based on 165 deals with valid values")

---

## Scalability Considerations

### Current Performance
- **Data Load**: ~2 seconds (GraphQL fetch + normalization)
- **Query Response**: ~3 seconds (LLM parse + analytics + insight generation)
- **Max Dataset**: ~10K rows (Pandas limit for real-time analysis)

### Scaling Path

**For 10K-100K rows:**
1. Add PostgreSQL database
2. Use SQL for aggregations (Pandas for viz only)
3. Add Redis cache for monday.com data

**For 100K+ rows:**
1. Switch to DuckDB or ClickHouse (OLAP database)
2. Pre-compute common metrics (materialized views)
3. Use async data loading

**For Multiple Users:**
1. Add authentication (Streamlit supports OAuth)
2. User-specific board access
3. Rate limiting per user

---

## Security Considerations

### Current Security

✅ **API Keys in .env**: Not committed to git
✅ **No SQL injection**: No SQL, only Python
✅ **LLM prompt injection**: Intent-based, not executing arbitrary code

### Production Requirements

**Before deploying:**
1. **Environment variables**: Use secrets manager (AWS Secrets, GCP Secret Manager)
2. **Rate limiting**: Prevent API abuse
3. **Input validation**: Sanitize user queries
4. **Audit logging**: Track who asked what
5. **HTTPS only**: For network security

---

## Testing Strategy

### Current Test Coverage

**Manual Testing:**
- Tested various query types (pipeline, revenue, risks)
- Tested edge cases (null data, missing fields)
- Tested follow-up questions (contextual memory)

**Not Implemented:**
- Unit tests
- Integration tests
- Load testing

### Recommended Tests

**Unit Tests (pytest):**
```python
def test_parse_date_flexible():
    assert parse_date_flexible("01/12/2025") == datetime(2025, 12, 1)
    assert pd.isna(parse_date_flexible("invalid"))

def test_duplicate_detection():
    df = pd.DataFrame({'deal_code': ['D1', 'D1', 'D2']})
    cleaner = DataCleaner()
    cleaner._check_duplicates(df, 'Test', 'deal_code')
    assert len(cleaner.data_quality_issues) == 1
```

**Integration Tests:**
```python
def test_end_to_end_query():
    system = init_system()
    intent = system['parser'].parse_query("Show revenue for mining")
    assert intent['intent'] == 'revenue_analysis'
    assert intent['filters']['sector'] == 'Mining'
```

---

## Future Enhancements

### High Priority
1. **Architecture diagram** (Mermaid/Draw.io)
2. **Follow-up suggestions** after each query
3. **Resource utilization** (owner workload analysis)

### Medium Priority
4. **Write capabilities** (update monday.com)
5. **Scheduled reports** (daily email summaries)
6. **Export to PDF/Excel**

### Low Priority
7. **Advanced forecasting** (regression models)
8. **Multi-board support** (query across >2 boards)
9. **Custom dashboards** (user-configurable widgets)

---

## Deployment

### Local Development
```bash
cd intelliquery
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/main.py
```

### Production (Streamlit Cloud)
1. Push to GitHub
2. Connect Streamlit Cloud to repo
3. Add environment variables in Streamlit dashboard
4. Deploy (auto-deploys on git push)

### Alternative: Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "src/main.py"]
```

---

## Conclusion

IntelliQuery is a production-ready MVP that demonstrates:
- ✅ Robust data handling for messy real-world data
- ✅ Intelligent query understanding with LLMs
- ✅ Transparent analytics with quality tracking
- ✅ Conversational UX with natural language insights

The architecture prioritizes **speed of development** while maintaining **production-grade data resilience**. For datasets under 10K rows, this design is optimal. Beyond that, migrate to SQL for scalability.

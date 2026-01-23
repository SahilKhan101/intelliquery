# IntelliQuery: AI-Powered Business Intelligence Agent

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_UI-red.svg)

An intelligent AI agent that answers founder-level business queries by integrating with monday.com boards. Built to handle messy real-world data with robust cleaning, natural language processing, and contextual memory.

## 🎯 Key Features

### Core Capabilities
- **Natural Language Queries**: Ask questions in plain English with conversational follow-ups
- **Contextual Memory**: Remembers previous questions for intelligent follow-ups
- **Multi-Board Analytics**: Joins deals and work orders for cross-board insights
- **AI-Powered Insights**: Natural language summaries explaining what the data means
- **Interactive Dashboard**: Clean Streamlit UI with dynamic visualizations

### Business Intelligence
- ✅ **Pipeline Analysis**: Deal value, probability, stages, trends
- ✅ **Revenue Analytics**: Billing, collections, sector performance  
- ✅ **Risk Assessment**: Stalled deals, uncollected invoices
- ✅ **Sector Performance**: Cross-board comparison (uses joined data)
- ✅ **Resource Utilization**: Owner workload analysis
- ✅ **Operational Metrics**: Conversion rates, deal cycle time

### Data Resilience
- ✅ Handles 52% missing deal values gracefully
- ✅ Detects and reports duplicates
- ✅ Aggregates one-to-many joins (multiple orders per deal)
- ✅ Normalizes inconsistent formats (dates, text, numbers)
- ✅ Transparent quality warnings shown to user

---

## 🏗️ Architecture

```
User Query → Gemini LLM (Intent Classification) → BI Engine (Analytics)
                ↓                                      ↓
         History Context                      Data Quality Tracking
                ↓                                      ↓
    Gemini LLM (Insight Generation) ← monday.com API (GraphQL)
                ↓
         Streamlit UI
```

**See [docs/architecture.md](docs/architecture.md) for detailed system design.**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ 
- monday.com account (free tier works)
- Google Gemini API key ([Get free key](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SahilKhan101/intelliquery.git
   cd intelliquery
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - GOOGLE_API_KEY=your_gemini_key
   # - MONDAY_API_KEY=your_monday_key  
   # - DEALS_BOARD_ID=your_board_id
   # - ORDERS_BOARD_ID=your_board_id
   ```

5. **Import data to monday.com**
   - See [docs/setup_guide.md](docs/setup_guide.md) for step-by-step instructions
   - Import provided CSV files to monday.com
   - Copy board IDs to `.env`

6. **Run the application**
   ```bash
   streamlit run src/main.py
   ```

7. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Enable "Generate AI Insights" in sidebar for natural language explanations
   - Start asking business questions!

---

## 💡 Example Queries

### Pipeline Analysis
- "How's our pipeline looking?"
- "Show me deals in the mining sector"
- "What's the total pipeline value for high-probability deals?"
- "Show monthly closed deals for 2025"

### Revenue Analysis  
- "What's our total revenue this quarter?"
- "Show monthly revenue trend"
- "What's our collection rate?"
- "Revenue for the energy sector"

### Risk & Performance
- "Which deals are at risk?"
- "Show me uncollected invoices"
- "Compare performance across sectors"
- "What's our conversion rate?"

### Follow-up Questions (Contextual)
- User: "Show revenue for mining"
- Bot: *[shows mining revenue]*
- User: "What about energy?" ← **Uses context!**
- Bot: *[shows energy revenue]*

---

## 🛠️ Technology Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **Language** | Python 3.12 | Modern, rich ecosystem |
| **LLM** | Google Gemini 2.5 Flash | Fast, accurate, JSON mode |
| **SDK** | google.generativeai (native) | More reliable than LangChain |
| **Data Source** | monday.com GraphQL API | Flexible, single-request fetching |
| **UI** | Streamlit | Rapid prototyping, interactive |
| **Data Processing** | Pandas | Perfect for <10K rows |
| **Visualization** | Plotly | Interactive charts |

**Why not LangChain?** See [docs/architecture.md](docs/architecture.md#key-design-decisions) for rationale.

---

## 📁 Project Structure

```
intelliquery/
├── src/
│   ├── main.py                  # Streamlit application
│   ├── connectors/
│   │   └── monday_client.py     # monday.com GraphQL integration
│   ├── processors/
│   │   ├── data_cleaner.py      # Normalization & quality tracking
│   │   └── query_parser.py      # LLM-powered intent classification
│   ├── analytics/
│   │   └── bi_engine.py         # Business intelligence logic
│   └── utils/
│       └── date_utils.py        # Flexible date parsing
├── docs/
│   ├── setup_guide.md           # Step-by-step setup instructions
│   └── architecture.md          # System design & rationale
├── config/
│   └── settings.py              # Environment configuration
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 📊 Data Quality Handling

IntelliQuery handles real-world data issues transparently:

### What It Handles
- ✅ **Missing Values**: 52% of deals have null `deal_value` → Still calculates totals from valid data
- ✅ **Inconsistent Dates**: Excel serial dates, ISO strings, DD/MM/YYYY → Normalized via `parse_date_flexible()`
- ✅ **Duplicates**: Detects duplicate `deal_code` entries → Reports in quality section
- ✅ **One-to-Many Joins**: Deals with multiple work orders → Aggregates numeric fields (sums revenue)
- ✅ **Text Normalization**: "High" vs "high" vs "HIGH" → Standardized

### Transparency
- Data quality warnings shown in expandable UI sections
- Severity-based reporting (🔴 High, 🟡 Medium, 🟢 Low)
- Tells users exactly what data was excluded and why

---

## 🧪 Testing

### Quick API Test
```bash
python test_api_key.py
```

### Manual Testing Checklist
1. ✅ Pipeline analysis works
2. ✅ Revenue analysis shows trend charts
3. ✅ Risk assessment identifies stalled deals
4. ✅ Sector performance shows cross-board analytics
5. ✅ Follow-up questions use context
6. ✅ Data quality warnings appear
7. ✅ Charts render without duplicate ID errors

---

## 🔒 Security

- ✅ API keys in `.env` (never committed to git)
- ✅ `.gitignore` configured for sensitive files
- ✅ No hardcoded credentials
- ✅ No SQL injection risk (intent-based, not text-to-SQL)

---

##  Limitations & Known Issues

### Current Limitations
1. **No Write Capabilities**: Read-only access to monday.com (marked as bonus feature)
2. **Single User**: No authentication or multi-tenancy
3. **Small Dataset Optimized**: Best for <10K rows (uses Pandas in-memory)
4. **No Forecasting**: Shows trends but not predictive analytics

### When to Scale
- **>10K rows**: Migrate to PostgreSQL
- **>100K rows**: Use DuckDB or ClickHouse
- **Multiple users**: Add authentication & rate limiting

See [docs/architecture.md](docs/architecture.md#scalability-considerations) for scaling path.

---

## 📖 Documentation

- **[Setup Guide](docs/setup_guide.md)**: Detailed installation and configuration
- **[Architecture Document](docs/architecture.md)**: System design, tech choices, trade-offs

---

## 📝 Assignment Compliance

This project fulfills all requirements:

| Requirement | Status | Implementation |
|------------|--------|----------------|
| monday.com Integration | ✅ Complete | GraphQL API, dynamic boards |
| Data Resilience | ✅ Complete | Nulls, duplicates, normalization, transparency |
| Query Understanding | ✅ Complete | Intent classification, clarifying questions |
| Business Intelligence | ✅ Complete | 6 analysis types, joined board analytics |
| Natural Language Output | ✅ Complete | AI-generated insights (toggle in sidebar) |
| Setup Instructions | ✅ Complete | docs/setup_guide.md |
| Architecture Doc | ✅ Complete | docs/architecture.md |
| Source Code Quality | ✅ Complete | Clean, documented, error-handled |

---

## 🎓 What I Learned

- **LangChain isn't always the answer**: Native SDK gave better reliability
- **Data resilience > perfect data**: Real-world data is always messy
- **Transparency builds trust**: Show users what data is missing
- **Context matters**: Chat history enables intelligent follow-ups

---

## 🤝 Contributing

This is a technical assignment project. Feedback welcome via GitHub issues!

---

## 📧 Contact

**Author**: Sahil Khan  
**GitHub**: [@SahilKhan101](https://github.com/SahilKhan101)  
**Project**: [IntelliQuery](https://github.com/SahilKhan101/intelliquery)

---

Built with ❤️ for data-driven decision making

# IntelliQuery: AI-Powered Business Intelligence Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-green.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)

An intelligent AI agent that answers founder-level business queries by integrating with monday.com boards. Built to handle messy real-world data with robust cleaning and natural language processing.

## 🎯 Features

- **Natural Language Queries**: Ask questions in plain English about your business data
- **Multi-Board Integration**: Seamlessly combines data from Deal Funnel and Work Orders
- **Data Resilience**: Handles missing values, inconsistent formats, and messy data gracefully
- **Business Intelligence**: Provides insights, not just raw numbers
- **Interactive Dashboard**: Clean Streamlit interface with visualizations

## 🏗️ Architecture

```
User Query → Gemini LLM (Query Understanding) → monday.com API 
→ Data Normalization → Business Analytics → Insight Generation → UI
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- monday.com account (free tier works)
- Google Gemini API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
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
   # Edit .env with your API keys and board IDs
   ```

5. **Import data to monday.com**
   - See [Setup Guide](docs/setup_guide.md) for detailed instructions
   - Import `Deal funnel Data (Modified).xlsx`
   - Import `Work_Order_Tracker Data.xlsx`

6. **Run the application**
   ```bash
   streamlit run src/main.py
   ```

7. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Start asking business questions!

## 💡 Example Queries

- "What's our total pipeline value?"
- "Show me high-probability deals in the mining sector"
- "What's our revenue trend over the last 6 months?"
- "Which deals are at risk of not closing?"
- "How much have we billed vs collected this quarter?"
- "What's our average deal size by sector?"

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM | Google Gemini (via LangChain) |
| Integration | monday.com GraphQL API |
| UI | Streamlit |
| Data Processing | Pandas |
| Visualization | Plotly |

## 📁 Project Structure

```
intelliquery/
├── src/
│   ├── main.py                  # Streamlit application
│   ├── connectors/
│   │   └── monday_client.py     # monday.com API integration
│   ├── processors/
│   │   ├── data_cleaner.py      # Data normalization
│   │   └── query_parser.py      # Query understanding
│   ├── analytics/
│   │   └── bi_engine.py         # Business intelligence logic
│   └── utils/
│       └── date_utils.py        # Date conversion helpers
├── tests/
│   └── test_queries.py          # Sample queries for testing
├── docs/
│   └── setup_guide.md           # Detailed setup instructions
├── config/
│   └── settings.py              # Configuration management
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Test with sample queries:
```bash
python tests/test_queries.py
```

## 📊 Data Quality

IntelliQuery handles real-world data issues:
- ✅ Missing values
- ✅ Inconsistent date formats (Excel serial dates)
- ✅ Varying text formats
- ✅ Incomplete records
- ✅ Duplicate detection

All data quality issues are reported transparently to the user.

## 🔒 Security

- API keys stored in `.env` (never committed)
- `.gitignore` configured for sensitive files
- No hardcoded credentials

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a technical assignment project. Feedback and suggestions welcome!

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Built with ❤️ for data-driven decision making

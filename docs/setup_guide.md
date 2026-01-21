# Monday.com Setup Guide

This guide walks you through setting up monday.com boards and importing your data.

## Step 1: Create monday.com Account

1. Go to [monday.com](https://monday.com)
2. Sign up for a free account (no credit card required)
3. Complete the onboarding flow

## Step 2: Create Workspace

1. After logging in, create a new workspace called "IntelliQuery Workspace"
2. This will contain your data boards

## Step 3: Import Deal Funnel Data

1. **Create a new board:**
   - Click "Add" → "Board"
   - Name it: "Deal Funnel"
   - Choose "Blank board" template

2. **Import CSV data:**
   - Click the menu (⋮) on the board
   - Select "Import data" → "Import from Excel/CSV"
   - Upload `Deal funnel Data (Modified).xlsx`
   - Map columns appropriately:
     - Text columns → Text
     - Date columns → Date (monday.com will try to auto-detect)
     - Number columns → Numbers
     - Status columns → Status/Dropdown

3. **Configure column types after import:**
   - Click on column headers to change types if needed
   - For date columns with Excel serial numbers, you may need to convert them
   - For status columns (Deal Status, Deal Stage), ensure they're set to "Status" type

4. **Note the Board ID:**
   - Click board settings (top right)
   - Copy the Board ID (you'll need this for `.env`)

## Step 4: Import Work Order Tracker Data

1. **Create another board:**
   - Click "Add" → "Board"
   - Name it: "Work Order Tracker"
   - Choose "Blank board" template

2. **Import CSV data:**
   - Follow same process as Step 3
   - Upload `Work_Order_Tracker Data.xlsx`
   - Map columns appropriately

3. **Note the Board ID:**
   - Copy the Board ID for your `.env` file

## Step 5: Get API Key

1. Click on your profile picture (top right)
2. Go to "Developers" → "My Access Tokens"
3. Click "Generate" or "Show"
4. **Copy your API token** (keep it secret!)

## Step 6: Configure IntelliQuery

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
MONDAY_API_KEY=your_actual_api_key_here
DEAL_BOARD_ID=1234567890
WORK_ORDER_BOARD_ID=0987654321

GOOGLE_API_KEY=your_google_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## Step 7: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `.env`

## Step 8: Verify Setup

Run the verification script:

```bash
python -c "from config.settings import Config; Config.validate(); print('✅ Configuration valid!')"
```

## Troubleshooting

### Excel Date Issues
If dates appear as numbers (e.g., 46079):
- These are Excel serial dates
- IntelliQuery automatically converts them
- Or manually convert in monday.com: Right-click column → Change column type → Date

### API Connection Issues
- Verify your API key is correct
- Check that board IDs are accurate (numeric IDs, not names)
- Ensure you have read permissions on the boards

### Missing Data
- IntelliQuery handles missing values gracefully
- You'll see data quality warnings in the UI

## Next Steps

Once setup is complete:
1. Run `streamlit run src/main.py`
2. Open http://localhost:8501
3. Start querying your data!

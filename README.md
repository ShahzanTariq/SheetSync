# SheetSync

SheetSync is a lightweight web application that automates the process of importing bank CSV files into Google Sheets. Upload your transaction CSV files and instantly distribute them to your organized Google Sheets with one click.

## Features

- **Multi-Account Support**: Route transactions to Primary, Business, Secondary, or Joint accounts
- **Bank-Agnostic**: Configurable CSV parsing for any bank format
- **Duplicate Detection**: Automatic hash-based duplicate prevention
- **Transaction Preview**: Review transactions before sending to sheets
- **One-Click Processing**: Single button to process and distribute transactions
- **Secure Integration**: Uses Google Sheets API with service account authentication

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Cloud Project with Sheets API enabled
- Google Service Account credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SheetSync
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment Variables**
   
   Create `.env` file in the backend directory:
   ```env
   PRIMARY_SHEETID=your_primary_sheet_id
   BUSINESS_SHEETID=your_business_sheet_id
   SECONDARY_SHEETID=your_secondary_sheet_id
   JOINT_SHEETID=your_joint_sheet_id
   ```
   
   Replace the values with your actual Google Sheet IDs (found in the sheet URLs).

5. **Add Google Service Account Credentials**
   
   Place your `credentials.json` file in the backend directory. This file contains your Google Service Account credentials and is required for API authentication.

6. **Create Master CSV File**
   
   Create an empty `master.csv` file in the backend directory with the following headers:
   ```csv
   Transaction Date,Amount,Description,Category,Card Name,Hash,Completion
   ```
   
   This file serves as the transaction database and must exist before running the application.

7. **Configure Bank Settings**
   
   Edit `backend/config.json` to match your bank's CSV format:
   ```json
   {
     "your_bank": {
       "display_name": "Your Bank Name",
       "date_col": 0,
       "amount_col": 1,
       "description_col": 2,
       "category_col": 3,
       "header": true,
       "skip_rows": 0
     }
   }
   ```

### Running the Application

**Development Mode:**
```bash
cd frontend
npm run dev
```

**Or run separately:**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm start
```

## Configuration

### Bank CSV Configuration

Each bank entry in `config.json` supports:

- `display_name`: Human-readable name shown in the UI
- `date_col`: Column index for transaction date (0-based)
- `amount_col`: Column index for transaction amount
- `description_col`: Column index for transaction description
- `category_col`: Column index for category (optional)
- `header`: Whether CSV has a header row
- `skip_rows`: Number of rows to skip at the beginning

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable the Google Sheets API
3. Create a Service Account and download the JSON credentials
4. Share your Google Sheets with the service account email
5. Copy the Sheet IDs from the URLs to your `.env` file

## Tech Stack

- **Frontend**: React, Mantine UI
- **Backend**: FastAPI (Python)
- **APIs**: Google Sheets API
- **Data Processing**: Pandas

## Project Structure

```
SheetSync/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── transformer.py       # CSV processing logic
│   ├── sheetUtil.py         # Google Sheets integration
│   ├── masterUtil.py        # Master CSV management
│   ├── config.json          # Bank configurations
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   └── components/
│   │       └── masterTable.js # Transaction table
│   └── package.json        # Node dependencies
└── README.md
```
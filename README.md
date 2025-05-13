# GoogleSheetInput

GoogleSheetInput is a lightweight web tool that parses bank CSV files and sends transaction data to pre-linked Google Sheets. Originally built for personal use, it automates the tedious process of copying and pasting transaction data into spreadsheets.

## 🚀 Features

- 📂 **CSV Upload**: Supports CSV files via file picker with bank-specific parsing.
- 🔄 **Google Sheets Integration**: Uses OAuth-authenticated Google Sheets API to input data securely.
- 🔘 **One-Click Syncing**: Each button represents a pre-linked sheet; clicking sends and clears matching transactions.
- 🛠️ **Configurable Parsing**: Users can define CSV structures (date, amount, description, etc.) for different banks in a JSON file.
- ⚙️ **FastAPI Backend**: Handles CSV processing and communication with Google Sheets.

## 🔧 Tech Stack

- **Frontend**: HTML, JavaScript
- **Backend**: Python (FastAPI)
- **APIs**: Google Sheets API (OAuth 2.0)

## 📁 Sample Bank Config

```json
{
  "TD": {
    "display_name": "TD Bank",
    "date_col": 1,
    "amount_col": 4,
    "description_col": 3,
    "category_col": 6,
    "header": true,
    "skip_rows": 0
  }
}

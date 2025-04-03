# sheetUtil.py
import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Optional, Set, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

SHEET_IDS = {
    'Shahzan': os.getenv("SHAHZAN_SHEETID"),
    'Baba': os.getenv("BABA_SHEETID"),
    'Mama': os.getenv("MAMA_SHEETID"),
    'Ishal': os.getenv("ISHAL_SHEETID")
}
MASTER_SHEET_ID = os.getenv("MASTER_SHEETID") # Get Master ID

SERVICE_ACCOUNT_FILE = 'credentials.json'

def authenticate_google_sheets():
    # ... (keep existing authentication function - ensure SCOPES are set) ...
    creds = None
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: Service account key file not found at: {SERVICE_ACCOUNT_FILE}")
        return None
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # Ensure scopes
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        print("Credentials loaded successfully.")
    except Exception as e:
        print(f"ERROR loading credentials: {e}")
        return None
    try:
        service = build('sheets', 'v4', credentials=creds)
        print("Google Sheets API service built successfully.")
        return service
    except Exception as e:
        print(f"ERROR building Google Sheets service: {e}")
        return None


def get_target_sheet_details(sheet_name_key: str) -> Optional[str]:
    return SHEET_IDS.get(sheet_name_key)


def read_column_data(service, spreadsheet_id: str, range_name: str) -> Optional[List[str]]:
    """Reads all values from a single specified column range (e.g., 'Sheet1!F:F')."""
    if not service or not spreadsheet_id: return None
    print(f"Reading column data from range: {range_name} in sheet: {spreadsheet_id}")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = result.get('values', [])
        # Flatten the list of lists [[val1], [val2], []] into [val1, val2, None]
        column_data = [(row[0] if row else None) for row in values]
        print(f"Read {len(column_data)} values from column {range_name}.")
        return column_data
    except HttpError as err:
        print(f"API error reading column {range_name}: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error reading column {range_name}: {e}")
        return None


def append_rows_to_sheet(service, spreadsheet_id: str, sheet_name: str, rows_data: List[List[Any]]) -> bool:
    """Appends multiple rows of data to the specified sheet using batch append."""
    if not service or not spreadsheet_id or not rows_data:
        print("Append Error: Missing service, sheet ID, or data.")
        return False

    print(f"Appending {len(rows_data)} rows to sheet: {sheet_name} in spreadsheet: {spreadsheet_id}")
    try:
        range_to_append = sheet_name # Append relative to the whole sheet table
        body = {
            'values': rows_data
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_to_append,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print(f"Successfully appended {len(rows_data)} rows. Result range: {result.get('updates', {}).get('updatedRange')}")
        return True
    except HttpError as err:
        print(f"API error appending rows to {sheet_name}: {err}")
        return False
    except Exception as e:
        print(f"Unexpected error appending rows to {sheet_name}: {e}")
        return False


def write_row_to_sheet(service, sheet_name_key: str, transactionDate:str, amount:float, description:str, category: Optional[str]):
    # ... (keep existing logic that finds first empty 'A' row and uses UPDATE) ...
    # This function writes to the TARGET sheet (Shahzan, Baba etc), not the Master sheet
    if not service: return False
    sheet_id = get_target_sheet_details(sheet_name_key)
    if not sheet_id: return False

    target_worksheet_name = ""
    row_data_to_write = []
    # --- Define structure based on target key (Keep this logic) ---
    if sheet_name_key == 'Shahzan':
        target_worksheet_name = "Eth"; row_data_to_write = [transactionDate, None, amount, description, category]
    elif sheet_name_key == 'Baba':
        target_worksheet_name = "Sheet1"; row_data_to_write = [transactionDate, -abs(amount), description, None, category]
    elif sheet_name_key == 'Mama':
        return [transactionDate, None, amount, description, category], "Eth!A:A", mama_sheetID
    elif sheet_name_key == 'Ishal':
        return [transactionDate, None, amount, description, category], "Eth!A:A", ishal_sheetID
    else: return False

    print(f"\nAttempting to write to first empty 'A' row in sheet key: '{sheet_name_key}'...")
    try:
        # 1. Read Column A of the TARGET sheet/worksheet
        col_a_range = f"{target_worksheet_name}!A:A"
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=col_a_range).execute()
        col_a_values = result.get('values', [])

        # 2. Find first empty row number (1-based)
        next_row_number = 1
        for i, cell_list in enumerate(col_a_values):
            if not cell_list or not cell_list[0]: next_row_number = i + 1; break
        else: next_row_number = len(col_a_values) + 1

        # 3. Define target range for update
        target_range = f"{target_worksheet_name}!A{next_row_number}"
        body = {'values': [row_data_to_write]}

        print(f"Writing data via UPDATE to range: {target_range}")
        update_result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range=target_range, valueInputOption='USER_ENTERED', body=body
        ).execute()
        print(f"Update successful for range starting at {target_range}")
        return True
    except HttpError as err:
        print(f"API error during update for sheet '{sheet_name_key}': {err}")
        return False
    except Exception as e:
        print(f"Unexpected error during update for sheet '{sheet_name_key}': {e}")
        return False
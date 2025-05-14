import os.path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()
primary_sheetID = os.getenv("PRIMARY_SHEETID")
business_sheetID = os.getenv("BUSINESS_SHEETID")
secondary_sheetID = os.getenv("SECONDARY_SHEETID")
joint_sheetID = os.getenv("JOINT_SHEETID")
SERVICE_ACCOUNT_FILE = 'credentials.json'

def authenticate_google_sheets():
    """Authenticates using the service account file and returns the service object."""
    creds = None
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: Service account key file not found at: {SERVICE_ACCOUNT_FILE}")
        print("Please ensure the path is correct.")
        return None

    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE)
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
    
def append_row_to_sheet(service, sheet_name: str, transactionDate:str, amount:float, description:str, category:str):
    """
    Appends a single row of data to the specified sheet (SHEET_NAME).

    Args:
        service: The authenticated Google Sheets service object.
        data_to_append: A list of values for the new row (e.g., ['Value A', 'Value B', 'Value C']).
    """
    if not service:
        print("ERROR: Google Sheets service is not available.")
        return False
    

    row_data, range, sheetID = get_row(sheet_name, transactionDate, amount, description, category)
    

    if (not transactionDate) and (not amount) and (not description) and (not category):
        print("WARN: A piece of data is missing")
        return False

    try:
        range_to_append = range

        values_to_append = [row_data]
        body = {
            'values': values_to_append
        }

        print(f"\nAttempting to append data to sheet: '{sheet_name}'")
        print(f"Row Data: {row_data}")

        result = service.spreadsheets().values().append(
            spreadsheetId=sheetID,
            range=range_to_append,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        print(f"Append successful for row: {row_data}")
        updated_range = result.get('updates', {}).get('updatedRange')
        if updated_range:
            print(f"Data written to range: {updated_range}")
        return True

    except HttpError as err:
        print(f"\nAn API error occurred during append for row {row_data}:")
        print(f"Status Code: {err.resp.status}")
        error_details = err.content.decode('utf-8')
        print(f"Details: {error_details}")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred during append for row {row_data}: {e}")
        return False
    
def get_row(sheet_name, transactionDate, amount, description, category):
    if sheet_name == 'Primary':
        return [transactionDate, None, amount, description, category], "Eth!A:A", primary_sheetID
    if sheet_name == 'Business':
        return [transactionDate, -abs(amount), description, None, category], "Sheet1!A:A", business_sheetID
    if sheet_name == 'Secondary':
        return [transactionDate, None, amount, description, category], "Eth!A:A", secondary_sheetID
    if sheet_name == 'Joint':
        return [transactionDate, None, amount, description, category], "Eth!A:A", joint_sheetID

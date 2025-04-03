# masterUtil.py
import pandas as pd # Still useful for structuring data read from sheets
from typing import List, Dict, Any, Set, Optional
# Import specific functions needed from sheetUtil
from sheetUtil import read_column_data, append_rows_to_sheet
from pydantic import BaseModel # Keep Pydantic model for consistency
from googleapiclient.errors import HttpError

class ItemDetail(BaseModel): # Keep model definition or import
    hash: str
    transactionDate: str
    amount: float
    description: str
    category: Optional[str] = None

class masterUtil:
    def __init__(self, service):
        if not service:
            raise ValueError("Google Sheets service object is required.")
        self.service = service
        # No need to read CSV here

    def get_master_sheet_data(self, master_sheet_id: str, master_worksheet_name: str = 'Sheet1') -> List[Dict[str, Any]]:
        """Reads data from the master Google Sheet and filters for incomplete."""
        # ... (Keep the implementation from the previous step that reads from Google Sheet) ...
        # Ensure header definition matches your actual Master Sheet columns
        print(f"masterUtil: Getting rows from Master Sheet ID: {master_sheet_id}")
        if not self.service: return {"error": "Google service unavailable."} # Type hint change: return list or dict
        try:
            range_name = f"{master_worksheet_name}!A:Z" # Adjust as needed
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=master_sheet_id, range=range_name).execute()
            values = result.get('values', [])

            if not values or len(values) < 1: return []
            # --- IMPORTANT: Define expected Master Sheet header order ---
            header = ["Transaction Date", "Amount", "Description", "Category", "Card Name", "Hash", "Completion"]
            # Optional: Verify header row matches expected header
            # actual_header = values[0]
            # if actual_header != header: print("Warning: Master sheet header mismatch!")

            data = []
            for row_idx, row in enumerate(values[1:], start=2): # Start from row 2
                 padded_row = row + [None] * (len(header) - len(row))
                 row_dict = dict(zip(header, padded_row))
                 try: # Convert types safely
                     row_dict['Completion'] = int(float(row_dict.get('Completion', 0)))
                     row_dict['Amount'] = float(row_dict.get('Amount')) if row_dict.get('Amount') is not None else None
                 except (ValueError, TypeError) as e:
                      print(f"Warning: Type conversion error in master sheet row {row_idx}: {e} - Data: {row}")
                      # Handle error - maybe skip row or set defaults? Set Completion to 1 to avoid processing?
                      row_dict['Completion'] = 1 # Mark as completed/error to avoid reprocessing
                      row_dict['Amount'] = None

                 # Ensure essential fields exist for display, maybe Hash
                 if row_dict.get('Hash') is not None:
                      data.append(row_dict)
                 else:
                      print(f"Warning: Skipping master sheet row {row_idx} due to missing Hash.")


            rows_filtered = [row for row in data if row.get('Completion', 1) == 0] # Default to 1 (completed) if missing
            print(f"masterUtil: Returning {len(rows_filtered)} incomplete rows.")
            return rows_filtered

        except HttpError as err:
            print(f"API ERROR in get_master_sheet_data: {err}")
            # Return an empty list or raise? Returning empty for now.
            return []
        except Exception as e:
            print(f"ERROR in get_master_sheet_data: {e}")
            return []


    def get_existing_hashes(self, master_sheet_id: str, hash_column_range: str = 'Sheet1!F:F') -> Set[str]:
        """Reads the hash column from the Master Sheet and returns a set."""
        print(f"Getting existing hashes from {hash_column_range} in {master_sheet_id}")
        hash_list = read_column_data(self.service, master_sheet_id, hash_column_range)
        # Filter out None/empty values and convert to string for consistent set comparison
        return set(str(h) for h in hash_list if h)


    def append_rows_to_master(self, master_sheet_id: str, rows_to_append: List[Dict[str, Any]], master_worksheet_name: str = 'Sheet1') -> bool:
        """Appends multiple rows (list of dicts) to the Master Google Sheet."""
        if not rows_to_append:
            print("No rows provided to append to master.")
            return True # Nothing to do, count as success

        # --- Define expected Master Sheet header order AGAIN (must be consistent) ---
        header = ["Transaction Date", "Amount", "Description", "Category", "Card Name", "Hash", "Completion"]

        # Convert list of dicts to list of lists in the correct order
        rows_data_list = []
        for row_dict in rows_to_append:
            row_list = [row_dict.get(col_name) for col_name in header]
            rows_data_list.append(row_list)

        print(f"Appending {len(rows_data_list)} rows to Master Sheet {master_sheet_id}")
        return append_rows_to_sheet(self.service, master_sheet_id, master_worksheet_name, rows_data_list)


    def update_completion_status_in_master(self, master_sheet_id: str, hash_to_update: str, master_worksheet_name: str = 'Sheet1') -> bool:
        """Finds row by hash in Master Sheet and updates Completion column to 1."""
        # ... (Keep the implementation from the previous step that updates Google Sheet) ...
        print(f"Attempting to update completion for hash {hash_to_update} in Master Sheet {master_sheet_id}")
        if not self.service: return False
        try:
            # --- IMPORTANT: Adjust columns based on your Master Sheet ---
            hash_col_range = f"{master_worksheet_name}!F:F"      # Example: Hash in Column F
            completion_col_letter = "G"                         # Example: Completion in Column G

            hash_values = read_column_data(self.service, master_sheet_id, hash_col_range)
            if hash_values is None: # Check if read failed
                 print("Failed to read hash column from master sheet.")
                 return False

            row_number = -1
            # Use enumerate starting from 1 for direct row number
            for i, current_hash in enumerate(hash_values, start=1):
                if current_hash == str(hash_to_update):
                    row_number = i
                    break

            if row_number == -1:
                print(f"ERROR: Hash {hash_to_update} not found in Master Sheet range {hash_col_range}.")
                return False

            target_cell = f"{master_worksheet_name}!{completion_col_letter}{row_number}"
            body = {'values': [[1]]}

            update_result = self.service.spreadsheets().values().update(
                spreadsheetId=master_sheet_id, range=target_cell, valueInputOption='USER_ENTERED', body=body
            ).execute()
            print(f"Successfully updated completion status for hash {hash_to_update} at cell {target_cell}.")
            return True
        # ... (Keep HttpError and Exception handling) ...
        except HttpError as err: print(f"API Error updating completion: {err}"); return False
        except Exception as e: print(f"Error updating completion: {e}"); return False
# transformer.py
import pandas as pd
import csv
import hashlib
from dateutil import parser
import io
import os # For checking file existence
from typing import List, Tuple, Optional


# Global Variable to store hash dictionary (Keep as is)
hash_dict = {}

# precheck_hash_dupe (Keep as is)
def precheck_hash_dupe():
    global hash_dict
    try:
        df = pd.read_csv("master.csv")
        # Ensure Hash column is string for consistent dictionary keys
        if 'Hash' in df.columns:
             df['Hash'] = df['Hash'].astype(str)
             hash_dict.update(df.set_index('Hash').to_dict('index')) # key is the hash string
             print(f"Preloaded {len(hash_dict)} hashes from master.csv")
        else:
             print("Warning: 'Hash' column not found in master.csv during precheck.")
             hash_dict = {}

    except FileNotFoundError:
        print("master.csv not found, starting with empty hash dictionary.")
        hash_dict = {}
    except Exception as e:
        print(f"Error pre-loading hashes: {e}")
        hash_dict = {}


class Transformer:
    # UPDATED constructor to accept config values directly
    def __init__(self, card_name: str, date_col: int, amount_col: int, description_col: int, category_col: Optional[int], header: bool, skip_rows: int):
        self.card_name = card_name # Display name from config
        self.header = header
        self.date_col = date_col # Index from config
        self.amount_col = amount_col # Index from config
        self.description_col = description_col # Index from config
        self.category_col = category_col # Index from config (might be None)
        self.skip_rows = skip_rows # From config

        # Define the columns to *read* from the input CSV based on config
        self.cols_to_read = [self.date_col, self.amount_col, self.description_col]
        if self.category_col is not None:
            self.cols_to_read.append(self.category_col)
        # Ensure indices are unique and sorted if needed by pandas
        self.cols_to_read = sorted(list(set(self.cols_to_read)))

        # Define the structure expected when *writing* to master.csv (based on original code)
        # These seem to be the intended final columns in order
        self.output_date_col_name = self.date_col # Use original index as name? This seems brittle.
        self.output_amount_col_name = self.amount_col
        self.output_desc_col_name = self.description_col
        self.output_cat_col_name = self.category_col if self.category_col is not None else 'Category_Placeholder' # Need a name if category doesn't exist

        # Let's stick *exactly* to original output structure logic:
        # Read specific columns, keep their original index-based names (or header names),
        # then insert 'Card Name', 'Hash', 'Completion'.


    def reformat_csv(self, inputCSV) -> Tuple[bool, List[str]]:
        """
        Processes the CSV and returns a tuple: (success_status, list_of_messages).
        """
        all_messages = [] # Initialize list to collect messages
        success = False # Track overall success

        header_param = 0 if self.header else None

        try:
            df = pd.read_csv(
                inputCSV,
                usecols=self.cols_to_read,
                skiprows=self.skip_rows,
                header=header_param,
                keep_default_na=False,
                encoding='utf-8'
            )
            all_messages.append(f"Successfully read CSV using config for '{self.card_name}'.")

        except Exception as e:
            error_msg = f"Error reading CSV for card '{self.card_name}': {e}"
            all_messages.append(error_msg)
            print(error_msg) # Keep console log for server debugging
            # return False, all_messages # Return immediately on read error
            # Or re-raise if main.py should handle it:
            raise e # Let main.py catch and handle HTTP response

        if df.empty:
            msg = f"No data read from CSV for card '{self.card_name}' (possibly empty or only skipped rows)."
            all_messages.append(msg)
            print(msg)
            return True, all_messages # Considered success, but no data processed

        # --- Column mapping and ordering (keep as before) ---
        actual_col_names = df.columns.tolist()
        map_original_index_to_actual_name = {}
        for i, actual_name in enumerate(actual_col_names):
            original_index = self.cols_to_read[i]
            map_original_index_to_actual_name[original_index] = actual_name

        cols_for_output_df = []
        if self.date_col in map_original_index_to_actual_name:
             cols_for_output_df.append(map_original_index_to_actual_name[self.date_col])
        # ... (add amount_col, description_col logic) ...
        if self.amount_col in map_original_index_to_actual_name:
            cols_for_output_df.append(map_original_index_to_actual_name[self.amount_col])
        if self.description_col in map_original_index_to_actual_name:
            cols_for_output_df.append(map_original_index_to_actual_name[self.description_col])


        category_col_actual_name = None
        if self.category_col is not None and self.category_col in map_original_index_to_actual_name:
            category_col_actual_name = map_original_index_to_actual_name[self.category_col]
            cols_for_output_df.append(category_col_actual_name)
        else:
            df['temp_category_placeholder'] = None
            cols_for_output_df.append('temp_category_placeholder')

        df_ordered = df[cols_for_output_df].copy()

        # --- Insert metadata columns (keep as before) ---
        df_ordered.insert(4, 'Card Name', self.card_name)
        df_ordered.insert(5, 'Hash', pd.NA)
        df_ordered.insert(6, 'Completion', 0)

        if 'temp_category_placeholder' in df_ordered.columns:
             output_category_col_name = category_col_actual_name if category_col_actual_name else 'Category'
             df_ordered = df_ordered.rename(columns={'temp_category_placeholder': output_category_col_name})
             # Make sure the renamed category column exists if we need it later
             if output_category_col_name not in df_ordered.columns:
                  df_ordered[output_category_col_name] = None # Add it back if rename failed somehow


        # --- Hashing and Duplicate Removal ---
        inputCSV.seek(0)
        # Get back the filtered DataFrame and the messages from hashing
        df_final, hash_messages, duplicate_rows = self.append_hash(inputCSV, df_ordered)
        all_messages.extend(hash_messages) # Add messages from append_hash

        if df_final.empty:
            msg = "No new transactions found after duplicate check."
            all_messages.append(msg)
            print(msg)
            return True, all_messages, duplicate_rows # Success, but nothing to append

        # --- Final Formatting (Standardize Date) ---
        date_col_actual_name = map_original_index_to_actual_name.get(self.date_col)
        if date_col_actual_name and date_col_actual_name in df_final.columns:
             try:
                 df_final[date_col_actual_name] = df_final[date_col_actual_name].apply(self.standardize_date)
             except Exception as e:
                 msg = f"Warning: Error standardizing date column '{date_col_actual_name}': {e}"
                 all_messages.append(msg)
                 print(msg)
        else:
             msg = f"Warning: Could not find date column (index {self.date_col}) to standardize."
             all_messages.append(msg)
             print(msg)


        # --- Append to Master CSV ---
        master_file = "master.csv"
        file_exists = os.path.exists(master_file)
        is_empty = file_exists and os.path.getsize(master_file) == 0

        try:
            df_final.to_csv(
                master_file,
                mode='a',
                header=not file_exists or is_empty,
                index=False
            )
            success_msg = f"Appended {len(df_final)} new rows to {master_file}."
            all_messages.append(success_msg)
            print(success_msg)
            success = True

            # Note: Hash dict update was moved inside append_hash in previous steps

        except Exception as e:
            error_msg = f"Error writing to {master_file}: {e}"
            all_messages.append(error_msg)
            print(error_msg)
            success = False # Mark as failed

        return success, all_messages, duplicate_rows


    # Modified append_hash to return messages
    def append_hash(self, inputCSV, df) -> Tuple[pd.DataFrame, List[str], List]:
        """ Returns filtered DataFrame and a list of status messages. """
        global hash_dict
        messages = [] # Collect messages here
        rows_to_drop = []

        lines_to_skip = self.skip_rows
        if self.header:
            lines_to_skip += 1

        file_content = inputCSV.getvalue().decode("utf-8")
        lines = file_content.splitlines()

        processed_line_count = 0
        duplicate_count = 0
        new_hashes_added_to_dict = 0

        current_data_row_index = 0
        for line_index, line in enumerate(lines):
            if line_index < lines_to_skip:
                continue
            if not line.strip():
                 continue

            if current_data_row_index >= len(df):
                 messages.append(f"Warning: More lines in CSV than rows in DataFrame. Stopped processing at line {line_index + 1}.")
                 break

            processed_line_count += 1
            str_bytes = bytes(line, "UTF-8")
            m = hashlib.md5(str_bytes)
            hash_val_hex = m.hexdigest()
            hash_key = str(int(hash_val_hex, base=16))

            if self.check_hashDict(hash_key):
                rows_to_drop.append(df.index[current_data_row_index])
                duplicate_count += 1
            else:
                df.loc[df.index[current_data_row_index], 'Hash'] = hash_key
                # Add to runtime dictionary immediately *if* it's a new hash
                self.append_hashDict(df.loc[df.index[current_data_row_index]])
                # Check if it was actually added (append_hashDict has internal checks)
                if hash_key in hash_dict:
                     new_hashes_added_to_dict +=1


            current_data_row_index += 1
        
        duplicate_rows = []
        if duplicate_count > 0:
            messages.append(f"Checked {processed_line_count} data lines: Found and skipped {duplicate_count} duplicate rows based on existing hashes.")
            df_duplicates = df.loc[rows_to_drop].copy()
            df_duplicates = df_duplicates.iloc[:, :-2] # Gets rid of Hash and Completion column
            duplicate_rows = df_duplicates.to_dict(orient='records')
        else:
            messages.append(f"Checked {processed_line_count} data lines: No duplicates found based on existing hashes.")
        
        # Add summary message about duplicates
        if new_hashes_added_to_dict > 0:
             messages.append(f"Added {new_hashes_added_to_dict} new transaction hashes to the runtime dictionary.")

        # Drop rows marked as duplicates
        df_filtered = df.drop(index=rows_to_drop)

        # Return the filtered df and the collected messages
        return df_filtered.reset_index(drop=True), messages, duplicate_rows

    # Keep standardize_date as is
    def standardize_date(self, date_str):
        try:
            if pd.isna(date_str) or date_str == '': return None
            if not isinstance(date_str, str): date_str = str(date_str)
            parsed_date = parser.parse(date_str)
            return parsed_date.strftime("%A, %B %d, %Y")
        except Exception as e:
             print(f"Error parsing date '{date_str}': {e}. Returning original.")
             return date_str

    # Keep check_hashDict as is
    def check_hashDict(self, new_hash_str):
        global hash_dict
        return str(new_hash_str) in hash_dict

    # Keep append_hashDict as is - it adds the row data to the runtime dict
    # Ensure it uses the correct column names present in the row Series
    def append_hashDict(self, new_data_row_series):
        global hash_dict
        new_hash = new_data_row_series.get('Hash') # Get hash from the row
        if pd.isna(new_hash):
             print("Warning: Trying to add row with NA hash to hash_dict. Skipping.")
             return
        new_hash_str = str(new_hash)

        if new_hash_str in hash_dict:
            # This case should ideally not happen if check_hashDict was called before
            # print(f"append_hashDict: hash {new_hash_str} already present.")
            return

        # Store the row data (excluding Hash itself) in the dictionary
        # The keys in the stored dict will be the column names from the Series
        dataAdd = new_data_row_series.drop('Hash').to_dict()
        hash_dict[new_hash_str] = dataAdd
        # print(f"Added hash {new_hash_str} to runtime hash_dict.")
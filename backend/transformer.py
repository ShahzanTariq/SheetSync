# transformer.py
import pandas as pd
import hashlib
from dateutil import parser
import io
from typing import List, Dict, Any # Type hinting

# --- REMOVE HASH PRECHECK ---
# No global hash_set needed, no precheck_hash_dupe function needed

class Transformer:
    def __init__(self, config: dict):
        self.config = config.get("transformerConfig", {})
        self.card_name = config.get("displayName", "Unknown Card")

        # Extract config values (using 0-based indexing)
        self.date_col_idx = self.config.get("dateColIndex")
        self.amount_col_idx = self.config.get("amountColIndex")
        self.desc_col_idx = self.config.get("descriptionColIndex")
        self.cat_col_idx = self.config.get("categoryColIndex")
        self.skip_rows = self.config.get("headerRowsToSkip", 0)

        self.use_cols_indices = [
            idx for idx in [self.date_col_idx, self.amount_col_idx, self.desc_col_idx, self.cat_col_idx]
            if idx is not None
        ]
        if not self.use_cols_indices:
            raise ValueError(f"No valid column indices found in configuration for {self.card_name}")

    def process_csv(self, input_csv_bytes_io: io.BytesIO) -> List[Dict[str, Any]]:
        """
        Processes CSV data, generates hashes, standardizes format.
        Returns a list of ALL processed rows (including potential duplicates).
        Duplicate checking happens later against the Google Sheet.
        """
        processed_data = []
        try:
            df = pd.read_csv(input_csv_bytes_io,
                             usecols=self.use_cols_indices,
                             skiprows=self.skip_rows,
                             header=None,
                             encoding='utf-8',
                             on_bad_lines='warn')
        except Exception as e:
            print(f"Error reading CSV for {self.card_name}: {e}")
            raise ValueError(f"Could not read CSV file. Error: {e}")

        # --- Generate Hash based on original line ---
        input_csv_bytes_io.seek(0)
        try:
            original_lines = input_csv_bytes_io.read().decode('utf-8').splitlines()
        except Exception as e:
            raise ValueError(f"Could not read original lines for hashing: {e}")

        original_data_lines = original_lines[self.skip_rows:]

        if len(original_data_lines) != len(df):
             print(f"Warning: Mismatch lines ({len(original_data_lines)}) vs DataFrame rows ({len(df)}).")

        # Iterate through the DataFrame rows
        for index, row in df.iterrows():
            standardized_row = {}
            standardized_row['Transaction Date'] = row.get(self.date_col_idx)
            standardized_row['Amount'] = pd.to_numeric(row.get(self.amount_col_idx), errors='coerce')
            standardized_row['Description'] = row.get(self.desc_col_idx)
            standardized_row['Category'] = row.get(self.cat_col_idx) if self.cat_col_idx is not None else None
            standardized_row['Card Name'] = self.card_name

            # Standardize Date
            try:
                 if standardized_row['Transaction Date']:
                      parsed = parser.parse(str(standardized_row['Transaction Date']))
                      standardized_row['Transaction Date'] = parsed.strftime("%Y-%m-%d")
                 else: standardized_row['Transaction Date'] = None
            except Exception as e:
                print(f"Warning: Date parse error '{standardized_row['Transaction Date']}' row {index}. Error: {e}")
                standardized_row['Transaction Date'] = None

            # Generate Hash
            row_hash = None
            if index < len(original_data_lines):
                original_line = original_data_lines[index]
                try:
                    str_bytes = bytes(original_line, "UTF-8")
                    m = hashlib.md5(str_bytes)
                    row_hash = m.hexdigest() # Store as string
                except Exception as e:
                    print(f"Warning: Hash generation error row {index}. Error: {e}")

            standardized_row['Hash'] = row_hash
            standardized_row['Completion'] = 0 # Default completion

            # Add row even if hash failed? Decide policy. Skipping for now if hash fails.
            if row_hash:
                 processed_data.append(standardized_row)
            else:
                 print(f"Skipping row {index} due to missing hash.")


        print(f"Transformer processed {len(processed_data)} rows for {self.card_name}.")
        return processed_data
import pandas as pd

class masterUtil:
    def __init__ (self):
        self.master_df = pd.read_csv('master.csv') 
        self.current_row_index = 0 # Skip 0 index (header)

    def get_current_row(self): 
        if 0 <= self.current_row_index < len(self.master_df): # Check if in range
            return self.master_df.iloc[[self.current_row_index], [0,1,2,3,4]].to_dict('records')[0] # Return as dictionary
        return None  # If its out of bound (will change)

    def move_to_next_row(self):
        if self.current_row_index < len(self.master_df) - 1: # Check if already at last row.
            self.current_row_index += 1
            return self.get_current_row() 
        return None # If its out of bound (will change)

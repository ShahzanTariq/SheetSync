import pandas as pd

class masterUtil:
    def __init__ (self):
        self.master_df = pd.read_csv('master.csv') 
        self.current_row_index = 0

    def get_current_row(self): 
        if 0 <= self.current_row_index < len(self.master_df):
            return self.master_df.iloc[[self.current_row_index], [0,1,2,3,4]].to_dict('records')[0]
        return None

    def move_to_next_row(self):
        if self.current_row_index < len(self.master_df) - 1:
            self.current_row_index += 1
            return self.get_current_row()
        return None
    
    def get_rows(self):
        rows = self.master_df.reset_index()
        rows_filtered = rows[rows['Completion']==0].to_dict(orient='records')
        return rows_filtered
    
    def update_completion(self, hash):
        rowIndex = self.master_df[self.master_df['Hash'] == hash].index
        self.master_df.loc[rowIndex, 'Completion'] = 1
        self.master_df.to_csv('master.csv', index = False)

    def update_ignore(self, hash):
        try:
            rowIndex = self.master_df[self.master_df['Hash'] == hash].index
            self.master_df.loc[rowIndex, 'Completion'] = -1
            self.master_df.to_csv('master.csv', index = False)
            return True
        except Exception as e:
             print(f"Error ignoring transaction (setting completion to -1) for hash {hash}: {e}")
             return False

    def test(self, list):
        print(list)



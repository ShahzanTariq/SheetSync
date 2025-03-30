import pandas as pd
import csv
import hashlib
from dateutil import parser
import io

#Global Variable to store hash dictionary
hash_dict = {}

# This should be run when program compiles
def precheck_hash_dupe():
    global hash_dict
    df = pd.read_csv("master.csv")
    hash_dict.update(df.set_index('Hash').to_dict('index')) # key is the hash and values are the rest of the columns


class Transformer:
    def __init__(self, card_name: str, date_col: int, amount_col: int, description_col: int, category_col: int, header: bool):
        self.card_name = card_name
        self.header = header
        self.date_col = date_col
        self.amount_col = amount_col
        self.description_col = description_col
        self.category_col = category_col
        self.cols = [date_col, amount_col, description_col, category_col]

    def reformat_csv(self, inputCSV):
        df = pd.read_csv(inputCSV, usecols = self.cols, skiprows=1, header=None)
        df = df[[self.date_col, self.amount_col, self.description_col, self.category_col]]
        df.insert(4, 'Card Name', self.card_name)    # Insert at index 4, name it "Card Name"
        df.insert(5, 'Hash', pd.NA)   
        df.insert(6, 'Completion', 0)
        df = self.append_hash(inputCSV, df) # Returns df with hashes and no duplicates
        df[self.date_col] = df[self.date_col].apply(self.standardize_date)
        df.to_csv("master.csv", mode='a', header = False, index = False) #mode = 'a' will append, and header should be false when appending. Index gets rid of df indexes


    # Helper to reformat_csv(). Adds Hashes to each row and removes duplicates based on hash
    def append_hash(self, inputCSV, df):
        i=0
        start_index = 0
        file_content = inputCSV.getvalue().decode("utf-8")
        lines = file_content.splitlines()
        if (self.header):
            start_index = 1
        for line in lines[start_index:]:
            str_bytes = bytes(line, "UTF-8")
            m = hashlib.md5(str_bytes)
            hash = int(m.hexdigest(), base=16) 
            if self.check_hashDict(hash):
                print(line + "is already in master.csv")
                df = df.drop(index = i)
            else:
                df.loc[i, 'Hash'] = hash
                self.append_hashDict(df.loc[i])
            i+=1
        return df
    
    def standardize_date(self, date_str):
        parsed_date = parser.parse(date_str)
        return parsed_date.strftime("%A, %B %d, %Y")


    # Checks if new Hash is in hash dict
    def check_hashDict(self, new_hash):
        global hash_dict
        if str(new_hash) in hash_dict:
            return True
        else:
            return False

    # Adds any successful line's hash to global hash_dict
    def append_hashDict(self, new_data):
        global hash_dict
        new_hash = new_data['Hash']
        if new_hash in hash_dict:
            print("append_hashDict: new hash is already in hash_dict")
            return
        dataAdd = new_data.drop('Hash')
        hash_dict[str(new_hash)]= dataAdd.to_dict()
        print(hash_dict)



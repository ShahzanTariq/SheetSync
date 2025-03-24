import pandas as pd
import csv
import hashlib


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
        df[4] = self.card_name  # Card Name Column
        df[5] = pd.NA   # Hash Column
        self.append_hash(inputFile, df)
        df.to_csv("master.csv", mode='a', header = False, index = False) #mode = 'a' will append, and header should be false when appending. Index gets rid of df indexes

    # Helper to reformat_csv(). Adds Hashes to each row
    def append_hash(self, inputCSV, df):
        i=0
        with open(inputCSV, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            if (self.header):
                next(reader)
            for line in reader:
                line = str(line)
                str_bytes = bytes(line, "UTF-8")
                m = hashlib.md5(str_bytes)
                final = int(m.hexdigest(), base=16) 
                df.loc[i, 5] = final
                i+=1

inputFile = "test.csv"
tdCard = Transformer(card_name="TD", date_col=1, amount_col=4,description_col=3,category_col=6, header=True)
tdCard.reformat_csv(inputFile)
import pandas as pd
import csv
import hashlib



def reformat_csv(inputCSV, outputCSV):
    df = pd.read_csv(inputCSV, usecols= ['Transaction Date', 'Amount', 'Description', 'Category'])
    df = df[['Transaction Date', 'Amount', 'Description', 'Category']]
    df["Card Name"] = "TD"
    df["Hash"] = pd.NA
    append_hash(inputFile, df, True)
    df.to_csv(outputCSV, mode='w', header = True, index = False) # mode and header are the default values, mode = 'a' will append, and header should be false when appending. Index gets rid of df indexes


def append_hash(inputCSV, df, header:bool):
    i=0
    with open(inputCSV, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        if (header): # Skips first line of csv if it has headers
            next(reader)
            i+=1
        for line in reader:
            line = str(line)
            print(line)
            str_bytes = bytes(line, "UTF-8")
            m = hashlib.md5(str_bytes)
            final = int(m.hexdigest(), base=16)  
            df.loc[i, "Hash"] = final
            i+=1

inputFile = "test.csv"
output = "output.csv"
reformat_csv(inputFile, output)
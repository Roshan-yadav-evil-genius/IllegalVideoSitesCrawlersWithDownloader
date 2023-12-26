import pandas as pd 

df = pd.read_json("Embedoutput.json")

df.to_csv("output.csv",index=False)
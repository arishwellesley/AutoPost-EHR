import pandas as pd

# Load Excel
df = pd.read_excel("D:\\AutoPost-EHR\\Data\\users.xlsx")

users = df.to_dict(orient="records")
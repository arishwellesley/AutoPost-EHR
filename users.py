import pandas as pd

# Load Excel
df = pd.read_excel("D:\\AutoPost-EHR\\Data\\users_v2.xlsx")

users = df.to_dict(orient="records")
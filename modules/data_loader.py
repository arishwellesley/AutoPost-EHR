import pandas as pd

patients_df = pd.read_excel("Data/patients_v2.xlsx")
claims_df = pd.read_excel("Data/claims_v2.xlsx")

claims_df["date_of_service"] = pd.to_datetime(claims_df["date_of_service"]).dt.date
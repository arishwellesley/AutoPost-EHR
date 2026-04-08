import pandas as pd
from modules.data_loader import claims_df, payments_df
from model.matching_engine import process_eob

# Load EOB (your test file)
eob_df = pd.read_excel("Data/eob_sample.xlsx")

# Run model
posted, manual, duplicate = process_eob(eob_df, claims_df, payments_df)

# Save results
posted.to_excel("Data/posted_claims.xlsx", index=False)
manual.to_excel("Data/manual_review.xlsx", index=False)
duplicate.to_excel("Data/duplicate_claims.xlsx", index=False)

print("Processing completed")
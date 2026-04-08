import pandas as pd
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# Load data
claims_df = pd.read_excel("Data/claims.xlsx")
payments_df = pd.read_excel("Data/payments.xlsx")
patients_df = pd.read_excel("Data/patients.xlsx")
payers_df = pd.read_excel("Data/payers.xlsx")
providers_df = pd.read_excel("Data/providers.xlsx")

# Merge datasets
df = payments_df.merge(claims_df, on="claim_number", how="left")
df = df.merge(patients_df, on="patient_account_number", how="left")
df = df.merge(payers_df, left_on="primary_payer_code", right_on="payer_code", how="left")
df = df.merge(providers_df, on="provider_id", how="left")

# Output folder
output_folder = "eob_pdfs"
os.makedirs(output_folder, exist_ok=True)

styles = getSampleStyleSheet()

# Group by check number (one EOB per payment/check)
for check_number, group in df.groupby("check_number"):

    payer_name = group["payer_name"].iloc[0]
    payment_date = str(group["paid_date"].iloc[0]).split(" ")[0]

    address = group["mailing_address_line1"].iloc[0]
    phone = group["phone_number"].iloc[0]

    provider_name = group["provider_name"].iloc[0]
    npi = group["npi"].iloc[0] if "npi" in group.columns else ""

    file_path = os.path.join(output_folder, f"EOB_{check_number}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    # Header
    elements.append(Paragraph(f"PAYER: {payer_name}", styles["Normal"]))
    elements.append(Paragraph(f"Check #: {check_number}", styles["Normal"]))
    elements.append(Paragraph(f"Payment Date: {payment_date}", styles["Normal"]))
    elements.append(Paragraph(f"Mailing address: {address}", styles["Normal"]))
    elements.append(Paragraph(f"Phone number: {phone}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Provider
    elements.append(Paragraph(f"NPI: {npi}", styles["Normal"]))
    elements.append(Paragraph(f"Provider Name: {provider_name}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Loop each claim
    for _, row in group.iterrows():

        member_id = row["primary_member_number"]
        invoice = row["patient_account_number"]
        claim = row["claim_number"]

        dos = str(row["date_of_service"]).split(" ")[0] if pd.notnull(row["date_of_service"]) else ""

        billed = float(row["billed_amount"])
        paid = float(row["paid_amount"])
        adjustment = float(row["adjustment"])

        allowed = paid + adjustment

        # Split patient responsibility (realistic simple split)
        remaining = billed - allowed if billed > allowed else 0
        copay = round(remaining * 0.4, 2)
        coinsurance = round(remaining * 0.3, 2)
        deductible = round(remaining * 0.3, 2)

        # Member + invoice + claim
        elements.append(Paragraph(f"Member ID: {member_id}", styles["Normal"]))
        elements.append(Paragraph(f"Invoice#: {invoice}", styles["Normal"]))
        elements.append(Paragraph(f"Claim#: {claim}", styles["Normal"]))
        elements.append(Spacer(1, 8))

        # Table
        table_data = [
            ["DOS", "Billed", "Allowed", "Paid", "Adjustment", "Copay", "Coinsurance", "Deductible"],
            [
                dos,
                f"{billed:.2f}",
                f"{allowed:.2f}",
                f"{paid:.2f}",
                f"{adjustment:.2f}",
                f"{copay:.2f}",
                f"{coinsurance:.2f}",
                f"{deductible:.2f}"
            ]
        ]

        table = Table(table_data)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 8))

        # Remark
        elements.append(Paragraph("CO 45 - Charges exceeds Fees Schedule.", styles["Normal"]))
        elements.append(Spacer(1, 20))

    # Totals
    total_paid = group["paid_amount"].sum()
    total_adj = group["adjustment"].sum()

    elements.append(Paragraph(f"Total Paid: {total_paid:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Total Adjustment: {total_adj:.2f}", styles["Normal"]))

    # Build PDF
    doc.build(elements)

print("EOB PDFs generated successfully")
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# =========================
# LOAD DATA (FIXED PATH)
# =========================
df = pd.read_excel("Data/eob_100_with_claim.xlsx")

# Clean columns
df.columns = df.columns.str.strip().str.lower()

# =========================
# CREATE OUTPUT FOLDER
# =========================
output_folder = "eob_pdfs"
os.makedirs(output_folder, exist_ok=True)

# =========================
# GROUP BY CHECK NUMBER
# =========================
if "check_eft_number" not in df.columns:
    raise Exception("❌ 'check_eft_number' column missing in EOB file")

grouped = df.groupby("check_eft_number")

# =========================
# LOOP EACH CHECK → PDF
# =========================
for check_no, group in grouped:

    file_name = f"{output_folder}/EOB_{check_no}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)

    y = 750

    # ================= HEADER =================
    payer = group["payer_name"].iloc[0] if "payer_name" in group.columns else "Unknown"
    paid_date = str(group["paid_date"].iloc[0]) if "paid_date" in group.columns else ""

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"PAYER: {payer}")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Check #: {check_no}")
    y -= 15

    c.drawString(50, y, f"Payment Date: {paid_date}")
    y -= 30

    # ================= TABLE HEADER =================
    headers = [
        "Claim#", "Patient", "DOS", "CPT",
        "Billed", "Allowed", "Paid", "Adj", "PTR"
    ]

    x_positions = [50, 100, 180, 240, 300, 360, 420, 480, 530]

    c.setFont("Helvetica-Bold", 8)
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], y, header)

    y -= 15

    # ================= TABLE DATA =================
    c.setFont("Helvetica", 8)

    for _, row in group.iterrows():

        # PTR calculation
        ptr = (
            row.get("copay", 0)
            + row.get("coinsurance", 0)
            + row.get("deductible", 0)
        )

        values = [
            str(row.get("claim_number", "")),
            str(row.get("patient_name", "")),
            str(row.get("date_of_service", "")),
            str(row.get("cpt_code", "")),
            f"${row.get('billed_amount', 0):.2f}",
            f"${row.get('allowed_amount', 0):.2f}",
            f"${row.get('paid_amount', 0):.2f}",
            f"${row.get('contractual_adjustment', 0):.2f}",
            f"${ptr:.2f}",
        ]

        for i, val in enumerate(values):
            c.drawString(x_positions[i], y, val)

        y -= 15

        # New page if needed
        if y < 50:
            c.showPage()
            y = 750

    # ================= FOOTER =================
    y -= 20

    total_paid = group["paid_amount"].sum()
    total_adj = group["contractual_adjustment"].sum()

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, f"Total Paid: ${total_paid:.2f}")
    y -= 15
    c.drawString(50, y, f"Total Adjustment: ${total_adj:.2f}")

    c.save()

print("✅ PDFs Generated Successfully!")
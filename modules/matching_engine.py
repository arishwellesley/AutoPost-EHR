import pandas as pd

# =========================
# NORMALIZE FUNCTION
# =========================
def normalize(text):
    return str(text).strip().lower()

# =========================
# CONFIDENCE SCORE
# =========================
def calculate_confidence(eob, claim):
    score = 0

    # Invoice Number (25)
    if normalize(eob['invoice_number']) == normalize(claim['invoice_number']):
        score += 25

    # Member ID (20)
    if normalize(eob['member_id']) == normalize(claim['member_id']):
        score += 20

    # CPT (15)
    if normalize(eob['cpt_code']) == normalize(claim['cpt_code']):
        score += 15

    # DOS (15)
    if str(eob['dos']) == str(claim['date_of_service']):
        score += 15

    # Billed Amount (15) with tolerance
    if abs(float(eob['billed_amount']) - float(claim['billed_amount'])) <= 5:
        score += 15

    # Payer Name (10)
    if normalize(eob['payer_name']) in normalize(claim['primary_payer_name']):
        score += 10

    return score

# =========================
# FIND BEST MATCH
# =========================
def find_best_match(eob_row, claims_df):
    best_score = 0
    best_match = None

    for _, claim_row in claims_df.iterrows():
        score = calculate_confidence(eob_row, claim_row)

        if score > best_score:
            best_score = score
            best_match = claim_row

    return best_match, best_score

# =========================
# DUPLICATE CHECK
# =========================
def check_duplicate(eob_row, payments_df):
    return (
        (payments_df['invoice_number'] == eob_row['invoice_number']) &
        (payments_df['cpt_code'] == eob_row['cpt_code'])
    ).any()

# =========================
# FINAL DECISION
# =========================
def process_eob(eob_df, claims_df, payments_df):

    posted = []
    manual = []
    duplicate = []

    for _, eob_row in eob_df.iterrows():

        match, score = find_best_match(eob_row, claims_df)

        is_duplicate = check_duplicate(eob_row, payments_df)

        eob_row['confidence_score'] = score

        if is_duplicate:
            eob_row['decision'] = "DUPLICATE"
            duplicate.append(eob_row)

        elif score >= 90:
            eob_row['decision'] = "POST"
            posted.append(eob_row)

        else:
            eob_row['decision'] = "MANUAL_REVIEW"
            manual.append(eob_row)

    return (
        pd.DataFrame(posted),
        pd.DataFrame(manual),
        pd.DataFrame(duplicate)
    )
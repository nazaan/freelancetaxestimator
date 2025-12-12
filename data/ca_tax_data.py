# --- Static Tax Data for Canada (2025 Projections) ---

# 1. Federal Income Tax Brackets (Taxable Income)
# (Threshold, Marginal Rate) - Using the effective 14.5% rate for 2025 on the lowest bracket.
FEDERAL_TAX_BRACKETS = [
    (57375, 0.145),  # 14.5% on the first $57,375
    (114750, 0.205), # 20.5% on the next $57,375 (up to $114,750)
    (177882, 0.26),  # 26% on the next $63,132 (up to $177,882)
    (253414, 0.29),  # 29% on the next $75,532 (up to $253,414)
    (float('inf'), 0.33) # 33% on income over $253,414
]

# 2. Provincial Income Tax Brackets (Taxable Income) - Major Provinces
# Key: 'AB' = Alberta, 'BC' = British Columbia, 'ON' = Ontario, 'QC' = Quebec
PROVINCIAL_TAX_BRACKETS = {
    'AB': [ # Alberta (New 8% bracket for 2025)
        (60000, 0.08),
        (151234, 0.10),
        (181481, 0.12),
        (241974, 0.13),
        (362961, 0.14),
        (float('inf'), 0.15)
    ],
    'BC': [ # British Columbia
        (49279, 0.0506),
        (98560, 0.077),
        (113158, 0.105),
        (137407, 0.1229),
        (186306, 0.147),
        (259829, 0.168),
        (float('inf'), 0.205)
    ],
    'ON': [ # Ontario
        (52886, 0.0505),
        (105775, 0.0915),
        (150000, 0.1116),
        (220000, 0.1216),
        (float('inf'), 0.1316)
    ],
    'QC': [ # Quebec (Note: Quebec handles its own QPP, we use CPP/QPP rates for simplicity)
        (53255, 0.14),
        (106495, 0.19),
        (129590, 0.24),
        (float('inf'), 0.2575)
    ]
    # NOTE: You can add more provinces (MB, SK, NB, NS, PE, NL, etc.) using the search results.
}

# 3. Basic Personal Amount (BPA) for Tax Credits (2025)
# This amount reduces Tax Payable (multiplied by the lowest tax rate).
BASIC_PERSONAL_AMOUNT = {
    'FEDERAL': 16129,
    'AB': 22323,
    'BC': 12399,  # This amount varies based on income for BC, simplified here.
    'ON': 12747,
    'QC': 18055
}

# 4. Canada Pension Plan (CPP) for Self-Employed (2025)
CPP_DATA = {
    'EXEMPTION_AMOUNT': 3500.00,  # Basic Exemption Amount (YBE) - Unchanged
    # CPP Tier 1 (Base Contribution)
    'YMPE_CEILING': 71300.00,     # Year's Maximum Pensionable Earnings
    'SELF_EMPLOYED_RATE_BASE': 0.119, # Combined self-employed rate on YMPE band
    # CPP Tier 2 (Additional Contribution - CPP2)
    'YAMPE_CEILING': 81200.00,    # Year's Additional Maximum Pensionable Earnings
    'SELF_EMPLOYED_RATE_CPP2': 0.08   # Combined self-employed rate on YAMPE band
}

# 5. Business Expense Categories (Simplified list from CRA Form T2125)
EXPENSE_CATEGORIES = [
    "Advertising",
    "Meals and Entertainment (50%)",
    "Motor Vehicle Expenses",
    "Office Supplies",
    "Home Office Expenses",
    "Professional Fees",
    "Insurance",
    "Other"
]

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
BASIC_PERSONAL_AMOUNT = {
    'FEDERAL': 16129,
    'AB': 22323,
    'BC': 12399,
    'MB': 16194,
    'NB': 12891,
    'NL': 10839,
    'NS': 9419,
    'NT': 15810,
    'NU': 17788,
    'ON': 12747,
    'PE': 12500,
    'QC': 18055,
    'SK': 18991,
    'YT': 15000 # Simplified
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

# 5. Full Business Expense Categories (Based on CRA T2125, Part 4)
# We use a dictionary to store expense line numbers (for later reference) and display names.
EXPENSE_CATEGORIES = {
    "8521_Advertising": "Advertising",
    "8523_Meals_and_Entertainment": "Meals & Entertainment (50% rule applied in code)",
    "8690_Insurance": "Insurance (Commercial/Business)",
    "8710_Interest_Bank_Charges": "Interest & Bank Charges",
    "8760_Business_Taxes_Licences_Dues": "Business Taxes, Licences, & Dues",
    "8810_Office_Expenses": "Office Expenses (Pens, Paper, etc.)",
    "8860_Professional_Fees": "Professional Fees (Legal, Accounting, Consulting)",
    "8910_Rent": "Rent (Office space, equipment, etc.)",
    "8960_Repairs_Maintenance": "Repairs and Maintenance (Minor/Current)",
    "9060_Salaries_Wages_Benefits": "Salaries, Wages, and Benefits (Hired help)",
    "9180_Property_Taxes": "Property Taxes (Business property only)",
    "9200_Travel_Expenses": "Travel Expenses (Flights, Accommodation, etc.)",
    "9220_Utilities": "Utilities (Excluding Home Office portion)",
    "9224_Fuel_Costs": "Fuel Costs (Except Motor Vehicle)",
    "9275_Delivery_Freight_Express": "Delivery, Freight, and Express",
    "9281_Motor_Vehicle_Expenses": "Motor Vehicle Expenses (Total, use logs for calculation)",
    "9945_Business_Use_of_Home": "Business-Use-of-Home Expenses", # Calculated separately on T2125
    "9270_Other_Expenses": "Other Expenses (Must be itemized)"
}

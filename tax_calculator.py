import math
from data.ca_tax_data import FEDERAL_TAX_BRACKETS, PROVINCIAL_TAX_BRACKETS, BASIC_PERSONAL_AMOUNT, CPP_DATA

def calculate_marginal_tax(taxable_income, brackets, bpa_amount):
    """
    Calculates the total tax payable based on a set of progressive tax brackets
    and the Basic Personal Amount (BPA) tax credit.

    Args:
        taxable_income (float): The income amount subject to tax.
        brackets (list): A list of (threshold, rate) tuples.
        bpa_amount (float): The Basic Personal Amount for the jurisdiction.
    
    Returns:
        float: The total tax calculated.
    """
    total_tax = 0.0
    remaining_income = taxable_income
    
    # Calculate tax credit value from BPA (using the lowest marginal rate)
    # The lowest rate is always the rate of the first bracket in the list
    lowest_rate = brackets[0][1]
    bpa_tax_credit = bpa_amount * lowest_rate
    
    # 1. Calculate Tax Payable using Progressive Brackets
    previous_threshold = 0.0
    
    for threshold, rate in brackets:
        # Determine the width of the current bracket
        bracket_income = min(remaining_income, threshold - previous_threshold)
        
        if bracket_income > 0:
            total_tax += bracket_income * rate
            remaining_income -= bracket_income
        
        previous_threshold = threshold
        
        # Stop calculation if all income has been accounted for
        if remaining_income <= 0:
            break
            
    # 2. Apply the Basic Personal Amount Tax Credit
    # Tax credits reduce the tax bill directly.
    final_tax_payable = max(0, total_tax - bpa_tax_credit)
    
    return round(final_tax_payable, 2)


def calculate_cpp_self_employed(net_income):
    """
    Calculates the two tiers of self-employed CPP contribution (Tier 1 & Tier 2)
    based on 2025 CRA rules. Net income is equivalent to pensionable earnings.
    
    Args:
        net_income (float): Net business income (Gross - Expenses).
        
    Returns:
        float: The total self-employed CPP contribution.
    """
    
    # Constants from CPP_DATA
    EXEMPTION = CPP_DATA['EXEMPTION_AMOUNT']
    YMPE = CPP_DATA['YMPE_CEILING']
    YAMPE = CPP_DATA['YAMPE_CEILING']
    RATE_BASE = CPP_DATA['SELF_EMPLOYED_RATE_BASE']
    RATE_CPP2 = CPP_DATA['SELF_EMPLOYED_RATE_CPP2']
    
    total_cpp = 0.0
    
    # --- Tier 1: Base CPP Contribution (up to YMPE) ---
    contributory_earnings_base = max(0, min(net_income, YMPE) - EXEMPTION)
    total_cpp += contributory_earnings_base * RATE_BASE

    # --- Tier 2: CPP2 Contribution (between YMPE and YAMPE) ---
    if net_income > YMPE:
        # Only income between the ceilings is pensionable for CPP2
        contributory_earnings_cpp2 = min(net_income, YAMPE) - YMPE
        total_cpp += contributory_earnings_cpp2 * RATE_CPP2
        
    return round(total_cpp, 2)


def calculate_tax_breakdown(gross_income, total_expenses, province_code):
    """
    Orchestrates the tax calculation process, including Net Income, CPP, and Total Tax.
    """    
    # FIX: Use new local variables for the rounded values
    # This ensures Python does not confuse the arguments with unassigned local variables.
    income_rounded = round(gross_income, 2)
    expenses_rounded = round(total_deductible_expenses, 2)

    # 1. Calculate Net Business Income (Used as the Taxable Income Base)
    net_income = max(0, income_rounded - expenses_rounded)
    net_income = round(net_income, 2) # Ensure net income is also clean
    
    # ... (Now replace 'gross_income' with 'income_rounded' and 
    # 'total_deductible_expenses' with 'expenses_rounded' throughout the rest of the function)
    # ... 
    
    # 2. Calculate CPP Contribution (mandatory for self-employed)
    cpp_contribution = calculate_cpp_self_employed(net_income)
    
    # ... (rest of the logic remains the same, using net_income, cpp_contribution, etc.)
    
    # 3. Determine the final Taxable Income for Income Tax (after deductions like CPP)
    # The self-employed can deduct 50% of the CPP contribution (employer portion)
    cpp_deduction = cpp_contribution * 0.5
    taxable_income = max(0, net_income - cpp_deduction)
    
    # 4. Calculate Federal Tax
    fed_bpa = BASIC_PERSONAL_AMOUNT['FEDERAL']
    federal_tax = calculate_marginal_tax(taxable_income, FEDERAL_TAX_BRACKETS, fed_bpa)
    
    # 5. Calculate Provincial Tax
    provincial_brackets = PROVINCIAL_TAX_BRACKETS.get(province_code, [])
    if not provincial_brackets:
        raise ValueError("Invalid province code provided.")

    prov_bpa = BASIC_PERSONAL_AMOUNT.get(province_code, 0) # Fallback to 0 if BPA not defined
    provincial_tax = calculate_marginal_tax(taxable_income, provincial_brackets, prov_bpa)
    
    # 6. Summation
    total_income_tax = federal_tax + provincial_tax
    total_estimated_tax_bill = total_income_tax + cpp_contribution
    
    # 7. Final estimated take-home pay
    take_home_pay = net_income - total_estimated_tax_bill
    
    return {
        'net_income': net_income,
        'cpp_contribution': cpp_contribution,
        'cpp_deduction': cpp_deduction,
        'taxable_income': taxable_income,
        'federal_tax': federal_tax,
        'provincial_tax': provincial_tax,
        'total_income_tax': total_income_tax,
        'total_estimated_tax_bill': total_estimated_tax_bill,
        'take_home_pay': take_home_pay
    }

# Example usage (for testing purposes)
# if __name__ == '__main__':
#     # Test Case: Net income below YMPE
#     test_result_on = calculate_tax_breakdown(gross_income=60000, total_expenses=10000, province_code='ON')
#     print("--- Ontario Test Case (Net Income $50k) ---")
#     for k, v in test_result_on.items():
#         print(f"{k}: ${v:,.2f}")

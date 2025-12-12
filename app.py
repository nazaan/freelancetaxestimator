import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_breakdown
from data.ca_tax_data import PROVINCIAL_TAX_BRACKETS, EXPENSE_CATEGORIES

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Freelance CA Tax Estimator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE FOR EXPENSES ---
# Use session_state to store expenses across user interactions
if 'expense_list' not in st.session_state:
    st.session_state.expense_list = []


# --- HELPER FUNCTION ---
def add_expense(amount, category, date, description):
    """Appends a new expense to the session state list, ensuring amounts are rounded."""
    # Ensure Meal & Entertainment is flagged for 50% deduction later
    is_50_percent = "Meals_and_Entertainment" in category
    
    # Calculate and round the deductible amount immediately
    deductible_amount = round(amount * (0.5 if is_50_percent else 1.0), 2)
    
    st.session_state.expense_list.append({
        'Date': date,
        'Category_Code': category,
        'Category_Name': EXPENSE_CATEGORIES.get(category, "Other"),
        'Description': description,
        'Amount': round(amount, 2), # Also round the gross amount
        'Deductible_Amount': deductible_amount
    })

# --- TITLE AND INTRODUCTION ---
st.title("🇨🇦 2025 Freelance Income & Tax Estimator")
st.markdown("Track your income and get a detailed estimate of your Canadian income tax and CPP contributions.")

# --- SIDEBAR (USER INPUT) ---
with st.sidebar:
    st.header("👤 Your Profile & Summary")
    
   # 1. Location Input (Dropdown with all 13 codes)
    province_options = list(PROVINCIAL_TAX_BRACKETS.keys())
    
    # Safely find the index of the default province ('ON')
    default_province_code = 'ON'
    try:
        default_index = province_options.index(default_province_code)
    except ValueError:
        default_index = 0 # Default to the first element (AB) if 'ON' not found

    province_code = st.selectbox(
        "Select Your Province/Territory:",
        options=province_options,
        format_func=lambda x: f"{x} ({PROVINCIAL_TAX_BRACKETS[x][0][1]*100:.2f}% min rate)",
        index=default_index, # Use the safely determined index
        key='province_select'
    )

    # --- 1. SALES TAX SECTION (GST/HST/QST) ---
st.sidebar.markdown("---")
st.sidebar.subheader("Sales Tax (GST/HST)")

# Checkbox for GST/HST registration (small supplier threshold is $30,000)
is_gst_registered = st.sidebar.checkbox(
    "Are you registered for GST/HST/QST?",
    help="You must register if your gross revenue exceeds $30,000 in a single calendar quarter or over the last four consecutive calendar quarters."
)

if is_gst_registered:
    # Get the combined Federal and Provincial Sales Tax Rate
    # Note: This is an *oversimplification* as GST/HST/QST rates vary wildly by province.
    # We will assume a simple combined rate for the sake of the estimator.
    
    # Common Canadian Combined Sales Tax Rates (e.g., HST/GST+PST)
    if province_code in ['ON', 'NB', 'NL', 'NS', 'PE']:
        # HST Provinces (13% or 15%)
        hst_rate = 0.13 if province_code == 'ON' else 0.15 
    elif province_code == 'QC':
        # QST + GST
        hst_rate = 0.14975 # approx 5% GST + 9.975% QST
    else:
        # GST + PST provinces (varies, using a common rate for estimate)
        hst_rate = 0.12 # e.g. 5% GST + 7% PST/RST
    
    # Calculate Sales Tax Payable (Gross Income * Rate)
    # This assumes the user is on the regular method and passes all sales tax through.
    estimated_sales_tax_payable = gross_income * hst_rate
    
    st.session_state.hst_payable = estimated_sales_tax_payable
    st.session_state.hst_rate = hst_rate * 100
    
else:
    # Add a strong warning for the user if they're not registered.
    st.sidebar.warning("🚨 Remember: If your annual sales exceed $30,000, you **must** register for and charge sales tax (GST/HST/QST) on your services.")
    st.session_state.hst_payable = 0
    st.session_state.hst_rate = 0

    
    # 2. Income Input (Gross Income)
    st.subheader("Gross Income")
    gross_income = st.number_input(
        "Total Gross Income Earned (YTD):",
        min_value=0.0,
        value=50000.00,
        step=100.00,
        format="%.2f",
        key='gross_income_input'
    )
    
    st.divider()
    
    # 3. Itemized Expense Input Form (New Feature)
    st.header("➕ Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date")
        expense_category = st.selectbox(
            "Expense Category (CRA T2125 Line):",
            options=list(EXPENSE_CATEGORIES.keys()),
            format_func=lambda x: EXPENSE_CATEGORIES[x],
            key='expense_category_input'
        )
        expense_amount = st.number_input(
            "Amount ($):",
            min_value=0.01,
            step=5.00,
            format="%.2f",
            key='expense_amount_input'
        )
        expense_description = st.text_input("Description (e.g., 'New laptop purchase')", max_chars=100)
        
        submit_button = st.form_submit_button("Add Expense to Tracker")
        
        if submit_button:
            add_expense(expense_amount, expense_category, expense_date, expense_description)
            st.success("Expense Added!")


# --- MAIN PAGE LOGIC ---
st.header("🧾 Expense Tracker and Deduction Summary")
st.markdown("Review your tracked expenses and the calculated deductions below.")

# Calculate total deductible expenses from the stored list
total_deductible_expenses = sum(item['Deductible_Amount'] for item in st.session_state.expense_list)

# Display the expense table
if st.session_state.expense_list:
    df_expenses = pd.DataFrame(st.session_state.expense_list)
    df_expenses['Date'] = df_expenses['Date'].astype(str) # Convert date objects for clean display

    st.dataframe(
        df_expenses[['Date', 'Category_Name', 'Description', 'Amount', 'Deductible_Amount']].sort_values(by='Date', ascending=False),
        column_order=('Date', 'Category_Name', 'Description', 'Amount', 'Deductible_Amount'),
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Gross Amount", format="$%0.2f"
            ),
            "Deductible_Amount": st.column_config.NumberColumn(
                "Deductible Amount", format="$%0.2f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

st.metric("Total Deductible Expenses (YTD)", f"${total_deductible_expenses:,.2f}")
st.divider()


# --- TAX CALCULATION AND OUTPUT ---
if gross_income >= 0 and province_code and total_deductible_expenses >= 0:
    try:
        # Pass the calculated total deductible expenses to the tax function
        results = calculate_tax_breakdown(gross_income, total_deductible_expenses, province_code)


# Display Sales Tax (Point 1)
if st.session_state.hst_payable > 0:
    st.subheader("Sales Tax (GST/HST/QST) Estimate")
    st.markdown(f"**Assumed Rate:** {st.session_state.hst_rate:.2f}%")
    st.metric(
        label="Estimated Sales Tax Payable (Remittance)",
        value=f"**{st.session_state.hst_payable:,.2f}** {CURRENCY}",
        help="This is the estimated total sales tax you must collect from clients and remit to the government (e.g., HST in Ontario). This amount is NOT part of your income or expense deduction."
    )
    st.markdown("---")
        
        st.header("💰 Tax & Contribution Summary")

        col1, col2, col3 = st.columns(3)
        
        # Display key summary metrics
        col1.metric("Net Business Income", f"${results['net_income']:,.2f}")
        col2.metric("Total Estimated Tax Bill (Income Tax + CPP)", f"${results['total_estimated_tax_bill']:,.2f}", delta_color="inverse")
        col3.metric("Estimated Take-Home Pay (After Taxes)", f"${results['take_home_pay']:,.2f}")
        
        st.divider()

        st.subheader("Detailed Breakdown")
        
        # Display the detailed results in a DataFrame
        breakdown_data = {
            'Component': [
                'Gross Income',
                'Total Deductible Expenses',
                'Net Business Income',
                '---',
                'Self-Employed CPP Contribution',
                'Taxable Income (for Income Tax)',
                '---',
                'Federal Income Tax',
                'Provincial Income Tax',
                'Total Income Tax (Federal + Provincial)',
                'Total Estimated Tax Bill (Income Tax + CPP)'
            ],
            'Amount': [
                gross_income,
                total_deductible_expenses,
                results['net_income'],
                None,
                results['cpp_contribution'],
                results['taxable_income'],
                None,
                results['federal_tax'],
                results['provincial_tax'],
                results['total_income_tax'],
                results['total_estimated_tax_bill']
            ]
        }
        
        df = pd.DataFrame(breakdown_data)
        df.iloc[3, 1] = '---' 
        df.iloc[6, 1] = '---' 
        
        def format_currency(val):
            if isinstance(val, (int, float)):
                return f"${val:,.2f}"
            return val

      
        st.dataframe(
            df.style.format({'Amount': format_currency}),
            hide_index=True,
            use_container_width=True,
            height="content" # <-- This ensures the full table height is displayed
        )

    except ValueError as e:
        st.error(f"Calculation Error: {e}")
        st.warning("Please ensure your selected province is configured correctly in the tax data.")

# --- LEGAL DISCLAIMER ---
    st.divider()
    st.info(
    """
    **⚠️ IMPORTANT DISCLAIMER: NOT LEGAL OR PROFESSIONAL TAX ADVICE**
    
    This **Freelance Income & Tax Estimator** is a planning tool based on *estimated* 2025 federal and provincial tax rates, CPP contributions, and public tax data. 
    
    * **Accuracy:** The calculations are estimates only and do not account for every complex tax situation (e.g., specific tax credits, provincial surtaxes, investments, capital gains, etc.). 
    * **Professional Advice:** This tool is **not a substitute for the advice of a qualified, licensed professional**. You must consult with a **Chartered Professional Accountant (CPA)** or other licensed tax professional to ensure 100% accuracy and compliance with the Canada Revenue Agency (CRA) and Revenu Québec.
    * **Use at your own risk.**
    """
)
# --- END OF APP.PY ---
    
# --- END OF APP.PY ---

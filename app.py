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

# Define currency for display purposes
CURRENCY = "CAD" 

# --- INITIALIZE SESSION STATE FOR EXPENSES ---
if 'expense_list' not in st.session_state:
    st.session_state.expense_list = []
if 'hst_payable' not in st.session_state:
    st.session_state.hst_payable = 0.0
if 'hst_rate' not in st.session_state:
    st.session_state.hst_rate = 0.0


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
    
    # 1. Location Input
    province_options = list(PROVINCIAL_TAX_BRACKETS.keys())
    default_province_code = 'ON'
    try:
        default_index = province_options.index(default_province_code)
    except ValueError:
        default_index = 0

    province_code = st.selectbox(
        "Select Your Province/Territory:",
        options=province_options,
        format_func=lambda x: f"{x} ({PROVINCIAL_TAX_BRACKETS[x][0][1]*100:.2f}% min rate)",
        index=default_index,
        key='province_select'
    )
    
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
    
    st.markdown("---")
    st.subheader("Sales Tax (GST/HST)")

    # Checkbox for GST/HST registration (Point 1)
    is_gst_registered = st.checkbox(
        "Are you registered for GST/HST/QST?",
        help="You must register if your gross revenue exceeds $30,000 in a single calendar quarter or over the last four consecutive calendar quarters."
    )

    # --- SALES TAX CALCULATION LOGIC (Moved inside the sidebar to prevent NameError with gross_income) ---
    if is_gst_registered:
        if province_code in ['ON', 'NB', 'NL', 'NS', 'PE']:
            # HST Provinces (13% or 15%)
            hst_rate = 0.13 if province_code == 'ON' else 0.15 
        elif province_code == 'QC':
            # QST + GST
            hst_rate = 0.14975
        else:
            # GST + PST provinces
            hst_rate = 0.12 
        
        estimated_sales_tax_payable = gross_income * hst_rate
        
        st.session_state.hst_payable = estimated_sales_tax_payable
        st.session_state.hst_rate = hst_rate * 100
        
    else:
        st.warning("🚨 Remember: If your annual sales exceed $30,000, you **must** register for and charge sales tax (GST/HST/QST) on your services.")
        st.session_state.hst_payable = 0.0
        st.session_state.hst_rate = 0.0


    st.divider()
    
    # --- 2. EXPENSE IMPORT SECTION (Point 2) ---
    st.subheader("Load/Save Expenses")

    # CSV Import Uploader (New Feature)
    uploaded_file = st.file_uploader(
        "Import Expenses from CSV", 
        type="csv",
        help="Upload a CSV file previously exported from this app to load your expense list."
    )

    if uploaded_file is not None:
        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(uploaded_file)
            
            # Ensure necessary columns exist and fill NaT/NaN
            required_cols = ['Date', 'Category_Code', 'Category_Name', 'Description', 'Amount', 'Deductible_Amount']
            if not all(col in df.columns for col in required_cols):
                st.error("CSV file is missing one or more required columns.")
            else:
                df = df.fillna(0).astype({'Amount': float, 'Deductible_Amount': float})
                
                # Convert the DataFrame to a list of dictionaries matching the session state structure
                st.session_state.expense_list = df.to_dict('records')
                
                st.success(f"Successfully loaded {len(st.session_state.expense_list)} expenses.")
                st.experimental_rerun() # Rerun to refresh the main expense display
                
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")

    st.divider()
    
    # 3. Itemized Expense Input Form
    st.header("➕ Add New Expense")
    # ... (rest of the expense form is here) ...
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
    df_expenses['Date'] = df_expenses['Date'].astype(str)

    st.dataframe(
        df_expenses[['Date', 'Category_Name', 'Description', 'Amount', 'Deductible_Amount']].sort_values(by='Date', ascending=False),
        column_order=('Date', 'Category_Name', 'Description', 'Amount', 'Deductible_Amount'),
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Gross Amount", format=f"{CURRENCY} %0.2f"
            ),
            "Deductible_Amount": st.column_config.NumberColumn(
                "Deductible Amount", format=f"{CURRENCY} %0.2f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

st.metric("Total Deductible Expenses (YTD)", f"${total_deductible_expenses:,.2f}")
st.divider()


# --- TAX CALCULATION AND OUTPUT ---
# Ensure variables like results are initialized before the try block to avoid NameError if an exception occurs.
results = None
CURRENCY = "CAD" # Ensure CURRENCY is defined outside any block that might fail

if gross_income >= 0 and province_code and total_deductible_expenses >= 0:
    try:
        # Pass the calculated total deductible expenses to the tax function
        # NOTE: tax_calculator.py must be updated to return marginal/average tax rates
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
        col2.metric("Total Estimated Tax Bill (Income Tax + CPP)", f"${results['total_remittance']:,.2f}", delta_color="inverse")
        col3.metric("Estimated Take-Home Pay (After Taxes)", f"${results['take_home_pay']:,.2f}")
        
        st.divider()

        # --- Display Tax Rates (Point 3) ---
        st.subheader("Key Tax Rates")
        col_m, col_a = st.columns(2)

        # Marginal Tax Rate
        col_m.metric(
            label="Marginal Tax Rate",
            value=f"{results['marginal_tax_rate']:.2f}%",
            help="The highest combined Federal and Provincial rate your next dollar of income would be taxed at."
        )

        # Average Tax Rate
        col_a.metric(
            label="Average (Effective) Tax Rate",
            value=f"{results['average_tax_rate']:.2f}%",
            help="The actual percentage of your Net Business Income (after expenses) you pay in Income Tax and CPP."
        )
        st.markdown("---")
        
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
                results['total_remittance'] # Using total_remittance here
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
            height="content"
        )

    except Exception as e: # Catching general exception for better debugging
        st.error(f"Calculation Error: {e}")
        st.warning("Please ensure your selected province is configured correctly in the tax data.")
        st.warning("Also, verify the `tax_calculator.py` file is updated to return the new tax rate variables.")


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

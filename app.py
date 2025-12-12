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
    """Appends a new expense to the session state list."""
    # Ensure Meal & Entertainment is flagged for 50% deduction later
    is_50_percent = "Meals_and_Entertainment" in category
    
    st.session_state.expense_list.append({
        'Date': date,
        'Category_Code': category,
        'Category_Name': EXPENSE_CATEGORIES.get(category, "Other"),
        'Description': description,
        'Amount': amount,
        'Deductible_Amount': amount * (0.5 if is_50_percent else 1.0)
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
            use_container_width=True
        )

    except ValueError as e:
        st.error(f"Calculation Error: {e}")
        st.warning("Please ensure your selected province is configured correctly in the tax data.")
    
# --- END OF APP.PY ---

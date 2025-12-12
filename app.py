import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_breakdown
from data.ca_tax_data import EXPENSE_CATEGORIES

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Freelance CA Tax Estimator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TITLE AND INTRODUCTION ---
st.title("🇨🇦 2025 Freelance Income & Tax Estimator")
st.markdown("Use this tool to track your income and get a rough estimate of your Canadian income tax and CPP contributions.")

# --- SIDEBAR (USER INPUT) ---
with st.sidebar:
    st.header("👤 Your Financial Profile")
    
    # 1. Location Input
    province_code = st.selectbox(
        "Select Your Province/Territory (for tax brackets):",
        options=['ON', 'BC', 'AB', 'QC'], # Add more as you populate data/ca_tax_data.py
        index=0,
        key='province_select'
    )
    
    # 2. Financial Inputs
    st.subheader("Gross Income & Expenses")
    gross_income = st.number_input(
        "Total Gross Income Earned (Year-to-Date):",
        min_value=0.0,
        value=50000.00,
        step=100.00,
        format="%.2f",
        key='gross_income_input'
    )
    
    total_expenses = st.number_input(
        "Total Deductible Business Expenses (Year-to-Date):",
        min_value=0.0,
        value=5000.00,
        step=100.00,
        format="%.2f",
        key='total_expenses_input'
    )

# --- MAIN PAGE CALCULATION & OUTPUT ---
# Only run the calculation if the inputs are valid
if gross_income >= 0 and total_expenses >= 0 and province_code:
    try:
        # Call the core calculation function
        results = calculate_tax_breakdown(gross_income, total_expenses, province_code)
        
        st.header("💰 Tax & Contribution Summary")

        col1, col2, col3 = st.columns(3)
        
        # Display key summary metrics
        col1.metric("Net Business Income", f"${results['net_income']:,.2f}")
        col2.metric("Total Estimated Tax Bill (Income Tax + CPP)", f"${results['total_estimated_tax_bill']:,.2f}", delta_color="inverse")
        col3.metric("Estimated Take-Home Pay (After Taxes)", f"${results['take_home_pay']:,.2f}")
        
        st.divider()

        st.subheader("Detailed Breakdown")
        
        # Display the detailed results in a DataFrame for clarity
        breakdown_data = {
            'Component': [
                'Gross Income',
                'Total Expenses',
                'Net Income',
                '---',
                'Self-Employed CPP Contribution',
                'Taxable Income (for Income Tax)',
                '---',
                'Federal Income Tax',
                'Provincial Income Tax',
                'Total Income Tax',
                'Total Estimated Tax Bill'
            ],
            'Amount': [
                gross_income,
                total_expenses,
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
        
        # Format the DataFrame for better display
        df = pd.DataFrame(breakdown_data)
        df.iloc[3, 1] = '---' # Placeholder for divider row
        df.iloc[6, 1] = '---' # Placeholder for divider row
        
        # Use a custom formatting function to display currency nicely
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
        st.error(f"Configuration Error: {e}")
        st.warning("Please ensure your selected province is defined in the tax data.")
    
    # --- EXPENSE TRACKER (MVP Feature) ---
    st.subheader("Expense Tracker (Coming Soon)")
    st.markdown("The next step will be adding a feature to log individual expenses to build up the 'Total Expenses' figure automatically.")
    
# --- END OF APP.PY ---

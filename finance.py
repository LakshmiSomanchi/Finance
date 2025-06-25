import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid # For generating unique IDs for documents
import numpy as np # Added numpy for robust calculations

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="TechnoServe India: Finance & Budget Dashboard",
    page_icon="📊",
    layout="wide", # Changed to wide for more content
    initial_sidebar_state="expanded"
)

# --- Global User ID (for demo purposes) ---
# This is a Phase 1 blueprint. In a production environment,
# real user authentication would determine the user ID.
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'Test Finance' # Set user ID as requested

st.sidebar.info(f"Current User ID: `{st.session_state['user_id']}`")

# --- Data Management Functions (In-Memory Pandas DataFrame) ---
# This is a Phase 1 blueprint. Data will NOT persist across app restarts or new sessions.
# All data (financial and KRA/KPI) is arbitrary for demonstration purposes.

if 'finance_data' not in st.session_state:
    # Initialize DataFrame with dummy financial data
    financial_dummy_data = {
        'id': [str(uuid.uuid4()) for _ in range(30)], # Increased number of entries
        'Program': [
            'Education', 'Education', 'Education', 'Healthcare', 'Healthcare', 'Healthcare',
            'Community Dev', 'Community Dev', 'Community Dev', 'Greenr - RG1', 'Greenr - RG1', 'Greenr - RG2',
            'Greenr - RG2', 'PMU - Dairy Dev', 'PMU - Dairy Dev', 'PMU - Cotton', 'PMU - Coffee', 'PMU - Turmeric',
            'Education', 'Healthcare', 'Community Dev', 'Greenr - RG1', 'PMU - Dairy Dev',
            'PMU - Cotton', 'Education', 'Healthcare', 'Community Dev', 'Greenr - RG2', 'PMU - Coffee', 'PMU - Turmeric'
        ],
        'Category': [
            'Salaries', 'Rent', 'Utilities', 'Salaries', 'Supplies', 'Travel',
            'Marketing', 'Training', 'Operations', 'IT Services', 'Office Supplies', 'Consulting Fees',
            'Travel', 'Raw Materials', 'Processing', 'Seed Costs', 'Logistics', 'Packaging',
            'Salaries', 'Supplies', 'Rent', 'Travel', 'Processing',
            'Harvesting', 'Utilities', 'Training', 'Marketing', 'IT Services', 'Logistics', 'Raw Materials'
        ],
        'Budget': [
            150000, 30000, 15000, 100000, 20000, 25000,
            12000, 8000, 20000, 50000, 7000, 40000,
            18000, 60000, 35000, 22000, 15000, 10000,
            140000, 25000, 28000, 20000, 38000,
            24000, 16000, 9000, 13000, 48000, 17000, 11000
        ],
        'Actual': [
            145000, 32000, 14000, 98000, 22000, 27000,
            11000, 9000, 21000, 52000, 6500, 39000,
            19000, 58000, 37000, 23000, 16000, 9500,
            138000, 26000, 27500, 21000, 39000,
            23500, 15500, 9200, 12500, 47000, 17500, 10500
        ],
        'Status': [
            'Approved', 'Pending Approval', 'Draft', 'Approved', 'Approved', 'Pending Approval',
            'Approved', 'Draft', 'Approved', 'Pending Approval', 'Draft', 'Approved',
            'Rejected', 'Approved', 'Pending Approval', 'Draft', 'Approved', 'Approved',
            'Pending Approval', 'Draft', 'Approved', 'Rejected', 'Pending Approval',
            'Approved', 'Draft', 'Approved', 'Pending Approval', 'Approved', 'Rejected', 'Approved'
        ],
        'LastUpdatedBy': [
            'user123', 'Test Finance', 'user456', 'user123', 'user456', 'Test Finance',
            'user789', 'user123', 'Test Finance', 'user456', 'user789', 'Test Finance',
            'user123', 'user456', 'Test Finance', 'user789', 'user123', 'user456',
            'Test Finance', 'user789', 'user123', 'Test Finance', 'user456',
            'user789', 'user123', 'Test Finance', 'user456', 'user789', 'Test Finance', 'user123'
        ],
        'created_at': [datetime.now().isoformat() for _ in range(30)]
    }
    st.session_state['finance_data'] = pd.DataFrame(financial_dummy_data)

if 'kpi_data' not in st.session_state:
    # Initialize DataFrame with dummy KRA/KPI data
    kpi_dummy_data = {
        'id': [str(uuid.uuid4()) for _ in range(8)],
        'name': [
            'Reduce Operational Costs (Education)', 'Increase Beneficiary Reach (Healthcare)',
            'Improve Community Engagement (Community Dev)', 'Greenr - Achieve Carbon Neutrality (RG1)',
            'PMU - Dairy Yield Improvement', 'PMU - Cotton Quality Index',
            'PMU - Coffee Farmer Income Growth', 'PMU - Turmeric Production Increase'
        ],
        'associated_program': [
            'Education', 'Healthcare', 'Community Dev', 'Greenr - RG1',
            'PMU - Dairy Dev', 'PMU - Cotton', 'PMU - Coffee', 'PMU - Turmeric'
        ],
        'target_value': [100000, 5000, 80, 100, 10000, 0.9, 0.15, 50000], # Arbitrary targets
        'actual_value': [95000, 4800, 75, 90, 9500, 0.85, 0.12, 48000], # Arbitrary actuals
        'unit': ['₹', 'Beneficiaries', '% Participation', '% of Target', 'Litres/Day', 'Index', '% Growth', 'Kg'],
        'status': ['On Track', 'On Track', 'At Risk', 'At Risk', 'On Track', 'At Risk', 'On Track', 'On Track'],
        'last_updated_by': ['user123', 'Test Finance', 'user789', 'Test Finance', 'user456', 'user123', 'Test Finance', 'user789'],
        'created_at': [datetime.now().isoformat() for _ in range(8)]
    }
    st.session_state['kpi_data'] = pd.DataFrame(kpi_dummy_data)


# Function to fetch all budget data (from session state)
def get_budgets():
    return st.session_state['finance_data']

# Function to add/update budget entry (in session state)
def add_or_update_budget(doc_id=None, **data):
    current_df = st.session_state['finance_data']
    if doc_id:
        # Update existing document
        if doc_id in current_df['id'].values:
            idx = current_df[current_df['id'] == doc_id].index[0]
            for key, value in data.items():
                current_df.loc[idx, key] = value
            st.success(f"Budget entry updated successfully! (ID: {doc_id})")
        else:
            st.error(f"Error: Entry with ID {doc_id} not found for update.")
    else:
        # Add new document
        new_id = str(uuid.uuid4())
        new_entry = {
            'id': new_id,
            'created_at': datetime.now().isoformat(), # Store as ISO format string
            **data
        }
        st.session_state['finance_data'] = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("New budget entry added successfully!")
    st.rerun() # Rerun to update UI immediately

# Function to delete budget entry (from session state)
def delete_budget(doc_id):
    current_df = st.session_state['finance_data']
    initial_rows = len(current_df)
    st.session_state['finance_data'] = current_df[current_df['id'] != doc_id].reset_index(drop=True)
    if len(st.session_state['finance_data']) < initial_rows:
        st.success(f"Budget entry (ID: {doc_id}) deleted successfully!")
    else:
        st.warning(f"Entry with ID {doc_id} not found for deletion.")
    st.rerun() # Rerun to update UI immediately

# Function to fetch all KPI data (from session state)
def get_kpis():
    return st.session_state['kpi_data']

# Function to add/update KPI entry (in session state)
def add_or_update_kpi(doc_id=None, **data):
    current_df = st.session_state['kpi_data']
    if doc_id:
        if doc_id in current_df['id'].values:
            idx = current_df[current_df['id'] == doc_id].index[0]
            for key, value in data.items():
                current_df.loc[idx, key] = value
            st.success(f"KPI entry updated successfully! (ID: {doc_id})")
        else:
            st.error(f"Error: KPI entry with ID {doc_id} not found for update.")
    else:
        new_id = str(uuid.uuid4())
        new_entry = {
            'id': new_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        st.session_state['kpi_data'] = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("New KPI entry added successfully!")
    st.rerun()

# Function to delete KPI entry (from session state)
def delete_kpi(doc_id):
    current_df = st.session_state['kpi_data']
    initial_rows = len(current_df)
    st.session_state['kpi_data'] = current_df[current_df['id'] != doc_id].reset_index(drop=True)
    if len(st.session_state['kpi_data']) < initial_rows:
        st.success(f"KPI entry (ID: {doc_id}) deleted successfully!")
    else:
        st.warning(f"KPI entry with ID {doc_id} not found for deletion.")
    st.rerun()


# --- Streamlit UI ---

st.title("💰 TechnoServe India: Finance & Budget Dashboard")
st.markdown("""
Welcome to the TechnoServe India Finance and Budget Tracking Dashboard.
This dashboard supports a Maker-Checker-Approver workflow for budget management.
**Note: This is a Phase 1 blueprint. Data is arbitrary and not persistent; it will reset when the app restarts.**
""")

# --- User Role Selection (Simulation) ---
st.sidebar.subheader("Select Your Role")
selected_role = st.sidebar.radio(
    "Choose your role to access different functionalities:",
    ('Viewer', 'Maker', 'Checker', 'Approver'),
    index=0 # Default to Viewer
)

# Load data using the in-memory functions
finance_df = get_budgets()
kpi_df = get_kpis()

# Ensure numeric columns for financial data are correct type after loading (important for calculations)
if not finance_df.empty:
    finance_df['Budget'] = pd.to_numeric(finance_df['Budget'], errors='coerce').fillna(0)
    finance_df['Actual'] = pd.to_numeric(finance_df['Actual'], errors='coerce').fillna(0)
    finance_df['Variance'] = finance_df['Actual'] - finance_df['Budget']
    # Calculate Variance (%) using numpy.where for robust handling of division by zero
    finance_df['Variance (%)'] = np.where(
        finance_df['Budget'] != 0,
        ((finance_df['Variance'] / finance_df['Budget']) * 100).round(2),
        0.0 # If Budget is 0, Variance (%) is 0.0
    )

# Ensure numeric columns for KPI data are correct type
if not kpi_df.empty:
    kpi_df['target_value'] = pd.to_numeric(kpi_df['target_value'], errors='coerce').fillna(0)
    kpi_df['actual_value'] = pd.to_numeric(kpi_df['actual_value'], errors='coerce').fillna(0)
    kpi_df['Progress (%)'] = np.where(
        kpi_df['target_value'] != 0,
        ((kpi_df['actual_value'] / kpi_df['target_value']) * 100).round(2),
        0.0
    )


# --- Sidebar Filters ---
st.sidebar.subheader("Filter Dashboard")
all_programs = ['All Programs'] + sorted(finance_df['Program'].unique().tolist()) if not finance_df.empty and 'Program' in finance_df.columns else ['All Programs']
selected_program = st.sidebar.selectbox("Filter by Program:", all_programs)

# Filter financial dataframe based on selected program
filtered_finance_df = finance_df.copy()
if selected_program != 'All Programs':
    filtered_finance_df = filtered_finance_df[filtered_finance_df['Program'] == selected_program]

# Filter KPI dataframe based on selected program
filtered_kpi_df = kpi_df.copy()
if selected_program != 'All Programs':
    filtered_kpi_df = filtered_kpi_df[filtered_kpi_df['associated_program'] == selected_program]


# --- Main Dashboard Content ---
st.header("Overall Financial Overview")

if filtered_finance_df.empty:
    st.info("No financial data available for the selected filters. Please add some budget entries.")
else:
    col1, col2, col3 = st.columns(3)

    total_budget = filtered_finance_df['Budget'].sum()
    total_actual = filtered_finance_df['Actual'].sum()
    total_variance = filtered_finance_df['Variance'].sum()

    with col1:
        st.metric(label="Total Budgeted", value=f"₹{total_budget:,.2f}")
    with col2:
        st.metric(label="Total Actual", value=f"₹{total_actual:,.2f}")
    with col3:
        st.metric(label="Total Variance", value=f"₹{total_variance:,.2f}", delta=f"{total_variance:,.2f}")

    st.markdown("---")

    # --- Charts ---
    st.subheader("Budget vs. Actuals by Category")
    fig_budget_actual = px.bar(
        filtered_finance_df.groupby('Category')[['Budget', 'Actual']].sum().reset_index(),
        x='Category',
        y=['Budget', 'Actual'],
        barmode='group',
        title='Budget vs. Actual Expenditure by Category',
        labels={'value': 'Amount (₹)', 'Category': 'Expense Category'},
        height=400,
        color_discrete_map={'Budget': '#1f77b4', 'Actual': '#ff7f0e'}
    )
    fig_budget_actual.update_layout(xaxis_title="Expense Category", yaxis_title="Amount (₹)")
    st.plotly_chart(fig_budget_actual, use_container_width=True)

    st.subheader("Variance Analysis by Category")
    fig_variance = px.bar(
        filtered_finance_df.groupby('Category')['Variance'].sum().reset_index(),
        x='Category',
        y='Variance',
        color='Variance',
        color_continuous_scale=px.colors.sequential.RdBu,
        title='Variance (Actual - Budget) by Category',
        labels={'Variance': 'Variance (₹)'},
        height=400
    )
    fig_variance.update_layout(xaxis_title="Expense Category", yaxis_title="Variance (₹)")
    st.plotly_chart(fig_variance, use_container_width=True)

st.markdown("---")
st.header("Key Results & Performance Indicators (KRAs/KPIs)")

if filtered_kpi_df.empty:
    st.info("No KRA/KPI data available for the selected program. Please add some KPI entries.")
else:
    st.subheader("KPI Progress Overview")
    for index, row in filtered_kpi_df.iterrows():
        st.write(f"**{row['name']}** (Program: {row['associated_program']})")
        st.progress(min(float(row['Progress (%)']) / 100, 1.0), text=f"Progress: {row['Progress (%)']:.2f}% (Actual: {row['actual_value']:,} {row['unit']} / Target: {row['target_value']:,} {row['unit']})")
        st.markdown(f"<small>Status: **{row['status']}** | Last Updated By: {row['last_updated_by']}</small>", unsafe_allow_html=True)
        st.markdown("---")


# --- Role-Based Functionality ---

st.markdown("---")
st.header(f"Role: {selected_role} Functionality")

if selected_role == 'Maker':
    st.subheader("Add/Edit Budget Entries")
    with st.form("budget_entry_form", clear_on_submit=True):
        st.write("Enter details for a new budget item or select an existing one to edit.")

        # Dropdown to select existing entry for editing
        existing_finance_ids = ['']
        if not finance_df.empty and 'id' in finance_df.columns:
            existing_finance_ids += sorted(finance_df['id'].unique().tolist())
        selected_doc_id = st.selectbox("Select budget entry to Edit (leave blank for new):", existing_finance_ids, key="budget_edit_select")

        initial_data = {}
        if selected_doc_id and not finance_df.empty:
            initial_data = finance_df[finance_df['id'] == selected_doc_id].iloc[0].to_dict()

        program = st.text_input("Program Name:", value=initial_data.get('Program', ''), key="budget_program_input")
        category = st.text_input("Category (e.g., Salaries, Travel):", value=initial_data.get('Category', ''), key="budget_category_input")
        budget = st.number_input("Budget Amount (₹):", min_value=0.0, value=float(initial_data.get('Budget', 0.0)), key="budget_amount_input")
        actual = st.number_input("Actual Spent (₹):", min_value=0.0, value=float(initial_data.get('Actual', 0.0)), key="actual_spent_input")

        submit_button = st.form_submit_button("Save Budget Entry", key="save_budget_button")

        if submit_button:
            if not program or not category:
                st.warning("Program Name and Category cannot be empty.")
            else:
                entry_data = {
                    "Program": program,
                    "Category": category,
                    "Budget": budget,
                    "Actual": actual,
                    "Status": "Draft" if not selected_doc_id else initial_data.get('Status', 'Draft'), # Maintain status if editing
                    "LastUpdatedBy": st.session_state['user_id']
                }
                add_or_update_budget(doc_id=selected_doc_id, **entry_data)
    
    # Maker can submit for review after saving
    st.write("---")
    st.subheader("Submit Budget for Review")
    if not finance_df.empty:
        maker_submittable_entries = finance_df[
            (finance_df['LastUpdatedBy'] == st.session_state['user_id']) &
            ((finance_df['Status'] == 'Draft') | (finance_df['Status'] == 'Rejected'))
        ]
        if not maker_submittable_entries.empty:
            submit_select_id = st.selectbox(
                "Select a budget entry to submit for Checker Review:",
                [''] + maker_submittable_entries['id'].tolist(),
                key="submit_budget_select"
            )
            if st.button(f"Submit Selected Budget ({submit_select_id}) for Review", key="submit_budget_button"):
                if submit_select_id:
                    idx = finance_df[finance_df['id'] == submit_select_id].index[0]
                    st.session_state['finance_data'].loc[idx, 'Status'] = "Pending Approval"
                    st.success(f"Budget entry '{submit_select_id}' submitted for review!")
                    st.rerun()
                else:
                    st.warning("Please select an entry to submit.")
        else:
            st.info("No draft or rejected budget entries available for submission.")


    st.subheader("Manage KRAs/KPIs")
    with st.form("kpi_entry_form", clear_on_submit=True):
        st.write("Enter details for a new KPI or select an existing one to edit.")

        existing_kpi_ids = ['']
        if not kpi_df.empty and 'id' in kpi_df.columns:
            existing_kpi_ids += sorted(kpi_df['id'].unique().tolist())
        selected_kpi_id = st.selectbox("Select KPI to Edit (leave blank for new):", existing_kpi_ids, key="kpi_edit_select")

        initial_kpi_data = {}
        if selected_kpi_id and not kpi_df.empty:
            initial_kpi_data = kpi_df[kpi_df['id'] == selected_kpi_id].iloc[0].to_dict()

        kpi_name = st.text_input("KPI Name:", value=initial_kpi_data.get('name', ''), key="kpi_name_input")
        # Ensure available programs are based on financial data
        available_programs = sorted(finance_df['Program'].unique().tolist()) if not finance_df.empty else []
        selected_kpi_program = st.selectbox(
            "Associated Program:",
            [''] + available_programs,
            index=available_programs.index(initial_kpi_data.get('associated_program')) + 1 if initial_kpi_data.get('associated_program') in available_programs else 0,
            key="kpi_program_select"
        )
        target_value = st.number_input("Target Value:", min_value=0.0, value=float(initial_kpi_data.get('target_value', 0.0)), key="kpi_target_input")
        actual_value = st.number_input("Actual Value:", min_value=0.0, value=float(initial_kpi_data.get('actual_value', 0.0)), key="kpi_actual_input")
        unit = st.text_input("Unit (e.g., ₹, %, Beneficiaries):", value=initial_kpi_data.get('unit', ''), key="kpi_unit_input")
        
        submit_kpi_button = st.form_submit_button("Save KPI Entry", key="save_kpi_button")

        if submit_kpi_button:
            if not kpi_name or not selected_kpi_program or not unit:
                st.warning("KPI Name, Associated Program, and Unit cannot be empty.")
            else:
                kpi_entry_data = {
                    "name": kpi_name,
                    "associated_program": selected_kpi_program,
                    "target_value": target_value,
                    "actual_value": actual_value,
                    "unit": unit,
                    "status": "On Track" if actual_value >= target_value else "At Risk", # Simple status logic
                    "last_updated_by": st.session_state['user_id']
                }
                add_or_update_kpi(doc_id=selected_kpi_id, **kpi_entry_data)
    
    st.subheader("Your KPI Entries")
    if not kpi_df.empty:
        maker_kpis = kpi_df[kpi_df['last_updated_by'] == st.session_state['user_id']]
        if not maker_kpis.empty:
            st.dataframe(maker_kpis[['name', 'associated_program', 'target_value', 'actual_value', 'unit', 'Progress (%)', 'status', 'id']].style.format({
                'target_value': "{:,.2f}", 'actual_value': "{:,.2f}", 'Progress (%)': "{:.2f}%"
            }), use_container_width=True)

            st.markdown("---")
            st.write("Delete your own KPI entries:")
            delete_kpi_id = st.text_input("Enter ID of KPI entry to delete:", key="maker_delete_kpi_id")
            if st.button("Delete Selected KPI Entry", key="maker_delete_kpi_button"):
                if delete_kpi_id and delete_kpi_id in maker_kpis['id'].tolist():
                    delete_kpi(delete_kpi_id)
                else:
                    st.warning("Invalid ID or you don't have permission to delete this KPI entry.")
        else:
            st.info("You currently have no KPI entries.")

    st.subheader("Your Draft and Pending Budget Entries")
    if not finance_df.empty:
        maker_entries = finance_df[(finance_df['LastUpdatedBy'] == st.session_state['user_id']) &
                                    ((finance_df['Status'] == 'Draft') | (finance_df['Status'] == 'Pending Approval') | (finance_df['Status'] == 'Rejected'))] # Maker can see rejected too
        if not maker_entries.empty:
            st.dataframe(maker_entries[['Program', 'Category', 'Budget', 'Actual', 'Status', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}"
            }), use_container_width=True)

            # Option to delete own entries
            st.markdown("---")
            st.write("Delete your own draft or pending/rejected budget entries:")
            delete_id = st.text_input("Enter ID of entry to delete:", key="maker_delete_id") # Added unique key
            if st.button("Delete Selected Entry", key="maker_delete_button"): # Added unique key
                if delete_id and delete_id in maker_entries['id'].tolist():
                    delete_budget(delete_id)
                else:
                    st.warning("Invalid ID or you don't have permission to delete this entry.")
        else:
            st.info("You currently have no draft, pending, or rejected budget entries.")


elif selected_role == 'Checker':
    st.subheader("Review Pending Budget Entries")
    if not finance_df.empty:
        pending_entries = finance_df[finance_df['Status'] == 'Pending Approval']
        if not pending_entries.empty:
            st.dataframe(pending_entries[['Program', 'Category', 'Budget', 'Actual', 'Variance', 'Status', 'LastUpdatedBy', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}", 'Variance': "₹{:,.2f}"
            }), use_container_width=True)

            st.markdown("---")
            st.write("Action on selected entries:")
            review_doc_id = st.text_input("Enter ID of entry to review:", key="checker_review_id") # Added unique key

            col_checker_actions = st.columns(2)
            with col_checker_actions[0]:
                if st.button("Approve for Approver", key="checker_approve_button"): # Added unique key
                    if review_doc_id and review_doc_id in pending_entries['id'].tolist():
                        idx = finance_df[finance_df['id'] == review_doc_id].index[0]
                        st.session_state['finance_data'].loc[idx, 'Status'] = "Approved by Checker"
                        st.session_state['finance_data'].loc[idx, 'CheckerReviewedBy'] = st.session_state['user_id']
                        st.success("Entry approved by Checker, awaiting final approval!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID that is 'Pending Approval'.")
            with col_checker_actions[1]:
                if st.button("Send Back to Maker", key="checker_sendback_button"): # Added unique key
                    if review_doc_id and review_doc_id in pending_entries['id'].tolist():
                        idx = finance_df[finance_df['id'] == review_doc_id].index[0]
                        st.session_state['finance_data'].loc[idx, 'Status'] = "Draft"
                        st.session_state['finance_data'].loc[idx, 'CheckerComments'] = "Needs revision by Maker"
                        st.session_state['finance_data'].loc[idx, 'CheckerReviewedBy'] = st.session_state['user_id']
                        st.info("Entry sent back to Maker for revisions.")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID that is 'Pending Approval'.")
        else:
            st.info("No budget entries are currently pending review.")
    else:
        st.info("No budget data available to review.")


elif selected_role == 'Approver':
    st.subheader("Approve/Reject Budget Entries")
    if not finance_df.empty:
        # Approver can see both 'Pending Approval' and 'Approved by Checker'
        entries_for_approval = finance_df[(finance_df['Status'] == 'Pending Approval') | (finance_df['Status'] == 'Approved by Checker')]
        if not entries_for_approval.empty:
            st.dataframe(entries_for_approval[['Program', 'Category', 'Budget', 'Actual', 'Variance', 'Status', 'LastUpdatedBy', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}", 'Variance': "₹{:,.2f}"
            }), use_container_width=True)

            st.markdown("---")
            st.write("Action on selected entries:")
            approve_doc_id = st.text_input("Enter ID of entry to approve/reject:", key="approver_approve_id") # Added unique key

            col_approver_actions = st.columns(2)
            with col_approver_actions[0]:
                if st.button("Final Approve", key="approver_final_approve_button"): # Added unique key
                    if approve_doc_id and approve_doc_id in entries_for_approval['id'].tolist():
                        idx = finance_df[finance_df['id'] == approve_doc_id].index[0]
                        st.session_state['finance_data'].loc[idx, 'Status'] = "Approved"
                        st.session_state['finance_data'].loc[idx, 'ApprovedBy'] = st.session_state['user_id']
                        st.success("Budget entry **Approved**!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID for approval.")
            with col_approver_actions[1]:
                if st.button("Reject", key="approver_reject_button"): # Added unique key
                    if approve_doc_id and approve_doc_id in entries_for_approval['id'].tolist():
                        idx = finance_df[finance_df['id'] == approve_doc_id].index[0]
                        st.session_state['finance_data'].loc[idx, 'Status'] = "Rejected"
                        st.session_state['finance_data'].loc[idx, 'RejectedBy'] = st.session_state['user_id']
                        st.error("Budget entry **Rejected**.")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID for rejection.")
        else:
            st.info("No budget entries are currently awaiting final approval.")
    else:
        st.info("No budget data available to approve/reject.")


else: # Viewer role
    st.subheader("All Approved Budget Entries")
    if not finance_df.empty:
        approved_entries = finance_df[finance_df['Status'] == 'Approved']
        if not approved_entries.empty:
            st.dataframe(approved_entries[['Program', 'Category', 'Budget', 'Actual', 'Variance', 'Status', 'LastUpdatedBy', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}", 'Variance': "₹{:,.2f}"
            }), use_container_width=True)
        else:
            st.info("No budget entries have been approved yet.")
    else:
        st.info("No budget data available.")

    st.subheader("All Defined KRAs/KPIs")
    if not kpi_df.empty:
        st.dataframe(kpi_df[['name', 'associated_program', 'target_value', 'actual_value', 'unit', 'Progress (%)', 'status', 'id']].style.format({
            'target_value': "{:,.2f}", 'actual_value': "{:,.2f}", 'Progress (%)': "{:.2f}%"
        }), use_container_width=True)
    else:
        st.info("No KRA/KPI data has been defined yet.")


# --- Footer ---
st.markdown("""
<br><hr><center><i>Powered by Streamlit</i></center>
""", unsafe_allow_html=True)

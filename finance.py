import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid # For generating unique IDs for documents

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="TechnoServe Finance Dashboard",
    page_icon="📊",
    layout="wide", # Changed to wide for more content
    initial_sidebar_state="expanded"
)

# --- Global User ID (for demo purposes) ---
# For demo, userId can be simulated. In a real app with persistence,
# you might associate users with specific roles or IDs from an auth system.
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = str(uuid.uuid4()) # Generate a random UUID for demo
st.sidebar.info(f"Current User ID: `{st.session_state['user_id']}`")

# --- Data Management Functions (In-Memory Pandas DataFrame) ---
# Data will NOT persist across app restarts or new sessions
if 'finance_data' not in st.session_state:
    # Initialize an empty DataFrame if no data is present
    st.session_state['finance_data'] = pd.DataFrame(columns=[
        'id', 'Program', 'Category', 'Budget', 'Actual', 'Status', 'LastUpdatedBy', 'created_at'
    ])

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


# --- Streamlit UI ---

st.title("💰 TechnoServe India: Finance & Budget Dashboard")
st.markdown("""
Welcome to the TechnoServe India Finance and Budget Tracking Dashboard.
This dashboard supports a Maker-Checker-Approver workflow for budget management.
**Note: Data is not persistent and will reset when the app restarts.**
""")

# --- User Role Selection (Simulation) ---
st.sidebar.subheader("Select Your Role")
selected_role = st.sidebar.radio(
    "Choose your role to access different functionalities:",
    ('Viewer', 'Maker', 'Checker', 'Approver'),
    index=0 # Default to Viewer
)

# Load data using the in-memory function
finance_df = get_budgets()

# Ensure numeric columns are correct type after loading (important for calculations)
if not finance_df.empty:
    finance_df['Budget'] = pd.to_numeric(finance_df['Budget'], errors='coerce').fillna(0)
    finance_df['Actual'] = pd.to_numeric(finance_df['Actual'], errors='coerce').fillna(0)
    finance_df['Variance'] = finance_df['Actual'] - finance_df['Budget']
    # Avoid division by zero for Variance (%)
    finance_df['Variance (%)'] = finance_df.apply(lambda row: (row['Variance'] / row['Budget'] * 100).round(2) if row['Budget'] != 0 else 0.0, axis=1)

# --- Sidebar Filters ---
st.sidebar.subheader("Filter Dashboard")
all_programs = ['All Programs'] + sorted(finance_df['Program'].unique().tolist()) if not finance_df.empty and 'Program' in finance_df.columns else ['All Programs']
selected_program = st.sidebar.selectbox("Filter by Program:", all_programs)

# Filter dataframe based on selected program
filtered_df = finance_df.copy()
if selected_program != 'All Programs':
    filtered_df = filtered_df[filtered_df['Program'] == selected_program]

# --- Main Dashboard Content ---
st.header("Overall Financial Overview")

if filtered_df.empty:
    st.info("No data available for the selected filters. Please add some budget entries.")
else:
    col1, col2, col3 = st.columns(3)

    total_budget = filtered_df['Budget'].sum()
    total_actual = filtered_df['Actual'].sum()
    total_variance = filtered_df['Variance'].sum()

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
        filtered_df.groupby('Category')[['Budget', 'Actual']].sum().reset_index(),
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
        filtered_df.groupby('Category')['Variance'].sum().reset_index(),
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


# --- Role-Based Functionality ---

st.markdown("---")
st.header(f"Role: {selected_role} Functionality")

if selected_role == 'Maker':
    st.subheader("Add/Edit Budget Entries")
    with st.form("budget_entry_form", clear_on_submit=True):
        st.write("Enter details for a new budget item or select an existing one to edit.")

        # Dropdown to select existing entry for editing
        # Ensure 'id' column exists before trying to access it
        existing_entries = ['']
        if not finance_df.empty and 'id' in finance_df.columns:
            existing_entries += sorted(finance_df['id'].unique().tolist())
        selected_doc_id = st.selectbox("Select entry to Edit (leave blank for new):", existing_entries)

        initial_data = {}
        if selected_doc_id and not finance_df.empty:
            # Load existing data for editing
            initial_data = finance_df[finance_df['id'] == selected_doc_id].iloc[0].to_dict()

        program = st.text_input("Program Name:", value=initial_data.get('Program', ''))
        category = st.text_input("Category (e.g., Salaries, Travel):", value=initial_data.get('Category', ''))
        budget = st.number_input("Budget Amount (₹):", min_value=0.0, value=float(initial_data.get('Budget', 0.0)))
        actual = st.number_input("Actual Spent (₹):", min_value=0.0, value=float(initial_data.get('Actual', 0.0)))

        submit_button = st.form_submit_button("Save Budget Entry")

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
                # After saving, potentially allow Maker to submit for review
                # The button should be within the form if it modifies form data directly,
                # but here it's an action on a saved item, so it's placed separately.
                # However, for simplicity and to avoid complex state management,
                # we'll put a placeholder and suggest a better approach.
                pass # Moved the submission logic outside the form's immediate submit block for clarity

    if selected_doc_id and selected_doc_id in finance_df['id'].tolist():
        # Check if the selected item is in a state where it can be submitted
        item_status = finance_df[finance_df['id'] == selected_doc_id]['Status'].iloc[0]
        if item_status == 'Draft' or item_status == 'Rejected': # Allow maker to resubmit if rejected
            if st.button(f"Submit '{selected_doc_id}' for Checker Review"):
                idx = finance_df[finance_df['id'] == selected_doc_id].index[0]
                st.session_state['finance_data'].loc[idx, 'Status'] = "Pending Approval"
                st.success("Entry submitted for review!")
                st.rerun() # Refresh


    st.subheader("Your Draft and Pending Entries")
    if not finance_df.empty:
        maker_entries = finance_df[(finance_df['LastUpdatedBy'] == st.session_state['user_id']) &
                                    ((finance_df['Status'] == 'Draft') | (finance_df['Status'] == 'Pending Approval') | (finance_df['Status'] == 'Rejected'))] # Maker can see rejected too
        if not maker_entries.empty:
            st.dataframe(maker_entries[['Program', 'Category', 'Budget', 'Actual', 'Status', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}"
            }), use_container_width=True)

            # Option to delete own entries
            st.markdown("---")
            st.write("Delete your own draft or pending/rejected entries:")
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


# --- Footer ---
st.markdown("""
<br><hr><center><i>Powered by Streamlit</i></center>
""", unsafe_allow_html=True)

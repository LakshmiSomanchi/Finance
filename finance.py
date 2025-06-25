import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import firestore # Changed from firebase_admin
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
import json
import uuid # For generating unique IDs for documents if needed


# --- Initialize Firebase (if not already initialized) ---
# Check if Firestore client is already initialized to prevent re-initialization errors
if not st.session_state.get('firestore_initialized', False): # Changed flag name
    try:
        # Load Firebase config from global variable __firebase_config
        # This variable is provided by the Canvas environment
        firebase_config_str = st.secrets["__firebase_config"] # Access from st.secrets
        firebase_config = json.loads(firebase_config_str)

        # Initialize Firestore client using the project_id from config
        # The 'project' argument is usually sufficient if running in an environment
        # with default credentials or if GOOGLE_APPLICATION_CREDENTIALS env var is set.
        # If running locally, ensure you have authenticated with `gcloud auth application-default login`
        project_id = firebase_config.get("projectId")
        if not project_id:
            st.error("Firebase config does not contain 'projectId'. Cannot initialize Firestore.")
            st.stop() # Stop execution if critical config is missing

        db = firestore.Client(project=project_id) # Initialize using google-cloud-firestore
        st.session_state['firestore_initialized'] = True # Changed flag name
        st.session_state['db'] = db # Store db client in session state
        st.success("Firestore client initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing Firestore: {e}")
        st.warning("Please ensure your Firebase project is properly configured and credentials are accessible (e.g., via `gcloud auth application-default login` if running locally, or proper environment variables in deployment).")

# Ensure db client is available
db = st.session_state.get('db')


# --- Streamlit Configuration ---
st.set_page_config(
    page_title="TechnoServe Finance Dashboard",
    page_icon="�",
    layout="wide", # Changed to wide for more content
    initial_sidebar_state="expanded"
)

# --- Global App ID and User ID (for Firestore paths) ---
# __app_id is provided by the Canvas environment
app_id = st.secrets["__app_id"] # Access from st.secrets
# For demo, userId can be simulated or obtained from actual authentication
# In a real app, you would get this from Firebase Auth (e.g., auth.current_user.uid)
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = str(uuid.uuid4()) # Generate a random UUID for demo
st.sidebar.info(f"Current User ID: `{st.session_state['user_id']}`")


# --- Data Management Functions (Firestore) ---
# Collection path for public data
BUDGETS_COLLECTION = db.collection(f"artifacts/{app_id}/public/data/budgets") if db else None

# Function to fetch all budget data with real-time listener
def get_budgets_realtime():
    if not BUDGETS_COLLECTION:
        return pd.DataFrame() # Return empty if DB not initialized

    # Use on_snapshot for real-time updates
    # This will be called initially and whenever the data changes
    def on_snapshot(col_snapshot, changes, read_time):
        data = []
        for doc in col_snapshot.docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id # Add document ID
            data.append(doc_data)
        st.session_state['finance_data'] = pd.DataFrame(data)
        st.rerun() # Rerun Streamlit app to update UI

    # Register the listener. The callback `on_snapshot` will update `st.session_state['finance_data']`
    # and trigger a rerun.
    # Store the listener in session_state to manage its lifecycle if needed (e.g., to stop it)
    if 'budget_listener' not in st.session_state:
        st.session_state['budget_listener'] = BUDGETS_COLLECTION.on_snapshot(on_snapshot)

    # Return the current state data
    return st.session_state.get('finance_data', pd.DataFrame())


# Function to add/update budget entry
def add_or_update_budget(doc_id=None, **data):
    if not BUDGETS_COLLECTION:
        st.error("Database not initialized.")
        return

    try:
        if doc_id:
            # Update existing document
            doc_ref = BUDGETS_COLLECTION.document(doc_id)
            doc_ref.update(data)
            st.success(f"Budget entry updated successfully! (ID: {doc_id})")
        else:
            # Add new document
            doc_ref = BUDGETS_COLLECTION.document() # Let Firestore auto-generate ID
            doc_ref.set({
                **data,
                'created_at': firestore.SERVER_TIMESTAMP # Add timestamp
            })
            st.success("New budget entry added successfully!")
    except Exception as e:
        st.error(f"Error saving budget entry: {e}")

# Function to delete budget entry
def delete_budget(doc_id):
    if not BUDGETS_COLLECTION:
        st.error("Database not initialized.")
        return
    try:
        BUDGETS_COLLECTION.document(doc_id).delete()
        st.success(f"Budget entry (ID: {doc_id}) deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting budget entry: {e}")


# --- Streamlit UI ---

st.title("💰 TechnoServe India: Finance & Budget Dashboard")
st.markdown("""
Welcome to the TechnoServe India Finance and Budget Tracking Dashboard.
This dashboard supports a Maker-Checker-Approver workflow for budget management.
""")

# --- User Role Selection (Simulation) ---
st.sidebar.subheader("Select Your Role")
selected_role = st.sidebar.radio(
    "Choose your role to access different functionalities:",
    ('Viewer', 'Maker', 'Checker', 'Approver'),
    index=0 # Default to Viewer
)

# Load data using the real-time listener. This will update st.session_state['finance_data']
finance_df = get_budgets_realtime()

# Ensure required columns exist, especially if no data is present yet
if not finance_df.empty:
    for col in ['Budget', 'Actual', 'Variance', 'Variance (%)', 'Program', 'Category', 'Status']:
        if col not in finance_df.columns:
            if col in ['Budget', 'Actual', 'Variance', 'Variance (%)']:
                finance_df[col] = 0.0
            else:
                finance_df[col] = ''

    # Recalculate derived columns in case of direct updates
    finance_df['Budget'] = pd.to_numeric(finance_df['Budget'], errors='coerce').fillna(0)
    finance_df['Actual'] = pd.to_numeric(finance_df['Actual'], errors='coerce').fillna(0)
    finance_df['Variance'] = finance_df['Actual'] - finance_df['Budget']
    # Avoid division by zero for Variance (%)
    finance_df['Variance (%)'] = finance_df.apply(lambda row: (row['Variance'] / row['Budget'] * 100).round(2) if row['Budget'] != 0 else 0.0, axis=1)

# --- Sidebar Filters ---
st.sidebar.subheader("Filter Dashboard")
all_programs = ['All Programs'] + sorted(finance_df['Program'].unique().tolist()) if not finance_df.empty else ['All Programs']
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
        existing_entries = [''] + sorted(finance_df['id'].unique().tolist()) if not finance_df.empty else ['']
        selected_doc_id = st.selectbox("Select entry to Edit (leave blank for new):", existing_entries)

        initial_data = {}
        if selected_doc_id:
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
                if st.button("Submit for Checker Review"):
                    if selected_doc_id and BUDGETS_COLLECTION:
                        BUDGETS_COLLECTION.document(selected_doc_id).update({"Status": "Pending Approval"})
                        st.success("Entry submitted for review!")
                        st.rerun() # Refresh


    st.subheader("Your Draft and Pending Entries")
    if not finance_df.empty:
        maker_entries = finance_df[(finance_df['LastUpdatedBy'] == st.session_state['user_id']) &
                                    ((finance_df['Status'] == 'Draft') | (finance_df['Status'] == 'Pending Approval'))]
        if not maker_entries.empty:
            st.dataframe(maker_entries[['Program', 'Category', 'Budget', 'Actual', 'Status', 'id']].style.format({
                'Budget': "₹{:,.2f}", 'Actual': "₹{:,.2f}"
            }), use_container_width=True)

            # Option to delete own entries
            st.markdown("---")
            st.write("Delete your own draft or pending entries:")
            delete_id = st.text_input("Enter ID of entry to delete:")
            if st.button("Delete Selected Entry"):
                if delete_id and delete_id in maker_entries['id'].tolist():
                    delete_budget(delete_id)
                    st.rerun() # Refresh
                else:
                    st.warning("Invalid ID or you don't have permission to delete this entry.")
        else:
            st.info("You currently have no draft or pending budget entries.")


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
            review_doc_id = st.text_input("Enter ID of entry to review:")

            col_checker_actions = st.columns(2)
            with col_checker_actions[0]:
                if st.button("Approve for Approver"):
                    if review_doc_id and BUDGETS_COLLECTION:
                        BUDGETS_COLLECTION.document(review_doc_id).update({"Status": "Approved by Checker", "CheckerReviewedBy": st.session_state['user_id']})
                        st.success("Entry approved by Checker, awaiting final approval!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID.")
            with col_checker_actions[1]:
                if st.button("Send Back to Maker"):
                    if review_doc_id and BUDGETS_COLLECTION:
                        BUDGETS_COLLECTION.document(review_doc_id).update({"Status": "Draft", "CheckerComments": "Needs revision by Maker", "CheckerReviewedBy": st.session_state['user_id']})
                        st.info("Entry sent back to Maker for revisions.")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID.")
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
            approve_doc_id = st.text_input("Enter ID of entry to approve/reject:")

            col_approver_actions = st.columns(2)
            with col_approver_actions[0]:
                if st.button("Final Approve"):
                    if approve_doc_id and BUDGETS_COLLECTION:
                        BUDGETS_COLLECTION.document(approve_doc_id).update({"Status": "Approved", "ApprovedBy": st.session_state['user_id']})
                        st.success("Budget entry **Approved**!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID.")
            with col_approver_actions[1]:
                if st.button("Reject"):
                    if approve_doc_id and BUDGETS_COLLECTION:
                        BUDGETS_COLLECTION.document(approve_doc_id).update({"Status": "Rejected", "RejectedBy": st.session_state['user_id']})
                        st.error("Budget entry **Rejected**.")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid entry ID.")
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
<br><hr><center><i>Powered by Streamlit & Firestore</i></center>
""", unsafe_allow_html=True)

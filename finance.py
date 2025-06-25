import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
st.set_page_config(
    page_title="TechnoServe Finance Dashboard",
    page_icon="📊",
    layout="centered", # Can be "wide" or "centered"
    initial_sidebar_state="expanded"
)

# --- Title and Introduction ---
st.title("💰 TechnoServe India: Finance & Budget Dashboard")
st.markdown("""
Welcome to the TechnoServe India Finance and Budget Tracking Dashboard.
This initial version provides a basic overview of budget vs. actual expenditures.
""")

# --- Dummy Data Generation ---
# In a real application, you would load this data from a database, CSV, or API.
@st.cache_data # Cache data to improve performance
def load_data():
    data = {
        'Category': ['Salaries', 'Rent', 'Utilities', 'Travel', 'Supplies', 'Marketing', 'Training', 'Operations'],
        'Budget': [150000, 30000, 15000, 25000, 10000, 12000, 8000, 20000],
        'Actual': [145000, 32000, 14000, 28000, 9500, 11000, 9000, 21000]
    }
    df = pd.DataFrame(data)
    # Calculate Variance
    df['Variance'] = df['Actual'] - df['Budget']
    df['Variance (%)'] = (df['Variance'] / df['Budget'] * 100).round(2)
    return df

finance_df = load_data()

# --- Display Raw Data (Optional) ---
st.subheader("Budget vs. Actuals by Category")
st.dataframe(finance_df.style.format({
    'Budget': "₹{:,.2f}",
    'Actual': "₹{:,.2f}",
    'Variance': "₹{:,.2f}",
    'Variance (%)': "{:.2f}%"
}), use_container_width=True)

# --- Summary Metrics ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

total_budget = finance_df['Budget'].sum()
total_actual = finance_df['Actual'].sum()
total_variance = finance_df['Variance'].sum()

with col1:
    st.metric(label="Total Budgeted", value=f"₹{total_budget:,.2f}")
with col2:
    st.metric(label="Total Actual", value=f"₹{total_actual:,.2f}")
with col3:
    st.metric(label="Total Variance", value=f"₹{total_variance:,.2f}", delta=f"{total_variance:,.2f}")

st.markdown("---")

# --- Interactive Chart: Budget vs Actual ---
st.subheader("Visualizing Expenditures")
fig = px.bar(
    finance_df,
    x='Category',
    y=['Budget', 'Actual'],
    barmode='group',
    title='Budget vs. Actual Expenditure by Category',
    labels={'value': 'Amount (₹)', 'Category': 'Expense Category'},
    height=400,
    color_discrete_map={'Budget': '#1f77b4', 'Actual': '#ff7f0e'} # Custom colors
)
fig.update_layout(xaxis_title="Expense Category", yaxis_title="Amount (₹)")
st.plotly_chart(fig, use_container_width=True)

# --- Interactive Chart: Variance Analysis ---
st.subheader("Variance Analysis")
fig_variance = px.bar(
    finance_df,
    x='Category',
    y='Variance',
    color='Variance', # Color bars based on variance value
    color_continuous_scale=px.colors.sequential.RdBu, # Red-Blue color scale
    title='Variance (Actual - Budget) by Category',
    labels={'Variance': 'Variance (₹)'},
    height=400
)
fig_variance.update_layout(xaxis_title="Expense Category", yaxis_title="Variance (₹)")
st.plotly_chart(fig_variance, use_container_width=True)


# --- Footer ---
st.markdown("""
<br><hr><center><i>Powered by Streamlit</i></center>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page title
st.title('Personal Finance Dashboard')

# Load data
try:
    net_worth_df = pd.read_csv('net_worth_example.csv', skiprows=1)
    expenses_df = pd.read_csv('expenses_example.csv')
except FileNotFoundError:
    st.error("Please ensure 'net_worth.csv' and 'expenses.csv' are in the same directory as this script.")
    st.stop()

# Clean net worth data
# Convert Date to datetime
net_worth_df['Date'] = pd.to_datetime(net_worth_df['Date'], format='%b %d, %Y')
# Remove '$' and ',' from numerical columns and convert to float
for col in net_worth_df.columns[1:]:
    net_worth_df[col] = net_worth_df[col].replace('[\$,"]', '', regex=True).astype(float)

# Clean expenses data
# Convert Date to datetime (format like "Aug '22")
expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], format="%b '%y")
# Remove '$' and ',' from numerical columns and convert to float
for col in expenses_df.columns[1:]:
    expenses_df[col] = expenses_df[col].replace('[\$,"]', '', regex=True).astype(float)

# Set Date as index for easier plotting
net_worth_df.set_index('Date', inplace=True)
expenses_df.set_index('Date', inplace=True)

# Sort dataframes by date
net_worth_df.sort_index(inplace=True)
expenses_df.sort_index(inplace=True)

# Determine the latest and earliest dates
latest_date = min(net_worth_df.index.max(), expenses_df.index.max())
earliest_date = max(net_worth_df.index.min(), expenses_df.index.min())

# **1. Net Worth Trend**
st.header('Net Worth Over Time')
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(net_worth_df.index, net_worth_df['Net Worth'], marker='o', color='blue')
ax1.set_title('Net Worth Over Time', fontsize=14)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Net Worth ($)', fontsize=12)
ax1.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

# **2. Asset Composition**
st.header('Asset Composition Over Time')
# Dynamically populate assets as all columns except 'Date', 'Net Worth', and 'CC Balance'
assets = [col for col in net_worth_df.columns if col not in ['Net Worth', 'CC Balance']]
fig2, ax2 = plt.subplots(figsize=(10, 6))
net_worth_df[assets].plot(kind='area', stacked=True, ax=ax2, alpha=0.6)
ax2.set_title('Asset Composition Over Time', fontsize=14)
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Value ($)', fontsize=12)
ax2.legend(title='Asset Type')
ax2.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

# **3. Monthly Total Expenses Trend**
st.header('Monthly Total Expenses')
fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.plot(expenses_df.index, expenses_df['TOTAL'], marker='o', color='orange')
ax4.set_title('Monthly Total Expenses', fontsize=14)
ax4.set_xlabel('Date', fontsize=12)
ax4.set_ylabel('Total Expenses ($)', fontsize=12)
ax4.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig4)

# **4. Expense Breakdown by Category with Slider**
st.header('Expense Breakdown by Category')

# Assuming expenses_df is a DataFrame with dates as index and categories as columns
available_dates = expenses_df.index.strftime('%b %Y').tolist()
selected_date_str = st.select_slider(
    'Select a month for expense breakdown:',
    options=available_dates,
    value=available_dates[-1]  # Default to the most recent month
)
selected_date = pd.to_datetime(selected_date_str, format='%b %Y')
selected_expenses = expenses_df.loc[selected_date].drop('TOTAL')

# Filter out categories with zero spending
selected_expenses = selected_expenses[selected_expenses > 0]

# Calculate total and percentages
total = selected_expenses.sum()
percentages = 100 * selected_expenses / total

# Separate categories > 3% and ≤ 3%
large_categories = selected_expenses[percentages > 3]
small_categories = selected_expenses[percentages <= 3]

# Create 'Other' category by summing small categories
if not small_categories.empty:
    other_value = small_categories.sum()
    if other_value > 0:
        large_categories['Other'] = other_value

# Prepare data for pie chart, sorted by percentage in descending order
pie_data = large_categories if not large_categories.empty else pd.Series()
pie_percentages = 100 * pie_data / pie_data.sum() if not pie_data.empty else pd.Series()
sorted_indices = pie_percentages.sort_values(ascending=False).index
sorted_expenses = pie_data[sorted_indices]
sorted_percentages = pie_percentages[sorted_indices]

# Define labels (show all categories)
labels = [category for category in sorted_expenses.index]

# Define custom autopct: show percentage as integer
def custom_autopct(pct):
    return f'{int(np.round(pct))}%'

# Use Matplotlib's tab20 colormap to assign colors dynamically
colors = plt.cm.tab20(np.linspace(0, 1, len(sorted_expenses)))
# Convert to HTML hex codes
colors = [plt.matplotlib.colors.to_hex(color) for color in colors]

# Create the pie chart with dynamic colors
fig5, ax5 = plt.subplots(figsize=(10, 6))
patches, texts, autotexts = ax5.pie(
    sorted_expenses,
    labels=labels,
    autopct=custom_autopct,
    startangle=30,
    colors=colors  # Apply dynamic colors
)

# Set title and display the plot
ax5.set_title(f'Expense Breakdown for {selected_date_str}', fontsize=14)
plt.tight_layout()
st.pyplot(fig5)

# **5. Key Statistics with Time Frame Selection**
st.header('Key Statistics')

# Select time frame
time_frame = st.selectbox('Select time frame for statistics:', ['Past 6 months', 'Past year'])

# Calculate start date based on time frame
if time_frame == 'Past 6 months':
    start_date = latest_date - pd.DateOffset(months=6)
else:
    start_date = latest_date - pd.DateOffset(years=1)

# Filter data based on start date
filtered_net_worth = net_worth_df[net_worth_df.index >= start_date]
filtered_expenses = expenses_df[expenses_df.index >= start_date]

# Check if the selected time frame exceeds available data
if start_date < earliest_date:
    st.write(f"Note: Data only available from {earliest_date.strftime('%b %Y')}")

# Calculate statistics
if not filtered_expenses.empty:
    avg_monthly_expenses = filtered_expenses['TOTAL'].mean()
    max_expenses = filtered_expenses['TOTAL'].max()
    min_expenses = filtered_expenses['TOTAL'].min()
    category_averages = filtered_expenses.drop(columns='TOTAL').mean()
    top_5_expenses = category_averages.sort_values(ascending=False).head(5)
else:
    avg_monthly_expenses = max_expenses = min_expenses = 0
    top_5_expenses = pd.Series()

if not filtered_net_worth.empty and len(filtered_net_worth) > 1:
    net_worth_change = filtered_net_worth['Net Worth'].iloc[-1] - filtered_net_worth['Net Worth'].iloc[0]
    avg_net_worth_change = filtered_net_worth['Net Worth'].diff().mean()
else:
    net_worth_change = avg_net_worth_change = 0

# Display statistics
st.subheader(f'Statistics for the {time_frame.lower()}')
st.markdown(f"**Average Monthly Expenses:** ${avg_monthly_expenses:,.2f}")
st.markdown(f"**Total Net Worth Change:** ${net_worth_change:,.2f}")
st.markdown(f"**Average Monthly Net Worth Change:** ${avg_net_worth_change:,.2f}")
st.markdown(f"**Maximum Monthly Expenses:** ${max_expenses:,.2f}")
st.markdown(f"**Minimum Monthly Expenses:** ${min_expenses:,.2f}")

st.subheader('Top 5 Expense Categories (Average Monthly Spending)')
if not top_5_expenses.empty:
    for category, avg in top_5_expenses.items():
        st.markdown(f"**{category}:** ${avg:,.2f} per month")
else:
    st.write("No expense data available for the selected time frame.")
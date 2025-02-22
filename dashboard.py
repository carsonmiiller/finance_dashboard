import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Initialize session state
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'

# Function to display detailed view
def show_detailed_view(date):
    st.title(f"Detailed View for {date.strftime('%b %d, %Y') if 'Net Worth' in net_worth_df.columns else date.strftime('%b %Y')}")
    
    # Determine if it's Net Worth or Expenses data
    if date in net_worth_df.index:
        st.subheader("Net Worth Details")
        net_worth_data = net_worth_df.loc[date]
        st.write(f"**Net Worth:** ${net_worth_data['Net Worth']:,.2f}")
        st.write("**Asset Breakdown:**")
        for asset in [col for col in net_worth_df.columns if col not in ['Net Worth', 'CC Balance']]:
            st.write(f"{asset}: ${net_worth_data[asset]:,.2f}")
        st.write(f"**Credit Card Balance:** ${net_worth_data['CC Balance']:,.2f}")
    elif date in expenses_df.index:
        st.subheader("Expense Details")
        expense_data = expenses_df.loc[date]
        st.write(f"**Total Expenses:** ${expense_data['TOTAL']:,.2f}")
        st.write("**Category Breakdown:**")
        for category in expense_data.index[:-1]:  # Exclude TOTAL
            st.write(f"{category}: ${expense_data[category]:,.2f}")
    
    # Back button
    if st.button("Back to Dashboard"):
        st.session_state.view = 'dashboard'
        st.session_state.selected_date = None

# Load data
try:
    net_worth_df = pd.read_csv('net_worth_example.csv', skiprows=1)
    expenses_df = pd.read_csv('expenses_example.csv')
except FileNotFoundError:
    st.error("Please ensure 'net_worth.csv' and 'expenses.csv' are in the same directory as this script.")
    st.stop()

# Clean net worth data
net_worth_df['Date'] = pd.to_datetime(net_worth_df['Date'], format='%b %d, %Y')
for col in net_worth_df.columns[1:]:
    net_worth_df[col] = net_worth_df[col].replace('[\$,"]', '', regex=True).astype(float)

# Clean expenses data
expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], format="%b '%y")
for col in expenses_df.columns[1:]:
    expenses_df[col] = expenses_df[col].replace('[\$,"]', '', regex=True).astype(float)

# Set Date as index
net_worth_df.set_index('Date', inplace=True)
expenses_df.set_index('Date', inplace=True)

# Sort dataframes by date
net_worth_df.sort_index(inplace=True)
expenses_df.sort_index(inplace=True)

# Determine latest and earliest dates
latest_date = min(net_worth_df.index.max(), expenses_df.index.max())
earliest_date = max(net_worth_df.index.min(), expenses_df.index.min())

# Main Dashboard or Detailed View
if st.session_state.view == 'dashboard':
    st.title('Personal Finance Dashboard')

    # **1. Net Worth Trend with Hover and Click**
    st.header('Net Worth Over Time')
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=net_worth_df.index,
            y=net_worth_df['Net Worth'],
            mode='lines+markers',
            line=dict(color='blue'),
            marker=dict(size=8),
            hovertemplate='<b>Date</b>: %{x|%b %d, %Y}<br><b>Net Worth</b>: $%{y:,.2f}<extra></extra>'
        )
    )
    fig1.update_layout(
        title='Net Worth Over Time',
        xaxis_title='Date',
        yaxis_title='Net Worth ($)',
        xaxis=dict(tickangle=45),
    )
    # Handle click event
    def on_net_worth_click(trace, points, selector):
        if points.point_inds:
            selected_date = net_worth_df.index[points.point_inds[0]]
            st.session_state.selected_date = selected_date
            st.session_state.view = 'detailed'
    fig1.data[0].on_click(on_net_worth_click)
    st.plotly_chart(fig1, use_container_width=True)

    # **2. Asset Composition with Hover and Click**
    st.header('Asset Composition Over Time')
    assets = [col for col in net_worth_df.columns if col not in ['Net Worth', 'CC Balance']]
    fig2 = go.Figure()
    for asset in assets:
        fig2.add_trace(
            go.Scatter(
                x=net_worth_df.index,
                y=net_worth_df[asset],
                mode='lines',
                name=asset,
                stackgroup='one',
                hoverinfo='x+y+name',
                line=dict(width=0.5)
            )
        )
    fig2.update_layout(
        title='Asset Composition Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        xaxis=dict(tickangle=45),
        hovermode='x unified',
        legend_title_text='Asset Type'
    )
    fig2.update_traces(
        hovertemplate='<b>%{fullData.name}</b>: $%{y:,.2f}<extra></extra>'
    )
    # Handle click event
    def on_asset_click(trace, points, selector):
        if points.point_inds:
            selected_date = net_worth_df.index[points.point_inds[0]]
            st.session_state.selected_date = selected_date
            st.session_state.view = 'detailed'
    for trace in fig2.data:
        trace.on_click(on_asset_click)
    st.plotly_chart(fig2, use_container_width=True)

    # **3. Monthly Total Expenses with Hover and Click**
    st.header('Monthly Total Expenses')
    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(
            x=expenses_df.index,
            y=expenses_df['TOTAL'],
            mode='lines+markers',
            line=dict(color='orange'),
            marker=dict(size=8),
            hovertemplate='<b>Date</b>: %{x|%b %Y}<br><b>Total Expenses</b>: $%{y:,.2f}<extra></extra>'
        )
    )
    fig4.update_layout(
        title='Monthly Total Expenses',
        xaxis_title='Date',
        yaxis_title='Total Expenses ($)',
        xaxis=dict(tickangle=45),
    )
    # Handle click event
    def on_expense_click(trace, points, selector):
        if points.point_inds:
            selected_date = expenses_df.index[points.point_inds[0]]
            st.session_state.selected_date = selected_date
            st.session_state.view = 'detailed'
    fig4.data[0].on_click(on_expense_click)
    st.plotly_chart(fig4, use_container_width=True)

    # **4. Expense Breakdown by Category with Slider**
    st.header('Expense Breakdown by Category')
    available_dates = expenses_df.index.strftime('%b %Y').tolist()
    selected_date_str = st.select_slider(
        'Select a month for expense breakdown:',
        options=available_dates,
        value=available_dates[-1]
    )
    selected_date = pd.to_datetime(selected_date_str, format='%b %Y')
    selected_expenses = expenses_df.loc[selected_date].drop('TOTAL')
    selected_expenses = selected_expenses[selected_expenses > 0]
    total = selected_expenses.sum()
    percentages = 100 * selected_expenses / total
    large_categories = selected_expenses[percentages > 3]
    small_categories = selected_expenses[percentages <= 3]
    if not small_categories.empty:
        other_value = small_categories.sum()
        if other_value > 0:
            large_categories['Other'] = other_value
    pie_data = large_categories if not large_categories.empty else pd.Series()
    sorted_indices = (100 * pie_data / pie_data.sum()).sort_values(ascending=False).index
    sorted_expenses = pie_data[sorted_indices]
    fig5 = px.pie(
        values=sorted_expenses,
        names=sorted_expenses.index,
        title=f'Expense Breakdown for {selected_date_str}',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig5.update_traces(
        textinfo='percent+label',
        textposition='inside',
        hovertemplate='<b>%{label}</b>: $%{value:,.2f}<br>%{percent}<extra></extra>'
    )
    st.plotly_chart(fig5, use_container_width=True)

    # **5. Key Statistics with Time Frame Selection**
    st.header('Key Statistics')
    time_frame = st.selectbox('Select time frame for statistics:', ['Past 6 months', 'Past year'])
    start_date = latest_date - pd.DateOffset(months=6 if time_frame == 'Past 6 months' else 12)
    filtered_net_worth = net_worth_df[net_worth_df.index >= start_date]
    filtered_expenses = expenses_df[expenses_df.index >= start_date]
    if start_date < earliest_date:
        st.write(f"Note: Data only available from {earliest_date.strftime('%b %Y')}")
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

elif st.session_state.view == 'detailed' and st.session_state.selected_date is not None:
    show_detailed_view(st.session_state.selected_date)
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Specify the file path to your CSV file
file_path = 'data/nifty_df.csv'
nifty = pd.read_csv(file_path)

file_path = 'data/junior_df.csv'
junior = pd.read_csv(file_path)

file_path = 'data/liq.csv'
liquid = pd.read_csv(file_path)

file_path = 'data/mid_df.csv'
mid = pd.read_csv(file_path)

file_path = 'data/gold_df.csv'
gold = pd.read_csv(file_path)

file_path = 'data/bank_df.csv'
bank = pd.read_csv(file_path)


# Function to calculate SIP returns
def calculate_sip_returns(invested_amount, start_date, end_date, df):
    # Convert start_date and end_date to strings
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    # Filter the DataFrame for the specified date range and select only "Date" and "Close" columns
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)][['Date', 'Close']]

    # Convert the 'Date' column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Extract the year and month from the 'Date' column
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Create a new column 'StartingDateOfMonth' to mark the starting date of each month
    df['StartingDateOfMonth'] = df.groupby(['Year', 'Month'])['Date'].transform('min')

    # Filter the DataFrame to include only rows with starting dates
    starting_dates_df = df[df['Date'] == df['StartingDateOfMonth']]

    # Create the 'Investment' column by performing the calculation and rounding
    starting_dates_df['No_Of_Units'] = (invested_amount / starting_dates_df['Close']).round(0)

    # Calculate the cumulative sum of the 'Investment' column and assign it to the 'Cumulative' column
    starting_dates_df['Cumulative'] = starting_dates_df['No_Of_Units'].cumsum()

    # Insert a new column 'Investment' with the constant value of the invested amount
    starting_dates_df['Investment'] = invested_amount

    # Calculate the cumulative sum of the 'Investment' column and assign it to the 'Invested' column
    starting_dates_df['Invested'] = starting_dates_df['Investment'].cumsum()

    # Calculate the product of the 'Close' and 'Cumulative' columns and assign it to the 'Returns' column
    starting_dates_df['Returns'] = starting_dates_df['Close'] * starting_dates_df['Cumulative']

    return starting_dates_df


# Function to calculate lumpsum returns
def calculate_lumpsum_returns(invested_amount, start_date, end_date, df):
    # Convert start_date and end_date to strings
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    # Filter the DataFrame for the specified date range and select only "Date" and "Close" columns
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)][['Date', 'Close']]

    # Convert the 'Date' column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Check if December 19, 2019 falls within the date range
    special_condition = (pd.to_datetime('2019-12-19') >= pd.to_datetime(start_date)) and \
                        (pd.to_datetime('2019-12-19') <= pd.to_datetime(end_date))

    # Insert a new column 'Investment' with the constant value of the invested amount
    df['Investment'] = invested_amount

    # Create the 'Investment' column by performing the calculation and rounding
    df['No_Of_Units'] = (invested_amount / df['Close']).round(0)

    # Apply the special condition only at the last date
    if special_condition:
        # Multiply the number of units by 10 at the last date
        df.loc[df.index[-1], 'No_Of_Units'] *= 10

    # Calculate the product of the 'Close' and 'No_Of_Units' columns and assign it to the 'Returns' column
    df['Returns'] = df['Close'] * df['No_Of_Units']

    return df


# Function to visualize SIP returns
def visualize_sip_returns(data_df):
    # Create a figure for the plot
    fig = go.Figure()

    # Add traces for 'Invested' and 'Returns' lines
    fig.add_trace(go.Scatter(x=data_df['Date'], y=data_df['Invested'],
                             mode='lines+markers',
                             name='Invested',
                             hoverinfo='x+y+text',
                             text=[f'Invested Amount: {inv:.2f}<br>Returns: {ret:.2f}'
                                   for inv, ret in zip(data_df['Invested'], data_df['Returns'])],
                             line=dict(shape='hv')))

    fig.add_trace(go.Scatter(x=data_df['Date'], y=data_df['Returns'],
                             mode='lines',
                             name='Returns',
                             hoverinfo='none',
                             line=dict(shape='hv')))

    # Customize the layout
    fig.update_layout(title='Invested vs. Returns Over Months (SIP Format)',
                      xaxis_title='Date',
                      yaxis_title='Amount (Rs)',
                      hovermode='closest',
                      showlegend=True)

    # Show the interactive plot
    st.plotly_chart(fig)


# Function to visualize Lumpsum returns
def visualize_lumpsum_returns(data_df):
    # Create a figure for the plot
    fig = go.Figure()

    # Add a line from 'Investment' to 'Returns' with a custom hover template
    fig.add_trace(go.Scatter(x=[data_df['Date'].iloc[0], data_df['Date'].iloc[-1]],
                             y=[data_df['Investment'].iloc[0], data_df['Returns'].iloc[-1]],
                             mode='lines',
                             name='Investment to Returns',
                             hoverinfo='x+y+text',
                             text=[
                                 f'Date: {data_df["Date"].iloc[0]}<br>Investment: {data_df["Investment"].iloc[0]:.2f}<br>Returns: {data_df["Returns"].iloc[-1]:.2f}'],
                             line=dict(color='blue', width=2)))  # Customize line appearance

    # Add a constant 'Investment' line with a custom hover template
    fig.add_trace(go.Scatter(x=data_df['Date'], y=data_df['Investment'],
                             mode='lines',
                             name='Investment',
                             hoverinfo='x+y+text',
                             text=[f'Date: {date}<br>Investment: {investment:.2f}<br>Returns: {returns:.2f}' for
                                   date, investment, returns in
                                   zip(data_df['Date'], data_df['Investment'], data_df['Returns'])],
                             line=dict(color='green', width=2)))  # Customize line appearance

    # Customize the layout
    fig.update_layout(title='Lumpsum Investment and Returns Over Time',
                      xaxis_title='Date',
                      yaxis_title='Amount (Rs)',
                      showlegend=True)

    # Show the interactive plot
    st.plotly_chart(fig)


# Streamlit app
st.title("Stock Investment Calculator")

# Input fields
start_date = st.date_input("Start Date", min_value=datetime(2007, 1, 1), max_value=datetime(2023, 9, 29),
                           value=datetime(2007, 1, 1))
end_date = st.date_input("End Date", min_value=datetime(2007, 1, 1), max_value=datetime(2023, 9, 29),
                         value=datetime(2023, 9, 29))
investment_amount = st.number_input("Investment Amount", min_value=1)
stock_selection = st.multiselect("Select Stocks",
                                 ["Nifty", "JuniorBees", "Mid150Bees", "LiquidBees", "GoldBees", "BankBees"])
calculation_type = st.selectbox("Calculation Type", ["SIP", "Lumpsum"])
calculate_button = st.button("Calculate Returns")

# Create a list to store DataFrames for selected stocks
selected_dfs = []
selected_stocks = []

# Check if the Calculate Returns button is clicked
if calculate_button:
    # Fetch data for selected stocks and perform calculations
    for stock in stock_selection:
        if stock == "Nifty":
            df = calculate_sip_returns(investment_amount, start_date, end_date, nifty) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, nifty)
            selected_dfs.append(df)
            selected_stocks.append(stock)
        elif stock == "JuniorBees":
            df = calculate_sip_returns(investment_amount, start_date, end_date, junior) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, junior)
            selected_dfs.append(df)
            selected_stocks.append(stock)
        elif stock == "Mid150Bees":
            df = calculate_sip_returns(investment_amount, start_date, end_date, mid) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, mid)
            selected_dfs.append(df)
            selected_stocks.append(stock)
        elif stock == "LiquidBees":
            df = calculate_sip_returns(investment_amount, start_date, end_date, liquid) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, liquid)
            selected_dfs.append(df)
            selected_stocks.append(stock)
        elif stock == "GoldBees":
            df = calculate_sip_returns(investment_amount, start_date, end_date, gold) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, gold)
            selected_dfs.append(df)
            selected_stocks.append(stock)
        elif stock == "BankBees":
            df = calculate_sip_returns(investment_amount, start_date, end_date, bank) if calculation_type == "SIP" else calculate_lumpsum_returns(investment_amount, start_date, end_date, bank)
            selected_dfs.append(df)
            selected_stocks.append(stock)

# Display calculated returns and visualization if the button is clicked
for i, df in enumerate(selected_dfs):
    st.subheader(f"Returns for {selected_stocks[i]}:")

    # Display the final return value neatly
    final_return = df['Returns'].iloc[-1]
    st.info(f"Final Return: {final_return:.2f} Rs")    
    
    # Button to show full data using st.expander
    with st.expander("See Full Data"):
        st.write(df)  # Display the full DataFrame returns

        # Generate a file name with start and end dates
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        file_name = f"{selected_stocks[i]}_returns_{start_date_str}_to_{end_date_str}.csv"

        # Button to download the entire DataFrame as a CSV file with the custom file name
    csv_export_button = st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name=file_name,
        key=f"{selected_stocks[i]}_csv",
    )

    # Visualize the returns
    if calculation_type == "SIP":
        st.subheader(f"Visualization for {selected_stocks[i]}:")
        visualize_sip_returns(df)
    elif calculation_type == "Lumpsum":
        st.subheader(f"Visualization for {selected_stocks[i]}:")
        visualize_lumpsum_returns(df)

    # Display the download button
    st.markdown(csv_export_button, unsafe_allow_html=True)

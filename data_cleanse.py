import os
import glob
import pandas as pd
import numpy as np

# Folder where the CSV files are stored
folder = 'sp500_data'

# Lists to collect processed dataframes for the two outputs
financials_list = []
stockprice_list = []

# Get list of all CSV files in the folder
all_files = glob.glob(os.path.join(folder, '*.csv'))

# Dictionaries to hold file paths for financial and stock price files
financial_files = {}  # key: ticker, value: dict with file types
stock_files = {}      # key: ticker, value: filepath

# Separate files based on naming convention
for filepath in all_files:
    filename = os.path.basename(filepath)
    # Check if the file is one of the three financial statements
    if any(x in filename for x in ['_balance_sheet.csv', '_cashflow.csv', '_financials.csv']):
        # Extract ticker from file name (assumes ticker is before the first underscore)
        ticker = filename.split('_')[0]
        if ticker not in financial_files:
            financial_files[ticker] = {}
        if '_balance_sheet.csv' in filename:
            financial_files[ticker]['balance_sheet'] = filepath
        elif '_cashflow.csv' in filename:
            financial_files[ticker]['cashflow'] = filepath
        elif '_financials.csv' in filename:
            financial_files[ticker]['financials'] = filepath
    else:
        # For files like "AAPL.csv", assume it contains stock price data
        ticker = filename.replace('.csv', '')
        stock_files[ticker] = filepath

# Process financial files for each ticker (only if all three exist)
for ticker, files_dict in financial_files.items():
    if set(files_dict.keys()) == {'balance_sheet', 'cashflow', 'financials'}:
        # Read each CSV file with the metric names as the index.
        # It is assumed that rows are metrics and columns are dates.
        df_bs = pd.read_csv(files_dict['balance_sheet'], index_col=0)
        df_cf = pd.read_csv(files_dict['cashflow'], index_col=0)
        df_fin = pd.read_csv(files_dict['financials'], index_col=0)
        
        # Pivot the data: transpose so that dates become rows and metrics become columns.
        df_bs = df_bs.transpose().reset_index().rename(columns={'index': 'Year'})
        df_cf = df_cf.transpose().reset_index().rename(columns={'index': 'Year'})
        df_fin = df_fin.transpose().reset_index().rename(columns={'index': 'Year'})
        
        # Optionally, you might want to rename columns to indicate their origin:
        # df_bs = df_bs.rename(columns=lambda x: x + " (BS)" if x not in ['Year'] else x)
        # df_cf = df_cf.rename(columns=lambda x: x + " (CF)" if x not in ['Year'] else x)
        # df_fin = df_fin.rename(columns=lambda x: x + " (Fin)" if x not in ['Year'] else x)
        
        # Merge the three dataframes on "Year" (outer join in case one file has extra years)
        df_merge = pd.merge(df_bs, df_cf, on='Year', how='outer')
        df_merge = pd.merge(df_merge, df_fin, on='Year', how='outer')
        
        # Add a column for the ticker symbol
        df_merge.insert(0, 'Ticker', ticker)
        
        financials_list.append(df_merge)
    else:
        print(f"Skipping {ticker} because not all financial files are available.")

# Concatenate all tickers' financial data and write to CSV if any
if financials_list:
    df_financials = pd.concat(financials_list, ignore_index=True)
    df_financials.to_csv('Financials.csv', index=False)
    print("Financials.csv has been created.")
else:
    print("No complete financial data available to process.")

# Process stock price files: calculate annual coefficient of variation (CoV) of (Close * Volume)
for ticker, filepath in stock_files.items():
    # Read CSV while skipping the 2nd and 3rd rows (index positions 1 and 2)
    # The first row (index 0) is used as header ("Price,Close,High,Low,Open,Volume")
    df_stock = pd.read_csv(filepath, skiprows=[1, 2])
    
    # Rename the "Price" column to "Date" since it actually contains the date information
    df_stock.rename(columns={"Price": "Date"}, inplace=True)
    
    # Convert the Date column to datetime
    df_stock['Date'] = pd.to_datetime(df_stock['Date'])
    
    # Calculate the product of Close and Volume
    df_stock['CloseVolume'] = df_stock['Close'] * df_stock['Volume']
    
    # Extract the year from the Date column
    df_stock['Year'] = df_stock['Date'].dt.year
    
    # Define a function to compute the Coefficient of Variation (std/mean)
    def coefficient_of_variation(x):
        return x.std() / x.mean() if x.mean() != 0 else np.nan
    
    # Group by Year and compute the CoV for the product column
    annual_cov = df_stock.groupby('Year')['CloseVolume'].apply(coefficient_of_variation).reset_index()
    
    # Rename the computed column to CoV
    annual_cov.rename(columns={'CloseVolume': 'CoV'}, inplace=True)
    
    # Add the ticker column to the result
    annual_cov.insert(0, 'Ticker', ticker)
    
    stockprice_list.append(annual_cov)

# Concatenate all stock price CoV results and write to CSV if any
if stockprice_list:
    df_stockprice = pd.concat(stockprice_list, ignore_index=True)
    df_stockprice.to_csv('StockPrice.csv', index=False)
    print("StockPrice.csv has been created.")
else:
    print("No stock price data available to process.")

# Read the financials CSV
df_financials = pd.read_csv('Financials.csv')

# Convert the 'Year' column in Financials.csv to datetime and extract only the year.
# If the 'Year' column contains dates (e.g. "2015-12-31"), this will convert it to 2015.
df_financials['Year'] = pd.to_datetime(df_financials['Year'], errors='coerce').dt.year

# Read the stock price CSV
df_stockprice = pd.read_csv('StockPrice.csv')

# Ensure that the Year column in the stock price data is integer (if needed)
df_stockprice['Year'] = df_stockprice['Year'].astype(int)

# Merge the two DataFrames on 'Ticker' and 'Year'
# This will bring in all the financials columns into the stock price data rows that have matching Ticker and Year.
df_data = pd.merge(df_stockprice, df_financials, on=['Ticker', 'Year'], how='left')

# Save the combined DataFrame to a new CSV file
df_data.to_csv('Data.csv', index=False)

print("Data.csv has been created.")
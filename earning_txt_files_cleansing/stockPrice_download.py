# run below line first in terminal:
# .\.venv\Scripts\activate

import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Step 1: Get the list of S&P 500 companies
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]
    return tickers

def get_unique_tickers_from_files(folder_path):
    tickers = set()
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            ticker = filename.split('_')[0]
            tickers.add(ticker)
    return list(tickers)

# Step 2: Download historical data
def download_historical_data(tickers, start_date='2015-01-01', end_date='2024-12-31'):
    if not os.path.exists('sp500_data'):
        os.makedirs('sp500_data')
    
    for ticker in tickers:
        try:
            print(f"Downloading data for {ticker}")
            data = yf.download(ticker, start=start_date, end=end_date)
            data.to_csv(f'sp500_data/{ticker}.csv')
            
            print(f"Downloading financials for {ticker}")
            ticker_obj = yf.Ticker(ticker)
            financials = ticker_obj.financials
            financials.to_csv(f'sp500_data/{ticker}_financials.csv')
            
            balance_sheet = ticker_obj.balance_sheet
            balance_sheet.to_csv(f'sp500_data/{ticker}_balance_sheet.csv')
            
            cashflow = ticker_obj.cashflow
            cashflow.to_csv(f'sp500_data/{ticker}_cashflow.csv')

        except Exception as e:
            print(f"Failed to download data for {ticker}: {e}")

# Step 3: Main function
def main():
    # tickers = get_sp500_tickers()
    folder_path = os.path.join(os.path.dirname(__file__), '..', 'earning_files_ticker')
    tickers = get_unique_tickers_from_files(folder_path)
    tickers.sort()
    print("Tickers to be downloaded:", tickers)
    download_historical_data(tickers)

if __name__ == "__main__":
    main()

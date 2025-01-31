import os
import requests
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
from datetime import datetime
import shutil

def get_sp500_tickers():
    """Fetch S&P 500 tickers from Wikipedia."""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    return tickers

def extract_year_from_accession(accession_folder):
    """Extract and correct the year from the accession number."""
    year_fragment = accession_folder.split("-")[1]  # e.g., '99' or '20'
    
    # Handle 1900s and 2000s
    if int(year_fragment) >= 80:
        return "19" + year_fragment  # 1980–1999
    else:
        return "20" + year_fragment  # 2000–2079
    

def download_10k(tickers, start_year):
    """Download and reorganize 10-K filings for the last 10 years."""
    dl = Downloader("sc3899@columbia.edu", "sec-edgar-filings")

    # Save all files in ./10-K
    save_dir = "./10-K"
    os.makedirs(save_dir, exist_ok=True)

    for ticker in tickers:
        ticker_folder = os.path.join("sec-edgar-filings", ticker)

        # Skip download if already exists
        if os.path.exists(ticker_folder):
            print(f"Skipping {ticker}, already downloaded.")
            continue

        print(f"Downloading 10-K filings for {ticker}...")

        try:
            # Download all available 10-Ks
            dl.get("10-K", ticker)
        except ValueError as e:
            print(f"Skipping {ticker}: {e}")
            continue

        # Correct path to include EDGAR's accession number folders
        source_dir = f"./sec-edgar-filings/{ticker}/10-K"

        if not os.path.exists(source_dir):
            print(f"No filings found for {ticker}")
            continue

        # Traverse subfolders (e.g., 0000320193-20-000096)
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file == "full-submission.txt":
                    accession_folder = os.path.basename(root)
                    
                    # Extract the year from the accession number (e.g., '20' for 2020)
                    filing_year = extract_year_from_accession(accession_folder)

                    # Only move filings from the past 10 years
                    if int(filing_year) >= start_year:
                        new_filename = f"{ticker}_{filing_year}.txt"
                        src = os.path.join(root, file)
                        dst = os.path.join(save_dir, new_filename)

                        # Move and rename the file
                        shutil.move(src, dst)
                        print(f"Saved: {dst}")

        # Optional: Clean up the original download folder
        # shutil.rmtree(source_dir)


def download_8k(tickers, start_year):
    """Download and reorganize 8-K filings for the last 10 years."""
    dl = Downloader("sc3899@columbia.edu", "sec-edgar-filings")

    # Save all files in ./8-K
    save_dir = "./8-K"
    os.makedirs(save_dir, exist_ok=True)

    for ticker in tickers:
        ticker_folder = os.path.join("sec-edgar-filings", ticker)

        # Skip download if already exists
        if os.path.exists(ticker_folder):
            print(f"Skipping {ticker}, already downloaded.")
            continue

        print(f"Downloading 8-K filings for {ticker}...")

        try:
            # Download all available 8-Ks
            dl.get("8-K", ticker)
        except ValueError as e:
            print(f"Skipping {ticker}: {e}")
            continue

        # Correct path to include EDGAR's accession number folders
        source_dir = f"./sec-edgar-filings/{ticker}/8-K"

        if not os.path.exists(source_dir):
            print(f"No filings found for {ticker}")
            continue

        # Traverse subfolders (e.g., 0000320193-20-000096)
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file == "full-submission.txt":
                    accession_folder = os.path.basename(root)
                    
                    # Extract the year from the accession number (e.g., '20' for 2020)
                    filing_year = extract_year_from_accession(accession_folder)

                    # Only move filings from the past 10 years
                    if int(filing_year) >= start_year:
                        new_filename = f"{ticker}_{filing_year}.txt"
                        src = os.path.join(root, file)
                        dst = os.path.join(save_dir, new_filename)

                        # Move and rename the file
                        shutil.move(src, dst)
                        print(f"Saved: {dst}")

        # Optional: Clean up the original download folder
        # shutil.rmtree(source_dir)


if __name__ == "__main__":
    # tickers = get_sp500_tickers()
    tickers = ['AAPL', 'TSLA', 'NVDA']
    current_year = datetime.now().year
    # download_10k(tickers, current_year - 10)
    download_8k(tickers, current_year - 10)

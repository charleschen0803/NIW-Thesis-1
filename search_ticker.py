#!/usr/bin/env python3
import os
import csv
import time
import requests
import argparse

def extract_company_names(folder):
    """
    Walks through the files in the folder and returns a set of unique company names.
    Assumes filenames are of the form "company name_yyyymmdd.txt".
    """
    company_names = set()
    for filename in os.listdir(folder):
        if not filename.lower().endswith('.txt'):
            continue
        base, _ = os.path.splitext(filename)  # remove .txt extension
        # Expecting the pattern: "company name_yyyymmdd"
        if '_' in base:
            # Split at the last underscore so that company names that include underscores are handled.
            company, _ = base.rsplit('_', 1)
            company_names.add(company.strip())
        else:
            # If no underscore found, assume the entire filename is the company name.
            company_names.add(base.strip())
    return company_names

def find_ticker(company_name):
    """
    Uses Yahoo Finance's search API to try to find a ticker for the given company name.
    Returns the ticker symbol if found, otherwise returns None.
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": company_name,
        "quotesCount": 5,
        "newsCount": 0,
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        quotes = data.get("quotes", [])
        if quotes:
            # Try to find a quote whose longname or shortname contains the company name.
            lower_company = company_name.lower()
            for quote in quotes:
                longname = quote.get("longname", "").lower()
                shortname = quote.get("shortname", "").lower()
                if lower_company in longname or lower_company in shortname:
                    return quote.get("symbol")
            # If none match well, return the symbol from the first result.
            return quotes[0].get("symbol")
    except Exception as e:
        print(f"Error fetching ticker for '{company_name}': {e}")
    return None

def write_mapping_to_csv(mapping, output_csv):
    """
    Writes the list of (company_name, ticker) pairs to a CSV file.
    """
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Company Name", "Ticker"])
        for company, ticker in mapping:
            writer.writerow([company, ticker])
    print(f"Mapping written to {output_csv}")

def main(folder, output_csv):
    # 1. Extract unique company names.
    company_names = extract_company_names(folder)
    print(f"Found {len(company_names)} unique company names.")
    
    # 2. For each company name, try to find its ticker.
    mapping = []
    for company in sorted(company_names):
        print(f"Searching ticker for: '{company}'")
        ticker = find_ticker(company)
        if ticker:
            print(f"  Found ticker: {ticker}")
        else:
            print(f"  No ticker found for: '{company}'")
            ticker = ""  # leave blank if not found
        mapping.append((company, ticker))
        # Pause briefly between requests to avoid overloading the API.
        time.sleep(1)
    
    # 3. Write the mapping to a CSV file.
    write_mapping_to_csv(mapping, output_csv)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Parse through files with names of the form 'company name_yyyymmdd.txt', "
                    "search for ticker info via Yahoo Finance, and store the mapping in a CSV."
    )
    parser.add_argument(
        "folder", 
        help="Path to the folder containing files without ticker info (e.g. ./earning_files_no_ticker)"
    )
    parser.add_argument(
        "output_csv", 
        help="Path to the output CSV file (e.g. company_ticker_mapping.csv)"
    )
    args = parser.parse_args()
    
    main(args.folder, args.output_csv)

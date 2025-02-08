#!/usr/bin/env python3
import os
import csv
import argparse
import shutil

def read_mapping(csv_file):
    """
    Reads the CSV file and returns a dictionary mapping
    company name to ticker.
    
    Expects a CSV with headers: "company name" and "ticker"
    """
    mapping = {}
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip any extra whitespace from the fields
            company = row['Company Name'].strip()
            ticker = row['Ticker'].strip()
            mapping[company] = ticker
    return mapping

def process_files(source_folder, dest_folder, mapping):
    """
    Loops through files in the source folder, extracts the company name
    and date from each file name of the form "company name_yyyymmdd.txt",
    looks up the ticker using the provided mapping, and copies the file
    to the destination folder, renaming it to "ticker_yyyymmdd.txt".
    """
    os.makedirs(dest_folder, exist_ok=True)
    
    for filename in os.listdir(source_folder):
        if not filename.lower().endswith('.txt'):
            continue  # only process .txt files

        # Remove the extension
        base, ext = os.path.splitext(filename)
        if '_' not in base:
            print(f"Skipping file '{filename}': Underscore not found in filename.")
            continue
        
        # Use rsplit so that if the company name itself contains underscores, we use the last one as the delimiter.
        company, date_part = base.rsplit('_', 1)
        company = company.strip()
        date_part = date_part.strip()
        
        ticker = mapping.get(company)
        if ticker:
            new_filename = f"{ticker}_{date_part}{ext}"
            src_path = os.path.join(source_folder, filename)
            dest_path = os.path.join(dest_folder, new_filename)
            print(f"Copying '{filename}' -> '{new_filename}'")
            shutil.copy(src_path, dest_path)
        else:
            print(f"No ticker mapping found for company '{company}' in file '{filename}'. Skipping file.")

def main(csv_file, source_folder, dest_folder):
    mapping = read_mapping(csv_file)
    print(f"Loaded mapping for {len(mapping)} companies from '{csv_file}'.")
    process_files(source_folder, dest_folder, mapping)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Rename and copy earnings files using a company-to-ticker CSV mapping."
    )
    parser.add_argument(
        "csv_file", 
        help="Path to the CSV file with 'company name' and 'ticker' columns (e.g., company_ticker_mapping.csv)"
    )
    parser.add_argument(
        "source_folder", 
        help="Folder with earnings files without ticker info (e.g., ./earning_files_no_ticker)"
    )
    parser.add_argument(
        "dest_folder", 
        help="Destination folder for renamed earnings files (e.g., ./earnings_files_ticker)"
    )
    args = parser.parse_args()
    
    main(args.csv_file, args.source_folder, args.dest_folder)

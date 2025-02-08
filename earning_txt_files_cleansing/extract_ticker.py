#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
import argparse

def parse_date_from_filename(filename):
    """
    Extracts the date from the filename.
    
    Two patterns are supported:
      1. Underscore form: e.g., "AES Corp_20200405.txt" → "20200405"
      2. Comma-separated form with month abbreviation:
         e.g., "The Kraft Heinz Company, Q2 2021 Pre Recorded Earnings Call, Aug 04, 2021.txt"
         will extract "Aug 04, 2021" and convert it to "20210804".
    """
    # First try underscore pattern
    m = re.search(r'_(\d{8})\.txt$', filename)
    if m:
        return m.group(1)
    
    # Otherwise, try to find a date pattern with a month abbreviation.
    # This regex looks for a three-letter month, one or two digit day, a comma, and a four-digit year.
    m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s*\d{4}', filename)
    if m:
        date_str = m.group(0)
        try:
            dt = datetime.strptime(date_str, '%b %d, %Y')
            return dt.strftime('%Y%m%d')
        except Exception as e:
            print(f"Error parsing date from {date_str} in {filename}: {e}")
            return None
    # If no date pattern is found, return None.
    return None

def extract_ticker_from_file(file_path):
    """
    Reads the file and searches for ticker information.
    
    Looks for lines containing either 'NYSE:' or 'NasdaqGS:'.
    Returns the ticker (the non‐whitespace string immediately following the colon)
    if found; otherwise returns None.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read line by line (we assume the ticker is in one of the first few lines)
            for line in f:
                # Search for either NYSE or NasdaqGS followed by a colon and ticker text.
                match = re.search(r'(NYSE|NasdaqGS):(\S+)', line)
                if match:
                    return match.group(2)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return None

def main(input_folder, output_folder_ticker, output_folder_no_ticker):
    # Create the output directories if they do not already exist.
    os.makedirs(output_folder_ticker, exist_ok=True)
    os.makedirs(output_folder_no_ticker, exist_ok=True)
    
    # Process each .txt file in the input folder.
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith('.txt'):
            continue  # skip non-txt files
        
        file_path = os.path.join(input_folder, filename)
        ticker = extract_ticker_from_file(file_path)
        date_str = parse_date_from_filename(filename)
        
        if ticker and date_str:
            # If ticker and date are available, rename as "TICKER_yyyymmdd.txt"
            new_filename = f"{ticker}_{date_str}.txt"
            destination = os.path.join(output_folder_ticker, new_filename)
            print(f"Copying and renaming '{filename}' to '{destination}'")
            shutil.copy(file_path, destination)
        else:
            # If no ticker info (or date extraction fails), copy the file as-is.
            destination = os.path.join(output_folder_no_ticker, filename)
            print(f"Copying '{filename}' to '{destination}' without renaming")
            shutil.copy(file_path, destination)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Copy .txt files to new folders. Files with ticker info are renamed to TICKER_yyyymmdd.txt; files without ticker info are simply copied."
    )
    parser.add_argument("input_folder", help="Path to folder containing .txt files")
    parser.add_argument("output_folder_ticker", help="Path to output folder for files with ticker info")
    parser.add_argument("output_folder_no_ticker", help="Path to output folder for files without ticker info")
    args = parser.parse_args()
    
    main(args.input_folder, args.output_folder_ticker, args.output_folder_no_ticker)

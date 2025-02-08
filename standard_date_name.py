import os
import re
import sys
import datetime
from dateutil.relativedelta import relativedelta

def standardize_filename(filename):
    """
    Given a filename (with extension), return a standardized filename if it matches
    an Earnings Call pattern. Otherwise, return None.

    Expected variations include:
      - "MetLife, Inc., Q3 2020 Pre Recorded Earnings Call, Nov 04, 2020.txt"
      - "Leidos Holdings, Inc., 2020 Earnings Call, Feb 23, 2021.txt"
      - "The Kraft Heinz Company, Q1 2021 Pre Recorded Earnings Call, Apr 29, 2021.txt"

    The standardized format is: "Company Name_yyyymmdd.txt"

    Special rule: If the quarter info (if present) starts with "Q1", subtract 2 months
    from the parsed date.
    """
    base, ext = os.path.splitext(filename)
    
    # If already standardized (ends with "_" and exactly 8 digits), do nothing.
    if re.match(r'.*_\d{8}$', base):
        return None

    # We expect at least two commas (since the date "MMM dd, YYYY" has a comma).
    parts = base.rsplit(',', 2)
    if len(parts) < 3:
        return None

    # Part 0: everything before the date portion.
    remainder = parts[0].strip()
    # Parts 1 and 2 form the date string.
    date_str = f"{parts[1].strip()}, {parts[2].strip()}"
    
    # Try to parse the date.
    try:
        dt = datetime.datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        # Date did not match expected format.
        return None

    # Look for "earnings call" (case-insensitive) in the remainder.
    lower_remainder = remainder.lower()
    idx = lower_remainder.find("earnings call")
    if idx == -1:
        # If not found, skip.
        return None

    # Take the part before "earnings call" as our prefix.
    prefix = remainder[:idx].strip().rstrip(',')
    
    # If there's a comma in the prefix, assume the last comma separates
    # the company name from the quarter (or year) info.
    if ',' in prefix:
        company_part, quarter_info = prefix.rsplit(',', 1)
        company = company_part.strip()
        quarter_info = quarter_info.strip()
    else:
        company = prefix
        quarter_info = ""
    
    # Special adjustment for Q1 calls.
    if quarter_info.lower().startswith("q1"):
        dt = dt - relativedelta(months=2)
    
    new_date_str = dt.strftime('%Y%m%d')
    new_filename = f"{company}_{new_date_str}{ext}"
    return new_filename

def rename_files(directory):
    """
    Walk through all .txt files in the specified directory.
    For files matching an Earnings Call pattern, rename them to the standardized
    "Company Name_yyyymmdd.txt" format.
    Files already standardized or not matching the pattern are skipped.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith('.txt'):
            new_name = standardize_filename(filename)
            if new_name and new_name != filename:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                if os.path.exists(new_path):
                    print(f"Warning: '{new_name}' already exists. Skipping renaming of '{filename}'.")
                else:
                    print(f"Renaming '{filename}' to '{new_name}'")
                    os.rename(old_path, new_path)
            else:
                print(f"Skipping '{filename}' (either already standardized or not matching expected pattern).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_script.py <directory>")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    rename_files(target_directory)

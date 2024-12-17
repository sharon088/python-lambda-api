import pandas as pd
import os
import sys

def convert_csv_to_excel(csv_file):
    """ Converts a CSV file to an Excel file """
    try:
        dir_name = os.path.dirname(csv_file)
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        excel_file = os.path.join(dir_name, f"{base_name}.xlsx")       
        pd.read_csv(csv_file).to_excel(excel_file, index=False)
        print(f"Successfully converted '{csv_file}' to '{excel_file}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 csv_to_excel.py <path/to/csv_file.csv>")
    else:
        convert_csv_to_excel(sys.argv[1])

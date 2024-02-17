import pandas as pd
import os
import re

def names(csv_input, xlsx_input, output_csv):
    try:
        # Read the csv file without a header
        csv_df = pd.read_csv(csv_input, header=None)
        csv_first_column = csv_df.iloc[:, 0]
        csv_first_column.name = 'First names'
        # Read the Excel file with a header
        xlsx_df = pd.read_excel(xlsx_input)
        xlsx_first_column = xlsx_df.iloc[:, 0]
        xlsx_first_column.name = 'Second names'
        # Combine the two columns
        combined_df = pd.concat([csv_first_column, xlsx_first_column], axis=1)
        # Save the combined DataFrame to a new CSV file
        combined_df.to_csv(output_csv, index=False)
    except Exception as e:
        return e

def dictionary(directory, output_file):
    with open(output_file, 'w', encoding='utf-8', errors='replace') as outfile:
        # Iterate over each file in the directory
        for filename in os.listdir(directory):
            # Check if the file ends with a number
            if re.search(r'\d$', filename):
                file_path = os.path.join(directory, filename)
                try:
                    # Try opening with utf-8 encoding
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read() + '\n')
                except UnicodeDecodeError:
                    # If utf-8 fails, try with latin-1, as there are some characters with accent used
                    with open(file_path, 'r', encoding='latin-1') as infile:
                        outfile.write(infile.read() + '\n')

# Build the names database
names('interall.csv', 'app_c.xlsx', 'names.csv')
# Build the dictionary database
dictionary('final', 'dictionary.txt')

import pandas as pd

def cleaning(file_path, cleaned_file_path):
    data = pd.read_csv(file_path)
    # Fill missing values with 0
    data.fillna(0, inplace=True)
    # Validate the range of each attribute
    for column in data.columns[:-1]:  # Exclude the last column
        # Remove rows with values outside the range {-1, 0, 1}
        data = data[data[column].isin([-1, 0, 1])]
    # Save the cleaned data
    data.to_csv(cleaned_file_path, index=False)

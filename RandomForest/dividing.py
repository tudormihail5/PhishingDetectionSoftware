import pandas as pd

def dividing(cleaned, training, validation, testing):
    df = pd.read_csv(cleaned)
    # Calculate the number of rows for each split
    total_rows = len(df)
    train_size = int(0.7 * total_rows)
    validation_size = int(0.15 * total_rows)
    test_size = total_rows - train_size - validation_size
    # Split the data
    train_df = df.iloc[:train_size]
    validation_df = df.iloc[train_size:train_size + validation_size]
    test_df = df.iloc[train_size + validation_size:]
    # Save the splits to new CSV files
    train_df.to_csv(training, index=False)
    validation_df.to_csv(validation, index=False)
    test_df.to_csv(testing, index=False)

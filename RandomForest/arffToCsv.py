import csv

def convert_arff_to_csv(arff_file_path, csv_file_path, excluded_columns):
    with open(arff_file_path, 'r') as arff_file:
        # Initialize a list to hold attribute names (column headers)
        attributes = []
        # Flag to indicate when we're in the data section
        in_data_section = False
        csv_data = []
        for line in arff_file:
            line = line.strip()
            if not line or line.startswith('%'):  # Skip empty lines and comments
                continue
            # Extract attribute names before the data section
            if not in_data_section:
                if line.lower().startswith('@attribute'):
                    attribute_name = line.split()[1]
                    attributes.append(attribute_name)
                elif line.lower().startswith('@data'):
                    in_data_section = True
                    # Exclude specified columns
                    attributes = [attr for i, attr in enumerate(attributes) if i not in excluded_columns]
                    csv_data.append(attributes)  # Add header row to CSV data
            else:
                # Process data lines
                data = line.split(',')
                # Exclude specified columns
                data = [data[i] for i in range(len(data)) if i not in excluded_columns]
                csv_data.append(data)
    # Write the prepared data to a CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)

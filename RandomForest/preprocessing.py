import arffToCsv
import cleaning
import dividing

# Convert arff to csv
arffToCsv.convert_arff_to_csv('database.arff', 'database.csv', [25, 26, 28, 29])
# Clean the data
cleaning.cleaning('database.csv', 'cleaned.csv')
# Divide the data into 70% for training, 15% for validation, and 15% for testing
dividing.dividing('cleaned.csv', 'training.csv', 'validation.csv', 'testing.csv')

import pickle
import randomForest
import pandas as pd
from sklearn.metrics import accuracy_score

# Load the model from the file; the second one is for the library implementation
with open('random_forest_model.pkl', 'rb') as file:
# with open('library_model.pkl', 'rb') as file:
    forest = pickle.load(file)

# Make predictions using the loaded model
def make_predictions(forest, test_data):
    predictions = []
    for row in test_data:
        predictions.append(randomForest.bagging_predict(forest, row))
    return predictions

# Load the testing dataset and separate features and target variable
test_df = pd.read_csv('testing.csv')
test_features = test_df.drop('Result', axis=1) 
test_labels = test_df['Result']
test_data = test_features.values.tolist()
# The second one is for the library implementation
predictions = make_predictions(forest, test_data)
# predictions = forest.predict(test_features)

# Calculate and print the accuracy of the model
accuracy = accuracy_score(test_labels, predictions) 
print(f'Accuracy: {accuracy}')

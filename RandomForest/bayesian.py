import numpy as np
import randomForest
import pandas as pd
from math import sqrt
import os
import pickle
from sklearn.metrics import accuracy_score
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

# Load the datasets and separate features and target variable
train_df = pd.read_csv('training.csv')
validation_df = pd.read_csv('validation.csv')
train_data = train_df.values.tolist()
validation_features = validation_df.drop('Result', axis=1) 
validation_labels = validation_df['Result']
validation_data = validation_features.values.tolist()

n_jobs = os.cpu_count()
n_features = int(sqrt(len(train_data[0])-1))

# Make predictions using the loaded model
def make_predictions(forest, test_data):
    predictions = []
    for row in test_data:
        predictions.append(randomForest.bagging_predict(forest, row))
    return predictions

# Perform hyperparameter optimization
def objective(params):
    # Define the search space for hyperparameters
    max_depth = int(params['max_depth'])
    min_size = int(params['min_size'])
    sample_size = int(params['sample_size'])
    n_trees = int(params['n_trees'])
    # Train the model with the given parameters
    forest = randomForest.random_forest(train_data, max_depth, min_size, sample_size / 10, n_trees, n_features, n_jobs)
    # Evaluate the model
    predictions = make_predictions(forest, validation_data)
    accuracy = accuracy_score(validation_labels, predictions)
    # Loss must be minimized
    loss = 1 - accuracy
    return {'loss': loss, 'status': STATUS_OK, 'accuracy': accuracy}
    
# Define the space of hyperparameters to search (intervals)
space = {
    'max_depth': hp.quniform('max_depth', 1, 100, 1),
    'min_size': hp.quniform('min_size', 1, 100, 1),
    'sample_size': hp.quniform('sample_size', 1, 10, 1),
    'n_trees': hp.quniform('n_trees', 1, 500, 1)
}

# Run the optimization
trials = Trials()
best_indices = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=1, trials=trials)

# Decode the best hyperparameters
best_hyperparameters = {
    'max_depth': int(best_indices['max_depth']),
    'min_size': int(best_indices['min_size']),
    'sample_size': int(best_indices['sample_size']) / 10,
    'n_trees': int(best_indices['n_trees'])
}
print('Best Hyperparameters:', best_hyperparameters)

# Find the best model performance achieved during the optimization
best_accuracy = 0
for trial in trials.trials:
    if trial['result']['accuracy'] > best_accuracy:
        best_accuracy = trial['result']['accuracy']
print('Best validation accuracy:', best_accuracy)

# Train the best model and save it
forest = randomForest.random_forest(train_data, int(best_indices['max_depth']), int(best_indices['min_size']), int(best_indices['sample_size']) / 10, int(best_indices['n_trees']), n_features, n_jobs)
filename = 'random_forest_model.pkl'
with open(filename, 'wb') as file:
    pickle.dump(forest, file)

print('Model trained and saved')

"""
Best hyperparameters: {'max_depth': 60, 'min_size': 13, 'sample_size': 0.5, 'n_trees': 63}
Best validation accuracy: 0.9396863691194209
Best testing accuracy: 0.9403254972875226
"""

import numpy as np
import pandas as pd
from math import sqrt
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

# Load the datasets and separate features and target variable
train_df = pd.read_csv('training.csv')
validation_df = pd.read_csv('validation.csv')
x_train = train_df.drop('Result', axis=1)
y_train = train_df['Result']
x_validation = validation_df.drop('Result', axis=1)
y_validation = validation_df['Result']

# Perform hyperparameter optimization
def objective(params):
    # Define the search space for hyperparameters
    n_estimators = int(params['n_estimators'])
    max_depth = int(params['max_depth'])
    min_samples_split = int(params['min_samples_split'])
    # Train the model with the given parameters
    model = RandomForestClassifier(n_estimators = n_estimators, max_depth = max_depth, min_samples_split = min_samples_split, max_features  = 'sqrt', n_jobs = os.cpu_count())
    model.fit(x_train, y_train)
    # Evaluate the model
    predictions = model.predict(x_validation)
    accuracy = accuracy_score(y_validation, predictions)
    # Loss must be minimized
    loss = 1 - accuracy
    return {'loss': loss, 'status': STATUS_OK, 'accuracy': accuracy}

# Define the space of hyperparameters to search
space = {
    'n_estimators': hp.quniform('n_estimators', 1, 500, 1),
    'max_depth': hp.quniform('max_depth', 1, 100, 1),
    'min_samples_split': hp.quniform('min_samples_split', 2, 100, 1)
}

# Run the optimization
trials = Trials()
best_indices = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=10, trials=trials)

# Decode the best hyperparameters
best_hyperparameters = {
    'n_estimators': int(best_indices['n_estimators']),
    'max_depth': int(best_indices['max_depth']),
    'min_samples_split': int(best_indices['min_samples_split'])
}
print('Best Hyperparameters:', best_hyperparameters)

# Find the best model performance achieved during the optimization
best_accuracy = 0
for trial in trials.trials:
    if trial['result']['accuracy'] > best_accuracy:
        best_accuracy = trial['result']['accuracy']
print('Best validation accuracy:', best_accuracy)

# Train the best model and save it
model = RandomForestClassifier(**best_hyperparameters, max_features  = 'sqrt', n_jobs = os.cpu_count())
model.fit(x_train, y_train)
filename = 'library_model.pkl'
with open(filename, 'wb') as file:
    pickle.dump(model, file)

print('Model trained and saved')

"""
Best hyperparameters: {'n_estimators': 312, 'max_depth': 48, 'min_samples_split': 77}
Best validation accuracy: 0.9372738238841978
Best testing accuracy: 0.9367088607594937
"""

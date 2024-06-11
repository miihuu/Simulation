import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from simulation.data import data_directory
import numpy as np


# Step 1: Load the data
file_path = 'C:/Users/tamze/OneDrive/Documents/GitHub/Simulation/simulation/data/hyperparam_search/Hyperparameter Search - Round 2.csv'
data = pd.read_csv(file_path)

# Clean the data
# Drop sequence and average fitness columns
data.drop(data.columns[[0, -1]], axis=1, inplace=True)

# Get categorical columns
categorical_columns = data.select_dtypes(include=['object']).columns

# Apply Label Encoding (Random Forest cant handle string data)
label_encoders = {}
for col in categorical_columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Split hyperparameters and target fitness 
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Get Random Forest model
model = RandomForestRegressor()

# Set up the hyperparameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Run the hyperparameter search
print("Running search")
grid_search = RandomizedSearchCV(estimator=model, param_distributions=param_grid, cv=3, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)
print("Finished search")

# Results
best_model = grid_search.best_estimator_
print(f'Best hyperparameters: {grid_search.best_params_}')
# y_pred = best_model.predict(X_test)
# accuracy = accuracy_score(y_test, y_pred)
# print(f'Accuracy: {accuracy}')


# Decode column
# column_to_decode = 'Crossover'  # Replace with column to decode
# encoded_values = data[column_to_decode].head()  # Get encoded column values
# decoded_values = label_encoders[column_to_decode].inverse_transform(encoded_values)

# Predict the fitness values for the entire dataset
predictions = best_model.predict(X)

# Find the row with the highest predicted fitness value
max_fitness_index = np.argmax(predictions)
best_row = data.iloc[max_fitness_index]

# Decode the categorical cols back to their original values
for col in categorical_columns:
    best_row[col] = label_encoders[col].inverse_transform([int(best_row[col])])[0]

print("Row with the highest fitness value:")
print(best_row)
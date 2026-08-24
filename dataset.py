import pandas as pd
import random
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib

# Step 1: Generate dummy dataset
categories = ['Vegetables', 'Fruits', 'Grains']
seasons = ['Summer', 'Winter', 'Spring', 'Autumn']

data = {
    'Product Category': [random.choice(categories) for _ in range(10)],
    'Supply Quantity (Tons)': [random.randint(5, 50) for _ in range(10)],
    'Demand (Number of Buyers)': [random.randint(500, 3000) for _ in range(10)],
    'Season': [random.choice(seasons) for _ in range(10)],
    'Competitor Price (₹)': [random.randint(30, 100) for _ in range(10)],
}

data['Actual Price (₹)'] = [
    price + random.randint(-10, 20) for price in data['Competitor Price (₹)']
]

df = pd.DataFrame(data)

# Step 2: Feature encoding for 'Season' using OneHotEncoder
encoder = ColumnTransformer(
    transformers=[('season', OneHotEncoder(), ['Season'])],
    remainder='passthrough'
)

# Step 3: Create a pipeline with preprocessing and regression model
pipeline = Pipeline(steps=[
    ('preprocessor', encoder),
    ('model', LinearRegression())
])

# Step 4: Train the model with the pipeline
X = df[['Competitor Price (₹)', 'Supply Quantity (Tons)', 'Demand (Number of Buyers)', 'Season']]
y = df['Actual Price (₹)']

pipeline.fit(X, y)

# Step 5: Predict and update the dataset
df['Predicted Optimal Price (₹)'] = pipeline.predict(X)

# Step 6: Save the updated dataset and model
df.to_csv('dummy_data_with_predicted_prices.csv', index=False)  # Save to the correct file
joblib.dump(pipeline, 'pricing_model.pkl')  # Save model for future use

# Print success message
print("Dataset with predictions saved to 'dummy_data_with_predicted_prices.csv'")
print("Pipeline saved to 'pricing_model.pkl'")

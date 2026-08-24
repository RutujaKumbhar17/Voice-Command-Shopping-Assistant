import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Step 1: Load the dataset
try:
    df = pd.read_csv('dummy_data_with_predicted_prices.csv')
    print("Dataset loaded successfully.")
    print(df.head())
    print(f"Number of rows in dataset: {len(df)}")
except FileNotFoundError:
    print("Error: The dataset file 'dummy_data_with_predicted_prices.csv' was not found.")
    exit()

# Step 2: Extract relevant columns
actual_prices = df['Actual Price (₹)']
predicted_prices = df['Predicted Optimal Price (₹)']

# Step 3: Evaluate the model
mse = mean_squared_error(actual_prices, predicted_prices)
mae = mean_absolute_error(actual_prices, predicted_prices)

print(f"Mean Squared Error (MSE): {mse}")
print(f"Mean Absolute Error (MAE): {mae}")

# Step 4: Plot the graph
plt.figure(figsize=(10, 6))
plt.plot(range(len(actual_prices)), actual_prices, label='Actual Prices', color='blue', marker='o')
plt.plot(range(len(predicted_prices)), predicted_prices, label='Predicted Prices', color='green', marker='x')
plt.xlabel('Product Index')
plt.ylabel('Price (₹)')
plt.title('Actual vs Predicted Prices')
plt.legend()
plt.grid(True)
plt.show()

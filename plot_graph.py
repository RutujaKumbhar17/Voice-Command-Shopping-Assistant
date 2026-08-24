import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv('dummy_data_with_predicted_prices.csv')

# Extract values
product_indices = range(len(df))
actual_prices = df['Actual Price (₹)']
competitor_prices = df['Competitor Price (₹)']
predicted_prices = df['Predicted Optimal Price (₹)']

# Plot
plt.figure(figsize=(12, 6))
plt.plot(product_indices, actual_prices, label='Actual Prices', color='blue', marker='o')
plt.plot(product_indices, competitor_prices, label='Competitor Prices', color='orange', linestyle='--')
plt.plot(product_indices, predicted_prices, label='Predicted Prices', color='green', marker='x')
plt.xlabel('Product Index')
plt.ylabel('Price (₹)')
plt.title('Price Comparison: Actual, Competitor, and Predicted Prices')
plt.legend()
plt.grid(True)
plt.show()

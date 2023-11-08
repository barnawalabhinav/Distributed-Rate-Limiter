import matplotlib.pyplot as plt
import numpy as np

# Prepare your data
products = ['Product A', 'Product B']
sales_2022 = [200, 350]  # Sales data for 2022
sales_2023 = [250, 400]  # Sales data for 2023

# Create an array of x-values for the bars
x = np.arange(len(products))

# Set the width of the bars and the gap between pairs
bar_width = 0.35
bar_gap = 0.05

# Create the first pair of bars
plt.bar(x - bar_width/2 - bar_gap-2, sales_2022, bar_width, label='2022')

# Create the second pair of bars
plt.bar(x + bar_width/2 + bar_gap-2, sales_2023, bar_width, label='2023')

# Set the labels for the x-axis and y-axis
plt.xlabel('Products')
plt.ylabel('Sales')

# Set the labels for the x-axis ticks
plt.xticks(x, products)

# Add a legend
plt.legend()

# Show the plot
plt.show()

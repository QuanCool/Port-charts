#%%
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set basic style parameters for better visibility
plt.rcParams['figure.figsize'] = [15, 8]
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Read the Excel file
excel_file = 'Sales NPATMI quarter.xlsx'
df = pd.read_excel(excel_file, sheet_name='Sales')

# Extract data for VSC
quarters = df['Sales']  # Quarter column is under 'Sales'
vsc_sales = df['VSC']  # Sales data
vsc_volume = df['VSC.1']  # Container volume data
vsc_npatmi = df['VSC.2']  # NPATMI data

# Create figure with two subplots sharing x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)

# Plot Container Volume as bars
ax1.bar(quarters, vsc_volume, color='skyblue')
ax1.set_title('Quarterly Container Volume - VSC', pad=10)
ax1.set_ylabel('Container Volume')
ax1.grid(True, linestyle='--', alpha=0.7)
# Format y-axis with comma separator
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
# Add data labels for volume
for i, v in enumerate(vsc_volume):
    ax1.text(i, v, format(int(v), ','), ha='center', va='bottom')

# Plot Sales and NPATMI as lines
ax2.plot(quarters, vsc_sales, color='lightgreen', marker='o', linewidth=2, markersize=8, label='Sales')
ax2.plot(quarters, vsc_npatmi, color='coral', marker='s', linewidth=2, markersize=8, label='NPATMI')
ax2.set_title('Quarterly Sales & NPATMI - VSC', pad=10)
ax2.set_ylabel('Billion VND')
ax2.set_xlabel('Quarter')
ax2.grid(True, linestyle='--', alpha=0.7)
# Format y-axis with comma separator
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
# Add legend
ax2.legend()

# Add data labels for both lines
for i, (s, n) in enumerate(zip(vsc_sales, vsc_npatmi)):
    ax2.text(i, s, format(int(s), ','), ha='center', va='bottom')
    ax2.text(i, n, format(int(n), ','), ha='center', va='top')

# Rotate x-axis labels for better readability
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Adjust layout to prevent overlapping
plt.tight_layout()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()

# Print the values
print("\nQuarterly Data for VSC:")
print("\nContainer Volume:")
for q, v in zip(quarters, vsc_volume):
    print(f"{q}: {format(int(v), ',')}")

print("\nSales (Billion VND):")
for q, v in zip(quarters, vsc_sales):
    print(f"{q}: {format(int(v), ',')}")

print("\nNPATMI (Billion VND):")
for q, v in zip(quarters, vsc_npatmi):
    print(f"{q}: {format(int(v), ',')}")

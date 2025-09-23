#%%
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import os

# Suppress warnings
warnings.filterwarnings('ignore')

# Set basic style parameters for better visibility
plt.rcParams['figure.figsize'] = [15, 8]
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Read the Excel file
excel_file = 'Monthly container volume tracking Jul 2025.xlsx'
df = pd.read_excel(excel_file)

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# List of companies to include
companies = ['VSC', 'GMD', 'PHP', 'SNP', 'HAH']

# Filter data for specified companies
filtered_df = df[df['Company'].isin(companies)].copy()

# Create month column in the desired format
filtered_df['YearMonth'] = filtered_df['Date'].dt.strftime('%B-%y')

# Create pivot table for stacked column chart
pivot_data = filtered_df.pivot_table(
    index='YearMonth',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).fillna(0)

# Sort months chronologically
sort_order = filtered_df['Date'].dt.to_period('M').unique()
sort_order = [d.strftime('%B-%y') for d in sort_order]
pivot_data = pivot_data.reindex(sort_order)

# Create the plot
plt.figure(figsize=(15, 8))

# Create stacked bar plot with distinct colors
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
ax = pivot_data.plot(kind='bar', stacked=True, color=colors, width=0.8)

# Customize the plot
plt.title('Monthly Container Throughput by Company', fontsize=14, pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Throughput', fontsize=12)

# Rotate x-axis labels
plt.xticks(rotation=45, ha='right')

# Add commas to y-axis values
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Customize legend
plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add grid lines behind the bars
plt.grid(True, axis='y', linestyle='--', alpha=0.7, zorder=0)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()

# Print the values
print("\nMonthly Throughput Values by Company:")
formatted_data = pivot_data.applymap(lambda x: f"{int(x):,}")
print(formatted_data.to_string())

# Save to Excel file with full path
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Container_Throughput_by_Company.xlsx')

# Save to Excel using default engine
pivot_data.to_excel(output_file, sheet_name='Monthly Throughput', index=True)

print(f"\nData has been saved to: {output_file}")
chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})

# Add data series for each company
for col in range(len(companies)):
    chart.add_series({
        'name':       ['Monthly Throughput', 0, col + 1],
        'categories': ['Monthly Throughput', 1, 0, len(pivot_data), 0],
        'values':     ['Monthly Throughput', 1, col + 1, len(pivot_data), col + 1],
    })

# Configure chart
chart.set_title({'name': 'Monthly Container Throughput by Company'})
chart.set_x_axis({'name': 'Month', 'num_font': {'rotation': -45}})
chart.set_y_axis({'name': 'Total Throughput'})
chart.set_size({'width': 1000, 'height': 600})

# Insert chart into the worksheet
worksheet.insert_chart('H2', chart)

# Save the workbook
writer.close()

print("\nExcel file has been saved to:")
print(f"'{output_file}'")
print("\nThe file includes:")
print("1. Data table with monthly throughput values")
print("2. Stacked column chart visualization")
warnings.filterwarnings('ignore')

# Set basic style parameters for better visibility
plt.rcParams['figure.figsize'] = [15, 7]
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Read the Excel file
excel_file = 'Monthly container volume tracking Jul 2025.xlsx'
df = pd.read_excel(excel_file)

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# List of companies to include
companies = ['VSC', 'GMD', 'PHP', 'SNP', 'HAH']

# Filter data for specified companies
filtered_df = df[df['Company'].isin(companies)].copy()

# Create month column in the desired format
filtered_df['YearMonth'] = filtered_df['Date'].dt.strftime('%B-%y')

# Create pivot table for stacked column chart
pivot_data = filtered_df.pivot_table(
    index='YearMonth',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).fillna(0)

# Sort months chronologically
sort_order = filtered_df['Date'].dt.to_period('M').unique()
sort_order = [d.strftime('%B-%y') for d in sort_order]
pivot_data = pivot_data.reindex(sort_order)

# Create the plot
plt.figure(figsize=(15, 8))

# Create stacked bar plot with distinct colors
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
ax = pivot_data.plot(kind='bar', stacked=True, color=colors, width=0.8)

# Customize the plot
plt.title('Monthly Container Throughput by Company', fontsize=14, pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Throughput', fontsize=12)

# Rotate x-axis labels
plt.xticks(rotation=45, ha='right')

# Add commas to y-axis values
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Customize legend
plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add grid lines behind the bars
plt.grid(True, axis='y', linestyle='--', alpha=0.7, zorder=0)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Format y-axis with comma separator for thousands
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Add grid
plt.grid(True, linestyle='--', alpha=0.7)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()

# Print the values
print("\nMonthly Throughput Values for VSC:")
# Format the output with commas for thousands
formatted_data = pivot_data.applymap(lambda x: f"{int(x):,}")
print(formatted_data.to_string())

# Read the Excel file
df = pd.read_excel('Monthly container volume tracking Jul 2025.xlsx')

# Print column names to see the structure of the data
print("Available columns in the Excel file:")
print(df.columns.tolist())
print("\nFirst few rows of data:")
print(df.head())

# Clean up column names (remove whitespace and convert to lowercase)
df.columns = df.columns.str.strip().str.lower()

# If the first row contains actual headers, use it
if df.columns.str.contains('unnamed:').any():
    df = pd.read_excel('Monthly container volume tracking Jul 2025.xlsx', header=0)
    new_headers = df.iloc[0]
    df = df[1:]
    df.columns = new_headers
    df = df.reset_index(drop=True)

# Find month and throughput columns
month_col = None
throughput_col = None
for col in df.columns:
    col_lower = str(col).lower()
    if 'month' in col_lower or 'date' in col_lower:
        month_col = col
    if 'throughput' in col_lower or 'volume' in col_lower or 'total' in col_lower:
        throughput_col = col

print(f"\nUsing columns: Month='{month_col}', Throughput='{throughput_col}'")

if month_col and throughput_col:
    # Convert date column to datetime if it's not already
    df[month_col] = pd.to_datetime(df[month_col])
    # Format date to show only month and year
    df[month_col] = df[month_col].dt.strftime('%b %Y')
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Group by month and sum throughput
    monthly_data = df.groupby(month_col)[throughput_col].sum()
    
    # Create bar plot
    monthly_data.plot(kind='bar', color='skyblue')
    
    # Customize the plot
    plt.title('Total Container Throughput by Month', pad=20)
    plt.xlabel('Month')
    plt.ylabel('Total Throughput')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    
    # Print the values
    print("\nMonthly Throughput Values:")
    print(monthly_data)




# Normalize column names for easier matching
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace('\n', ' ', regex=False)
    .str.replace('\r', ' ', regex=False)
)
print("\nNormalized columns:")
print(df.columns.tolist())

# Helper to find a best-matching column from keywords
def find_column(keywords):
    for col in df.columns:
        for kw in keywords:
            if kw in col:
                return col
    return None

month_col = find_column(['month', 'date', 'period'])
port_col = find_column(['port'])
throughput_col = find_column(['throughput', 'total throughput', 'total', 'volume', 'containers', 'container'])

print('\nDetected columns:')
print('month_col =', month_col)
print('port_col  =', port_col)
print('throughput_col =', throughput_col)

# If a month column is a full date, convert to month label
if month_col is not None:
    try:
        df[month_col] = pd.to_datetime(df[month_col], errors='coerce')
        if df[month_col].notna().any():
            df[month_col] = df[month_col].dt.to_period('M').astype(str)
    except Exception:
        pass

# Make throughput numeric
if throughput_col is not None:
    df[throughput_col] = pd.to_numeric(df[throughput_col], errors='coerce')

# Clean up any remaining code
else:
    # Create a larger figure for better visibility
    plt.figure(figsize=(15, 8))
    
    # Filter data for specific ports
    port_data = []


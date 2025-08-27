import pandas as pd
import matplotlib.pyplot as plt
import os

try:
    # Read the Excel file
    excel_file = "Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Monthly container volume")

    # Print the structure of the data to understand it better
    print("DataFrame columns:", df.columns.tolist())
    print("\nSample of the data:")
    print(df.head())
    
    # Convert Date column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])

    # Group data by Date and Company, summing the Total throughput
    monthly_data = df.groupby(['Date', 'Company'])['Total throughput'].sum().reset_index()
    
    # Pivot the data for plotting
    pivot_data = monthly_data.pivot(index='Date', columns='Company', values='Total throughput').fillna(0)
    
    # List of companies to plot (only those that exist in the data)
    companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']
    available_companies = [company for company in companies if company in pivot_data.columns]
    
    # Create the stacked bar chart
    plt.figure(figsize=(15, 8))
    pivot_data[available_companies].plot(kind='bar', stacked=True)
    
    plt.title('Monthly Container Volume by Company')
    plt.xlabel('Date')
    plt.ylabel('Total Throughput')
    plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('container_volume_chart.png', bbox_inches='tight', dpi=300)
    print("\nChart has been saved as 'container_volume_chart.png'")

except FileNotFoundError:
    print(f"Error: Could not find the Excel file '{excel_file}'")
except Exception as e:
    print(f"An error occurred: {str(e)}")

# Check which companies are actually in the data
available_companies = [company for company in companies if company in df['Company'].unique()]
print(f"Available companies in data: {available_companies}")

# Resample the data to get monthly totals
df_monthly = df.groupby(['Date', 'Company'])['Total throughput'].sum().reset_index()

# Pivot the data to get monthly volumes for each company
df_pivot = df_monthly.pivot_table(
    index='Date',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).fillna(0)

# Create the stacked column chart
plt.figure(figsize=(15, 8))

# Only plot available companies
available_companies = [c for c in companies if c in df_pivot.columns]
df_pivot[available_companies].plot(kind='bar', stacked=True)

plt.title('Monthly Container Volume by Company')
plt.xlabel('Date')
plt.ylabel('Total Throughput')
plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('container_volume_chart.png', bbox_inches='tight')
print("Chart has been saved as 'container_volume_chart.png'")

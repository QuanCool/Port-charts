<<<<<<< HEAD
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Read the Excel file
df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                   sheet_name='Monthly container volume')

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Filter for the companies we want and the date range
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']
df_filtered = df[
    (df['Company'].isin(companies)) & 
    (df['Date'] >= '2020-01-01') &  # Include from January 2020
    (df['Date'] <= '2025-07-31')    # Include up to July 2025
]

# Convert values from TEUs to Thousand TEUs by dividing by 1000
df_filtered['Total throughput'] = df_filtered['Total throughput'] / 1000

# Group by Date and Company, sum the Total throughput
df_pivot = df_filtered.pivot_table(
    index='Date',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).fillna(0)

# Create the stacked bar chart
plt.figure(figsize=(15, 8))

# Plot the stacked bars
df_pivot.plot(kind='bar', stacked=True, ax=plt.gca())

# Customize the chart
plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Container Volume (Thousand TEUs)', fontsize=12)
plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')

# Format x-axis labels to show Month-YY
ax = plt.gca()
date_labels = [d.strftime('%b-%y') for d in df_pivot.index]
ax.set_xticklabels(date_labels, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('monthly_stacked_volume.png', bbox_inches='tight', dpi=300)
plt.close()

print("Stacked column chart has been created and saved as 'monthly_stacked_volume.png'")
=======
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Read the Excel file
df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                   sheet_name='Monthly container volume')

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Filter for the companies we want and the date range
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']
df_filtered = df[
    (df['Company'].isin(companies)) & 
    (df['Date'] >= '2020-01-01') &  # Include from January 2020
    (df['Date'] <= '2025-07-31')    # Include up to July 2025
]

# Convert values from TEUs to Thousand TEUs by dividing by 1000
df_filtered['Total throughput'] = df_filtered['Total throughput'] / 1000

# Group by Date and Company, sum the Total throughput
df_pivot = df_filtered.pivot_table(
    index='Date',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).fillna(0)

# Create the stacked bar chart
plt.figure(figsize=(15, 8))

# Plot the stacked bars
df_pivot.plot(kind='bar', stacked=True, ax=plt.gca())

# Customize the chart
plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Container Volume (Thousand TEUs)', fontsize=12)
plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')

# Format x-axis labels to show Month-YY
ax = plt.gca()
date_labels = [d.strftime('%b-%y') for d in df_pivot.index]
ax.set_xticklabels(date_labels, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('monthly_stacked_volume.png', bbox_inches='tight', dpi=300)
plt.close()

print("Stacked column chart has been created and saved as 'monthly_stacked_volume.png'")
>>>>>>> d4a3375b61336330aa3631cc2ff60ac968030890

<<<<<<< HEAD
import pandas as pd
import matplotlib.pyplot as plt

try:
    # Read the Excel file
    excel_file = "Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Monthly container volume")

    # Convert Date column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])

    # List of companies to plot
    companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

    # Group data by Date and Company, summing the Total throughput
    monthly_data = df.groupby(['Date', 'Company'])['Total throughput'].sum().reset_index()
    
    # Create a pivot table for easier plotting
    pivot_data = monthly_data.pivot(
        index='Date', 
        columns='Company', 
        values='Total throughput'
    ).fillna(0)

    # Create the stacked column chart
    plt.figure(figsize=(15, 8))
    
    # Format the date index to "Month-Year" with 2-digit year
    pivot_data.index = pivot_data.index.strftime('%b-%y')

    # Plot only the specified companies that exist in the data
    available_companies = [c for c in companies if c in pivot_data.columns]
    pivot_data[available_companies].plot(kind='bar', stacked=True)

    # Customize the chart
    plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Container Volume', fontsize=12)
    plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the plot with high resolution
    plt.savefig('monthly_container_volume.png', dpi=300, bbox_inches='tight')
    print("Chart has been saved as 'monthly_container_volume.png'")

except FileNotFoundError:
    print(f"Error: Could not find the Excel file '{excel_file}'")
except Exception as e:
    print(f"An error occurred: {str(e)}")
=======
import pandas as pd
import matplotlib.pyplot as plt

try:
    # Read the Excel file
    excel_file = "Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Monthly container volume")

    # Convert Date column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])

    # List of companies to plot
    companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

    # Group data by Date and Company, summing the Total throughput
    monthly_data = df.groupby(['Date', 'Company'])['Total throughput'].sum().reset_index()
    
    # Create a pivot table for easier plotting
    pivot_data = monthly_data.pivot(
        index='Date', 
        columns='Company', 
        values='Total throughput'
    ).fillna(0)

    # Create the stacked column chart
    plt.figure(figsize=(15, 8))
    
    # Format the date index to "Month-Year" with 2-digit year
    pivot_data.index = pivot_data.index.strftime('%b-%y')

    # Plot only the specified companies that exist in the data
    available_companies = [c for c in companies if c in pivot_data.columns]
    pivot_data[available_companies].plot(kind='bar', stacked=True)

    # Customize the chart
    plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Container Volume', fontsize=12)
    plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the plot with high resolution
    plt.savefig('monthly_container_volume.png', dpi=300, bbox_inches='tight')
    print("Chart has been saved as 'monthly_container_volume.png'")

except FileNotFoundError:
    print(f"Error: Could not find the Excel file '{excel_file}'")
except Exception as e:
    print(f"An error occurred: {str(e)}")
>>>>>>> d4a3375b61336330aa3631cc2ff60ac968030890

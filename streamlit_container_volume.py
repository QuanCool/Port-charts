import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def create_container_volume_chart():
    try:
        # Set page config
        st.set_page_config(page_title="Container Volume Analysis", layout="wide")
        
        # Add title
        st.title("Container Volume Analysis")
        
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

        # Format the date index to "Month-Year" with 2-digit year
        pivot_data.index = pivot_data.index.strftime('%b-%y')

        # Create the stacked column chart
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Plot only the specified companies that exist in the data
        available_companies = [c for c in companies if c in pivot_data.columns]
        pivot_data[available_companies].plot(kind='bar', stacked=True, ax=ax)

        # Customize the chart
        plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Container Volume', fontsize=12)
        plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Display the chart in Streamlit
        st.pyplot(fig)

        # Add data table below the chart
        st.subheader("Monthly Container Volume Data")
        st.dataframe(pivot_data.style.format("{:,.0f}"))

        # Add download button for the data
        csv = pivot_data.to_csv()
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="container_volume_data.csv",
            mime="text/csv",
        )

    except FileNotFoundError:
        st.error(f"Error: Could not find the Excel file '{excel_file}'")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    create_container_volume_chart()

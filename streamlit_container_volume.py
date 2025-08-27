import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def create_container_volume_chart():
    try:
        # Set page config
        st.set_page_config(page_title="Container Volume Analysis", layout="wide")
        
        # Add title
        st.title("Container Volume Analysis")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
        
        if uploaded_file is not None:
            # Read the Excel file
            df = pd.read_excel(uploaded_file, sheet_name="Monthly container volume")
        else:
            st.info("Please upload an Excel file containing container volume data")
            st.stop()

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
        
        # Convert values to thousands and format the data
        pivot_data_thousands = pivot_data / 1000

        # Plot only the specified companies that exist in the data
        available_companies = [c for c in companies if c in pivot_data.columns]
        pivot_data_thousands[available_companies].plot(kind='bar', stacked=True, ax=ax)

        # Customize the chart
        plt.title('Monthly Container Volume by Company', fontsize=14, pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Container Volume (Thousands TEUs)', fontsize=12)
        plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Format y-axis labels to include thousand separator
        def format_thousands(x, p):
            return f'{int(x):,}'
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_thousands))

        # Add value labels on the bars
        for c in ax.containers:
            ax.bar_label(c, fmt='%.1f', label_type='center')

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Display the chart in Streamlit
        st.pyplot(fig)

        # Add data table below the chart with enhanced formatting
        st.subheader("Monthly Container Volume Data")
        
        # Format the data table with thousand separators and one decimal place
        formatted_df = pivot_data_thousands.copy()
        st.dataframe(
            formatted_df.style
            .format("{:,.1f}")
            .set_caption("Values in Thousands TEUs")
            .set_properties(**{'text-align': 'right'})
            .background_gradient(cmap='Blues', axis=None)
        )

        # Add download button for the data in thousands
        csv = pivot_data_thousands.to_csv()
        st.download_button(
            label="Download data as CSV (Values in Thousands TEUs)",
            data=csv,
            file_name="container_volume_data_thousands.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    create_container_volume_chart()

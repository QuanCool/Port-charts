import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="Container Volume Analysis",
    layout="wide"
)

# Add title
st.title("Monthly Container Volume Analysis")

# Read and process data
@st.cache_data
def load_data():
    # Read the Excel file
    df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                       sheet_name='Monthly container volume')
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df

# Load the data
try:
    df = load_data()
    
    # Filter and process data
    companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']
    df_filtered = df[
        (df['Company'].isin(companies)) & 
        (df['Date'] >= '2020-01-01') &  # Include from January 2020
        (df['Date'] <= '2025-07-31')    # Include up to July 2025
    ]

    # Convert values from TEUs to Thousand TEUs
    df_filtered['Total throughput'] = df_filtered['Total throughput'] / 1000

    # Create pivot table
    df_pivot = df_filtered.pivot_table(
        index='Date',
        columns='Company',
        values='Total throughput',
        aggfunc='sum'
    ).fillna(0)

    # Create the stacked bar chart
    fig, ax = plt.subplots(figsize=(15, 8))
    df_pivot.plot(kind='bar', stacked=True, ax=ax)

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

    # Adjust layout
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)

    # Add data analysis section
    st.subheader("Data Analysis")
    
    # Show total volume by company
    st.write("Total Container Volume by Company (Thousand TEUs)")
    total_by_company = df_filtered.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    st.bar_chart(total_by_company)
    
    # Show the raw data with filters
    st.subheader("Raw Data")
    
    # Add company filter
    selected_companies = st.multiselect(
        "Select Companies",
        companies,
        default=companies
    )
    
    # Add date range filter
    date_range = st.date_input(
        "Select Date Range",
        value=(df_filtered['Date'].min(), df_filtered['Date'].max()),
        min_value=df_filtered['Date'].min().to_pydatetime(),
        max_value=df_filtered['Date'].max().to_pydatetime()
    )
    
    # Filter data based on selection
    filtered_data = df_filtered[
        (df_filtered['Company'].isin(selected_companies)) &
        (df_filtered['Date'].dt.date >= date_range[0]) &
        (df_filtered['Date'].dt.date <= date_range[1])
    ]
    
    # Show filtered data
    st.dataframe(
        filtered_data.sort_values(['Date', 'Company'])[['Date', 'Company', 'Total throughput']]
    )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    
# Add footer
st.markdown("---")
st.markdown("Data source: Monthly container volume report")

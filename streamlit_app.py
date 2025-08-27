import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(page_title="Port Performance Dashboard", layout="wide", initial_sidebar_state="expanded")

# Function to load monthly container volume data
@st.cache_data
def load_monthly_data():
    file_name = 'Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx'
    df = pd.read_excel(file_name, sheet_name=0)
    
    # Convert Date to datetime if it isn't already
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Group by Date and Company, sum the Total throughput
    df_grouped = df.groupby(['Date', 'Company'])['Total throughput'].sum().reset_index()
    
    # Pivot the data to get companies as columns
    df_pivot = df_grouped.pivot(index='Date', columns='Company', values='Total throughput').reset_index()
    
    # Sort by date
    df_pivot = df_pivot.sort_values('Date')
    
    # Keep the original Date column and add formatted Month column
    df_pivot['Month'] = df_pivot['Date'].dt.strftime('%Y-%m')
    
    return df_pivot

# Add title
st.title("Port Operations Dashboard")

# Load both datasets
@st.cache_data
def load_quarterly_data():
    excel_file = 'Sales NPATMI quarter.xlsx'
    return pd.read_excel(excel_file, sheet_name='Sales')

# Load the data
monthly_df = load_monthly_data()
quarterly_df = load_quarterly_data()

# Create tabs for different views
tab1, tab2 = st.tabs(["Monthly Container Volume", "Quarterly Performance"])

with tab1:
    st.subheader("Monthly Container Volume by Company")
    
    try:
        # Prepare data for stacked column chart
        companies = ['PHP', 'VSC', 'CDN', 'GMD', 'SNP']
        available_companies = [c for c in companies if c in monthly_df.columns]
        
        if not available_companies:
            st.error("No company data found. Available columns: " + ", ".join(monthly_df.columns))
            st.write(monthly_df.head())
            
        # Create figure for stacked column chart
        fig_monthly = plt.figure(figsize=(15, 8))
        ax = fig_monthly.add_subplot(111)
        
        # Create x-axis positions
        x = np.arange(len(monthly_df))
        width = 0.8  # Width of the bars
        
        # Plot stacked columns
        bottom = np.zeros(len(monthly_df))
        for company in available_companies:
            values = monthly_df[company].fillna(0).values  # Replace NaN with 0
            ax.bar(x, values, width, bottom=bottom, label=company)
            bottom += values
            
        # Set x-axis labels using the actual dates
        plt.xticks(x, monthly_df['Month'], rotation=45, ha='right')
        
        # Add gridlines for better readability
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(bottom=0.2)
        
        # Customize the plot
        plt.title('Monthly Container Volume by Company', pad=20)
        plt.xlabel('Month')
        plt.ylabel('Container Volume')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(title='Companies', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Format y-axis with comma separator
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig_monthly)
        
        # Show the data table
        st.subheader("Raw Data")
        display_columns = ['Month'] + available_companies
        st.dataframe(monthly_df[display_columns])
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        st.write("DataFrame shape:", monthly_df.shape)
        st.write("DataFrame head:", monthly_df.head())
        st.write("Available columns:", monthly_df.columns.tolist())
    
    # Customize the plot
    plt.title('Monthly Container Volume by Company', pad=20)
    plt.xlabel('Month')
    plt.ylabel('Container Volume')
    plt.xticks(rotation=45)
    plt.legend(title='Companies')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format y-axis with comma separator
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Adjust layout
    plt.tight_layout()
    
    # Display the plot
    st.pyplot(fig_monthly)
    
    # Show the data table
    st.subheader("Raw Data")
    st.dataframe(monthly_df[['Month'] + companies])

with tab2:
    st.subheader("VSC Quarterly Performance")
    
    # Extract quarterly data
    quarters = quarterly_df['Sales']
    vsc_sales = quarterly_df['VSC']
    vsc_volume = quarterly_df['VSC.1']
    vsc_npatmi = quarterly_df['VSC.2']

    # Create two columns for the charts
    col1, col2 = st.columns(2)

with col1:
    # Container Volume Bar Chart
    st.subheader("Quarterly Container Volume - VSC")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(quarters, vsc_volume, color='skyblue')
    ax1.set_title('Container Volume')
    ax1.set_ylabel('Volume')
    ax1.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    
    # Format y-axis with comma separator
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Add data labels
    for i, v in enumerate(vsc_volume):
        ax1.text(i, v, format(int(v), ','), ha='center', va='bottom')
    
    st.pyplot(fig1)

with col2:
    # Sales & NPATMI Line Chart
    st.subheader("Quarterly Sales & NPATMI - VSC")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(quarters, vsc_sales, marker='o', color='lightgreen', label='Sales', linewidth=2)
    ax2.plot(quarters, vsc_npatmi, marker='s', color='coral', label='NPATMI', linewidth=2)
    ax2.set_title('Sales & NPATMI')
    ax2.set_ylabel('Billion VND')
    ax2.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    
    # Format y-axis with comma separator
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Add data labels
    for i, (s, n) in enumerate(zip(vsc_sales, vsc_npatmi)):
        ax2.text(i, s, format(int(s), ','), ha='center', va='bottom')
        ax2.text(i, n, format(int(n), ','), ha='center', va='top')
    
    ax2.legend()
    st.pyplot(fig2)

# Add raw data display
st.subheader("Raw Data")
raw_data = pd.DataFrame({
    'Quarter': quarters,
    'Container Volume': vsc_volume,
    'Sales': vsc_sales,
    'NPATMI': vsc_npatmi
})
st.dataframe(raw_data)

import streamlit as st
import pandas as pd
import altair as alt
import math

# Set page configuration
st.set_page_config(
    page_title="Container Volume Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Force light theme
st.markdown("""
    <script>
        var elements = window.parent.document.getElementsByClassName('stApp');
        elements[0].classList.add('light');
        elements[0].classList.remove('dark');
    </script>
    """, unsafe_allow_html=True)

# Custom CSS to style the app
st.markdown("""
    <style>
        /* Main title styling */
        .stTitle {
            color: #00513E !important;
            font-weight: 600 !important;
        }
        
        /* Subheader styling */
        .stSubheader {
            color: #00513E !important;
            font-weight: 500 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #FFFFFF;
        }
        
        /* Widget labels */
        .css-81oif8 {
            color: #000000 !important;
        }
        
        /* Ensure light theme colors */
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        /* DataFrame styling */
        .dataframe {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E5E5 !important;
        }
        
        /* Metric styling */
        .css-1xarl3l {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E5E5 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Add title
st.title("Monthly Container Volume Analysis")

# Data processing functions
@st.cache_data
def load_data():
    try:
        # Read the Excel file using relative path
        df = pd.read_excel(
            'Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
            sheet_name='Monthly container volume',
            engine='openpyxl'
        )
        
        # Convert and clean the Date column
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
        
        # Normalize dates to first of each month
        df['Date'] = df['Date'].dt.to_period('M').dt.to_timestamp()  # Convert to month start
        
        # Ensure data types are correct
        df['Total throughput'] = pd.to_numeric(df['Total throughput'], errors='coerce')
        df['Company'] = df['Company'].astype(str)
        
        # Check if the data is empty
        if df.empty:
            st.error("No data found in the Excel file.")
            return pd.DataFrame()
            
        # Basic data validation
        required_columns = ['Date', 'Company', 'Total throughput']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required columns. Expected: {required_columns}")
            return pd.DataFrame()
        
        # Ensure numeric type for Total throughput
        df['Total throughput'] = pd.to_numeric(df['Total throughput'], errors='coerce')
        
        # Drop any rows with NaN values
        df = df.dropna()
        
        # Create a complete date range with all months
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        date_range = pd.date_range(
            start=min_date,
            end=max_date,
            freq='MS'  # Month Start
        )
        
        # Get unique companies
        companies = df['Company'].unique()
        
        # Create all possible combinations of dates and companies
        dates_companies = [(date, company) for date in date_range for company in companies]
        df_complete = pd.DataFrame(dates_companies, columns=['Date', 'Company'])
        
        # Merge with actual data
        df = pd.merge(
            df_complete,
            df,
            on=['Date', 'Company'],
            how='left'
        ).fillna(0)
        
        # Sort by date and company
        df = df.sort_values(['Date', 'Company'])
        
        # Debug information
        st.sidebar.write("Data range:", 
                        f"From: {df['Date'].min().strftime('%Y-%m')}", 
                        f"To: {df['Date'].max().strftime('%Y-%m')}")
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the Excel file is in the same directory as the script.")
        raise e

def calculate_growth_rates(df_pivot, period='Monthly'):
    """Calculate year-on-year and period-on-period growth rates for all dates"""
    try:
        # Ensure index is datetime type
        if not isinstance(df_pivot.index, pd.DatetimeIndex):
            df_pivot.index = pd.to_datetime(df_pivot.index)
        
        # Ensure index is sorted
        df_pivot = df_pivot.sort_index()
        
        # Calculate total volume
        total_volume = df_pivot.sum(axis=1)
        
        # Calculate YoY growth without reindexing to preserve actual data points
        # First create shifted series for previous year using the original data
        total_volume_shift = total_volume.shift(12)
        
        # Calculate YoY growth only where we have actual data
        yoy_growth = ((total_volume - total_volume_shift) / total_volume_shift * 100)
        
        # Calculate period-on-period growth based on selected period
        if period == 'Monthly':
            # Month-on-Month growth
            pop_growth = total_volume.pct_change(periods=1) * 100
        elif period == 'Quarterly':
            # Quarter-on-Quarter growth
            pop_growth = total_volume.groupby([total_volume.index.year, total_volume.index.quarter]).sum()
            pop_growth = pop_growth.pct_change() * 100
            # Reindex back to monthly dates
            pop_growth = pop_growth.reindex(total_volume.index, method='ffill')
        elif period == 'Semi-annually':
            # Half-on-Half growth
            semester = (total_volume.index.month - 1) // 6
            pop_growth = total_volume.groupby([total_volume.index.year, semester]).sum()
            pop_growth = pop_growth.pct_change() * 100
            # Reindex back to monthly dates
            pop_growth = pop_growth.reindex(total_volume.index, method='ffill')
        else:  # Year-to-date
            # YTD growth
            ytd_mask = total_volume.index.month <= total_volume.index.max().month
            pop_growth = total_volume[ytd_mask].groupby(total_volume[ytd_mask].index.year).sum()
            pop_growth = pop_growth.pct_change() * 100
            # Reindex back to monthly dates
            pop_growth = pop_growth.reindex(total_volume.index, method='ffill')
        
    except Exception as e:
        st.warning(f"Unable to calculate some growth rates due to insufficient data: {str(e)}")
        # Return empty series with same index if calculation fails
        yoy_growth = pd.Series(index=total_volume.index)
        pop_growth = pd.Series(index=total_volume.index)
    
    return yoy_growth, pop_growth

def aggregate_data(df, period='Monthly'):
    """Aggregate data based on selected time period"""
    if period == 'Monthly':
        return df
    elif period == 'Quarterly':
        df['Period'] = df['Date'].dt.to_period('Q')
        grouped = df.groupby(['Period', 'Company'])['Total throughput'].sum().reset_index()
        grouped['Date'] = grouped['Period'].astype(str).map(lambda x: pd.Period(x).to_timestamp())
        return grouped.drop('Period', axis=1)
    elif period == 'Semi-annually':
        # Create a semester indicator (1 or 2)
        df = df.copy()
        df['Semester'] = ((df['Date'].dt.month - 1) // 6) + 1
        df['Year'] = df['Date'].dt.year
        
        # Group by year, semester and company
        grouped = df.groupby(['Year', 'Semester', 'Company'])['Total throughput'].sum().reset_index()
        
        # Create dates for first month of each semester (January and July)
        grouped['Month'] = grouped['Semester'].map({1: 1, 2: 7})  # January for H1, July for H2
        grouped['Day'] = 1  # First day of the month
        grouped['Date'] = pd.to_datetime(grouped[['Year', 'Month', 'Day']])
        
        return grouped.drop(['Year', 'Semester', 'Month', 'Day'], axis=1)
    elif period == 'Year-to-date':
        df = df.copy()
        current_year = df['Date'].max().year
        ytd_month = df['Date'].max().month
        
        # Create year and month columns
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        
        # Initialize empty list for YTD data
        ytd_data = []
        
        # Process each year
        for year in sorted(df['Year'].unique()):
            # For current year, use actual YTD
            if year == current_year:
                max_month = ytd_month
            else:
                # For past years, use the same month as current YTD
                max_month = ytd_month
            
            # Get data for this year up to max_month
            mask = (df['Year'] == year) & (df['Month'] <= max_month)
            year_data = df[mask].copy()
            
            if not year_data.empty:
                # Calculate YTD sum for each company
                ytd_sums = year_data.groupby('Company')['Total throughput'].sum().reset_index()
                ytd_sums['Date'] = pd.to_datetime(f"{year}-{max_month:02d}-01")
                ytd_data.append(ytd_sums)
        
        if ytd_data:
            return pd.concat(ytd_data, ignore_index=True)
        return pd.DataFrame(columns=['Date', 'Company', 'Total throughput'])

# Load the data
try:
    df = load_data()
    
    # Add time period selector to sidebar
    st.sidebar.header("Chart Controls")
    period = st.sidebar.selectbox(
        "Select Time Period",
        ["Monthly", "Quarterly", "Semi-annually", "Year-to-date"],
        index=0
    )
    
    # Add growth rate controls
    st.sidebar.header("Growth Rate Controls")
    
    # YoY growth is always shown from Jan-21 onwards, but can be toggled for clarity
    show_yoy = st.sidebar.checkbox(
        "Show Year-on-Year Growth",
        value=True,
        help="Year-on-Year growth is always available from Jan-21 onwards"
    )
    
    # Determine the appropriate period label for PoP growth
    pop_labels = {
        'Monthly': 'Month-on-Month',
        'Quarterly': 'Quarter-on-Quarter',
        'Semi-annually': 'Half-on-Half',
        'Year-to-date': 'YTD vs Previous Period'
    }
    pop_label = pop_labels.get(period, 'Period-on-Period')
    
    show_pop = st.sidebar.checkbox(
        f"Show {pop_label} Growth",
        value=True,
        help=f"Display {pop_label.lower()} growth rate"
    )
    
    # Add company selection in the sidebar
    st.sidebar.header('Filters')
    
    # Add date range selection with proper datetime handling
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    st.sidebar.subheader('Date Range')
    
    # Date range selection
    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        help="Select the start date for the chart"
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        help="Select the end date for the chart"
    )
    
    # Add company selection
    st.sidebar.subheader('Companies')
    # Get the list of companies that actually exist in the data
    available_companies = sorted(df['Company'].unique())
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        available_companies,
        default=available_companies,
        help="Choose which companies to display in the chart"
    )
    
    # Create a copy of the dataframe before filtering
    df_work = df.copy()
    
    # Convert date inputs to period for consistent comparison
    start_period = pd.Period(start_date, freq='M')
    end_period = pd.Period(end_date, freq='M')
    df_work['Period'] = df_work['Date'].dt.to_period('M')
    
    # Filter data based on selected date range and companies
    mask = (
        (df_work['Company'].isin(selected_companies)) & 
        (df_work['Period'] >= start_period) &
        (df_work['Period'] <= end_period)
    )
    df_filtered = df_work.loc[mask].drop('Period', axis=1).copy()
    
    # Show warning if no data in selected range
    if df_filtered.empty:
        st.warning("No data available for the selected date range and companies. Please adjust your selection.")
        st.stop()

    # Convert values from TEUs to Thousand TEUs
    df_filtered['Total throughput'] = df_filtered['Total throughput'] / 1000
    
    # Aggregate data based on selected period
    df_filtered = aggregate_data(df_filtered, period)

    # Create pivot table with proper handling of missing values
    df_pivot = df_filtered.pivot_table(
        index='Date',
        columns='Company',
        values='Total throughput',
        aggfunc='sum',
        fill_value=0  # Replace NaN with 0 during pivot
    )
    
    # Ensure datetime index and all months are present
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()
    
    # Reindex to ensure all months are present
    date_range = pd.date_range(
        start=df_pivot.index.min().replace(day=1),
        end=df_pivot.index.max().replace(day=1),
        freq='MS'
    )
    df_pivot = df_pivot.reindex(date_range, fill_value=0)
    
    # Calculate row sums (grand totals)
    grand_totals = df_pivot.sum(axis=1)

    # Calculate growth rates
    yoy_growth, pop_growth = calculate_growth_rates(df_pivot, period)

    # Prepare data for visualization
    # Reset index and ensure dates are in correct format
    df_pivot_reset = df_pivot.reset_index()
    
    # Normalize dates to first of month at midnight for consistency
    df_pivot_reset['Date'] = pd.to_datetime(df_pivot_reset['Date']).dt.normalize().dt.to_period('M').dt.to_timestamp()
    
    # Melt the data for visualization
    chart_data = df_pivot_reset.melt(
        id_vars=['Date'],
        value_vars=selected_companies,
        var_name='Company',
        value_name='Volume'
    ).sort_values('Date')
    
    # Create the stacked bar chart
    base_chart = alt.Chart(chart_data).encode(
        x=alt.X('yearmonth(Date):T',
                axis=alt.Axis(title='Period', labelAngle=-45, format='%b-%y'),
                timeUnit='yearmonth'),
        color=alt.Color('Company:N', 
                       scale=alt.Scale(scheme='category20'),
                       legend=alt.Legend(title="Companies"))
    )
    
    bars = base_chart.mark_bar().encode(
        y=alt.Y('Volume:Q',
                axis=alt.Axis(title='Container Volume (Thousand TEUs)'),
                stack='zero'),
        tooltip=[
            alt.Tooltip('Date:T', title='Date', format='%b-%y'),
            alt.Tooltip('Company:N', title='Company'),
            alt.Tooltip('Volume:Q', title='Volume', format=',.0f')
        ]
    )
    
    # Create chart title
    title_text = f"Container Volume by Company ({period})"
    if show_yoy or show_pop:
        growth_types = []
        if show_yoy:
            growth_types.append("YoY Growth")
        if show_pop:
            growth_types.append("PoP Growth")
        title_text += f" with {' & '.join(growth_types)}"

    # Create line charts for growth rates if enabled
    if show_yoy or show_pop:
        growth_data = pd.DataFrame({
            'Date': df_pivot.index,
            'YoY Growth': yoy_growth if show_yoy else None,
            'PoP Growth': pop_growth if show_pop else None
        }).melt(id_vars=['Date'], var_name='Type', value_name='Growth')
        
        lines = alt.Chart(growth_data).mark_line(point=True).encode(
            x='Date:T',
            y=alt.Y('Growth:Q',
                    axis=alt.Axis(title='Growth Rate (%)', titleColor='#FF4B4B'),
                    scale=alt.Scale(zero=False)),
            color=alt.Color('Type:N',
                          scale=alt.Scale(domain=['YoY Growth', 'PoP Growth'],
                                        range=['#FF4B4B', '#4B4BFF'])),
            tooltip=[
                alt.Tooltip('Date:T', title='Date', format='%b-%y'),
                alt.Tooltip('Type:N', title='Type'),
                alt.Tooltip('Growth:Q', title='Growth Rate', format='.1f')
            ]
        )
        
        # Combine bars and lines
        chart = alt.layer(bars, lines).resolve_scale(y='independent')
    else:
        chart = bars
    
    # Configure the chart
    chart = chart.configure_view(
        strokeWidth=0
    ).configure_axis(
        grid=True,
        gridColor='#E5E5E5',
        domainColor='#939598',
        tickColor='#939598'
    ).properties(
        width='container',
        height=500,
        title={
            'text': title_text,
            'color': '#00513E',
            'fontSize': 24
        }
    )
    
    # Display the chart
    st.altair_chart(chart, use_container_width=True)    # Add data analysis section
    st.subheader("Data Analysis")
    
    # Show total volume by company
    st.write("Total Container Volume by Company (Thousand TEUs)")
    total_by_company = df_filtered.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    st.bar_chart(total_by_company)
    
    # Show detailed data analysis
    st.subheader("Detailed Data Analysis")
    
    # Add tabs for different views
    tab1, tab2, tab3 = st.tabs(["Raw Data", "Monthly Summary", "Company Analysis"])
    
    with tab1:
        # Raw data view with filters
        companies_for_raw_data = st.multiselect(
            "Select Companies",
            sorted(df['Company'].unique()),
            default=selected_companies,
            key="raw_data_companies"
        )
        
        date_range = st.date_input(
            "Select Date Range",
            value=(df_filtered['Date'].min(), df_filtered['Date'].max()),
            min_value=df_filtered['Date'].min().to_pydatetime(),
            max_value=df_filtered['Date'].max().to_pydatetime(),
            key="raw_data_dates"
        )
        
        filtered_data = df_filtered[
            (df_filtered['Company'].isin(companies_for_raw_data)) &
            (df_filtered['Date'].dt.date >= date_range[0]) &
            (df_filtered['Date'].dt.date <= date_range[1])
        ]
        
        st.dataframe(
            filtered_data.sort_values(['Date', 'Company'])[['Date', 'Company', 'Total throughput']]
            .style.format({'Total throughput': '{:,.0f}'})
        )
    
    with tab2:
        # Monthly summary view
        st.write("Monthly Container Volume Summary (Thousand TEUs)")
        
        # Create monthly summary with more detailed formatting
        monthly_summary = df_filtered.pivot_table(
            index='Date',
            columns='Company',
            values='Total throughput',
            aggfunc='sum'
        ).round(0)
        
        # Add total column
        monthly_summary['Total'] = monthly_summary.sum(axis=1)
        
        # Format the index to show month-year
        monthly_summary.index = monthly_summary.index.strftime('%b-%Y')
        
        # Calculate column totals
        column_totals = monthly_summary.sum().round(0)
        column_means = monthly_summary.mean().round(0)
        
        # Add summary rows
        monthly_summary.loc['Total'] = column_totals
        monthly_summary.loc['Average'] = column_means
        
        # Create a styled dataframe
        styled_df = monthly_summary.style.format('{:,.0f}')
        
        # Highlight totals row
        styled_df = styled_df.apply(lambda x: ['background-color: #f0f2f6' if i == len(monthly_summary)-2 else 
                                             'background-color: #e6e9ef' if i == len(monthly_summary)-1 else ''
                                             for i in range(len(monthly_summary))], axis=0)
        
        # Highlight total column
        styled_df = styled_df.apply(lambda x: ['background-color: #f0f2f6' if monthly_summary.columns[i] == 'Total' 
                                             else '' for i in range(len(monthly_summary.columns))], axis=1)
        
        # Add borders
        styled_df = styled_df.set_properties(**{
            'border': '1px solid #e1e4e8',
            'padding': '5px'
        })
        
        # Display the styled table
        st.dataframe(
            styled_df,
            height=600  # Make table taller to show more rows
        )
        
        # Show summary statistics
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        # Calculate statistics for each company
        for i, company in enumerate(monthly_summary.columns[:-1]):  # Exclude 'Total' column
            with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
                st.metric(
                    f"{company}",
                    f"{column_totals[company]:,.0f}k TEUs",
                    f"Avg: {column_means[company]:,.0f}k TEUs"
                )
        
    with tab3:
        # Company analysis
        st.write("Company Performance Analysis")
        
        # Calculate company statistics
        company_stats = df_filtered.groupby('Company').agg({
            'Total throughput': ['sum', 'mean', 'min', 'max']
        }).round(0)
        
        company_stats.columns = ['Total Volume', 'Average Monthly Volume', 'Minimum Volume', 'Maximum Volume']
        company_stats = company_stats.sort_values('Total Volume', ascending=False)
        
        # Format the numbers with thousand separators
        st.dataframe(
            company_stats.style.format('{:,.0f}')
        )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    
# Add footer
st.markdown("---")
st.markdown("Data source: Monthly container volume report")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                          sheet_name='Monthly container volume')
        
        # Convert date to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the Excel file is in the same directory as the script.")
        raise e

def calculate_growth_rates(df_pivot, period='Monthly'):
    """Calculate year-on-year and period-on-period growth rates"""
    try:
        # Ensure index is datetime type
        if not isinstance(df_pivot.index, pd.DatetimeIndex):
            df_pivot.index = pd.to_datetime(df_pivot.index)
        
        # Ensure index is sorted
        df_pivot = df_pivot.sort_index()
        
        # Calculate total volume
        total_volume = df_pivot.sum(axis=1)
        
        # Calculate YoY growth
        if period == 'Monthly':
            # Calculate YoY growth rate directly using datetime index
            yoy_growth = total_volume.pct_change(periods=12) * 100
        elif period == 'Quarterly':
            # Calculate quarterly YoY growth rate
            yoy_growth = total_volume.pct_change(periods=4) * 100
        elif period == 'Semi-annually':
            # Calculate semi-annual YoY growth rate
            yoy_growth = total_volume.pct_change(periods=2) * 100
        else:  # Year-to-date
            # For YTD, compare with same month last year
            yoy_growth = total_volume.pct_change(periods=1) * 100
        
        # Calculate period-on-period growth
        pop_growth = total_volume.pct_change() * 100
        
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
    show_yoy = st.sidebar.checkbox(
        "Show Year-on-Year Growth",
        value=True,
        help="Display year-on-year growth rate"
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
    
    # Filter and process data
    all_companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']
    
    # Add company selection in the sidebar
    st.sidebar.header('Filters')
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        all_companies,
        default=all_companies,
        help="Choose which companies to display in the chart"
    )
    
    df_filtered = df[
        (df['Company'].isin(selected_companies)) & 
        (df['Date'] >= '2020-01-01') &  # Include from January 2020
        (df['Date'] <= '2025-07-31')    # Include up to July 2025
    ]

    # Convert values from TEUs to Thousand TEUs
    df_filtered['Total throughput'] = df_filtered['Total throughput'] / 1000
    
    # Aggregate data based on selected period
    df_filtered = aggregate_data(df_filtered, period)

    # Create pivot table
    df_pivot = df_filtered.pivot_table(
        index='Date',
        columns='Company',
        values='Total throughput',
        aggfunc='sum'
    ).fillna(0)
    
    # Ensure datetime index
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()

    # Calculate growth rates
    yoy_growth, pop_growth = calculate_growth_rates(df_pivot, period)

    # Create the figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Define color palette
    color_map = {
        'SNP': '#00513E',  # Dark green
        'GMD': '#00BF6F',  # Bright green
        'PHP': '#B0794E',  # Brown
        'VSC': '#939598',  # Gray
        'CDN': '#000000'   # Black
    }

    # Add bars for each company with specified colors
    for company in selected_companies:
        fig.add_trace(
            go.Bar(
                name=company,
                x=df_pivot.index,
                y=df_pivot[company],
                marker_color=color_map[company],
                hovertemplate="Date: %{x}<br>" +
                             "Volume: %{y:.1f}k TEUs<br>" +
                             f"Company: {company}<extra></extra>"
            ),
            secondary_y=False
        )
    
    # Add YoY growth rate line if enabled and we have data
    if show_yoy and not yoy_growth.isna().all():
        fig.add_trace(
            go.Scatter(
                name='YoY Growth',
                x=df_pivot.index,
                y=yoy_growth,
                line=dict(color='#FF4B4B', width=2, dash='solid'),
                hovertemplate="Date: %{x}<br>YoY Growth: %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )
    
    # Add period-on-period growth rate line if enabled and we have data
    if show_pop and not pop_growth.isna().all():
        growth_label = {
            'Monthly': 'MoM',
            'Quarterly': 'QoQ',
            'Semi-annually': 'HoH',
            'Year-to-date': 'YTD'
        }.get(period, 'Period')
        
        fig.add_trace(
            go.Scatter(
                name=f'{growth_label} Growth',
                x=df_pivot.index,
                y=pop_growth,
                line=dict(color='#4B4BFF', width=2, dash='dot'),
                hovertemplate=f"Date: %{{x}}<br>{growth_label} Growth: %{{y:.1f}}%<extra></extra>"
            ),
            secondary_y=True
        )

    # Update layout for stacked bars and growth lines
    # Create appropriate title based on period
    if period == 'Year-to-date':
        title_text = f"Container Volume and Growth Rates by Company (Year to Date as of {df['Date'].max().strftime('%B %Y')})"
    elif period == 'Semi-annually':
        title_text = "Container Volume and Growth Rates by Company (Semi-annual: H1/H2)"
    else:
        title_text = f"{period} Container Volume and Growth Rates by Company"
    
    fig.update_layout(
        barmode='stack',
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#00513E'}
        },
        xaxis_title={
            'text': "Period",
            'font': {'size': 14, 'color': '#000000'}
        },
        hovermode='x unified',
        showlegend=True,
        legend_title={
            'text': "Companies & Growth Rates",
            'font': {'color': '#00513E'}
        },
        legend={
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': '#939598',
            'borderwidth': 1
        },
        height=600,
        xaxis={
            'tickformat': '%b-%y',
            'tickangle': -45,
            'gridcolor': '#E5E5E5',
            'tickfont': {'color': '#000000'}
        },
        plot_bgcolor='white'
    )

    # Update primary y-axis
    fig.update_yaxes(
        title_text="Container Volume (Thousand TEUs)",
        gridcolor='#E5E5E5',
        gridwidth=0.5,
        tickfont={'color': '#000000'},
        secondary_y=False
    )
    
    # Only show secondary y-axis if any growth rate is enabled
    if show_yoy or show_pop:
        fig.update_yaxes(
            title_text="Growth Rate (%)",
            gridcolor='#E5E5E5',
            gridwidth=0.5,
            tickfont={'color': '#000000'},
            secondary_y=True,
            tickformat='.1f'
        )
    else:
        # Hide secondary y-axis when both growth rates are disabled
        fig.update_yaxes(
            visible=False,
            secondary_y=True
        )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Add data analysis section
    st.subheader("Data Analysis")
    
    # Show total volume by company
    st.write("Total Container Volume by Company (Thousand TEUs)")
    total_by_company = df_filtered.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    st.bar_chart(total_by_company)
    
    # Show the raw data with filters
    st.subheader("Raw Data")
    
    # Add company filter (Using the same selection as the chart)
    companies_for_raw_data = st.multiselect(
        "Select Companies",
        all_companies,
        default=selected_companies
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
        (df_filtered['Company'].isin(companies_for_raw_data)) &
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

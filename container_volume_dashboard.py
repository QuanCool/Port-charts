<<<<<<< HEAD
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta

# Set page configuration with light theme
st.set_page_config(
    page_title="Container Volume Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme using CSS and JavaScript
st.markdown("""
    <script>
        // Force light theme
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {
            stApp.classList.add('light-theme');
            stApp.classList.remove('dark-theme');
        }
        
        // Set theme in localStorage
        window.parent.localStorage.setItem('streamlit-theme', 'light');
    </script>
    
    <style>
        /* Force light theme styles */
        .stApp {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #F0F2F6 !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #FFFFFF !important;
        }
        
        /* Text elements */
        .stMarkdown, .stText {
            color: #262730 !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #262730 !important;
        }
        
        /* Selectbox and input widgets */
        .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            border: 1px solid #E0E0E0 !important;
        }
        
        /* Multiselect */
        .stMultiSelect > div > div {
            background-color: #FFFFFF !important;
        }
        
        /* Charts background */
        .vega-embed {
            background-color: #FFFFFF !important;
        }
        
        /* Data tables */
        .dataframe {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Additional custom CSS for enhanced light theme styling
st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            font-size: 2.5rem;
            color: #2D4A22 !important;
            text-align: center;
            margin-bottom: 2rem;
            background-color: #FFFFFF;
        }
        
        /* Metric containers */
        .metric-container {
            background-color: #F8F9FA !important;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 1px solid #E9ECEF;
        }
        
        /* Widget labels */
        .stSelectbox > label, .stMultiselect > label, .stCheckbox > label {
            font-weight: bold !important;
            color: #2D4A22 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">Monthly Container Volume Dashboard</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the Excel data"""
    try:
        # Read the Excel file
        df = pd.read_excel(
            'data/Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
            sheet_name='Monthly container volume'
        )
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Ensure numeric values for Total throughput
        df['Total throughput'] = pd.to_numeric(df['Total throughput'], errors='coerce')
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('Date')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def format_date_label(date, format_type='short'):
    """Format date labels with 2-digit years"""
    if format_type == 'short':
        return date.strftime('%b-%y')  # Jan-20
    elif format_type == 'quarter':
        quarter = f"Q{((date.month - 1) // 3) + 1}"
        return f"{quarter}-{date.strftime('%y')}"  # Q1-20
    elif format_type == 'semester':
        semester = "H1" if date.month <= 6 else "H2"
        return f"{semester}-{date.strftime('%y')}"  # H1-20
    elif format_type == 'ytd':
        return f"YTD-{date.strftime('%y')}"  # YTD-20

def aggregate_data(df, period='Monthly'):
    """Aggregate data based on selected time period and combine all ports under each company"""
    df_agg = df.copy()
    
    if period == 'Monthly':
        df_agg['Period'] = df_agg['Date']
        df_agg['Period_Label'] = df_agg['Date'].apply(lambda x: format_date_label(x, 'short'))
        # Group by Period, Period_Label, and Company to combine all ports
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Quarterly':
        df_agg['Period'] = df_agg['Date'].dt.to_period('Q').dt.to_timestamp()
        df_agg['Period_Label'] = df_agg['Period'].apply(lambda x: format_date_label(x, 'quarter'))
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Semi-annually':
        df_agg['Semester'] = df_agg['Date'].apply(lambda x: 1 if x.month <= 6 else 2)
        df_agg['Year'] = df_agg['Date'].dt.year
        df_agg['Period'] = df_agg.apply(lambda row: pd.Timestamp(f"{row['Year']}-{1 if row['Semester'] == 1 else 7}-01"), axis=1)
        df_agg['Period_Label'] = df_agg['Period'].apply(lambda x: format_date_label(x, 'semester'))
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Year-to-date':
        current_year = df_agg['Date'].max().year
        current_month = df_agg['Date'].max().month
        
        ytd_data = []
        for year in df_agg['Date'].dt.year.unique():
            year_data = df_agg[df_agg['Date'].dt.year == year].copy()
            if year == current_year:
                year_data = year_data[year_data['Date'].dt.month <= current_month]
            else:
                year_data = year_data[year_data['Date'].dt.month <= current_month]
            
            if not year_data.empty:
                ytd_sum = year_data.groupby('Company')['Total throughput'].sum().reset_index()
                ytd_sum['Period'] = pd.Timestamp(f"{year}-12-31")
                ytd_sum['Period_Label'] = f"YTD-{str(year)[2:]}"
                ytd_data.append(ytd_sum)
        
        if ytd_data:
            df_agg = pd.concat(ytd_data, ignore_index=True)
    
    return df_agg

def calculate_growth_rates(df, period='Monthly'):
    """Calculate YoY and PoP growth rates"""
    df_pivot = df.pivot_table(
        index='Period', 
        columns='Company', 
        values='Total throughput', 
        fill_value=0
    )
    
    # Calculate total volume
    total_volume = df_pivot.sum(axis=1).reset_index()
    total_volume.columns = ['Period', 'Total_Volume']
    
    # Calculate YoY growth
    if period == 'Monthly':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=12) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Month-on-Month"
    elif period == 'Quarterly':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=4) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Quarter-on-Quarter"
    elif period == 'Semi-annually':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=2) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Half-on-Half"
    else:  # YTD
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Year-on-Year"
    
    return total_volume, pop_label

def create_stacked_chart(df_melted, selected_companies, period_labels):
    """Create interactive stacked column chart with grand totals"""
    
    # Filter data for selected companies
    df_filtered = df_melted[df_melted['Company'].isin(selected_companies)]
    
    # Group by Period, Period_Label, and Company to combine all ports under each company
    df_combined = df_filtered.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
    
    # Calculate grand totals for each period
    grand_totals = df_combined.groupby(['Period', 'Period_Label'])['Total throughput'].sum().reset_index()
    grand_totals['Company'] = 'Grand Total'
    
    # Identify top 5 companies by total monthly container volume
    company_totals = df_combined.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    top_5_companies = company_totals.head(5).index.tolist()
    
    # Primary color palette (from your attachment)
    primary_color_palette = [
        '#2D4A22',  # Dark green
        '#00C853',  # Bright green
        '#D4A574',  # Light brown/tan
        '#9E9E9E',  # Gray
        '#000000',  # Black
        '#FFFFFF'   # White (for border if needed)
    ]
    
    # Create color mapping for top 5 companies
    color_mapping = {}
    for i, company in enumerate(top_5_companies):
        if i < len(primary_color_palette):
            color_mapping[company] = primary_color_palette[i]
    
    # For companies not in top 5, use a default gray color
    other_companies = [comp for comp in selected_companies if comp not in top_5_companies]
    for company in other_companies:
        color_mapping[company] = '#CCCCCC'  # Light gray for others
    
    # Add color column to the data
    df_combined['Color'] = df_combined['Company'].map(color_mapping)
    
    # Create base chart
    base = alt.Chart(df_combined).add_params(
        alt.selection_interval(bind='scales')
    )
    
    # Stacked bar chart with custom colors for top 5 companies
    bars = base.mark_bar().encode(
        x=alt.X('Period_Label:O', 
                title='Time Period',
                axis=alt.Axis(labelAngle=-45),
                sort=period_labels),
        y=alt.Y('Total throughput:Q', 
                title='Container Volume (Thousand TEUs)',
                scale=alt.Scale(nice=True)),
        color=alt.Color('Company:N', 
                       title='Company',
                       scale=alt.Scale(
                           domain=list(color_mapping.keys()),
                           range=list(color_mapping.values())
                       )),
        tooltip=['Period_Label:O', 'Company:N', 
                alt.Tooltip('Total throughput:Q', format='.1f', title='Volume (K TEUs)')]
    ).properties(
        width=800,
        height=400,
        title=alt.TitleParams(text="Container Volume by Company (Top 5 Highlighted)", fontSize=16, anchor='start')
    )
    
    # Add grand total labels on top of bars with rounded numbers
    grand_total_labels = alt.Chart(grand_totals).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=10,
        fontWeight='bold'
    ).encode(
        x=alt.X('Period_Label:O', sort=period_labels),
        y=alt.Y('Total throughput:Q'),
        text=alt.Text('Total throughput:Q', format='.0f')  # Changed from .1f to .0f for rounding
    )
    
    return bars + grand_total_labels

def create_growth_chart(growth_data, period_labels, show_yoy=True, show_pop=True, pop_label=""):
    """Create growth rate line chart"""
    
    # Prepare growth data for visualization
    growth_melted = []
    
    if show_yoy and 'YoY_Growth' in growth_data.columns:
        yoy_data = growth_data[['Period', 'YoY_Growth']].copy()
        yoy_data['Growth_Type'] = 'Year-on-Year'
        yoy_data['Growth_Rate'] = yoy_data['YoY_Growth']
        growth_melted.append(yoy_data[['Period', 'Growth_Type', 'Growth_Rate']])
    
    if show_pop and 'PoP_Growth' in growth_data.columns:
        pop_data = growth_data[['Period', 'PoP_Growth']].copy()
        pop_data['Growth_Type'] = pop_label
        pop_data['Growth_Rate'] = pop_data['PoP_Growth']
        growth_melted.append(pop_data[['Period', 'Growth_Type', 'Growth_Rate']])
    
    if not growth_melted:
        return alt.Chart().mark_text().encode(text=alt.value("No growth data to display"))
    
    growth_df = pd.concat(growth_melted, ignore_index=True)
    
    # Add period labels
    period_mapping = dict(zip(growth_data['Period'], period_labels))
    growth_df['Period_Label'] = growth_df['Period'].map(period_mapping)
    
    # Remove infinite and NaN values
    growth_df = growth_df.replace([np.inf, -np.inf], np.nan).dropna()
    
    if growth_df.empty:
        return alt.Chart().mark_text().encode(text=alt.value("No valid growth data to display"))
    
    # Create line chart with custom colors from the extended palette
    growth_color_palette = ['#2D4A22', '#1976D2']  # Dark green and blue from the palette
    
    line_chart = alt.Chart(growth_df).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X('Period_Label:O', 
                title='Time Period',
                axis=alt.Axis(labelAngle=-45),
                sort=period_labels),
        y=alt.Y('Growth_Rate:Q', 
                title='Growth Rate (%)',
                scale=alt.Scale(nice=True)),
        color=alt.Color('Growth_Type:N', 
                       title='Growth Type',
                       scale=alt.Scale(range=growth_color_palette)),
        tooltip=['Period_Label:O', 'Growth_Type:N', 
                alt.Tooltip('Growth_Rate:Q', format='.2f', title='Growth Rate (%)')]
    ).properties(
        width=800,
        height=300,
        title=alt.TitleParams(text="Growth Rates", fontSize=16, anchor='start')
    )
    
    # Add zero line
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='red',
        strokeDash=[3, 3]
    ).encode(y='y:Q')
    
    return line_chart + zero_line

# Main application
def main():
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please check the Excel file.")
        return
    
    # Sidebar controls
    st.sidebar.header("📊 Chart Controls")
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        ["Monthly", "Quarterly", "Semi-annually", "Year-to-date"],
        index=0
    )
    
    # Company selection
    available_companies = sorted(df['Company'].unique())
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        available_companies,
        default=available_companies
    )
    
    if not selected_companies:
        st.warning("Please select at least one company.")
        return
    
    # Growth rate controls
    st.sidebar.header("📈 Growth Rate Controls")
    show_yoy = st.sidebar.checkbox("Show Year-on-Year Growth", value=True)
    show_pop = st.sidebar.checkbox("Show Period-on-Period Growth", value=True)
    
    # Show top 5 companies info
    st.sidebar.header("🏆 Top 5 Companies")
    st.sidebar.write("*By total monthly volume*")
    company_totals = df.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    top_5_companies = company_totals.head(5)
    for i, (company, total) in enumerate(top_5_companies.items(), 1):
        st.sidebar.write(f"{i}. **{company}**: {total/1000:,.1f}K TEUs")
    
    # Process data
    df_agg = aggregate_data(df, period)
    
    if df_agg.empty:
        st.error("No data available for the selected period.")
        return
    
    # Convert to thousands of TEUs
    df_agg['Total throughput'] = df_agg['Total throughput'] / 1000
    
    # Filter for selected companies
    df_filtered = df_agg[df_agg['Company'].isin(selected_companies)]
    
    # Get unique period labels in chronological order
    period_labels = df_filtered.sort_values('Period')['Period_Label'].unique().tolist()
    
    # Calculate growth rates
    growth_data, pop_label = calculate_growth_rates(df_filtered, period)
    growth_data['Period_Label'] = growth_data['Period'].map(
        dict(zip(df_filtered['Period'], df_filtered['Period_Label']))
    )
    
    # Create visualizations
    st.subheader("� Data Range")
    min_date = df_filtered['Period'].min()
    max_date = df_filtered['Period'].max()
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**From:** {format_date_label(min_date, 'short')}")
    with col2:
        st.write(f"**To:** {format_date_label(max_date, 'short')}")
    
    # Display charts
    st.subheader("Container Volume Analysis")
    
    # Stacked column chart
    stacked_chart = create_stacked_chart(df_filtered, selected_companies, period_labels)
    st.altair_chart(stacked_chart, use_container_width=True)
    
    # Growth chart (only if growth options are selected)
    if show_yoy or show_pop:
        growth_chart = create_growth_chart(growth_data, period_labels, show_yoy, show_pop, pop_label)
        st.altair_chart(growth_chart, use_container_width=True)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.subheader("Aggregated Data")
        display_df = df_filtered.pivot_table(
            index='Period_Label',
            columns='Company',
            values='Total throughput',
            fill_value=0
        ).round(1)
        st.dataframe(display_df)
        
        if show_yoy or show_pop:
            st.subheader("Growth Rates Data")
            growth_display = growth_data[['Period_Label', 'Total_Volume', 'YoY_Growth', 'PoP_Growth']].copy()
            growth_display['Total_Volume'] = growth_display['Total_Volume'] / 1000  # Convert to thousands
            growth_display = growth_display.round(2)
            growth_display.columns = ['Period', 'Total Volume (K TEUs)', 'YoY Growth (%)', f'{pop_label} Growth (%)']
            st.dataframe(growth_display)

if __name__ == "__main__":
    main()
=======
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta

# Set page configuration with light theme
st.set_page_config(
    page_title="Container Volume Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme using CSS and JavaScript
st.markdown("""
    <script>
        // Force light theme
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {
            stApp.classList.add('light-theme');
            stApp.classList.remove('dark-theme');
        }
        
        // Set theme in localStorage
        window.parent.localStorage.setItem('streamlit-theme', 'light');
    </script>
    
    <style>
        /* Force light theme styles */
        .stApp {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #F0F2F6 !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #FFFFFF !important;
        }
        
        /* Text elements */
        .stMarkdown, .stText {
            color: #262730 !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #262730 !important;
        }
        
        /* Selectbox and input widgets */
        .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            border: 1px solid #E0E0E0 !important;
        }
        
        /* Multiselect */
        .stMultiSelect > div > div {
            background-color: #FFFFFF !important;
        }
        
        /* Charts background */
        .vega-embed {
            background-color: #FFFFFF !important;
        }
        
        /* Data tables */
        .dataframe {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Additional custom CSS for enhanced light theme styling
st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            font-size: 2.5rem;
            color: #2D4A22 !important;
            text-align: center;
            margin-bottom: 2rem;
            background-color: #FFFFFF;
        }
        
        /* Metric containers */
        .metric-container {
            background-color: #F8F9FA !important;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 1px solid #E9ECEF;
        }
        
        /* Widget labels */
        .stSelectbox > label, .stMultiselect > label, .stCheckbox > label {
            font-weight: bold !important;
            color: #2D4A22 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">Monthly Container Volume Dashboard</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the Excel data"""
    try:
        # Read the Excel file
        df = pd.read_excel(
            'data/Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
            sheet_name='Monthly container volume'
        )
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Ensure numeric values for Total throughput
        df['Total throughput'] = pd.to_numeric(df['Total throughput'], errors='coerce')
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('Date')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def format_date_label(date, format_type='short'):
    """Format date labels with 2-digit years"""
    if format_type == 'short':
        return date.strftime('%b-%y')  # Jan-20
    elif format_type == 'quarter':
        quarter = f"Q{((date.month - 1) // 3) + 1}"
        return f"{quarter}-{date.strftime('%y')}"  # Q1-20
    elif format_type == 'semester':
        semester = "H1" if date.month <= 6 else "H2"
        return f"{semester}-{date.strftime('%y')}"  # H1-20
    elif format_type == 'ytd':
        return f"YTD-{date.strftime('%y')}"  # YTD-20

def aggregate_data(df, period='Monthly'):
    """Aggregate data based on selected time period and combine all ports under each company"""
    df_agg = df.copy()
    
    if period == 'Monthly':
        df_agg['Period'] = df_agg['Date']
        df_agg['Period_Label'] = df_agg['Date'].apply(lambda x: format_date_label(x, 'short'))
        # Group by Period, Period_Label, and Company to combine all ports
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Quarterly':
        df_agg['Period'] = df_agg['Date'].dt.to_period('Q').dt.to_timestamp()
        df_agg['Period_Label'] = df_agg['Period'].apply(lambda x: format_date_label(x, 'quarter'))
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Semi-annually':
        df_agg['Semester'] = df_agg['Date'].apply(lambda x: 1 if x.month <= 6 else 2)
        df_agg['Year'] = df_agg['Date'].dt.year
        df_agg['Period'] = df_agg.apply(lambda row: pd.Timestamp(f"{row['Year']}-{1 if row['Semester'] == 1 else 7}-01"), axis=1)
        df_agg['Period_Label'] = df_agg['Period'].apply(lambda x: format_date_label(x, 'semester'))
        df_agg = df_agg.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
        
    elif period == 'Year-to-date':
        current_year = df_agg['Date'].max().year
        current_month = df_agg['Date'].max().month
        
        ytd_data = []
        for year in df_agg['Date'].dt.year.unique():
            year_data = df_agg[df_agg['Date'].dt.year == year].copy()
            if year == current_year:
                year_data = year_data[year_data['Date'].dt.month <= current_month]
            else:
                year_data = year_data[year_data['Date'].dt.month <= current_month]
            
            if not year_data.empty:
                ytd_sum = year_data.groupby('Company')['Total throughput'].sum().reset_index()
                ytd_sum['Period'] = pd.Timestamp(f"{year}-12-31")
                ytd_sum['Period_Label'] = f"YTD-{str(year)[2:]}"
                ytd_data.append(ytd_sum)
        
        if ytd_data:
            df_agg = pd.concat(ytd_data, ignore_index=True)
    
    return df_agg

def calculate_growth_rates(df, period='Monthly'):
    """Calculate YoY and PoP growth rates"""
    df_pivot = df.pivot_table(
        index='Period', 
        columns='Company', 
        values='Total throughput', 
        fill_value=0
    )
    
    # Calculate total volume
    total_volume = df_pivot.sum(axis=1).reset_index()
    total_volume.columns = ['Period', 'Total_Volume']
    
    # Calculate YoY growth
    if period == 'Monthly':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=12) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Month-on-Month"
    elif period == 'Quarterly':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=4) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Quarter-on-Quarter"
    elif period == 'Semi-annually':
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=2) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Half-on-Half"
    else:  # YTD
        total_volume['YoY_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        total_volume['PoP_Growth'] = total_volume['Total_Volume'].pct_change(periods=1) * 100
        pop_label = "Year-on-Year"
    
    return total_volume, pop_label

def create_stacked_chart(df_melted, selected_companies, period_labels):
    """Create interactive stacked column chart with grand totals"""
    
    # Filter data for selected companies
    df_filtered = df_melted[df_melted['Company'].isin(selected_companies)]
    
    # Group by Period, Period_Label, and Company to combine all ports under each company
    df_combined = df_filtered.groupby(['Period', 'Period_Label', 'Company'])['Total throughput'].sum().reset_index()
    
    # Calculate grand totals for each period
    grand_totals = df_combined.groupby(['Period', 'Period_Label'])['Total throughput'].sum().reset_index()
    grand_totals['Company'] = 'Grand Total'
    
    # Identify top 5 companies by total monthly container volume
    company_totals = df_combined.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    top_5_companies = company_totals.head(5).index.tolist()
    
    # Primary color palette (from your attachment)
    primary_color_palette = [
        '#2D4A22',  # Dark green
        '#00C853',  # Bright green
        '#D4A574',  # Light brown/tan
        '#9E9E9E',  # Gray
        '#000000',  # Black
        '#FFFFFF'   # White (for border if needed)
    ]
    
    # Create color mapping for top 5 companies
    color_mapping = {}
    for i, company in enumerate(top_5_companies):
        if i < len(primary_color_palette):
            color_mapping[company] = primary_color_palette[i]
    
    # For companies not in top 5, use a default gray color
    other_companies = [comp for comp in selected_companies if comp not in top_5_companies]
    for company in other_companies:
        color_mapping[company] = '#CCCCCC'  # Light gray for others
    
    # Add color column to the data
    df_combined['Color'] = df_combined['Company'].map(color_mapping)
    
    # Create base chart
    base = alt.Chart(df_combined).add_params(
        alt.selection_interval(bind='scales')
    )
    
    # Stacked bar chart with custom colors for top 5 companies
    bars = base.mark_bar().encode(
        x=alt.X('Period_Label:O', 
                title='Time Period',
                axis=alt.Axis(labelAngle=-45),
                sort=period_labels),
        y=alt.Y('Total throughput:Q', 
                title='Container Volume (Thousand TEUs)',
                scale=alt.Scale(nice=True)),
        color=alt.Color('Company:N', 
                       title='Company',
                       scale=alt.Scale(
                           domain=list(color_mapping.keys()),
                           range=list(color_mapping.values())
                       )),
        tooltip=['Period_Label:O', 'Company:N', 
                alt.Tooltip('Total throughput:Q', format='.1f', title='Volume (K TEUs)')]
    ).properties(
        width=800,
        height=400,
        title=alt.TitleParams(text="Container Volume by Company (Top 5 Highlighted)", fontSize=16, anchor='start')
    )
    
    # Add grand total labels on top of bars with rounded numbers
    grand_total_labels = alt.Chart(grand_totals).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=10,
        fontWeight='bold'
    ).encode(
        x=alt.X('Period_Label:O', sort=period_labels),
        y=alt.Y('Total throughput:Q'),
        text=alt.Text('Total throughput:Q', format='.0f')  # Changed from .1f to .0f for rounding
    )
    
    return bars + grand_total_labels

def create_growth_chart(growth_data, period_labels, show_yoy=True, show_pop=True, pop_label=""):
    """Create growth rate line chart"""
    
    # Prepare growth data for visualization
    growth_melted = []
    
    if show_yoy and 'YoY_Growth' in growth_data.columns:
        yoy_data = growth_data[['Period', 'YoY_Growth']].copy()
        yoy_data['Growth_Type'] = 'Year-on-Year'
        yoy_data['Growth_Rate'] = yoy_data['YoY_Growth']
        growth_melted.append(yoy_data[['Period', 'Growth_Type', 'Growth_Rate']])
    
    if show_pop and 'PoP_Growth' in growth_data.columns:
        pop_data = growth_data[['Period', 'PoP_Growth']].copy()
        pop_data['Growth_Type'] = pop_label
        pop_data['Growth_Rate'] = pop_data['PoP_Growth']
        growth_melted.append(pop_data[['Period', 'Growth_Type', 'Growth_Rate']])
    
    if not growth_melted:
        return alt.Chart().mark_text().encode(text=alt.value("No growth data to display"))
    
    growth_df = pd.concat(growth_melted, ignore_index=True)
    
    # Add period labels
    period_mapping = dict(zip(growth_data['Period'], period_labels))
    growth_df['Period_Label'] = growth_df['Period'].map(period_mapping)
    
    # Remove infinite and NaN values
    growth_df = growth_df.replace([np.inf, -np.inf], np.nan).dropna()
    
    if growth_df.empty:
        return alt.Chart().mark_text().encode(text=alt.value("No valid growth data to display"))
    
    # Create line chart with custom colors from the extended palette
    growth_color_palette = ['#2D4A22', '#1976D2']  # Dark green and blue from the palette
    
    line_chart = alt.Chart(growth_df).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X('Period_Label:O', 
                title='Time Period',
                axis=alt.Axis(labelAngle=-45),
                sort=period_labels),
        y=alt.Y('Growth_Rate:Q', 
                title='Growth Rate (%)',
                scale=alt.Scale(nice=True)),
        color=alt.Color('Growth_Type:N', 
                       title='Growth Type',
                       scale=alt.Scale(range=growth_color_palette)),
        tooltip=['Period_Label:O', 'Growth_Type:N', 
                alt.Tooltip('Growth_Rate:Q', format='.2f', title='Growth Rate (%)')]
    ).properties(
        width=800,
        height=300,
        title=alt.TitleParams(text="Growth Rates", fontSize=16, anchor='start')
    )
    
    # Add zero line
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='red',
        strokeDash=[3, 3]
    ).encode(y='y:Q')
    
    return line_chart + zero_line

# Main application
def main():
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please check the Excel file.")
        return
    
    # Sidebar controls
    st.sidebar.header("📊 Chart Controls")
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        ["Monthly", "Quarterly", "Semi-annually", "Year-to-date"],
        index=0
    )
    
    # Company selection
    available_companies = sorted(df['Company'].unique())
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        available_companies,
        default=available_companies
    )
    
    if not selected_companies:
        st.warning("Please select at least one company.")
        return
    
    # Growth rate controls
    st.sidebar.header("📈 Growth Rate Controls")
    show_yoy = st.sidebar.checkbox("Show Year-on-Year Growth", value=True)
    show_pop = st.sidebar.checkbox("Show Period-on-Period Growth", value=True)
    
    # Show top 5 companies info
    st.sidebar.header("🏆 Top 5 Companies")
    st.sidebar.write("*By total monthly volume*")
    company_totals = df.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    top_5_companies = company_totals.head(5)
    for i, (company, total) in enumerate(top_5_companies.items(), 1):
        st.sidebar.write(f"{i}. **{company}**: {total/1000:,.1f}K TEUs")
    
    # Process data
    df_agg = aggregate_data(df, period)
    
    if df_agg.empty:
        st.error("No data available for the selected period.")
        return
    
    # Convert to thousands of TEUs
    df_agg['Total throughput'] = df_agg['Total throughput'] / 1000
    
    # Filter for selected companies
    df_filtered = df_agg[df_agg['Company'].isin(selected_companies)]
    
    # Get unique period labels in chronological order
    period_labels = df_filtered.sort_values('Period')['Period_Label'].unique().tolist()
    
    # Calculate growth rates
    growth_data, pop_label = calculate_growth_rates(df_filtered, period)
    growth_data['Period_Label'] = growth_data['Period'].map(
        dict(zip(df_filtered['Period'], df_filtered['Period_Label']))
    )
    
    # Create visualizations
    st.subheader("� Data Range")
    min_date = df_filtered['Period'].min()
    max_date = df_filtered['Period'].max()
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**From:** {format_date_label(min_date, 'short')}")
    with col2:
        st.write(f"**To:** {format_date_label(max_date, 'short')}")
    
    # Display charts
    st.subheader("Container Volume Analysis")
    
    # Stacked column chart
    stacked_chart = create_stacked_chart(df_filtered, selected_companies, period_labels)
    st.altair_chart(stacked_chart, use_container_width=True)
    
    # Growth chart (only if growth options are selected)
    if show_yoy or show_pop:
        growth_chart = create_growth_chart(growth_data, period_labels, show_yoy, show_pop, pop_label)
        st.altair_chart(growth_chart, use_container_width=True)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.subheader("Aggregated Data")
        display_df = df_filtered.pivot_table(
            index='Period_Label',
            columns='Company',
            values='Total throughput',
            fill_value=0
        ).round(1)
        st.dataframe(display_df)
        
        if show_yoy or show_pop:
            st.subheader("Growth Rates Data")
            growth_display = growth_data[['Period_Label', 'Total_Volume', 'YoY_Growth', 'PoP_Growth']].copy()
            growth_display['Total_Volume'] = growth_display['Total_Volume'] / 1000  # Convert to thousands
            growth_display = growth_display.round(2)
            growth_display.columns = ['Period', 'Total Volume (K TEUs)', 'YoY Growth (%)', f'{pop_label} Growth (%)']
            st.dataframe(growth_display)

if __name__ == "__main__":
    main()
>>>>>>> d4a3375b61336330aa3631cc2ff60ac968030890

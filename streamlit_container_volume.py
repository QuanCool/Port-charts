import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Container Volume Analysis",
    layout="wide"
)

# Custom CSS to style the app
st.markdown("""
    <style>
        .stTitle {
            color: #00513E !important;
        }
        .stSubheader {
            color: #00513E !important;
        }
        .css-1dp5vir {
            background-color: #E5E5E5 !important;
        }
        .css-1l02zno {
            background-color: #FFFFFF !important;
            border: 1px solid #939598 !important;
        }
    </style>
""", unsafe_allow_html=True)

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

    # Create the interactive stacked bar chart using Plotly
    fig = go.Figure()
    
    # Define color palette
    color_map = {
        'SNP': '#00513E',  # Dark green
        'GMD': '#00BF6F',  # Bright green
        'PHP': '#B0794E',  # Brown
        'VSC': '#939598',  # Gray
        'CDN': '#000000'   # Black
    }

    # Add bars for each company with specified colors
    for company in companies:
        fig.add_trace(
            go.Bar(
                name=company,
                x=df_pivot.index,
                y=df_pivot[company],
                marker_color=color_map[company],
                hovertemplate="Date: %{x}<br>" +
                             "Volume: %{y:.1f}k TEUs<br>" +
                             f"Company: {company}<extra></extra>"
            )
        )

    # Update layout for stacked bars
    fig.update_layout(
        barmode='stack',
        title={
            'text': 'Monthly Container Volume by Company',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#00513E'}  # Dark green title
        },
        xaxis_title={
            'text': "Date",
            'font': {'size': 14, 'color': '#000000'}
        },
        yaxis_title={
            'text': "Container Volume (Thousand TEUs)",
            'font': {'size': 14, 'color': '#000000'}
        },
        hovermode='x unified',
        showlegend=True,
        legend_title={
            'text': "Companies",
            'font': {'color': '#00513E'}
        },
        legend={
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': '#939598',  # Gray
            'borderwidth': 1
        },
        height=600,
        xaxis={
            'tickformat': '%b-%y',
            'tickangle': -45,
            'gridcolor': '#E5E5E5',
            'tickfont': {'color': '#000000'}
        },
        yaxis={
            'gridcolor': '#E5E5E5',
            'gridwidth': 0.5,
            'tickfont': {'color': '#000000'}
        },
        plot_bgcolor='white'
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

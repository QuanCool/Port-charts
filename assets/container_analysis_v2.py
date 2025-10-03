import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Monthly Container Throughput", layout="wide")
st.title("Container Throughput (Top 5 Highlighted, Timeframe Selectable)")

file_path = "Monthly container volume -  Quarterly sales and NPATMI_Aug 2025.xlsx"
sheet_name = "Monthly container volume"

# Color palette from new attachment (for top 5)
color_palette = [
    '#18443B',  # dark green
    '#13D08B',  # green
    '#B38B4A',  # brown
    '#A1A1A1',  # gray
    '#000000',  # black
    '#FFFFFF'   # white (for background)
]

def aggregate_timeframe(df, date_col, company_col, value_col, timeframe):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    if timeframe == 'Monthly':
        df['Period'] = df[date_col].dt.to_period('M').astype(str)
    elif timeframe == 'Quarterly':
        df['Period'] = df[date_col].dt.to_period('Q').astype(str)
    elif timeframe == 'Semi-Annual':
        df['Period'] = df[date_col].dt.year.astype(str) + '-H' + ((df[date_col].dt.month-1)//6+1).astype(str)
    elif timeframe == 'Annual':
        df['Period'] = df[date_col].dt.year.astype(str)
    elif timeframe == 'Year-to-Date':
        this_year = pd.Timestamp.now().year
        df = df[df[date_col].dt.year == this_year]
        df['Period'] = str(this_year) + '-YTD'
    else:
        df['Period'] = df[date_col].dt.to_period('M').astype(str)
    grouped = df.groupby(['Period', company_col], as_index=False)[value_col].sum()
    pivot_df = grouped.pivot(index='Period', columns=company_col, values=value_col).fillna(0)
    return pivot_df

def calculate_growth(series, period_lag):
    return (series - series.shift(period_lag)) / series.shift(period_lag) * 100

try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # Ensure required columns exist
    required_cols = {'Date', 'Company', 'Total throughput'}
    if not required_cols.issubset(df.columns):
        st.error(f"Missing required columns: {required_cols - set(df.columns)}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # Get unique companies from the data
    available_companies = df['Company'].dropna().unique().tolist()
    available_companies.sort()

    # Sidebar for company selection
    st.sidebar.header("Company Selection")
    selected_companies = st.sidebar.multiselect(
        "Select companies to display",
        available_companies,
        default=available_companies
    )

    # Sidebar for timeframe selection
    st.sidebar.header("Timeframe Selection")
    timeframe = st.sidebar.selectbox(
        "Select timeframe",
        ['Monthly', 'Quarterly', 'Semi-Annual', 'Annual', 'Year-to-Date'],
        index=0
    )

    # Filter data for selected companies
    filtered_df = df[df['Company'].isin(selected_companies)]

    # Group by Company (all months), sum throughput to get top 5
    total_by_company = filtered_df.groupby('Company')['Total throughput'].sum().sort_values(ascending=False)
    top5_companies = total_by_company.head(5).index.tolist()

    # Aggregate by selected timeframe (convert to thousand TEUs)
    pivot_df = aggregate_timeframe(filtered_df, 'Date', 'Company', 'Total throughput', timeframe) / 1000
    pivot_df = pivot_df.sort_index()

    # Calculate grand totals for each period (in thousand TEUs, rounded up)
    grand_totals = np.ceil(pivot_df[selected_companies].sum(axis=1))

    # Throughput chart
    fig = go.Figure()
    for i, company in enumerate(selected_companies):
        if company in pivot_df.columns:
            if company in top5_companies:
                color_idx = top5_companies.index(company) % 5
                bar_color = color_palette[color_idx]
            else:
                bar_color = color_palette[3]  # gray for non-top5
            fig.add_bar(
                name=company,
                x=pivot_df.index,
                y=pivot_df[company],
                marker_color=bar_color,
                hovertemplate=f"<b>{company}</b><br>Period: %{{x}}<br>Throughput: %{{y:,.0f}} thousand TEUs<extra></extra>"
            )
    # Add grand total text annotations on top of each stacked column
    fig.add_trace(go.Scatter(
        x=grand_totals.index,
        y=grand_totals.values,
        mode='text',
        text=[f'{int(val):,}' for val in grand_totals.values],
        textposition='top center',
        showlegend=False,
        hoverinfo='skip',
        marker=dict(color=color_palette[0])
    ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Period",
        yaxis_title="Container Throughput (thousand TEUs)",
        title=f"Container Throughput (Top 5 Highlighted, {timeframe})",
        hovermode="closest",
        plot_bgcolor=color_palette[5],
        paper_bgcolor=color_palette[5],
        font=dict(color=color_palette[0])
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pivot_df[selected_companies])

    # Growth chart below
    st.subheader("Growth Chart")
    # Calculate total throughput for all selected companies per period
    total_series = grand_totals
    # Period-on-period growth (lag 1)
    pop_growth = calculate_growth(total_series, 1)
    # Year-on-year growth (lag 12 for monthly, 4 for quarterly, 2 for semi-annual, 1 for annual)
    if timeframe == 'Monthly':
        yoy_lag = 12
    elif timeframe == 'Quarterly':
        yoy_lag = 4
    elif timeframe == 'Semi-Annual':
        yoy_lag = 2
    elif timeframe == 'Annual':
        yoy_lag = 1
    else:
        yoy_lag = 1
    yoy_growth = calculate_growth(total_series, yoy_lag)

    growth_fig = go.Figure()
    growth_fig.add_trace(go.Scatter(
        x=total_series.index,
        y=pop_growth,
        mode='lines+markers',
        name='Period-on-Period Growth (%)',
        line=dict(color=color_palette[1], width=2)
    ))
    growth_fig.add_trace(go.Scatter(
        x=total_series.index,
        y=yoy_growth,
        mode='lines+markers',
        name='Year-on-Year Growth (%)',
        line=dict(color=color_palette[2], width=2, dash='dash')
    ))
    growth_fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Growth (%)",
        title=f"Growth Chart ({timeframe})",
        plot_bgcolor=color_palette[5],
        paper_bgcolor=color_palette[5],
        font=dict(color=color_palette[0]),
        hovermode="x unified"
    )
    st.plotly_chart(growth_fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading or plotting data: {e}")
    import traceback
    st.text(traceback.format_exc())

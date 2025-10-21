
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import init_db, import_excel_to_db, fetch_all, insert_row, to_dataframe



DB_PATH = 'monthly_income.db'

# Initialize DB and import Excel if DB empty
init_db()
rows = fetch_all()
if not rows:
	import_excel_to_db('Monthly income by quarter_2015-2025.xlsx')
	rows = fetch_all()
# Convert to dataframe
df = pd.DataFrame([dict(r) for r in rows])
if not df.empty:
	df['Quarter'] = pd.to_datetime(df['quarter_dt'])
	df = df.rename(columns={'urban':'Urban','rural':'Rural','nationwide':'Nationwide'})
else:
	df = pd.DataFrame(columns=['Quarter','Urban','Rural','Nationwide'])


# Convert Quarter column to datetime for filtering
df['Quarter'] = pd.to_datetime(df['Quarter'])

st.title('Average monthly income per salaried worker by Quarter (2015-2025)')
st.write('Preview of data:', df.head())


# Add control to select timeframe by quarter
quarter_options = df['Quarter'].dt.to_period('Q').astype(str).unique().tolist()
quarter_options.sort()
start_quarter, end_quarter = st.select_slider(
	'Select timeframe (quarter):',
	options=quarter_options,
	value=(quarter_options[0], quarter_options[-1])
)

# Filter data by selected quarters
filtered_df = df[
	(df['Quarter'].dt.to_period('Q').astype(str) >= start_quarter) &
	(df['Quarter'].dt.to_period('Q').astype(str) <= end_quarter)
]


# Add control to select worker type(s)
worker_types = st.multiselect(
	'Select worker type(s):',
	['Urban', 'Rural', 'Nationwide'],
	default=['Urban', 'Rural', 'Nationwide']
)


# Color panel from attachment
color_panel = [
	'#184C43',  # dark green
	'#00C98D',  # teal
	'#B8925A',  # gold
	'#A1A1A1',  # gray
	'#000000',  # black
	'#FFFFFF'   # white
]

# Assign colors for worker types
worker_color_map = {
	'Urban': color_panel[0],
	'Rural': color_panel[1],
	'Nationwide': color_panel[2]
}


# Round income values to 1 decimal place before plotting
fig = go.Figure()
for i, wt in enumerate(worker_types):
	fig.add_trace(go.Scatter(x=filtered_df['Quarter'], y=filtered_df[wt].round(1), mode='lines+markers', name=wt, line=dict(color=worker_color_map.get(wt, color_panel[i%len(color_panel)]))))
fig.update_layout(
	title=f"Average monthly income per salaried worker by Quarter (2015-2025) - {' & '.join(worker_types) if worker_types else 'None'}",
	xaxis_title='Quarter',
	yaxis_title='Monthly Income (VND mn)',
	legend_title='Worker Type',
	hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

# Add control for growth chart worker type
growth_worker_type = st.selectbox(
	'Select worker type for growth chart:',
	['Urban', 'Rural', 'Nationwide'],
	index=0,
	key='growth_worker_type'
)


# Calculate QoQ and YoY growth, rounded to 1 decimal (filtered)
qoq_growth = (filtered_df[growth_worker_type].pct_change() * 100).round(1)
yoy_growth = (filtered_df[growth_worker_type].pct_change(periods=4) * 100).round(1)



# Use two distinct colors for QoQ and YoY growth lines
qoq_color = color_panel[0]  # dark green
yoy_color = color_panel[1]  # teal

growth_fig = go.Figure()
growth_fig.add_trace(go.Scatter(
	x=df['Quarter'], y=qoq_growth, mode='lines+markers',
	name=f'{growth_worker_type} QoQ Growth (%)',
	line=dict(dash='dot', color=qoq_color)
))
growth_fig.add_trace(go.Scatter(
	x=df['Quarter'], y=yoy_growth, mode='lines+markers',
	name=f'{growth_worker_type} YoY Growth (%)',
	line=dict(dash='dash', color=yoy_color)
))
growth_fig.update_layout(
	title=f'YoY and QoQ Growth for {growth_worker_type} (2015-2025)',
	xaxis_title='Quarter',
	yaxis_title='Growth (%)',
	legend_title='Growth Type',
	hovermode='x unified'
)
st.plotly_chart(growth_fig, use_container_width=True)

# Admin form to add monthly datapoint
st.markdown('---')
st.subheader('Admin: add / update monthly datapoint')
with st.form('add_row'):
	q_label = st.text_input('Quarter label (YYYY-MM-DD)', value='')
	q_date = st.date_input('Quarter date')
	urban_val = st.number_input('Urban', value=0.0, format='%.2f')
	rural_val = st.number_input('Rural', value=0.0, format='%.2f')
	nationwide_val = st.number_input('Nationwide', value=0.0, format='%.2f')
	submitted = st.form_submit_button('Save')
	if submitted:
		insert_row(q_label or q_date.strftime('%Y-%m-%d'), q_date.strftime('%Y-%m-%d'), urban_val, rural_val, nationwide_val)
		st.success('Row saved to DB. Refresh the page to see updates.')

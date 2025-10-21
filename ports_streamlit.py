
import streamlit as st
import pandas as pd
from ports_db import init_db, to_dataframe, insert_throughput

init_db()

st.title('Port throughput admin')

# Upload area for Excel/CSV to bulk import monthly datapoints
st.subheader('Upload Excel / CSV to import monthly datapoints')
uploaded_file = st.file_uploader('Choose an Excel (.xlsx) or CSV file', type=['xlsx', 'csv'])
if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            u_df = pd.read_csv(uploaded_file)
        else:
            u_df = pd.read_excel(uploaded_file)

        # Normalize column names
        cols = [c.strip().lower() for c in u_df.columns]
        u_df.columns = cols

        # Required columns: Date, Region, Company, Port, Total throughput
        required = {'date', 'region', 'company', 'port', 'total throughput'}
        if not required.issubset(set(cols)):
            st.error(f'Uploaded file must contain columns: {required}. Found: {set(cols)}')
        else:
            count = 0
            for _, r in u_df.iterrows():
                try:
                    date = pd.to_datetime(r['date'])
                    year = int(date.year)
                    month = int(date.month)
                    region = str(r['region']) if pd.notna(r['region']) else None
                    company = str(r['company']) if pd.notna(r['company']) else None
                    port = str(r['port'])
                    throughput = float(r['total throughput'])
                    insert_throughput(port, year, month, throughput, region=region, company=company)
                    count += 1
                except Exception as e:
                    # skip bad rows but show a warning
                    st.warning(f'Skipped row due to error: {e}')
            st.success(f'Imported {count} rows into the database.')
    except Exception as e:
        st.error(f'Failed to read uploaded file: {e}')


df = to_dataframe()
st.write('Data preview:')
st.dataframe(df)

st.subheader('Add / update monthly throughput (single row)')
with st.form('add'):
    port = st.text_input('Port')
    year = st.number_input('Year', value=2025, min_value=2000, max_value=2100)
    month = st.number_input('Month', value=1, min_value=1, max_value=12)
    throughput = st.number_input('Throughput (TEU)', value=0.0, format='%.2f')
    submitted = st.form_submit_button('Save')
    if submitted:
        if not port:
            st.error('Port is required')
        else:
            insert_throughput(port, int(year), int(month), float(throughput))
            st.success('Saved. Refresh to see changes.')

st.markdown('---')
st.info('You can also run ports_db_init.py or use import_csv/import_excel in the ports_db module programmatically.')

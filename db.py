import sqlite3
from typing import List, Dict, Optional, Tuple
import pandas as pd

DB_PATH = 'monthly_income.db'

def get_connection(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(path: str = DB_PATH) -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS monthly_income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quarter TEXT NOT NULL UNIQUE,
        quarter_dt DATE,
        urban REAL,
        rural REAL,
        nationwide REAL
    )
    ''')
    conn.commit()
    conn.close()

def insert_row(quarter: str, quarter_dt: Optional[str], urban: Optional[float], rural: Optional[float], nationwide: Optional[float], path: str = DB_PATH) -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('''
    INSERT OR REPLACE INTO monthly_income (quarter, quarter_dt, urban, rural, nationwide)
    VALUES (?, ?, ?, ?, ?)
    ''', (quarter, quarter_dt, urban, rural, nationwide))
    conn.commit()
    conn.close()

def fetch_all(path: str = DB_PATH) -> List[sqlite3.Row]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM monthly_income ORDER BY quarter_dt')
    rows = cur.fetchall()
    conn.close()
    return rows

def to_dataframe(path: str = DB_PATH) -> pd.DataFrame:
    rows = fetch_all(path)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    # ensure quarter_dt is datetime
    df['quarter_dt'] = pd.to_datetime(df['quarter_dt'])
    # rename to original column names used by app
    df = df.rename(columns={'quarter_dt':'Quarter','urban':'Urban','rural':'Rural','nationwide':'Nationwide','quarter':'QuarterLabel'})
    return df[['Quarter','Urban','Rural','Nationwide']]

def import_excel_to_db(excel_path: str, path: str = DB_PATH, header=None, skiprows=4):
    # Read the same way the app previously read
    df = pd.read_excel(excel_path, header=header, skiprows=skiprows)
    # drop first empty column if present
    if df.shape[1] > 3:
        df = df.iloc[:, 1:]
    df.columns = ['Quarter', 'Urban', 'Rural', 'Nationwide']
    # convert Quarter to date string
    df['Quarter'] = pd.to_datetime(df['Quarter'])
    init_db(path)
    for _, row in df.iterrows():
        insert_row(str(row['Quarter'].strftime('%Y-%m-%d')), row['Quarter'].strftime('%Y-%m-%d'),
                   float(row['Urban']) if pd.notna(row['Urban']) else None,
                   float(row['Rural']) if pd.notna(row['Rural']) else None,
                   float(row['Nationwide']) if pd.notna(row['Nationwide']) else None,
                   path)

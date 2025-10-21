import sqlite3
from typing import List
import pandas as pd

DB_PATH = 'ports_throughput.db'

def get_connection(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(path: str = DB_PATH) -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS throughput (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
    port TEXT NOT NULL,
    region TEXT,
    company TEXT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    throughput REAL,
    UNIQUE(port, year, month)
    )
    ''')
    conn.commit()
    # Ensure columns 'region' and 'company' exist (handle older DBs)
    cur.execute("PRAGMA table_info('throughput')")
    cols = [row[1] for row in cur.fetchall()]
    if 'region' not in cols:
        cur.execute("ALTER TABLE throughput ADD COLUMN region TEXT")
    if 'company' not in cols:
        cur.execute("ALTER TABLE throughput ADD COLUMN company TEXT")
    conn.commit()
    conn.close()

def insert_throughput(port: str, year: int, month: int, throughput: float, region: str = None, company: str = None, path: str = DB_PATH) -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('''
    INSERT OR REPLACE INTO throughput (port, region, company, year, month, throughput)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (port, region, company, year, month, throughput))
    conn.commit()
    conn.close()

def fetch_all(path: str = DB_PATH) -> List[sqlite3.Row]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM throughput ORDER BY year, month')
    rows = cur.fetchall()
    conn.close()
    return rows

def to_dataframe(path: str = DB_PATH) -> pd.DataFrame:
    rows = fetch_all(path)
    if not rows:
        return pd.DataFrame(columns=['port','region','company','year','month','throughput','date'])

    df = pd.DataFrame([dict(r) for r in rows])
    # Ensure expected columns exist
    for col in ['port', 'region', 'company', 'year', 'month', 'throughput']:
        if col not in df.columns:
            df[col] = None

    # Coerce types where possible
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce')
    df['throughput'] = pd.to_numeric(df['throughput'], errors='coerce')
    # Create date column
    df['date'] = pd.to_datetime(df['year'].astype('Int64').astype(str) + '-' + df['month'].astype('Int64').astype(str) + '-01', errors='coerce')
    return df[['port','region','company','year','month','throughput','date']]

def import_csv(path_csv: str, db_path: str = DB_PATH) -> None:
    # expects columns: date or year/month, port, total throughput, and optional region/company
    df = pd.read_csv(path_csv)
    init_db(db_path)
    cols = [c.strip().lower() for c in df.columns]
    df.columns = cols
    for _, r in df.iterrows():
        # parse year/month
        if 'date' in df.columns:
            date = pd.to_datetime(r['date'])
            year = int(date.year)
            month = int(date.month)
        else:
            year = int(r.get('year'))
            month = int(r.get('month'))
        port = str(r.get('port'))
        throughput = float(r.get('total throughput') or r.get('throughput'))
        region = str(r.get('region')) if 'region' in df.columns else None
        company = str(r.get('company')) if 'company' in df.columns else None
        insert_throughput(port, year, month, throughput, region=region, company=company, path=db_path)

def import_excel(path_xlsx: str, db_path: str = DB_PATH, sheet_name=0) -> None:
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name)
    init_db(db_path)
    cols = [c.strip().lower() for c in df.columns]
    df.columns = cols
    for _, r in df.iterrows():
        if 'date' in df.columns:
            date = pd.to_datetime(r['date'])
            year = int(date.year)
            month = int(date.month)
        else:
            year = int(r.get('year'))
            month = int(r.get('month'))
        port = str(r.get('port'))
        throughput = float(r.get('total throughput') or r.get('throughput'))
        region = str(r.get('region')) if 'region' in df.columns else None
        company = str(r.get('company')) if 'company' in df.columns else None
        insert_throughput(port, year, month, throughput, region=region, company=company, path=db_path)

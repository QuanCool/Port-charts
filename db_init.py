from db import import_excel_to_db, init_db

EXCEL_PATH = 'Monthly income by quarter_2015-2025.xlsx'

if __name__ == '__main__':
    init_db()
    import_excel_to_db(EXCEL_PATH)
    print('DB initialized and data imported')

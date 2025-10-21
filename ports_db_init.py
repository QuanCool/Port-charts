from ports_db import init_db, import_csv, import_excel

if __name__ == '__main__':
    init_db()
    print('Ports DB initialized (empty).')
    # To import from csv or excel, call import_csv('file.csv') or import_excel('file.xlsx')

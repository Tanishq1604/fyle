import sqlite3

def view_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  Column: {column[1]}, Type: {column[2]}")
        
        # Get all data from the table
        cursor.execute(f"SELECT * FROM {table[0]};")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  Row: {row}")
        print()

    conn.close()

if __name__ == "__main__":
    db_path = 'core/store.sqlite3'
    view_db(db_path)

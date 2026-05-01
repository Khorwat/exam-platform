import sqlite3
import os

DB_PATH = 'db.sqlite3'

def check_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- TABLE DEFINITION ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='examinations_examsession'")
    res = cursor.fetchone()
    if res:
        print(res[0])
    
    conn.close()

if __name__ == "__main__":
    check_table()

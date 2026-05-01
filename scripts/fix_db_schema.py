import sqlite3
import os

DB_PATH = 'db.sqlite3'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Current Indexes on examinations_examsession ---")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='examinations_examsession'")
    indexes = cursor.fetchall()
    
    for name, sql in indexes:
        print(f"NAME: {name}")
        print(f"SQL: {sql}")
        
        # Hardcoded check for the known bad index name from migration 0001
        if "examination_exam_id_fef13f_idx" in name:
            print(f"!!! FOUND BAD INDEX BY NAME: {name} !!!")
            try:
                cursor.execute(f"DROP INDEX {name}")
                conn.commit()
                print(">>> DROPPED SUCCESSFULLY <<<")
            except Exception as e:
                print(f"Error dropping: {e}")
        
        # Also check for any index that covers status
        if sql and 'status' in sql and 'exam_id' in sql and 'student_id' in sql:
             print(f"!!! FOUND BAD INDEX BY SQL: {name} !!!")
             # Don't drop automatically to avoid double drop if name matched
             if "examination_exam_id_fef13f_idx" not in name:
                 try:
                    cursor.execute(f"DROP INDEX {name}")
                    conn.commit()
                    print(">>> DROPPED SUCCESSFULLY <<<")
                 except Exception as e:
                    print(f"Error dropping: {e}")

    print("--- Done ---")
    conn.close()

if __name__ == "__main__":
    fix_schema()

import sqlite3
import os


db_path = os.path.join(os.getcwd(), "db.sqlite3")


conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS SoilData;")
conn.commit()
conn.close()

print("Table 'SoilData' removed successfully!")

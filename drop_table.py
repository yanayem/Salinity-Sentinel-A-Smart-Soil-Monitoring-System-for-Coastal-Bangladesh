import sqlite3
import os

# Path to your database
db_path = os.path.join(os.getcwd(), "db.sqlite3")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the employees_leaverequest table if it exists
cursor.execute("DROP TABLE IF EXISTS SoilData;")
conn.commit()
conn.close()

print("Table 'SoilData' removed successfully!")

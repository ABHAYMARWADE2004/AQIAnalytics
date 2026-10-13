# database.py
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

def save_readings(rows):
    """rows = list of (city, aqi, measured_at). Already-saved hours are skipped."""
    if not rows:
        return 0
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(
        "INSERT IGNORE INTO aqi_readings (city, aqi, measured_at) VALUES (%s, %s, %s)",
        rows,
    )
    new_rows = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return new_rows

def get_all_readings():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT city, aqi, measured_at FROM aqi_readings ORDER BY measured_at DESC")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def clear_all_readings():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM aqi_readings")
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    try:
        get_connection().close()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
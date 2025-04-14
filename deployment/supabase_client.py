import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("POSTGRES_DB_USER")
PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DBNAME = os.getenv("POSTGRES_DB_NAME")


def connect():
    # Connect to the database
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")

        # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # Example query
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("Current Time:", result)

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")


def upload_sql_to_supabase(sql_path):
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        print("SQL uploaded successfully to Supabase.")
    except Exception as e:
        print("Error uploading SQL:", e)
    finally:
        cursor.close()
        conn.close()

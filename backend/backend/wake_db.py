import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file.")
    exit(1)

try:
    print(f"Attempting to wake up Neon compute at: {DATABASE_URL.split('@')[-1]}")
    
    # Try to strip away common URL issues
    clean_url = DATABASE_URL
    if "?sslmode=require" not in clean_url:
        clean_url += "?sslmode=require"
    
    # Attempt connection
    conn = psycopg2.connect(clean_url, connect_timeout=15)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("Database is Awake!")
    
    print("Checking if 'last_read_position' column exists...")
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='notes' AND column_name='last_read_position';
    """)
    column_exists = cur.fetchone()
    
    if not column_exists:
        print("Applying the fix: Adding 'last_read_position' column...")
        cur.execute("ALTER TABLE notes ADD COLUMN last_read_position INTEGER DEFAULT 0;")
        conn.commit()
        print("Success! Column added.")
    else:
        print("Column 'last_read_position' already exists. No action needed.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    print("\nIf you see 'transitioning' or 'not ready', please wait 30 seconds and run this script again.")

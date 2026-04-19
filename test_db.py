import psycopg2
from db import DB_CONFIG

def check_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, title, poster_url FROM movies;")
        rows = cur.fetchall()
        for r in rows:
            print(f"ID: {r[0]} | Title: {r[1]} | Poster: {r[2]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()

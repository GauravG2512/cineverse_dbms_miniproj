import psycopg2
from db import DB_CONFIG

def update_movies():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 1. Clear existing bookings and movies to start fresh with new data
    cur.execute("TRUNCATE bookings CASCADE;")
    cur.execute("TRUNCATE movies CASCADE;")
    cur.execute("ALTER SEQUENCE movies_id_seq RESTART WITH 1;")
    
    new_movies = [
        ("Dhurandhar: The Revenge", "Action / Thriller", 145, "Hindi", "UA", "movies_poster/Dhurandhar The Revenge.jpg"),
        ("The Dark Knight", "Action / Crime / Drama", 152, "English", "UA", "movies_poster/The_dark_knight.jpg"),
        ("Bhoot Bangla", "Horror / Comedy", 130, "Hindi", "UA", "movies_poster/bhoot_bangla.jpg"),
        ("Hoppers", "Sci-Fi / Adventure", 125, "English", "U", "movies_poster/hoppers.jpg"),
        ("The Super Mario Bros.", "Animation / Adventure", 92, "English", "U", "movies_poster/mario.jpg"),
        ("Michael", "Action / Drama", 155, "Telugu", "A", "movies_poster/michael.jpg"),
        ("Project Hail Mary", "Sci-Fi / Drama", 140, "English", "UA", "movies_poster/project_hail_mary.jpg"),
        ("The Drama", "Thriller / Mystery", 118, "Malayalam", "UA", "movies_poster/the_drama.jpg"),
    ]
    
    for title, genre, dur, lang, rat, url in new_movies:
        cur.execute(
            "INSERT INTO movies (title, genre, duration, language, rating, poster_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, genre, dur, lang, rat, url)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print("Movies updated successfully!")

if __name__ == "__main__":
    update_movies()

"""
db.py — CineReserve database helpers (psycopg2)
"""
import psycopg2
import psycopg2.extras
import streamlit as st

# ── Connection ──────────────────────────────────────────────────────────────
DB_CONFIG = dict(
    host     = "localhost",
    port     = 5432,
    dbname   = "cinema_db",
    user     = "postgres",
    password = "root",   # ← change this
)

@st.cache_resource
def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def _cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ── Movies ───────────────────────────────────────────────────────────────────
def fetch_movies():
    conn = get_conn()
    with _cursor(conn) as cur:
        cur.execute("SELECT * FROM movies ORDER BY id;")
        return cur.fetchall()


def fetch_movie(movie_id: int):
    conn = get_conn()
    with _cursor(conn) as cur:
        cur.execute("SELECT * FROM movies WHERE id = %s;", (movie_id,))
        return cur.fetchone()


# ── Seat availability ─────────────────────────────────────────────────────────
def fetch_seats_with_availability(movie_id: int):
    """
    Returns every seat with an `is_booked` boolean.
    Uses LEFT JOIN so unbooked seats still appear.
    """
    conn = get_conn()
    sql = """
        SELECT
            s.id,
            s.row_name,
            s.seat_number,
            s.tier,
            s.price,
            CASE WHEN b.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_booked
        FROM seats s
        LEFT JOIN bookings b
               ON b.seat_id   = s.id
              AND b.movie_id  = %s
        ORDER BY s.row_name DESC, s.seat_number;
    """
    with _cursor(conn) as cur:
        cur.execute(sql, (movie_id,))
        return cur.fetchall()


# ── Booking transaction ───────────────────────────────────────────────────────
def book_seats(movie_id: int, seat_ids: list[int], customer: str = "Guest") -> bool:
    """
    Inserts one booking row per seat inside a single transaction.
    Returns True on success, False if a conflict (double-booking) is detected.
    """
    conn = get_conn()
    try:
        with conn:                          # auto-commit on success, rollback on error
            with _cursor(conn) as cur:
                for sid in seat_ids:
                    cur.execute(
                        """
                        INSERT INTO bookings (movie_id, seat_id, customer)
                        VALUES (%s, %s, %s);
                        """,
                        (movie_id, sid, customer),
                    )
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    except Exception as e:
        conn.rollback()
        raise e

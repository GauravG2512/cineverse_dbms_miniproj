# 🎬 CineReserve — AI-Powered Movie Ticket Booking System

A modern, full-featured **Movie Ticket Booking System** built with **Python (Streamlit)** for the frontend and **PostgreSQL** as the database. Features real-time seat availability, tiered pricing (Recliner / Prime Plus / Prime), double-booking prevention via SQL constraints, and a cinematic dark-themed UI.

---

## ✨ Features

- 🎥 **Movie Discovery** — Grid-based landing page with movie posters, genre, duration, and language info
- 🪑 **Interactive Seat Map** — Full row layout (Q → E), color-coded by availability and tier
- 💺 **Tiered Pricing** — Recliner (₹500), Prime Plus (₹350), Prime (₹200)
- 🔒 **Double-Booking Prevention** — `UNIQUE(movie_id, seat_id)` constraint at the database level
- 🧾 **Live Booking Summary** — Real-time sidebar showing selected seats and total amount
- ✅ **Booking Confirmation** — Success screen with `st.balloons()` and a printable receipt
- 🔄 **Smooth Navigation** — Multi-page flow via `st.session_state` (no page refreshes)
- 🎭 **SCREEN THIS WAY** — Glowing blue screen orientation indicator on the seat map

---

## 📁 Folder Structure

```
cinereserve/
│
├── main.py               # Streamlit frontend — all UI pages and routing
├── db.py                 # Database connection and query functions (psycopg2)
├── schema.sql            # PostgreSQL schema + seed data (run this in pgAdmin)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

### File Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | Multi-page Streamlit app: Home (movie grid), Seats (seat map), Confirm (payment + receipt) |
| `db.py` | DB config, `fetch_movies()`, `fetch_seats_with_availability()`, `book_seats()` |
| `schema.sql` | Creates `movies`, `seats`, `bookings` tables + seeds 6 movies and 176 seats |
| `requirements.txt` | `streamlit`, `psycopg2-binary`, `pandas` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Python · Streamlit |
| Database | PostgreSQL (managed via pgAdmin) |
| DB Driver | psycopg2-binary |
| Data Display | pandas DataFrame |
| Styling | Custom CSS via `st.markdown()` |

---

## ⚙️ Setup Instructions

### Prerequisites

Make sure the following are installed on your system:

- Python 3.9 or higher → [python.org](https://www.python.org/downloads/)
- PostgreSQL 14 or higher → [postgresql.org](https://www.postgresql.org/download/)
- pgAdmin 4 → [pgadmin.org](https://www.pgadmin.org/download/) *(usually bundled with PostgreSQL)*
- Git → [git-scm.com](https://git-scm.com/)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/cinereserve.git
cd cinereserve
```

---

### Step 2 — Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up the PostgreSQL Database in pgAdmin

#### 4.1 — Open pgAdmin and Connect to Your Server

1. Launch **pgAdmin 4** from your applications
2. In the left panel, expand **Servers**
3. Click on your local PostgreSQL server (e.g., `PostgreSQL 16`)
4. Enter your **master password** if prompted

#### 4.2 — Create the Database

1. Right-click on **Databases** → select **Create** → **Database...**
2. In the **General** tab, set the **Database** name to:
   ```
   cinema_db
   ```
3. Leave all other settings as default
4. Click **Save**

#### 4.3 — Run the SQL Schema

1. Click on the newly created `cinema_db` in the left panel to select it
2. Click the **Query Tool** button in the top toolbar (or press `Alt + Shift + Q`)
3. In the Query Tool window, click **Open File** (folder icon) and select `schema.sql` from your project folder
   - Or copy-paste the entire contents of `schema.sql` into the Query Tool
4. Click the **Execute / Run** button (▶️ play icon, or press `F5`)
5. You should see a success message in the **Messages** tab at the bottom

> This will create the `movies`, `seats`, and `bookings` tables, and automatically seed 6 sample movies and 176 seats (11 rows × 16 seats).

#### 4.4 — Verify the Setup

In the Query Tool, run the following to verify data was inserted correctly:

```sql
SELECT * FROM movies;
SELECT COUNT(*) FROM seats;   -- Should return 176
SELECT * FROM seats LIMIT 5;
```

---

### Step 5 — Configure Database Connection

Open `db.py` in a text editor and update the `DB_CONFIG` dictionary with your PostgreSQL credentials:

```python
DB_CONFIG = dict(
    host     = "localhost",       # Usually localhost
    port     = 5432,              # Default PostgreSQL port
    dbname   = "cinema_db",       # Must match what you created in pgAdmin
    user     = "postgres",        # Your PostgreSQL username
    password = "your_password",   # ← Replace with your actual password
)
```

> 💡 Your PostgreSQL password is the one you set when you first installed PostgreSQL (not your pgAdmin master password — these can be different).

---

### Step 6 — Run the Application

```bash
streamlit run main.py
```

The app will open automatically in your browser at:
```
http://localhost:8501
```

---

## 🗃️ Database Schema

```
movies
├── id           SERIAL PRIMARY KEY
├── title        VARCHAR(200)
├── genre        VARCHAR(80)
├── duration     INT              (in minutes)
├── language     VARCHAR(40)
├── rating       VARCHAR(10)      (UA, A, U)
└── poster_url   TEXT

seats
├── id           SERIAL PRIMARY KEY
├── row_name     CHAR(1)          (Q, P, N, M, L, K, J, H, G, F, E)
├── seat_number  INT              (1–16)
├── tier         VARCHAR(20)      (Recliner | Prime Plus | Prime)
└── price        NUMERIC(8,2)

bookings
├── id           SERIAL PRIMARY KEY
├── movie_id     INT  → FK movies(id)
├── seat_id      INT  → FK seats(id)
├── booking_time TIMESTAMPTZ      (auto-set to NOW())
├── customer     VARCHAR(120)
└── UNIQUE (movie_id, seat_id)    ← Prevents double-booking
```

### Seat Tier Layout

| Rows | Tier | Price |
|------|------|-------|
| Q, P | Recliner | ₹500 |
| N, M, L, K | Prime Plus | ₹350 |
| J, H, G, F, E | Prime | ₹200 |

---

## 🧠 How It Works

1. **User opens the app** → sees a grid of movies fetched from the `movies` table
2. **Clicks "Book Now"** → navigated to the seat map for that movie
3. **Seat map loads** → a `LEFT JOIN` between `seats` and `bookings` fetches real-time availability for that specific movie
4. **User selects seats** → sidebar updates live with seat labels and total price
5. **Clicks "Confirm Booking"** → sees an order summary with a pandas table
6. **Clicks "Pay & Confirm"** → each selected seat is `INSERT`ed into `bookings` inside a single transaction
7. **On success** → `st.balloons()` fires and a receipt is shown
8. **On double-booking conflict** → `psycopg2.errors.UniqueViolation` is caught, the transaction is rolled back, and the user is sent back to re-select seats

---

## 🐛 Troubleshooting

**App shows "Cannot connect to database" error**
- Check that PostgreSQL service is running
- Verify your password in `db.py` is correct
- Make sure `cinema_db` exists in pgAdmin
- Confirm the port is `5432` (check in pgAdmin → Server Properties)

**`ModuleNotFoundError: No module named 'psycopg2'`**
- Make sure your virtual environment is activated
- Run `pip install psycopg2-binary` again

**Seats not showing on the seat map**
- Open pgAdmin Query Tool and run `SELECT COUNT(*) FROM seats;`
- If 0 rows, re-run `schema.sql` — the seed block may have been skipped
- Alternatively, run only the `DO $$ ... END $$` block from `schema.sql` manually

**pgAdmin asks for a "master password" — what is it?**
- This is a pgAdmin-specific password you set the first time you opened pgAdmin, used to encrypt stored server passwords. It is separate from your PostgreSQL user password.

---

## 👥 Team

| Name | Role |
|------|------|
| Gaurav Ghude | Developer |
| Yash Patil | Developer |
| Samprati Tikone | Developer |

**Institute:** Vidyalankar Institute of Technology

**Course:** DBMS — Mini Project

---

## 📄 License

This project is developed for academic purposes at Vidyalankar Institute of Technology.

---

> Built with ❤️ using Python, Streamlit, and PostgreSQL

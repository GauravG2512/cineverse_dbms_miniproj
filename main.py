"""
main.py — CineReserve  |  pip install streamlit psycopg2-binary
Run: streamlit run main.py
"""

import streamlit as st
from db import fetch_movies, fetch_movie, fetch_seats_with_availability, book_seats
from collections import defaultdict
import base64
import os

def get_base64(file_path):
    if not os.path.exists(file_path): return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineReserve",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  — dark luxury cinema theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&family=Bebas+Neue&display=swap');

:root {
    --primary: #f87171;
    --bg-dark: #0a0a0f;
    --card-bg: #11111d;
    --text-muted: #888;
}

/* ── Base Layout ────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] { background: var(--bg-dark); }
[data-testid="stSidebar"] { background: #0c0c16 !important; border-right: 1px solid #1e1e30; }

/* ── Top Navigation Bar ─────────────────────────────────────── */
.header {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 80px;
    background: rgba(10, 10, 15, 0.9);
    backdrop-filter: blur(15px);
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 5%;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.header-logo { font-family: 'Outfit', sans-serif; font-weight: 400; font-size: 28px; color: #fff; letter-spacing: 1px; }
.header-links { display: flex; gap: 40px; }
.header-link { font-family: 'Outfit', sans-serif; color: #fff; text-decoration: none; font-size: 14px; font-weight: 500; }
.header-link.active { font-weight: 700; color: #fff; border-bottom: 2px solid #fff; padding-bottom: 4px; }
.header-link:hover { opacity: 0.8; }

/* ── Hero Section ───────────────────────────────────────────── */
.hero {
    position: relative;
    width: 100%;
    height: 65vh;
    border-radius: 0 0 40px 40px;
    overflow: hidden;
    margin-bottom: 40px;
}
.hero-content {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 60px 40px;
    background: linear-gradient(to top, var(--bg-dark), transparent);
    color: #fff;
}
.hero-title { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 56px; margin: 0; letter-spacing: -2px; }
.hero-meta { color: #f87171; font-weight: 500; margin-top: 10px; font-size: 14px; }
.tag {
    display: inline-block;
    padding: 4px 18px;
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 20px;
    font-size: 12px;
    margin-right: 10px;
}

/* ── Cinema & Movie Cards ───────────────────────────────────── */
.section-title { font-family: 'Outfit', sans-serif; font-weight: 400; font-size: 40px; text-align: center; margin-bottom: 40px; }
.card {
    background: #1c1c1e;
    border-radius: 12px;
    overflow: hidden;
    height: 100%;
}
.card-img { width: 100%; aspect-ratio: 16/9; object-fit: cover; }
.card-body { padding: 20px; }
.card-title { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.card-sub { font-size: 13px; color: #666; margin-bottom: 20px; }
.card-stat { font-size: 12px; color: #888; display: flex; align-items: center; gap: 8px; margin-top: 8px; }

/* ── Streamlit Overrides ────────────────────────────────────── */
h1, h2, h3 { font-family: 'Outfit', sans-serif !important; font-weight: 400 !important; }
button[data-testid="stBaseButton-primary"] { border-radius: 30px !important; background: #fff !important; color: #000 !important; font-weight: 700 !important; }
button[data-testid="stBaseButton-secondary"] { border-radius: 10px !important; background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #fff !important; }

.movie-poster-img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: 12px;
}
.movie-info-area {
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    margin-top: 10px;
}
.movie-card-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 5px;
}

/* ── Seat Grid ─────────────────────────────────────────────── */
.seat-button {
    width: 32px;
    height: 32px;
    border: 1px solid #ddd;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    cursor: pointer;
    background: #fff;
    color: #333;
}
.seat-header {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    background: #f8f8fb;
    border-radius: 12px;
    margin-bottom: 30px;
    justify-content: space-between;
    color: #444;
}
.time-badge {
    background: #e1e1ef;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid #ccc;
}

/* ── Checkout Page ─────────────────────────────────────────── */
.checkout-container {
    padding: 20px;
}
.review-banner {
    background: #fdf2ff;
    color: #9333ea;
    text-align: center;
    padding: 8px;
    font-size: 13px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.checkout-card {
    background: #fff;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    color: #1a1a1a;
}
.fb-card {
    border: 1px solid #efefef;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    background: #fff;
    color: #111;
}
.fb-img {
    height: 100px;
    object-fit: contain;
    margin-bottom: 10px;
}
.pay-button {
    background: #1a1a1a !important;
    color: #fff !important;
    padding: 15px !important;
    border-radius: 12px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    width: 100% !important;
}
div[data-testid="stButton"] button:has(div:contains("Confirm Booking")),
div[data-testid="stButton"] button:has(div:contains("Proceed To Pay")) {
    background: #1a1a1a !important;
    color: #fff !important;
    padding: 12px !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
</style>

<div class="header">
  <div class="header-logo">CineReserve</div>
  <div class="header-links">
    <a href="#" class="header-link active">Home</a>
    <a href="#" class="header-link">Now Showing</a>
    <a href="#" class="header-link">Coming Soon</a>
    <a href="#" class="header-link">Cinemas</a>
  </div>
  <div style="color:#fff; font-size:20px;">👤</div>
</div>
<div style="height: 60px;"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
def init_state():
    defaults = dict(
        page="home",
        movie_id=None,
        selected_seats=[],   # list of seat dicts
        addons={},           # {item_name: {price: int, count: int}}
        booking_confirmed=False,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def nav(page, movie_id=None):
    st.session_state.page = page
    if movie_id:
        st.session_state.movie_id = movie_id
        st.session_state.selected_seats = []  # Clear only when starting new movie selection
    
    if page == "home":
        st.session_state.selected_seats = []
        st.session_state.addons = {}
        
    st.session_state.booking_confirmed = False
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR  — booking summary
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CineReserve")
    st.markdown("---")

    if st.session_state.page != "home":
        if st.button("← Back to Movies"):
            nav("home")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#444;'>Color legend</div>",
        unsafe_allow_html=True,
    )
    st.markdown("""
<div class='legend' style='flex-direction:column;align-items:flex-start;'>
  <span><span class='dot dot-avail'></span> Available</span>
  <span><span class='dot dot-sel'></span> Selected</span>
  <span><span class='dot dot-booked'></span> Booked</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: HOME — Movie grid
# ─────────────────────────────────────────────────────────────────────────────
def page_home():
    movies = fetch_movies()
    if not movies:
        st.error("Please ensure database is populated.")
        return

    # ── HERO SECTION ──────────────────────────────────────────────────────────
    hero_movie = movies[1] if len(movies) > 1 else movies[0]
    # Use the high-res wide backdrop for the hero
    hero_img_url = "https://img.englishcinemabarcelona.com/huTkZGEkT0gyszNkPlvk3mdsdYrPKJBve3_uzF8c-GU/resize:fill:800:450:1:0/gravity:sm/aHR0cHM6Ly9leHBhdGNpbmVtYXByb2QuYmxvYi5jb3JlLndpbmRvd3MubmV0L2ltYWdlcy9jZjg4OTJhMS03NWZiLTRjNDYtOWFmMy1kMzRjZTg3MTIzYzEuanBn.jpg"
    
    st.markdown(f"""
    <div class="hero" style="background: linear-gradient(to top, var(--bg-dark), transparent), url('{hero_img_url}'); background-size: cover; background-position: center;">
        <div class="hero-content">
            <div style="margin-bottom:15px;">
                <span class="tag">action</span><span class="tag">adventure</span><span class="tag">drama</span>
                <span style="color:#fbbf24; margin-left:10px;">★★★★★</span>
            </div>
            <div class="hero-title">{hero_movie['title']}</div>
            <div style="margin:10px 0 20px; color:#aaa; font-size:16px;">The greatest experience in cinema history.</div>
            <div class="hero-meta">Now Streaming in IMAX</div>
            <div style="font-size:12px; margin-top:10px; opacity:0.6;">{hero_movie['duration']} min &nbsp;·&nbsp; {hero_movie['genre']} &nbsp;·&nbsp; {hero_movie['language']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NOW SHOWING SECTION ───────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Now Showing</div>", unsafe_allow_html=True)
    
    cols = st.columns(4) # More columns as per grid idea
    for i, m in enumerate(movies):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="movie-card-container">
                <img src="data:image/jpeg;base64,{get_base64(m['poster_url'])}" class="movie-poster-img">
                <div class="movie-info-area">
                    <div style='font-weight:600; font-size:16px; line-height:1.2;'>{m['title']}</div>
                    <div style='color:#666; font-size:12px; margin-top:4px;'>{m['genre']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Buy Tickets", key=f"book_{m['id']}", use_container_width=True):
                nav("seats", movie_id=m["id"])
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # ── CINEMAS SECTION ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Our Cinemas</div>", unsafe_allow_html=True)
    c_cols = st.columns(3)
    cinemas = [
        {"name": "Global IMAX", "loc": "new york", "price": "30 €", "seats": 8},
        {"name": "Marvel Imax", "loc": "manchester", "price": "20 €", "seats": 10},
        {"name": "MCU IMAX", "loc": "seattle", "price": "20 €", "seats": 10},
    ]
    for i, c in enumerate(cinemas):
        with c_cols[i]:
            st.markdown(f"""
            <div class="card">
                <img src="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=3540&auto=format&fit=crop" class="card-img">
                <div class="card-body">
                    <div class="card-title">{c['name']}</div>
                    <div class="card-sub">{c['loc']}</div>
                    <div class="card-stat">💰 {c['price']} per movie</div>
                    <div class="card-stat">🪑 {c['seats']} seats Available</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"View Details {i}", key=f"cin_{i}", use_container_width=True)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px; color:#444; text-align:center;'>© Movie Store 2026 | Created with passion</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: SEATS — Interactive seat map
# ─────────────────────────────────────────────────────────────────────────────
TIER_ORDER = {
    "Recliner":   ("Q", "P"),
    "Prime Plus": ("N", "M", "L", "K"),
    "Prime":      ("J", "H", "G", "F", "E"),
}
TIER_CLASS = {
    "Recliner":   "tier-recliner",
    "Prime Plus": "tier-primeplus",
    "Prime":      "tier-prime",
}
TIER_PRICE = {"Recliner": 500, "Prime Plus": 350, "Prime": 200}

def page_seats():
    movie = fetch_movie(st.session_state.movie_id)
    if not movie:
        st.error("Movie not found.")
        return

    # Header like 3rd screenshot
    st.markdown("""
    <div class="seat-header">
        <div>
            <div style="font-size:12px; opacity:0.6;">Sun</div>
            <div style="font-size:18px; font-weight:700;">19 Apr</div>
        </div>
        <div class="time-badge">08:45 PM <span style="font-size:9px; opacity:0.5; margin-left:5px;">LASER</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 style='font-size:32px; text-align:center; margin-bottom:10px;'>{movie['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#666; font-size:14px; margin-bottom:40px;'>{movie['genre']} · {movie['language']} · {movie['rating']}</p>", unsafe_allow_html=True)

    # Fetch seats
    rows_data = fetch_seats_with_availability(st.session_state.movie_id)
    by_row = defaultdict(list)
    for s in rows_data:
        by_row[s["row_name"]].append(s)

    # Use fragment to make seat selection snappy and lag-free
    @st.fragment
    def render_grid():
        sel_ids = {s["id"] for s in st.session_state.selected_seats}

        def toggle_seat(seat):
            if seat["id"] in sel_ids:
                st.session_state.selected_seats = [s for s in st.session_state.selected_seats if s["id"] != seat["id"]]
            else:
                st.session_state.selected_seats.append(dict(seat))
            st.rerun(scope="fragment")

        for tier_name, tier_rows in TIER_ORDER.items():
            price = TIER_PRICE[tier_name]
            st.markdown(f"<div style='text-align:center; font-size:13px; font-weight:600; margin:30px 0 15px; color:#999; letter-spacing:1px;'>{tier_name.upper()} : ₹{price:.0f}</div>", unsafe_allow_html=True)

            for row in tier_rows:
                seats = sorted(by_row.get(row, []), key=lambda x: x["seat_number"])
                if not seats: continue

                col_main = st.columns([1, 10, 1, 10, 1])
                col_main[0].markdown(f"<div style='padding-top:8px; font-weight:600; color:#555;'>{row}</div>", unsafe_allow_html=True)

                left_seats = [s for s in seats if s['seat_number'] <= 8]
                with col_main[1]:
                    inner_cols = st.columns(8)
                    for i, seat in enumerate(left_seats):
                        render_seat_button(inner_cols[i], seat, sel_ids, toggle_seat)

                right_seats = [s for s in seats if s['seat_number'] > 8]
                with col_main[3]:
                    inner_cols = st.columns(8)
                    for i, seat in enumerate(right_seats):
                        render_seat_button(inner_cols[i], seat, sel_ids, toggle_seat)
        
        # Action Bar inside Fragment
        if st.session_state.selected_seats:
            st.markdown("<br><hr style='opacity:0.1;'><br>", unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            with c1:
                labels = [f"{s['row_name']}{s['seat_number']}" for s in st.session_state.selected_seats]
                st.markdown(f"**Selected:** {', '.join(labels)}")
                total = sum(float(s['price']) for s in st.session_state.selected_seats)
                st.markdown(f"<span style='color:#6366f1; font-size:20px; font-weight:700;'>Total: ₹{total:.0f}</span>", unsafe_allow_html=True)
            with c2:
                if st.button("🎟️ Confirm Booking", key="confirm_btn", type="primary", use_container_width=True):
                    # We need a full rerun to navigate
                    st.session_state.page = "confirm"
                    st.rerun(scope="app")
    
    render_grid()
    st.markdown("<br><br>", unsafe_allow_html=True)
    # Screen Image at bottom
    screen_b64 = get_base64("screen-img.png")
    if screen_b64:
        st.markdown(f"""
        <div style="text-align:center; margin-top:20px;">
            <img src="data:image/png;base64,{screen_b64}" style="width:100%; max-width:600px; opacity:0.8;">
        </div>
        """, unsafe_allow_html=True)

    # Legend
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div class='legend' style='justify-content:center; gap:30px;'>
  <span><span class='dot dot-avail'></span> Available</span>
  <span><span class='dot dot-sel' style='background:#6366f1;'></span> Selected</span>
  <span><span class='dot dot-booked' style='background:#222;'></span> Booked</span>
</div>""", unsafe_allow_html=True)

def render_seat_button(col, seat, sel_ids, toggle_seat):
    label = str(seat['seat_number'])
    is_booked = seat["is_booked"]
    is_sel = seat["id"] in sel_ids
    
    key = f"seat_{seat['id']}"
    help_text = f"Row {seat['row_name']} Seat {seat['seat_number']} · ₹{seat['price']}"

    if is_booked:
        col.markdown("<div style='text-align:center; padding:8px 0; color:#444; font-size:11px;'>✕</div>", unsafe_allow_html=True)
    elif is_sel:
        if col.button(label, key=key, help=help_text, type="primary"):
            toggle_seat(seat)
    else:
        if col.button(label, key=key, help=help_text):
            toggle_seat(seat)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: CONFIRM — Payment & booking
# ─────────────────────────────────────────────────────────────────────────────
def page_confirm():
    movie = fetch_movie(st.session_state.movie_id)
    sel   = st.session_state.selected_seats
    
    if not sel:
        st.warning("Please select at least one seat.")
        if st.button("Back to Seats"): nav("seats")
        return

    order_amount = sum(float(s["price"]) for s in sel)
    addons_amount = sum(item['price'] * item['count'] for item in st.session_state.addons.values())
    
    booking_fee  = (order_amount + addons_amount) * 0.12 # mock 12% GST/Fee
    total_amount = order_amount + addons_amount + booking_fee

    if st.session_state.booking_confirmed:
        st.balloons()
        st.markdown("<div style='text-align:center; padding:100px;'>", unsafe_allow_html=True)
        st.success(f"🎊 Booking Confirmed for {movie['title']}!")
        st.markdown(f"### Ticket ID: #CR{os.urandom(4).hex().upper()}")
        if st.button("Back to Movie Store"): nav("home")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Top Navigation placeholder
    st.markdown("<div style='text-align:center; margin-bottom:10px; font-weight:600; color:#555;'>Review your booking</div>", unsafe_allow_html=True)
    st.markdown("<div class='review-banner'>Complete your booking in 7.46 mins</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2.2, 1])

    with col_left:
        # Movie Info Card
        sb64 = get_base64(movie['poster_url'])
        st.markdown(f"""
<div class="checkout-card">
<div style="display:flex; justify-content:space-between;">
<div>
<div style="font-size:20px; font-weight:700;">{movie['title']}</div>
<div style="font-size:12px; color:#666; margin-top:5px;">A &nbsp;·&nbsp; {movie['language']} &nbsp;·&nbsp; 2D</div>
<div style="font-size:12px; color:#888; margin-top:5px;">PVR Luxe Square, Mumbai</div>
</div>
<img src="data:image/jpeg;base64,{sb64}" style="width:60px; height:80px; border-radius:4px; object-fit:cover;">
</div>
<hr style="margin:15px 0; opacity:0.1;">
<div style="font-size:14px; color:#444;">
<b>{len(sel)} Tickets</b><br>
<span style="color:#888;">{", ".join(f"{s['row_name']}{s['seat_number']}" for s in sel)}</span><br>
SCREEN 1
</div>
<div style="margin-top:15px; background:#f6fff8; color:#1a8754; font-size:11px; padding:10px; border-radius:6px; display:flex; align-items:center; justify-content:space-between;">
<span>🛡️ Cancellation available</span>
<span>❯</span>
</div>
</div>
""", unsafe_allow_html=True)

        # F&B Section mock
        st.markdown("<div style='font-weight:700; color:#fff; margin:20px 0 10px;'>Food and beverages</div>", unsafe_allow_html=True)
        fb_cols = st.columns(4)
        items = [
            {"name": "Regular Popcorn Salted", "price": 385, "img": "https://in.bmscdn.com/fnb/v3/xhdpi/1020004_27082024145536.png"},
            {"name": "Medium Popcorn Cheese", "price": 585, "img": "https://in.bmscdn.com/fnb/v3/xhdpi/1020001_13082018125322.png"},
            {"name": "Regular Popcorn Caramel", "price": 435, "img": "https://in.bmscdn.com/fnb/v3/xhdpi/1020001_13082018125322.png"},
            {"name": "Regular Pepsi", "price": 79, "img": "https://in.bmscdn.com/fnb/v3/xhdpi/1020009_08082024180317.png"}
        ]
        
        for i, item in enumerate(items):
            count = st.session_state.addons.get(item['name'], {}).get('count', 0)
            with fb_cols[i]:
                st.markdown(f"""
                <div class="fb-card">
                    <img src="{item['img']}" class="fb-img">
                    <div style="font-size:10px; height:30px; line-height:1.2;">{item['name']}</div>
                    <div style="font-size:12px; font-weight:700; margin-top:5px;">₹{item['price']}</div>
                    {f'<div style="color:#9333ea; font-size:11px; font-weight:600; margin-bottom:5px;">Qty: {count}</div>' if count > 0 else '<div style="height:16px;"></div>'}
                </div>
                """, unsafe_allow_html=True)
                
                # Stepper buttons
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Add", key=f"add_{i}", use_container_width=True):
                        if item['name'] not in st.session_state.addons:
                            st.session_state.addons[item['name']] = {'price': item[
                                'price'], 'count': 1}
                        else:
                            st.session_state.addons[item['name']]['count'] += 1
                        st.rerun()
                with b2:
                    if count > 0:
                        if st.button("Remove", key=f"rem_{i}", use_container_width=True):
                            st.session_state.addons[item['name']]['count'] -= 1
                            if st.session_state.addons[item['name']]['count'] == 0:
                                del st.session_state.addons[item['name']]
                            st.rerun()
                    else:
                        st.button("-", key=f"rem_dis_{i}", disabled=True, use_container_width=True)

    with col_right:
        # Payment Summary Card
        addon_rows = ""
        for name, data in st.session_state.addons.items():
            if data['count'] > 0:
                addon_rows += f"""
<div style="display:flex; justify-content:space-between; font-size:12px; color:#666; margin-bottom:4px;">
<span>{name} (x{data['count']})</span>
<span>₹{data['price'] * data['count']:.0f}.00</span>
</div>"""

        st.markdown(f"""
<div class="checkout-card" style="padding:15px;">
<div style="font-weight:700; margin-bottom:15px; font-size:16px;">Payment summary</div>
<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;">
<span>Tickets amount</span>
<span>₹{order_amount:.0f}.00</span>
</div>
{addon_rows}
<div style="display:flex; justify-content:space-between; font-size:13px; margin-top:8px; margin-bottom:12px;">
<span>Booking charge (incl. GST)</span>
<span>₹{booking_fee:.2f}</span>
</div>
<hr style="margin:10px 0; opacity:0.1;">
<div style="display:flex; justify-content:space-between; font-weight:700; font-size:16px;">
<span>To be paid</span>
<span>₹{total_amount:.2f}</span>
</div>
</div>
""", unsafe_allow_html=True)

        # User Details Card
        st.markdown(f"""
<div class="checkout-card" style="padding:15px;">
<div style="font-weight:700; margin-bottom:15px; font-size:14px;">Your details</div>
<div style="font-size:13px; line-height:1.6;">
<b>Gaurav Ghude</b><br>
<span style="color:#666;">+91-7276821465</span><br>
<span style="color:#666;">gaurav.ghude@vit.edu.in</span>
</div>
</div>
""", unsafe_allow_html=True)

        # Proceed to Pay Button
        if st.button(f"₹{total_amount:.0f} TOTAL &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Proceed To Pay ❯", key="pay_btn", type="primary"):
            seat_ids = [s["id"] for s in sel]
            success  = book_seats(st.session_state.movie_id, seat_ids)
            if success:
                st.session_state.booking_confirmed = True
                st.rerun()
            else:
                st.error("Payment failed. Some seats were already taken.")


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    page_home()
elif page == "seats":
    page_seats()
elif page == "confirm":
    page_confirm()

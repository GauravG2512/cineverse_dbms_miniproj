-- ============================================================
--  CineReserve · PostgreSQL Schema
--  Run this in pgAdmin against your `cinema_db` database
-- ============================================================

-- 1. MOVIES -------------------------------------------------------
CREATE TABLE IF NOT EXISTS movies (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200)  NOT NULL,
    genre       VARCHAR(80)   NOT NULL,
    duration    INT           NOT NULL DEFAULT 120,  -- minutes
    language    VARCHAR(40)   NOT NULL DEFAULT 'English',
    rating      VARCHAR(10)   NOT NULL DEFAULT 'UA',
    poster_url  TEXT          NOT NULL
);

-- 2. SEATS --------------------------------------------------------
-- Rows Q, P are Recliners; N, M, L, K are Prime Plus; J, H, G, F, E are Prime
CREATE TABLE IF NOT EXISTS seats (
    id          SERIAL PRIMARY KEY,
    row_name    CHAR(1)       NOT NULL CHECK (row_name IN ('Q','P','N','M','L','K','J','H','G','F','E')),
    seat_number INT           NOT NULL CHECK (seat_number BETWEEN 1 AND 20),
    tier        VARCHAR(20)   NOT NULL CHECK (tier IN ('Recliner','Prime Plus','Prime')),
    price       NUMERIC(8,2)  NOT NULL,
    UNIQUE (row_name, seat_number)
);

-- 3. BOOKINGS -----------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    id           SERIAL PRIMARY KEY,
    movie_id     INT           NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    seat_id      INT           NOT NULL REFERENCES seats(id)  ON DELETE CASCADE,
    booking_time TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    customer     VARCHAR(120),
    UNIQUE (movie_id, seat_id)            -- prevents double-booking
);

-- ============================================================
--  SEED DATA
-- ============================================================

-- Seats (Q-P = Recliner ₹500 | N-K = Prime Plus ₹350 | J-E = Prime ₹200)
DO $$
DECLARE
    r   CHAR(1);
    s   INT;
    tier_name  VARCHAR(20);
    tier_price NUMERIC(8,2);
BEGIN
    FOREACH r IN ARRAY ARRAY['Q','P','N','M','L','K','J','H','G','F','E'] LOOP
        IF r IN ('Q','P') THEN
            tier_name := 'Recliner';   tier_price := 500.00;
        ELSIF r IN ('N','M','L','K') THEN
            tier_name := 'Prime Plus'; tier_price := 350.00;
        ELSE
            tier_name := 'Prime';      tier_price := 200.00;
        END IF;

        FOR s IN 1..16 LOOP
            INSERT INTO seats (row_name, seat_number, tier, price)
            VALUES (r, s, tier_name, tier_price)
            ON CONFLICT DO NOTHING;
        END LOOP;
    END LOOP;
END $$;

-- Sample movies (poster_url uses public placeholder images)
INSERT INTO movies (title, genre, duration, language, rating, poster_url) VALUES
  ('Kalki 2898 AD',  'Sci-Fi / Action',  180, 'Telugu',  'UA', 'https://picsum.photos/seed/kalki/300/450'),
  ('Stree 2',        'Horror / Comedy',  135, 'Hindi',   'UA', 'https://picsum.photos/seed/stree2/300/450'),
  ('Pushpa 2',       'Action / Drama',   210, 'Telugu',  'A',  'https://picsum.photos/seed/pushpa/300/450'),
  ('Fighter',        'Action / Thriller',145, 'Hindi',   'UA', 'https://picsum.photos/seed/fighter/300/450'),
  ('Dunki',          'Drama / Comedy',   155, 'Hindi',   'UA', 'https://picsum.photos/seed/dunki/300/450'),
  ('Animal',         'Action / Drama',   200, 'Hindi',   'A',  'https://picsum.photos/seed/animal/300/450')
ON CONFLICT DO NOTHING;

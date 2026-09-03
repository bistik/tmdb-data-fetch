import logging
import sqlite3
from contextlib import closing


def get_connection(database_name: str) -> sqlite3.Connection:
    return sqlite3.connect(database_name)

def create_tables(database_name: str) -> None:
    """
        Create the tables in the database.
    """
    with closing(get_connection(database_name)) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                tmdb_id INTEGER,
                title TEXT,
                backdrop_path TEXT,
                poster_path TEXT,
                overview TEXT,
                release_date TEXT,
                popularity REAL,
                vote_average REAL,
                vote_count INTEGER,
                has_embedding BOOLEAN NOT NULL DEFAULT 0,
                date_added DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                url TEXT,
                date_requested DEFAULT CURRENT_TIMESTAMP
            );
        """)
    logging.info("Tables created successfully (if they don't exist already).")

def has_request(database_name: str, url: str) -> bool:
    """
        Check if a request has been made for the given url.
    """
    with closing(get_connection(database_name)) as conn:
        exists = conn.execute(
            "SELECT EXISTS(SELECT 1 FROM requests WHERE url = ? LIMIT 1)", (url,)
        ).fetchone()[0]
    return bool(exists)

def insert_movies(database_name: str, movies: list[dict]) -> int:
    """
        Insert movies into the database. (per page)
    """
    with closing(get_connection(database_name)) as conn:
        with conn:
            cur = conn.executemany("""
                INSERT INTO movies (
                    tmdb_id,
                    title,
                    backdrop_path,
                    poster_path,
                    overview,
                    release_date,
                    popularity,
                    vote_average,
                    vote_count
                ) VALUES (:id, :title, :backdrop_path, :poster_path, :overview, :release_date, :popularity, :vote_average, :vote_count)
            """, movies)
            inserted = cur.rowcount
    logging.info(f"Inserted {inserted} movies.")
    return inserted

def insert_request(database_name: str, url: str) -> None:
    """
        Insert a request into the database.
    """
    with closing(get_connection(database_name)) as conn:
        with conn:
            conn.execute("""
                INSERT INTO requests (
                    url
                ) VALUES (?)
            """, (url,))
    logging.info(f"Inserted request for {url}.")

def get_movies_by_release_year(database_name: str, release_year: int) -> list[dict]:
    """
        Get all movies for the given release year that has not been embedded.
    """
    with closing(get_connection(database_name)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM movies WHERE strftime('%Y', release_date) = ? AND has_embedding = FALSE",
            (str(release_year),)
        ).fetchall()
    return [dict(row) for row in rows]

def get_movie_by_title(database_name: str, title: str) -> dict | None:
    """
        Get a movie by title (case-insensitive, first match).
    """
    with closing(get_connection(database_name)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM movies WHERE title = ? COLLATE NOCASE LIMIT 1",
            (title,)
        ).fetchone()
    return dict(row) if row else None

def mark_movies_has_embedding(database_name: str, movie_ids: list[int]) -> int:
    """
        Set has_embedding = True for the given movie ids.
        Returns the number of rows updated.
    """
    if not movie_ids:
        return 0
    with closing(get_connection(database_name)) as conn:
        with conn:
            cur = conn.executemany(
                "UPDATE movies SET has_embedding = 1 WHERE id = ?",
                [(movie_id,) for movie_id in movie_ids],
            )
            updated = cur.rowcount
    logging.warning(f"Updated has_embedding for {updated} movies.")
    return updated

def save_movies(database_name: str, movie: dict) -> int:
    """
        Save movies to the database only if the url has not been requested before.
    """
    if has_request(database_name, movie['url']):
        return None
    inserted = insert_movies(database_name, movie['results'])
    insert_request(database_name, movie['url'])
    return inserted

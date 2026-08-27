import sys

from dotenv import load_dotenv

from tmdbdf import api, db
from tmdbdf.config import Config


def main():
    load_dotenv()
    cfg = Config.from_env()

    if not cfg.tmdb_token:
        print("Add your TMDB access token to .env (see .env.example).")
        sys.exit(1)

    db.create_tables(cfg.database)

    release_year = 2010
    movies = api.fetch_top_movies(release_year=release_year, auth_token=cfg.tmdb_token)
    print(f"Fetched {len(movies)} pages for {release_year}.")
    for movie in movies:
        db.save_movies(cfg.database, movie)

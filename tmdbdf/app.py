import sys

from dotenv import load_dotenv  # pyright: ignore[reportUnknownVariableType]

from tmdbdf import api, db
from tmdbdf.config import Config


def print_help() -> None:
    print("Usage: tmdbdf <command> [args]")
    print("Commands:")
    print("  add <release_year>          Fetch and store top movies for a year")
    print("  query <title_of_movie>      Search stored movies by title")
    print("  -h, --help                  Show this help")


def query_movies(title: str) -> None:
    pass


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print_help()
            sys.exit(1)
        load_dotenv()
        cfg = Config.from_env()
        release_year = int(sys.argv[2])
        if not cfg.tmdb_token:
            print("Add your TMDB access token to .env (see .env.example).")
            sys.exit(1)
        db.create_tables(cfg.database)
        movies = api.fetch_top_movies(release_year=release_year, pages=10, auth_token=cfg.tmdb_token)
        print(f"Fetched {len(movies)} pages for {release_year}.")
        for movie in movies:
            db.save_movies(cfg.database, movie)

    elif command == "query":
        if len(sys.argv) < 3:
            print_help()
            sys.exit(1)
        title = " ".join(sys.argv[2:])
        query_movies(title)

    else:
        print_help()
        sys.exit(1)

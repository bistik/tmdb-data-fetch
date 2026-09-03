import logging
import sys

from dotenv import load_dotenv  # pyright: ignore[reportUnknownVariableType]

from tmdbdf import cmd
from tmdbdf.config import Config


def _validate_command_arg():
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

def print_help() -> None:
    print("Usage: tmdbdf <command> [args]")
    print("Commands:")
    print("  add <release_year>          Fetch and store top movies for a year")
    print("  embed <release_year>        Generate embeddings for stored movies of a year")
    print("  query <title_of_movie>      Search stored movies by title")
    print("  -h, --help                  Show this help")


def query_movies(title: str) -> None:
    pass


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    load_dotenv()
    cfg = Config.from_env()
    logging.basicConfig(level=cfg.log_level)

    if command == "add":
        _validate_command_arg()
        release_year = int(sys.argv[2])
        if not cfg.tmdb_token:
            logging.error("Add your TMDB access token to .env (see .env.example).")
            sys.exit(1)
        cmd.add(cfg, release_year=release_year)

    elif command == "embed":
        _validate_command_arg()
        release_year = int(sys.argv[2])
        if not cfg.openai_api_key:
            logging.error("Add your opeani_api_key to .env (see .env.example).")
        if not cfg.chroma_db:
            logging.error("Add your chroma db data path to .env (see .env.example).")
        cmd.embed(cfg, release_year)

    elif command == "query":
        _validate_command_arg()
        title = " ".join(sys.argv[2:])
        cmd.find_similar(cfg, title=title)
        query_movies(title)

    else:
        print_help()
        sys.exit(1)

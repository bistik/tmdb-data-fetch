import logging

from . import api, chroma, config, db


def add(cfg: config.Config, release_year: int) -> None:
    db.create_tables(cfg.database)
    movies = api.fetch_top_movies(release_year=release_year, pages=10, auth_token=cfg.tmdb_token)
    logging.info(f"Fetched {len(movies)} pages for {release_year}.")
    add_count = 0
    for movie in movies:
        add_count += db.save_movies(cfg.database, movie)
    print(f"Added {add_count} movies to database.")

def embed(cfg: config.Config, release_year: int) -> None:
    movies = db.get_movies_by_release_year(cfg.database, release_year)
    before_count = chroma.get_count(cfg)
    if not movies:
        logging.info(f"Movies for year {release_year} either don't exist or already has embeddings.")
        return

    ids = []
    documents = []
    metadatas = []
    for movie in movies:
        ids.append(str(movie['id']))
        documents.append(movie['overview'])
        metadatas.append({'title': movie['title'], 'tmdb_id': movie['tmdb_id'], 'release_year': release_year})

    chroma.add_embeddings(cfg, ids, documents, metadatas)
    after_count = chroma.get_count(cfg)
    if after_count > before_count:
        # mark records that has embedding
        db.mark_movies_has_embedding(cfg.database, [movie['id'] for movie in movies])

    print(f"Added {after_count - before_count} embeddings to database.")

def find_similar(cfg: config.Config, title: str):
    movie = db.get_movie_by_title(cfg.database, title=title)
    movie_ids = chroma.find_similar(cfg, movie=movie, count=5)
    if movie_ids:
        logging.info('Similar movie IDs %s', movie_ids[0])
        similar_movies = db.get_movies_by_ids(cfg.database, [int(id) for id in movie_ids[0]])
        for sm in similar_movies:
            print(f"\n\tTitle: {sm['title']}")
            print(f"\tOverview: {sm['overview'][:100]}...")
            print(f"\tDate: {sm['release_date']}")

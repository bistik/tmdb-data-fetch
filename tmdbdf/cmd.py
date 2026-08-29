from . import api, config, db, chroma

def add(cfg: config.Config, release_year: int) -> None:
    db.create_tables(cfg.database)
    movies = api.fetch_top_movies(release_year=release_year, pages=10, auth_token=cfg.tmdb_token)
    print(f"Fetched {len(movies)} pages for {release_year}.")
    for movie in movies:
        db.save_movies(cfg.database, movie)

def embed(cfg: config.Config, release_year: int) -> None:
    movies = db.get_movies_by_release_year(cfg.database, release_year)
    if not movies:
        print(f"No movies found for {release_year}.")
        return
    ids = []
    documents = []
    metadatas = []
    for movie in movies:
        ids.append(str(movie['id']))
        documents.append(movie['overview'])
        metadatas.append({'title': movie['title'], 'tmdb_id': movie['tmdb_id'], 'release_year': release_year})

    collection_count = chroma.add_embeddings(cfg, ids, documents, metadatas)
    print(f"Collection count: {collection_count}")

def find_similar(cfg: config.Config, title: str):
    movie = db.get_movie_by_title(cfg.database, title=title)
    results = chroma.find_similar(cfg, movie=movie)
    print(results)

import logging
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from . import config


def _get_collection(dbpath: str, api_key: str = None, collection_name: str = "tmdb"):
    client = chromadb.PersistentClient(path=dbpath)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small"
        ),
    )
    return collection

def _get_embeddings(cfg: config.Config, id: int):
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    results = collection.get(
        ids=[str(id)],
        include=["embeddings", "metadatas"]
    )
    if results["ids"] and len(results["embeddings"]) > 0:
        return results["embeddings"]
    logging.info("No embeddings found for ID %s", id)


def add_embeddings(cfg: config.Config, ids, documents, metadatas) -> None:
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

def find_similar(cfg: config.Config, movie: dict, count: int = 3):
    embeddings = _get_embeddings(cfg, movie["id"])
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    if embeddings is not None and len(embeddings) > 0:
        results = collection.query(
            query_embeddings=embeddings,
            n_results=count,
            where={
                "title": {"$ne": movie["title"]}
            }
        )
        if results['ids']:
            logging.debug('results distances (ID, distance) %s', list(zip(results['ids'], results['distances'])))
            return results['ids']
    logging.info("No embeddings found for movie %s", movie)

def get_count(cfg: config.Config) -> int:
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    return collection.count()

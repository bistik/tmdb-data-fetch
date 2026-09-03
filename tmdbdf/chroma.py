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

def add_embeddings(cfg: config.Config, ids, documents, metadatas) -> None:
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

def find_similar(cfg: config.Config, movie: dict):
    querty_texts = [movie["overview"]]
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    return collection.query(
        query_texts=querty_texts,
        n_results=3
    )

def get_count(cfg: config.Config) -> int:
    collection = _get_collection(cfg.chroma_db, cfg.openai_api_key)
    return collection.count()

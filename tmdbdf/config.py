import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    database: str
    tmdb_token: str
    openai_api_key: str
    chroma_db: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            database=os.getenv("SQLITE_DATABASE", "tmdbdf.db"),
            tmdb_token=os.getenv("TMDB_AUTH_TOKEN", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            chroma_db=os.getenv("CHROMA_DATABASE", ""),
        )

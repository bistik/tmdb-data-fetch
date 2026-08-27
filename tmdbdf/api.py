import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _auth_headers(auth_token: str) -> dict:
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


def fetch_top_movies(
    release_year: int,
    pages: int = 10,
    auth_token: str = "",
    base_url: str = TMDB_BASE_URL,
) -> list[dict]:
    headers = _auth_headers(auth_token)
    results: list[dict] = []
    for page in range(pages):
        url = f"{base_url}/discover/movie?primary_release_year={release_year}&page={page + 1}&vote_count.gte=500&sort_by=vote_average.desc"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        result["url"] = url
        print(f"PAGE: {page + 1}", result.keys())
        results.append(result)
    return results

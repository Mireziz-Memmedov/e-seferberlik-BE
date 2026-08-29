from .normalization import normalize_text


MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 1000


def validate_query(query: str) -> bool:
    if not isinstance(query, str):
        return False

    query = query.strip()

    if len(query) < MIN_QUERY_LENGTH:
        return False

    if len(query) > MAX_QUERY_LENGTH:
        return False

    if not normalize_text(query):
        return False

    return True


def validate_result(result: dict) -> bool:
    if not isinstance(result, dict):
        return False

    article = result.get("article")

    if article is None:
        return False

    score = result.get("score")

    if score is not None:
        try:
            score = float(score)
        except (TypeError, ValueError):
            return False

        if not 0.0 <= score <= 1.0:
            return False

    return True


def filter_valid_results(results: list[dict]) -> list[dict]:
    if not results:
        return []

    return [
        result
        for result in results
        if validate_result(result)
    ]
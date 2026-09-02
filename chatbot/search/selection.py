# from .validation import filter_valid_results


# DEFAULT_LIMIT = 5
# MIN_SCORE = 0.20


# def select_results(
#     results: list[dict],
#     limit: int = DEFAULT_LIMIT,
#     min_score: float = MIN_SCORE,
# ) -> list[dict]:
#     if not results:
#         return []

#     valid_results = filter_valid_results(results)

#     selected = [
#         result
#         for result in valid_results
#         if result.get("score", 0.0) >= min_score
#     ]

#     selected.sort(
#         key=lambda result: result.get("score", 0.0),
#         reverse=True,
#     )

#     return selected[:limit]
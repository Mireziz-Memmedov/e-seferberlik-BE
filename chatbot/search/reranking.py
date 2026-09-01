from .scoring import calculate_score


def rerank_results(
    results: list[dict],
    *,
    limit: int = 10,
) -> list[dict]:
    """
    Search nəticələrini yekun score-a görə sıralayır.
    """

    reranked = []

    for result in results:
        semantic_score = result.get("semantic_score", 0.0)
        lexical_score = result.get("lexical_score", 0.0)
        intent_score = result.get("intent_score", 0.0)
        article_score = result.get("article_score", 0.0)
        phrase_score = result.get("phrase_score", 0.0)

        final_score = calculate_score(
            semantic_score=semantic_score,
            lexical_score=lexical_score,
            intent_score=intent_score,
            article_score=article_score,
            phrase_score=phrase_score,
        )

        item = dict(result)
        item["score"] = final_score

        reranked.append(item)

    reranked.sort(
        key=lambda item: item.get("score", 0.0),
        reverse=True,
    )

    return reranked[:limit]
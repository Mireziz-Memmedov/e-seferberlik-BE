from .normalization import normalize_text, tokenize
from .intents import analyze_intent
from .semantic import hybrid_search
from .lexical import lexical_search
from .reranking import rerank_results
from .selection import select_results
from .validation import validate_query


def search(
    query: str,
    limit: int = 5,
) -> list[dict]:

    # =========================================================
    # 1. VALIDATION
    # =========================================================

    if not validate_query(query):
        return []

    # =========================================================
    # 2. NORMALIZATION
    # =========================================================

    normalized = normalize_text(query)
    keywords = tokenize(normalized)

    # =========================================================
    # 3. ARTICLE NUMBER EXTRACTION
    # =========================================================

    import re

    article_numbers = []

    if "madd" in normalized:
        article_numbers = re.findall(
            r"\b\d+(?:\.\d+)*\b",
            normalized,
        )

    # =========================================================
    # 4. INTENT ANALYSIS
    # =========================================================

    analysis = analyze_intent(
        normalized=normalized,
        keywords=keywords,
        phrases=[],
        article_numbers=article_numbers,
    )

    if not isinstance(analysis, dict):
        analysis = {}

    # =========================================================
    # 5. SEMANTIC SEARCH
    # =========================================================

    semantic_results = hybrid_search(
        query,
        limit=20,
    )

    question_type = analysis.get("question_type", "general")

    # =========================================================
    # 6. LEXICAL SEARCH
    # =========================================================

    lexical_results = lexical_search(
        normalized,
        limit=30,
    )

    results = {}

    # =========================================================
    # 7. SEMANTIC RESULTS
    # =========================================================

    for item in semantic_results:

        article = item.get("article")
        distance = item.get("distance", 1.0)

        if article is None:
            continue

        article_id = getattr(article, "id", None)

        if not article_id:
            continue

        similarity_score = max(
            0.0,
            min(
                1.0,
                1.0 - float(distance),
            ),
        )

        results[article_id] = {
            "article": article,
            "semantic_score": similarity_score,
            "lexical_score": 0.0,
            "intent_score": 0.0,
            "article_score": 0.0,
            "phrase_score": 0.0,
        }

    # =========================================================
    # 8. LEXICAL RESULTS
    # =========================================================

    for item in lexical_results:

        article = item.get("article")

        if article is None:
            continue

        article_id = getattr(article, "id", None)

        if not article_id:
            continue

        if article_id not in results:
            results[article_id] = {
                "article": article,
                "semantic_score": 0.0,
                "lexical_score": 0.0,
                "intent_score": 0.0,
                "article_score": 0.0,
                "phrase_score": 0.0,
            }

        coverage = item.get("coverage", 0.0)

        try:
            coverage = float(coverage)
        except (TypeError, ValueError):
            coverage = 0.0

        results[article_id]["lexical_score"] = max(
            0.0,
            min(1.0, coverage),
        )

    # =========================================================
    # 9. INTENT SCORE
    # =========================================================

    intents = analysis.get("intents", set())

    if intents:

        for result in results.values():

            article = result["article"]

            title = getattr(article, "title", "") or ""
            content = getattr(article, "content", "") or ""

            article_text = normalize_text(
                f"{title} {content}"
            )

            matched_intents = sum(
                1
                for intent in intents
                if normalize_text(intent) in article_text
            )

            result["intent_score"] = min(
                1.0,
                matched_intents / len(intents),
            )

    # =========================================================
    # 10. ARTICLE NUMBER SCORE
    # =========================================================

    if article_numbers:

        for result in results.values():

            article = result["article"]

            article_number = getattr(
                article,
                "number",
                "",
            )

            article_number = normalize_text(
                str(article_number or "")
            )

            for target_number in article_numbers:

                if normalize_text(
                    str(target_number)
                ) == article_number:

                    result["article_score"] = 1.0
                    break

    # =========================================================
    # 11. RERANK
    # =========================================================

    reranked = rerank_results(
        list(results.values()),
        limit=20,
    )

    print("=== DEBUG SEARCH ===")
    print("RESULTS BEFORE RERANK:", len(results))
    print("RERANKED:", len(reranked))
    print("RERANKED DATA:", [
        (x["article"].number, x.get("score"))
        for x in reranked[:10]
    ])

    selected = select_results(
        reranked,
        limit=limit,
    )

    print("SELECTED:", len(selected))
    print("SELECTED DATA:", selected)

    return selected
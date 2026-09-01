from .normalization import normalize_text
from .intents import analyze_intent
from .semantic import semantic_search
from .lexical import lexical_search
from .reranking import rerank_results
from .selection import select_results
from .validation import validate_query


def search(
    query: str,
    limit: int = 5,
) -> list[dict]:

    if not validate_query(query):
        return []

    normalized = normalize_text(query)
    analysis = analyze_query(query)

    semantic_results = semantic_search(
        normalized,
        limit=20,
    )

    lexical_results = lexical_search(
        normalized,
        limit=30,
    )

    results = {}

    # -----------------------------
    # 1. SEMANTIC SEARCH INTEGRATION
    # -----------------------------
    for item in semantic_results:
        # semantic_search-in qaytardığı struktura əsasən article və distance təyini
        article = item.get("article", item) if isinstance(item, dict) else item
        article_id = article.id

        distance = getattr(article, "distance", item.get("distance", 0.0) if isinstance(item, dict) else 0.0)
        similarity_score = max(0.0, 1.0 - float(distance))

        results[article_id] = {
            "article": article,
            "semantic_score": similarity_score,
            "lexical_score": 0.0,
            "intent_score": 0.0,
            "article_score": 0.0,
            "phrase_score": 0.0,
        }

    # -----------------------------
    # 2. LEXICAL SEARCH INTEGRATION
    # -----------------------------
    for item in lexical_results:
        article = item["article"]
        article_id = article.id

        if article_id not in results:
            results[article_id] = {
                "article": article,
                "semantic_score": 0.0,
                "lexical_score": 0.0,
                "intent_score": 0.0,
                "article_score": 0.0,
                "phrase_score": 0.0,
            }

        results[article_id]["lexical_score"] = min(
            1.0,
            float(item.get("coverage", 0.0)),
        )

    # -----------------------------
    # 3. INTENT ANALYSIS
    # -----------------------------
    intents = analysis.get("intents", set())

    if intents:
        for result in results.values():
            article = result["article"]
            article_text = normalize_text(
                f"{article.title or ''} {article.content or ''}"
            )

            matched_intents = sum(
                1 for intent in intents if normalize_text(intent) in article_text
            )

            result["intent_score"] = min(
                1.0,
                matched_intents / len(intents),
            )

    # -----------------------------
    # 4. ARTICLE NUMBER MATCHING
    # -----------------------------
    article_numbers = analysis.get("article_numbers", [])

    if article_numbers:
        for result in results.values():
            article = result["article"]
            art_num_str = normalize_text(str(article.article_number or ""))
            art_content_str = normalize_text(f"{article.title or ''} {article.content or ''}")

            # Maddə nömrəsi həm article_number sahəsində, həm də mətndə dəqiq uyğunlaşa bilsin
            for target_num in article_numbers:
                target_norm = normalize_text(target_num)
                if target_norm == art_num_str or target_norm in art_content_str:
                    result["article_score"] = 1.0
                    break

    # -----------------------------
    # 5. RERANK & FINAL SELECTION
    # -----------------------------
    reranked = rerank_results(
        list(results.values()),
        limit=20,
    )

    return select_results(
        reranked,
        limit=limit,
    )
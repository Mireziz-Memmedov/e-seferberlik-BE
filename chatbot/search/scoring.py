def calculate_score(
    *,
    semantic_score: float = 0.0,
    lexical_score: float = 0.0,
    intent_score: float = 0.0,
    article_score: float = 0.0,
    phrase_score: float = 0.0,
) -> float:
    """
    Bütün axtarış siqnallarını vahid score-a çevirir (Cəm: 1.0).
    """
    # Giriş parametrlərini 0.0 - 1.0 aralığında limitləyirik
    sem = max(0.0, min(1.0, float(semantic_score)))
    lex = max(0.0, min(1.0, float(lexical_score)))
    intent = max(0.0, min(1.0, float(intent_score)))
    art = max(0.0, min(1.0, float(article_score)))
    phrase = max(0.0, min(1.0, float(phrase_score)))

    # Yaxşılaşdırılmış Çəki Balansı:
    # 1. Dəqiq Maddə Nömrəsi (Article): 0.30 -> Dəqiq bənd sorğularında önə çıxması üçün
    # 2. Semantik Məna (Semantic): 0.35 -> Təbii dildə verilən suallar üçün
    # 3. Söz Oxşarlığı (Lexical): 0.15
    # 4. Intent & Phrase: 0.10 + 0.10
    score = (
        sem * 0.35
        + art * 0.30
        + lex * 0.15
        + intent * 0.10
        + phrase * 0.10
    )

    return round(score, 6)


def normalize_score(score: float) -> float:
    """Əgər haradasa xarici balı normallaşdırmaq lazımdırsa saxlanılır."""
    return max(0.0, min(1.0, float(score)))
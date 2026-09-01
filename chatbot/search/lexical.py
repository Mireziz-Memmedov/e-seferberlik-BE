from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from chatbot.models import Article
from .normalization import normalize_text, tokenize


def lexical_search(query: str, limit: int = 30):
    normalized_query = normalize_text(query)
    query_words = tokenize(normalized_query)

    if not query_words:
        return []

    unique_words = set(query_words)

    # 1. Açar sözlər üzrə baza filtri
    word_query = Q()
    for word in unique_words:
        word_query |= Q(title__icontains=word) | Q(content__icontains=word)

    # 2. Bazada Trigram axtarışı (yalnız uyğun gələn məqalələr çəkilir)
    articles = (
        Article.objects
        .filter(word_query)
        .annotate(
            similarity=TrigramSimilarity("content", normalized_query) + 
                       TrigramSimilarity("title", normalized_query)
        )
        .filter(similarity__gt=0.05)
        .only("id", "title", "content", "law_id", "article_number")
        .order_by("-similarity")[:limit]
    )

    # 3. Orijinal strukturla 100% uyğun çıxış
    results = []
    for article in articles:
        text = normalize_text(f"{article.title or ''} {article.content or ''}")
        text_words = set(tokenize(text))

        # Neçə dənə unikal sorğu sözünün mətndə olduğunu tapırıq (Integer)
        matched_count = sum(1 for word in unique_words if word in text_words)

        results.append({
            "article": article,
            "matched": matched_count,
            "coverage": round(article.similarity, 4),  # Trigram oxşarlıq balı
        })

    return results
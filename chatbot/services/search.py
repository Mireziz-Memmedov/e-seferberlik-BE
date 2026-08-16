from chatbot.models import Article


STOP_WORDS = {
    "mən",
    "sən",
    "siz",
    "biz",
    "bu",
    "bir",
    "və",
    "ilə",
    "üçün",
    "olan",
    "olaraq",
    "haqqında",
    "necə",
    "nədir",
    "kimdir",
    "kimlər",
    "edə",
    "edilir",
    "edən",
    "mənim",
    "sənin",
    "var",
    "mi",
    "mı",
    "mu",
    "mü",
}


def normalize_text(text):
    """
    Azərbaycan dilində mətnin müqayisəsini
    sadələşdirir.
    """

    text = text.lower().strip()

    replacements = {
        "ə": "e",
        "ı": "i",
        "ö": "o",
        "ü": "u",
        "ğ": "g",
        "ş": "s",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def get_keywords(question):
    """
    Sualdan əsas açar sözləri çıxarır.
    """

    normalized = normalize_text(question)

    words = normalized.split()

    keywords = []

    for word in words:

        word = word.strip(
            ".,!?;:()[]{}\"'"
        )

        if not word:
            continue

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        keywords.append(word)

    return keywords


def search_articles(question, limit=5):
    """
    Suala uyğun qanun maddələrini tapır.

    Nəticələr score-a görə sıralanır.
    Eyni Article yalnız bir dəfə qaytarılır.
    """

    keywords = get_keywords(question)

    if not keywords:
        return []

    articles = (
        Article.objects
        .select_related("law")
        .all()
    )

    scored_articles = []

    for article in articles:

        title = normalize_text(
            article.title or ""
        )

        content = normalize_text(
            article.content or ""
        )

        full_text = f"{title} {content}"

        score = 0

        for keyword in keywords:

            # Başlıqda söz varsa daha yüksək bal
            if keyword in title:
                score += 5

            # Məzmun daxilində söz varsa
            if keyword in content:
                score += 1

        if score > 0:
            scored_articles.append(
                {
                    "article": article,
                    "score": score,
                }
            )

    # Ən uyğun maddələr əvvəl
    scored_articles.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Duplicate Article-ləri çıxar
    unique_articles = []

    seen_ids = set()

    for item in scored_articles:

        article = item["article"]

        if article.id in seen_ids:
            continue

        seen_ids.add(article.id)

        unique_articles.append(
            article
        )

        if len(unique_articles) >= limit:
            break

    return unique_articles
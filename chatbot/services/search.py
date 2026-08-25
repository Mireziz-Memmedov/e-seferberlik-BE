import re

from openai import OpenAI
from django.conf import settings
from pgvector.django import CosineDistance

from chatbot.models import Article


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# -----------------------------------------
# STOP WORDS
# -----------------------------------------

STOP_WORDS = {
    "men",
    "sen",
    "siz",
    "biz",
    "bu",
    "bir",
    "ve",
    "ile",
    "ucun",
    "olan",
    "olaraq",
    "haqqinda",
    "nece",
    "nedir",
    "kimdir",
    "kimler",
    "hansi",
    "hansilar",
    "eden",
    "edilir",
    "edilmesi",
    "var",
    "mi",
    "mı",
    "mu",
    "mü",
}


# -----------------------------------------
# NORMALIZE
# -----------------------------------------

def normalize_text(text):
    """
    Azərbaycan dilində mətnin müqayisəsini
    sadələşdirir.
    """

    if not text:
        return ""

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


# -----------------------------------------
# KEYWORDS
# -----------------------------------------

def get_keywords(question):
    """
    Sualdan əsas sözləri çıxarır.
    """

    normalized = normalize_text(question)

    words = re.findall(
        r"[a-z0-9-]+",
        normalized
    )

    keywords = []

    for word in words:

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords


# -----------------------------------------
# INTENT KEYWORDS
# -----------------------------------------

INTENTS = {

    "azadetme": {
        "azad",
        "azaddır",
        "azaddir",
        "azadlar",
        "azadetme",
        "azad edil",
        "azad olunur",
        "azad edilir",
        "azad olan",
        "kimler azaddır",
    },

    "toplanis": {
        "toplanis",
        "toplanislara",
        "toplanisa",
        "telim",
        "telime",
        "telimler",
        "cagir",
        "cagirilan",
        "cagirilir",
    },

    "ehtiyat": {
        "ehtiyat",
        "ehtiyatda",
        "ehtiyatdaki",
        "ehtiyatda olan",
    },

    "muddet": {
        "muddet",
        "nece",
        "ne qeder",
        "ne qederlik",
        "ayadek",
        "defeyedek",
    },
}


def detect_intents(question):
    """
    Sualın əsas hüquqi mövzusunu müəyyən edir.
    """

    normalized = normalize_text(question)

    detected = set()

    for intent, phrases in INTENTS.items():

        for phrase in phrases:

            normalized_phrase = normalize_text(
                phrase
            )

            if normalized_phrase in normalized:
                detected.add(intent)
                break

    return detected


# -----------------------------------------
# INTENT SCORE
# -----------------------------------------

def calculate_intent_score(
    article,
    intents
):
    """
    Maddənin başlığının və məzmununun
    sualın hüquqi mövzusu ilə uyğunluğunu
    əlavə balla qiymətləndirir.
    """

    if not intents:
        return 0

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    full_text = f"{title} {content}"

    score = 0

    # -------------------------------------
    # AZADOLMA
    # -------------------------------------

    if "azadetme" in intents:

        if "azadetme" in title:
            score += 50

        if "azad" in title:
            score += 30

        if "azad" in content:
            score += 15

        # "Toplanışlardan azadetmə" kimi başlıqlar
        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 40

    # -------------------------------------
    # TOPLANIŞ / TƏLİM
    # -------------------------------------

    if "toplanis" in intents:

        if "toplanis" in title:
            score += 25

        if "telim" in title:
            score += 20

        if "cagiril" in content:
            score += 10

    # -------------------------------------
    # EHTİYAT
    # -------------------------------------

    if "ehtiyat" in intents:

        if "ehtiyat" in title:
            score += 25

        if "ehtiyat" in content:
            score += 8

    # -------------------------------------
    # MÜDDƏT
    # -------------------------------------

    if "muddet" in intents:

        if "muddet" in title:
            score += 15

        if "muddet" in content:
            score += 5

    return score


# -----------------------------------------
# SEARCH
# -----------------------------------------

def search_articles(
    question,
    limit=5
):
    """
    Suala uyğun qanun maddələrini tapır.

    Axtarış:
    1. Embedding / semantic similarity
    2. Başlıq uyğunluğu
    3. Məzmun uyğunluğu
    4. Açar sözlərin uyğunluğu
    5. Sualın hüquqi intenti

    Daha uyğun hüquqi maddələr yuxarı çıxır.
    """

    if not question:
        return []

    question = question.strip()

    if not question:
        return []

    # -----------------------------------------
    # KEYWORDS
    # -----------------------------------------

    keywords = get_keywords(question)

    # -----------------------------------------
    # INTENTS
    # -----------------------------------------

    intents = detect_intents(question)

    # -----------------------------------------
    # QUESTION EMBEDDING
    # -----------------------------------------

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = response.data[0].embedding

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    articles = (
        Article.objects
        .select_related("law")
        .exclude(embedding=None)
        .annotate(
            distance=CosineDistance(
                "embedding",
                question_embedding
            )
        )
        .order_by("distance")[:20]
    )

    scored_articles = []

    normalized_question = normalize_text(
        question
    )

    # -----------------------------------------
    # SCORE
    # -----------------------------------------

    for article in articles:

        title = normalize_text(
            article.title or ""
        )

        content = normalize_text(
            article.content or ""
        )

        full_text = f"{title} {content}"

        # Semantic similarity
        semantic_score = max(
            0,
            1 - float(article.distance)
        )

        score = semantic_score * 30

        matched_keywords = 0

        # -------------------------------------
        # KEYWORD MATCHING
        # -------------------------------------

        for keyword in keywords:

            if keyword in title:
                score += 12
                matched_keywords += 1

            elif keyword in content:
                score += 3
                matched_keywords += 1

        # -------------------------------------
        # ALL KEYWORDS
        # -------------------------------------

        if keywords:

            all_keywords_match = all(
                keyword in full_text
                for keyword in keywords
            )

            if all_keywords_match:
                score += 15

        # -------------------------------------
        # EXACT QUESTION
        # -------------------------------------

        if normalized_question in title:
            score += 30

        if normalized_question in content:
            score += 20

        # -------------------------------------
        # INTENT SCORE
        # -------------------------------------

        intent_score = calculate_intent_score(
            article,
            intents
        )

        score += intent_score

        # -------------------------------------
        # COVERAGE
        # -------------------------------------

        if keywords:

            coverage = (
                matched_keywords
                / len(keywords)
            )

            score += coverage * 10

        # -------------------------------------
        # RESULT
        # -------------------------------------

        scored_articles.append(
            {
                "article": article,
                "score": score,
                "semantic_score": semantic_score,
                "matched_keywords": matched_keywords,
                "intent_score": intent_score,
            }
        )

    # -----------------------------------------
    # SORT
    # -----------------------------------------

    scored_articles.sort(
        key=lambda item: (
            item["score"],
            item["matched_keywords"],
            item["semantic_score"],
        ),
        reverse=True,
    )

    # -----------------------------------------
    # DEBUG
    # -----------------------------------------

    print(
        "\n================ SEARCH DEBUG ================"
    )

    print(
        f"QUESTION: {question}"
    )

    print(
        f"KEYWORDS: {keywords}"
    )

    print(
        f"INTENTS: {intents}"
    )

    print(
        "\nTOP RESULTS:"
    )

    for index, item in enumerate(
        scored_articles[:10],
        start=1
    ):

        article = item["article"]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Semantic={item['semantic_score']:.4f} | "
            f"Keywords={item['matched_keywords']} | "
            f"Intent={item['intent_score']} | "
            f"{article.title}"
        )

    print(
        "==============================================\n"
    )

    # -----------------------------------------
    # RETURN UNIQUE ARTICLES
    # -----------------------------------------

    results = []

    seen_ids = set()

    for item in scored_articles:

        article = item["article"]

        if article.id in seen_ids:
            continue

        seen_ids.add(article.id)

        results.append(article)

        if len(results) >= limit:
            break

    return results


import re

from openai import OpenAI
from django.conf import settings
from pgvector.django import CosineDistance

from chatbot.models import Article


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# =========================================================
# STOP WORDS
# =========================================================

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
    "verilen",
    "verilir",
    "verilirmi",
    "var",
    "mi",
    "mı",
    "mu",
    "mü",
    "de",
    "da",
    "ki",
    "gore",

    # Danışıq / qrammatik sözlər
    "menim",
    "senin",
    "sizin",
    "bizim",
    "oldugum",
    "oldugun",
    "oldugu",
    "olduqda",
    "halda",
    "halinda",
    "bilerem",
    "bilərəm",
    "biler",
    "bilermi",
    "bilərmi",
}


# =========================================================
# NORMALIZE
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower().strip()

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

    text = re.sub(r"\s+", " ", text)

    return text


# =========================================================
# KEYWORDS
# =========================================================

def get_keywords(question):

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


# =========================================================
# RELATED WORDS
# =========================================================

RELATED_WORDS = {

    # -----------------------------------------------------
    # TOPLANIŞ
    # -----------------------------------------------------

    "toplanis": {
        "toplanis",
        "toplanisa",
        "toplanisdan",
        "toplanislardan",
        "toplanislara",
        "toplanislar",
        "telim",
        "telime",
        "telimden",
        "telimler",
        "telimlere",
    },

    # -----------------------------------------------------
    # ÇAĞIRIŞ
    # -----------------------------------------------------

    "cagiris": {
        "cagiris",
        "cagirisdan",
        "cagirisa",
        "cagirisla",
        "cagir",
        "cagirilir",
        "cagirilirler",
        "cagirilacaq",
        "cagirilmasi",
        "cagirilma",
        "cagirila",
        "cagirilmaq",
        "cagirilmag",
    },

    # -----------------------------------------------------
    # AZADOLMA
    # -----------------------------------------------------

    "azadetme": {
        "azad",
        "azaddir",
        "azadliq",
        "azadlar",
        "azadetme",
        "azad edilen",
        "azad edilir",
        "azad olunur",
        "azad edilmis",
        "azad edilmesi",
    },

    # -----------------------------------------------------
    # MÖHLƏT
    # -----------------------------------------------------

    "mohlet": {
        "mohlet",
        "mohletin",
        "mohletle",
        "mohletler",
        "mohletden",
        "mohlet verilmesi",
        "mohlet verilir",
        "mohlet verilm",
    },

    # -----------------------------------------------------
    # SAĞLAMLIQ
    # -----------------------------------------------------

    "saglamliq": {
        "saglamliq",
        "saglamlig",
        "saglamligina",
        "saglamligindan",
        "saglamliqdan",
        "saglamliq veziyyeti",
        "saglamliq veziyyetine",
        "saglamliq veziyyetinden",
    },

    # -----------------------------------------------------
    # AİLƏ
    # -----------------------------------------------------

    "aile": {
        "aile",
        "ailesi",
        "ailenin",
        "aileye",
        "ailevi",
        "aile veziyyeti",
        "aile veziyyetine",

        # Uşaq / övlad
        "usaq",
        "usag",
        "usagi",
        "usagim",
        "usaqlar",
        "usaglar",
        "usaqlari",
        "usaglari",
        "usaqlarin",
        "usaglarin",

        "ovlad",
        "ovladi",
        "ovladim",
        "ovladlar",
        "ovladlari",
        "ovladlarin",

        # Say ilə istifadə oluna bilən ifadələr
        "iki usaq",
        "uc usaq",
        "dord usaq",
        "bes usaq",
        "alti usaq",
    },

    # -----------------------------------------------------
    # TƏHSİL
    # -----------------------------------------------------

    "tehsil": {
        "tehsil",
        "tehsili",
        "tehsile",
        "tehsilde",
        "tehsil alan",
        "tehsil etmek",
        "tehsil alanlar",
    },

    # -----------------------------------------------------
    # EHTİYAT
    # -----------------------------------------------------

    "ehtiyat": {
        "ehtiyat",
        "ehtiyatda",
        "ehtiyatdaki",
        "ehtiyatdakilar",
        "ehtiyatda olan",
        "ehtiyatda olanlar",
    },

    # -----------------------------------------------------
    # MÜDDƏT
    # -----------------------------------------------------

    "muddet": {
        "muddet",
        "muddeti",
        "muddetler",
        "muddetde",
        "defe",
        "defeyedek",
    },
}


# =========================================================
# INTENTS
# =========================================================

INTENTS = {

    "toplanis": {
        "toplanis",
        "toplanisdan",
        "toplanislardan",
        "toplanisa",
        "toplanislara",
        "telim",
        "telime",
        "telimden",
        "telimler",
        "telimlere",
    },

    "azadetme": {
        "azad",
        "azaddir",
        "azadetme",
        "azadliq",
    },

    "mohlet": {
        "mohlet",
        "mohletin",
        "mohletle",
        "mohletler",
    },

    "saglamliq": {
        "saglamliq",
        "saglamlig",
        "saglamligina",
    },

    "aile": {
        "aile",
        "ailesi",
        "ailenin",
        "ailevi",

        "usaq",
        "usag",
        "usagi",
        "usagim",
        "usaqlar",
        "usaglar",
        "usaqlari",
        "usaglari",
        "usaqlarin",
        "usaglarin",

        "ovlad",
        "ovladi",
        "ovladim",
        "ovladlar",
        "ovladlari",
        "ovladlarin",
    },

    "tehsil": {
        "tehsil",
        "tehsili",
        "tehsile",
    },

    "cagiris": {
        "cagiris",
        "cagirisdan",
        "cagirisa",
        "cagirila",
        "cagir",
    },

    "ehtiyat": {
        "ehtiyat",
        "ehtiyatda",
        "ehtiyatdaki",
        "ehtiyatdakilar",
    },
}


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intents(question):

    normalized = normalize_text(question)

    detected = set()

    for intent, words in INTENTS.items():

        for word in words:

            normalized_word = normalize_text(word)

            if re.search(
                rf"\b{re.escape(normalized_word)}\b",
                normalized
            ):
                detected.add(intent)
                break

    # -----------------------------------------------------
    # UŞAQ / ÖVLAD MƏNTİQİ
    # -----------------------------------------------------

    family_patterns = [
        r"\b\d+\s+usaq\b",
        r"\b\d+\s+usag\b",
        r"\b\d+\s+ovlad\b",
        r"\busaq\b",
        r"\busag\b",
        r"\bovlad\b",
    ]

    for pattern in family_patterns:

        if re.search(pattern, normalized):
            detected.add("aile")
            break

    return detected


# =========================================================
# QUESTION TYPE
# =========================================================

def detect_question_type(intents):

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):
        return "toplanis_ehtiyat_aile"

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
    ):
        return "toplanis_ehtiyat"

    # -----------------------------------------------------
    # TOPLANIŞ + AZADOLMA
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "azadetme" in intents
    ):
        return "toplanis_azadetme"

    # -----------------------------------------------------
    # ÇAĞIRIŞ + MÖHLƏT
    # -----------------------------------------------------

    if (
        "cagiris" in intents
        and "mohlet" in intents
    ):
        return "cagiris_mohlet"

    # -----------------------------------------------------
    # AİLƏ + MÖHLƏT
    # -----------------------------------------------------

    if (
        "aile" in intents
        and "mohlet" in intents
    ):
        return "aile_mohlet"

    # -----------------------------------------------------
    # SAĞLAMLIQ + MÖHLƏT
    # -----------------------------------------------------

    if (
        "saglamliq" in intents
        and "mohlet" in intents
    ):
        return "saglamliq_mohlet"

    # -----------------------------------------------------
    # TƏHSİL + MÖHLƏT
    # -----------------------------------------------------

    if (
        "tehsil" in intents
        and "mohlet" in intents
    ):
        return "tehsil_mohlet"

    # -----------------------------------------------------
    # SADƏ
    # -----------------------------------------------------

    if "azadetme" in intents:
        return "azadetme"

    if "mohlet" in intents:
        return "mohlet"

    if "toplanis" in intents:
        return "toplanis"

    if "cagiris" in intents:
        return "cagiris"

    return "general"


# =========================================================
# GROUP MATCH
# =========================================================

def matches_group(text, group_name):

    text = normalize_text(text)

    words = RELATED_WORDS.get(
        group_name,
        set()
    )

    for word in words:

        normalized_word = normalize_text(word)

        if re.search(
            rf"\b{re.escape(normalized_word)}\b",
            text
        ):
            return True

    return False


# =========================================================
# KEYWORD MATCH
# =========================================================

def keyword_matches(
    keyword,
    title,
    content
):

    keyword = normalize_text(keyword)
    title = normalize_text(title)
    content = normalize_text(content)

    # Birbaşa başlıq
    if re.search(
        rf"\b{re.escape(keyword)}\b",
        title
    ):
        return "title"

    # Birbaşa mətn
    if re.search(
        rf"\b{re.escape(keyword)}\b",
        content
    ):
        return "content"

    # Əlaqəli sözlər
    for group_name, words in RELATED_WORDS.items():

        normalized_words = {
            normalize_text(word)
            for word in words
        }

        if keyword in normalized_words:

            for related in normalized_words:

                if re.search(
                    rf"\b{re.escape(related)}\b",
                    title
                ):
                    return "related_title"

                if re.search(
                    rf"\b{re.escape(related)}\b",
                    content
                ):
                    return "related_content"

    return None


# =========================================================
# ARTICLE ROLE
# =========================================================

def detect_article_role(
    article,
    intents
):

    title = normalize_text(
        article.title or ""
    )

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):

        # Toplanışdan azadolmanı müəyyən edən maddə
        if (
            "toplanis" in title
            and "azad" in title
        ):
            return "primary"

        # Ehtiyatda olanların toplanışa çağırılması
        if (
            "ehtiyat" in title
            and (
                "toplanis" in title
                or "telim" in title
                or "cagiris" in title
            )
        ):
            return "primary"

        # Ailə / möhlət / çağırış maddəsi
        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return "companion"

    # -----------------------------------------------------
    # TOPLANIŞ + AZADOLMA
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "azadetme" in intents
    ):

        if (
            "toplanis" in title
            and "azad" in title
        ):
            return "primary"

        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return "companion"

        if (
            "saglamliq" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return "companion"

        if (
            "tehsil" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return "companion"

    return "normal"


# =========================================================
# RELATION SCORE
# =========================================================

def calculate_relation_score(
    article,
    intents
):

    title = normalize_text(
        article.title or ""
    )

    score = 0

    # =====================================================
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # =====================================================

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):

        # Toplanışdan azadolma
        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 500

        # Ehtiyat + toplanış
        if (
            "ehtiyat" in title
            and (
                "toplanis" in title
                or "telim" in title
                or "cagiris" in title
            )
        ):
            score += 400

        # Ailə + möhlət
        if (
            "aile" in title
            and "mohlet" in title
        ):
            score += 300

        # Ailə + çağırış
        elif (
            "aile" in title
            and "cagiris" in title
        ):
            score += 250

    # =====================================================
    # TOPLANIŞ + EHTİYAT
    # =====================================================

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
    ):

        if (
            "ehtiyat" in title
            and "toplanis" in title
        ):
            score += 450

        elif (
            "ehtiyat" in title
            and "telim" in title
        ):
            score += 300

        elif (
            "ehtiyat" in title
            and "cagiris" in title
        ):
            score += 300

        elif "toplanis" in title:
            score += 180

    # =====================================================
    # TOPLANIŞ + AZADOLMA
    # =====================================================

    if (
        "toplanis" in intents
        and "azadetme" in intents
    ):

        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 500

        if "aile" in intents:

            if (
                "aile" in title
                and (
                    "mohlet" in title
                    or "cagiris" in title
                )
            ):
                score += 300

        if "saglamliq" in intents:

            if (
                "saglamliq" in title
                and (
                    "mohlet" in title
                    or "cagiris" in title
                )
            ):
                score += 300

        if "tehsil" in intents:

            if (
                "tehsil" in title
                and (
                    "mohlet" in title
                    or "cagiris" in title
                )
            ):
                score += 300

    # =====================================================
    # AİLƏ + MÖHLƏT
    # =====================================================

    if (
        "aile" in intents
        and "mohlet" in intents
    ):

        if (
            "aile" in title
            and "mohlet" in title
        ):
            score += 350

        elif "aile" in title:
            score += 180

    # =====================================================
    # SAĞLAMLIQ + MÖHLƏT
    # =====================================================

    if (
        "saglamliq" in intents
        and "mohlet" in intents
    ):

        if (
            "saglamliq" in title
            and "mohlet" in title
        ):
            score += 350

        elif "saglamliq" in title:
            score += 180

    # =====================================================
    # TƏHSİL + MÖHLƏT
    # =====================================================

    if (
        "tehsil" in intents
        and "mohlet" in intents
    ):

        if (
            "tehsil" in title
            and "mohlet" in title
        ):
            score += 350

        elif "tehsil" in title:
            score += 180

    # =====================================================
    # SADƏ AZADOLMA
    # =====================================================

    if "azadetme" in intents:

        if (
            "azad" in title
            and "toplanis" in title
        ):
            score += 250

        elif "azad" in title:
            score += 120

    # =====================================================
    # SADƏ TOPLANIŞ
    # =====================================================

    if "toplanis" in intents:

        if "toplanis" in title:
            score += 120

        elif "telim" in title:
            score += 80

    return score


# =========================================================
# CONTEXT SCORE
# =========================================================

def calculate_context_score(
    article,
    intents
):

    title = normalize_text(
        article.title or ""
    )

    score = 0

    # =====================================================
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # =====================================================

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):

        # Toplanış maddəsi
        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 250

        # Ehtiyatda olanların çağırılması
        if (
            "ehtiyat" in title
            and (
                "toplanis" in title
                or "telim" in title
                or "cagiris" in title
            )
        ):
            score += 250

        # Ailə üzrə hüquqi əsas
        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            score += 200

    # =====================================================
    # TOPLANIŞ + AZADOLMA
    # =====================================================

    if (
        "toplanis" in intents
        and "azadetme" in intents
    ):

        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 180

        if "aile" in intents:

            if (
                "aile" in title
                and "mohlet" in title
            ):
                score += 180

        if "saglamliq" in intents:

            if (
                "saglamliq" in title
                and "mohlet" in title
            ):
                score += 180

        if "tehsil" in intents:

            if (
                "tehsil" in title
                and "mohlet" in title
            ):
                score += 180

    return score


# =========================================================
# DIRECT CONTEXT ARTICLE
# =========================================================

def is_direct_context_article(
    article,
    intents
):

    title = normalize_text(
        article.title or ""
    )

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # -----------------------------------------------------

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):

        if (
            "ehtiyat" in title
            and (
                "toplanis" in title
                or "telim" in title
                or "cagiris" in title
            )
        ):
            return True

        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return True

        if (
            "toplanis" in title
            and "azad" in title
        ):
            return True

    # -----------------------------------------------------
    # AİLƏ
    # -----------------------------------------------------

    if "aile" in intents:

        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return True

    # -----------------------------------------------------
    # SAĞLAMLIQ
    # -----------------------------------------------------

    if "saglamliq" in intents:

        if (
            "saglamliq" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return True

    # -----------------------------------------------------
    # TƏHSİL
    # -----------------------------------------------------

    if "tehsil" in intents:

        if (
            "tehsil" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            return True

    return False


# =========================================================
# CONTEXT ARTICLE DISCOVERY
# =========================================================

def get_context_articles(intents):

    context_articles = []

    # =====================================================
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # =====================================================

    if (
        "toplanis" in intents
        and "ehtiyat" in intents
        and "aile" in intents
    ):

        # -------------------------------------------------
        # EHTİYAT / TOPLANIŞ
        # -------------------------------------------------

        articles = (
            Article.objects
            .select_related("law")
            .exclude(embedding=None)
        )

        for article in articles:

            title = normalize_text(
                article.title or ""
            )

            if (
                "ehtiyat" in title
                and (
                    "toplanis" in title
                    or "telim" in title
                    or "cagiris" in title
                )
            ):
                context_articles.append(article)

        # -------------------------------------------------
        # TOPLANIŞDAN AZADOLMA
        # -------------------------------------------------

        articles = (
            Article.objects
            .select_related("law")
            .exclude(embedding=None)
        )

        for article in articles:

            title = normalize_text(
                article.title or ""
            )

            if (
                "toplanis" in title
                and "azad" in title
            ):
                context_articles.append(article)

        # -------------------------------------------------
        # AİLƏ / MÖHLƏT / ÇAĞIRIŞ
        # -------------------------------------------------

        articles = (
            Article.objects
            .select_related("law")
            .exclude(embedding=None)
            .filter(
                title__icontains="Ailə"
            )
        )

        for article in articles:

            title = normalize_text(
                article.title or ""
            )

            if (
                "aile" in title
                and (
                    "mohlet" in title
                    or "cagiris" in title
                )
            ):
                context_articles.append(article)

    # =====================================================
    # TOPLANIŞ + EHTİYAT
    # =====================================================

    elif (
        "toplanis" in intents
        and "ehtiyat" in intents
    ):

        articles = (
            Article.objects
            .select_related("law")
            .exclude(embedding=None)
        )

        for article in articles:

            title = normalize_text(
                article.title or ""
            )

            if (
                "ehtiyat" in title
                and (
                    "toplanis" in title
                    or "telim" in title
                    or "cagiris" in title
                )
            ):
                context_articles.append(article)

    # =====================================================
    # TOPLANIŞ + AZADOLMA
    # =====================================================

    elif (
        "toplanis" in intents
        and "azadetme" in intents
    ):

        if "aile" in intents:

            articles = (
                Article.objects
                .select_related("law")
                .exclude(embedding=None)
                .filter(
                    title__icontains="Ailə"
                )
            )

            for article in articles:

                title = normalize_text(
                    article.title or ""
                )

                if (
                    "aile" in title
                    and (
                        "mohlet" in title
                        or "cagiris" in title
                    )
                ):
                    context_articles.append(article)

        if "saglamliq" in intents:

            articles = (
                Article.objects
                .select_related("law")
                .exclude(embedding=None)
                .filter(
                    title__icontains="Sağlamlıq"
                )
            )

            for article in articles:

                title = normalize_text(
                    article.title or ""
                )

                if (
                    "saglamliq" in title
                    and (
                        "mohlet" in title
                        or "cagiris" in title
                    )
                ):
                    context_articles.append(article)

        if "tehsil" in intents:

            articles = (
                Article.objects
                .select_related("law")
                .exclude(embedding=None)
                .filter(
                    title__icontains="Təhsil"
                )
            )

            for article in articles:

                title = normalize_text(
                    article.title or ""
                )

                if (
                    "tehsil" in title
                    and (
                        "mohlet" in title
                        or "cagiris" in title
                    )
                ):
                    context_articles.append(article)

    return context_articles


# =========================================================
# SEARCH
# =========================================================

def search_articles(
    question,
    limit=5
):

    if not question:
        return []

    question = question.strip()

    if not question:
        return []

    # =====================================================
    # QUERY ANALYSIS
    # =====================================================

    keywords = get_keywords(question)

    intents = detect_intents(question)

    question_type = detect_question_type(
        intents
    )

    # =====================================================
    # EMBEDDING
    # =====================================================

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = (
        response.data[0].embedding
    )

    # =====================================================
    # SEMANTIC CANDIDATES
    # =====================================================

    semantic_articles = list(
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

    # =====================================================
    # CONTEXT CANDIDATES
    # =====================================================

    context_articles = get_context_articles(
        intents
    )

    # =====================================================
    # MERGE
    # =====================================================

    candidate_map = {}

    for article in semantic_articles:
        candidate_map[article.id] = article

    for article in context_articles:
        candidate_map[article.id] = article

    articles = list(
        candidate_map.values()
    )

    # =====================================================
    # SCORE
    # =====================================================

    scored_articles = []

    for article in articles:

        title = normalize_text(
            article.title or ""
        )

        content = normalize_text(
            article.content or ""
        )

        # -------------------------------------------------
        # SEMANTIC
        # -------------------------------------------------

        if hasattr(article, "distance"):

            semantic_score = max(
                0,
                1 - float(article.distance)
            )

        else:
            semantic_score = 0

        score = semantic_score * 50

        matched_keywords = 0

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        for keyword in keywords:

            match = keyword_matches(
                keyword,
                title,
                content
            )

            if match == "title":

                score += 20
                matched_keywords += 1

            elif match == "content":

                score += 4
                matched_keywords += 1

            elif match == "related_title":

                score += 10
                matched_keywords += 1

            elif match == "related_content":

                score += 2
                matched_keywords += 1

        # -------------------------------------------------
        # RELATION
        # -------------------------------------------------

        relation_score = calculate_relation_score(
            article,
            intents
        )

        score += relation_score

        # -------------------------------------------------
        # CONTEXT
        # -------------------------------------------------

        context_score = calculate_context_score(
            article,
            intents
        )

        score += context_score

        # -------------------------------------------------
        # DIRECT CONTEXT
        # -------------------------------------------------

        if is_direct_context_article(
            article,
            intents
        ):
            score += 150

        # -------------------------------------------------
        # ARTICLE ROLE
        # -------------------------------------------------

        article_role = detect_article_role(
            article,
            intents
        )

        if article_role == "primary":
            score += 200

        elif article_role == "companion":
            score += 100

        # =================================================
        # QUESTION TYPE
        # =================================================

        # -------------------------------------------------
        # TOPLANIŞ + EHTİYAT + AİLƏ
        # -------------------------------------------------

        if question_type == "toplanis_ehtiyat_aile":

            # Ehtiyat + toplanış
            if (
                "ehtiyat" in title
                and (
                    "toplanis" in title
                    or "telim" in title
                    or "cagiris" in title
                )
            ):
                score += 300

            # Toplanışdan azadolma
            if (
                "toplanis" in title
                and "azad" in title
            ):
                score += 250

            # Ailə üzrə maddə
            if (
                "aile" in title
                and (
                    "mohlet" in title
                    or "cagiris" in title
                )
            ):
                score += 200

        # -------------------------------------------------
        # TOPLANIŞ + EHTİYAT
        # -------------------------------------------------

        elif question_type == "toplanis_ehtiyat":

            if (
                "ehtiyat" in title
                and (
                    "toplanis" in title
                    or "telim" in title
                    or "cagiris" in title
                )
            ):
                score += 300

            elif "toplanis" in title:
                score += 150

        # -------------------------------------------------
        # TOPLANIŞ + AZADOLMA
        # -------------------------------------------------

        elif question_type == "toplanis_azadetme":

            if (
                "toplanis" in title
                and "azad" in title
            ):
                score += 250

            if "aile" in intents:

                if (
                    "aile" in title
                    and "mohlet" in title
                ):
                    score += 150

            if "saglamliq" in intents:

                if (
                    "saglamliq" in title
                    and "mohlet" in title
                ):
                    score += 150

            if "tehsil" in intents:

                if (
                    "tehsil" in title
                    and "mohlet" in title
                ):
                    score += 150

        # -------------------------------------------------
        # MÖHLƏT
        # -------------------------------------------------

        elif question_type == "mohlet":

            if "mohlet" in title:
                score += 150

        # -------------------------------------------------
        # AİLƏ + MÖHLƏT
        # -------------------------------------------------

        elif question_type == "aile_mohlet":

            if (
                "aile" in title
                and "mohlet" in title
            ):
                score += 200

        # -------------------------------------------------
        # SAĞLAMLIQ + MÖHLƏT
        # -------------------------------------------------

        elif question_type == "saglamliq_mohlet":

            if (
                "saglamliq" in title
                and "mohlet" in title
            ):
                score += 200

        # -------------------------------------------------
        # TƏHSİL + MÖHLƏT
        # -------------------------------------------------

        elif question_type == "tehsil_mohlet":

            if (
                "tehsil" in title
                and "mohlet" in title
            ):
                score += 200

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        scored_articles.append(
            {
                "article": article,
                "score": score,
                "semantic_score": semantic_score,
                "matched_keywords": matched_keywords,
                "relation_score": relation_score,
                "context_score": context_score,
                "article_role": article_role,
            }
        )

    # =====================================================
    # SORT
    # =====================================================

    scored_articles.sort(
        key=lambda item: (
            item["score"],
            item["relation_score"],
            item["context_score"],
            item["matched_keywords"],
            item["semantic_score"],
        ),
        reverse=True
    )

    # =====================================================
    # DEBUG
    # =====================================================

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
        f"QUESTION TYPE: {question_type}"
    )

    print(
        "\nTOP RESULTS:"
    )

    for index, item in enumerate(
        scored_articles[:limit],
        start=1
    ):

        article = item["article"]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Semantic={item['semantic_score']:.4f} | "
            f"Keywords={item['matched_keywords']} | "
            f"Relation={item['relation_score']} | "
            f"Context={item['context_score']} | "
            f"Role={item['article_role']} | "
            f"{article.title}"
        )

    print(
        "==============================================\n"
    )

    # =====================================================
    # RETURN
    # =====================================================

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



































































































































































































































# import re
# from collections import defaultdict

# from openai import OpenAI
# from django.conf import settings
# from django.contrib.postgres.search import (
#     SearchQuery,
#     SearchRank,
#     SearchVector,
# )
# from pgvector.django import CosineDistance

# from chatbot.models import Article


# # =========================================================
# # OPENAI
# # =========================================================

# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )


# # =========================================================
# # SEARCH SETTINGS
# # =========================================================

# SEMANTIC_LIMIT = 20
# LEXICAL_LIMIT = 20
# EXACT_LIMIT = 10

# FINAL_LIMIT = 5

# MAX_QUERY_TERMS = 30
# MAX_PHRASES = 10


# # =========================================================
# # SEMANTIC THRESHOLDS
# # =========================================================

# STRONG_SEMANTIC = 0.48
# MEDIUM_SEMANTIC = 0.32
# MIN_SEMANTIC_SCORE = 0.20


# # =========================================================
# # SCORE WEIGHTS
# # =========================================================

# SEMANTIC_WEIGHT = 100
# LEXICAL_WEIGHT = 35

# TITLE_KEYWORD_SCORE = 14
# CONTENT_KEYWORD_SCORE = 4

# PHRASE_TITLE_SCORE = 28
# PHRASE_CONTENT_SCORE = 10

# CONCEPT_TITLE_SCORE = 18
# CONCEPT_CONTENT_SCORE = 6

# NUMBER_TITLE_SCORE = 35
# NUMBER_CONTENT_SCORE = 14

# EXACT_SOURCE_SCORE = 300
# SEMANTIC_SOURCE_SCORE = 10
# LEXICAL_SOURCE_SCORE = 10

# MULTI_SOURCE_BONUS = 22
# THREE_SOURCE_BONUS = 15

# FULL_INTENT_BONUS = 35
# PARTIAL_INTENT_BONUS = 12

# STRONG_LEXICAL_BONUS = 18
# MEDIUM_LEXICAL_BONUS = 8


# # =========================================================
# # STOP WORDS
# # =========================================================

# STOP_WORDS = {
#     "men",
#     "mən",
#     "sen",
#     "sən",
#     "siz",
#     "biz",

#     "bu",
#     "bir",

#     "ve",
#     "və",
#     "ile",
#     "ilə",
#     "ucun",
#     "üçün",

#     "olan",
#     "olaraq",

#     "haqqinda",
#     "haqqında",

#     "nece",
#     "necə",
#     "nedir",
#     "nədir",

#     "kimdir",
#     "kimler",
#     "kimlər",

#     "hansi",
#     "hansı",
#     "hansilar",
#     "hansılar",

#     "eden",
#     "edən",
#     "edilir",

#     "edilmesi",
#     "edilməsi",

#     "verilen",
#     "verilən",
#     "verilir",
#     "verilirmi",

#     "var",

#     "mi",
#     "mı",
#     "mu",
#     "mü",

#     "de",
#     "də",
#     "da",

#     "ki",

#     "gore",
#     "görə",

#     "menim",
#     "mənim",
#     "senin",
#     "sənin",
#     "sizin",
#     "bizim",

#     "oldugum",
#     "olduğum",
#     "oldugun",
#     "olduğun",
#     "oldugu",
#     "olduğu",
#     "olduqda",

#     "halda",
#     "halinda",
#     "halında",

#     "olar",
#     "olur",

#     "ede",
#     "edə",

#     "etmek",
#     "etmək",

#     "olanlar",
#     "olanlari",
#     "olanları",
# }


# # =========================================================
# # RELATED WORDS
# # =========================================================

# RELATED_WORDS = {

#     "toplanis": {
#         "toplanis",
#         "toplanisa",
#         "toplanisdan",
#         "toplanislar",
#         "toplanislardan",
#         "toplanislara",
#         "toplanislarin",

#         "telim",
#         "telime",
#         "telimden",
#         "telimler",
#         "telimlere",
#         "telimlerden",
#         "telimlerin",
#     },

#     "cagiris": {
#         "cagiris",
#         "cagirisa",
#         "cagirisdan",
#         "cagirislar",
#         "cagirislarin",

#         "cagir",
#         "cagirilir",
#         "cagirilirler",
#         "cagirilacaq",
#         "cagirilacaqdir",
#         "cagirilmasi",
#         "cagirilma",
#         "cagirila",
#         "cagirma",
#     },

#     "azadetme": {
#         "azad",
#         "azaddir",
#         "azadliq",
#         "azadlar",
#         "azadetme",

#         "azad edilen",
#         "azad edilir",
#         "azad olunur",
#         "azad edilmis",
#         "azad edilmesi",
#         "azad edilme",
#         "azad olunma",
#     },

#     "mohlet": {
#         "mohlet",
#         "mohletin",
#         "mohletle",
#         "mohletler",
#         "mohletlerden",
#         "mohletden",

#         "mohlet verilmesi",
#         "mohlet verilir",
#         "mohlet verilme",
#         "mohlet alma",
#     },

#     "saglamliq": {
#         "saglamliq",
#         "saglamlig",
#         "saglamligina",
#         "saglamligindan",
#         "saglamliqdan",

#         "saglamliq veziyyeti",
#         "saglamliq veziyyetine",
#         "saglamliq veziyyetinden",

#         "tibbi",
#         "xestelik",
#         "xeste",
#         "yararsiz",
#         "yararli",
#     },

#     "aile": {
#         "aile",
#         "ailesi",
#         "ailenin",
#         "aileye",
#         "ailevi",

#         "aile veziyyeti",
#         "aile veziyyetine",
#         "aile veziyyetinden",

#         "usaq",
#         "usag",
#         "usagi",
#         "usagim",

#         "usaqlar",
#         "usaglar",
#         "usaqlari",
#         "usaglari",
#         "usaqlarin",
#         "usaglarin",

#         "ovlad",
#         "ovladi",
#         "ovladim",
#         "ovladlar",
#         "ovladlari",
#         "ovladlarin",

#         "ata",
#         "ana",
#         "valideyn",
#     },

#     "tehsil": {
#         "tehsil",
#         "tehsili",
#         "tehsile",
#         "tehsilde",

#         "tehsil alan",
#         "tehsil etmek",
#         "tehsil alanlar",

#         "telebe",
#         "telebeler",

#         "universitet",
#         "ali mekteb",
#         "mekteb",
#     },

#     "ehtiyat": {
#         "ehtiyat",
#         "ehtiyatda",
#         "ehtiyatdaki",
#         "ehtiyatdakilar",

#         "ehtiyatda olan",
#         "ehtiyatda olanlar",

#         "ehtiyatci",
#         "ehtiyatcilar",
#     },
# }


# # =========================================================
# # INTENTS
# # =========================================================

# INTENTS = {
#     "toplanis": RELATED_WORDS["toplanis"],
#     "cagiris": RELATED_WORDS["cagiris"],
#     "azadetme": RELATED_WORDS["azadetme"],
#     "mohlet": RELATED_WORDS["mohlet"],
#     "saglamliq": RELATED_WORDS["saglamliq"],
#     "aile": RELATED_WORDS["aile"],
#     "tehsil": RELATED_WORDS["tehsil"],
#     "ehtiyat": RELATED_WORDS["ehtiyat"],
# }


# # =========================================================
# # PRIMARY INTENT TERMS
# # =========================================================

# INTENT_PRIMARY_TERMS = {
#     "toplanis": [
#         "toplanis",
#         "telim",
#     ],

#     "cagiris": [
#         "cagiris",
#     ],

#     "azadetme": [
#         "azad",
#     ],

#     "mohlet": [
#         "mohlet",
#     ],

#     "saglamliq": [
#         "saglamliq",
#         "tibbi",
#     ],

#     "aile": [
#         "aile",
#         "usaq",
#         "ovlad",
#     ],

#     "tehsil": [
#         "tehsil",
#         "telebe",
#     ],

#     "ehtiyat": [
#         "ehtiyat",
#     ],
# }


# # =========================================================
# # QUESTION TYPE PRIORITY
# # =========================================================

# QUESTION_TYPE_COMBINATIONS = [
#     (
#         {"toplanis", "ehtiyat", "aile"},
#         "toplanis_ehtiyat_aile",
#     ),
#     (
#         {"toplanis", "ehtiyat"},
#         "toplanis_ehtiyat",
#     ),
#     (
#         {"toplanis", "azadetme"},
#         "toplanis_azadetme",
#     ),
#     (
#         {"cagiris", "mohlet"},
#         "cagiris_mohlet",
#     ),
#     (
#         {"aile", "mohlet"},
#         "aile_mohlet",
#     ),
#     (
#         {"saglamliq", "mohlet"},
#         "saglamliq_mohlet",
#     ),
#     (
#         {"tehsil", "mohlet"},
#         "tehsil_mohlet",
#     ),
#     (
#         {"aile", "toplanis"},
#         "toplanis_aile",
#     ),
# ]


# QUESTION_TYPE_PRIORITY = [
#     "azadetme",
#     "mohlet",
#     "toplanis",
#     "cagiris",
#     "ehtiyat",
#     "aile",
#     "tehsil",
#     "saglamliq",
# ]


# # =========================================================
# # NORMALIZATION
# # =========================================================

# def normalize_text(text):
#     """
#     Azərbaycan dilində xüsusi simvolları
#     search üçün sadələşdirir.
#     """

#     if not text:
#         return ""

#     text = str(text).lower().strip()

#     replacements = {
#         "ə": "e",
#         "ı": "i",
#         "ö": "o",
#         "ü": "u",
#         "ğ": "g",
#         "ş": "s",
#         "ç": "c",
#     }

#     for old, new in replacements.items():
#         text = text.replace(old, new)

#     text = re.sub(
#         r"[“”«»\"']",
#         " ",
#         text,
#     )

#     text = re.sub(
#         r"[\(\)\[\]\{\}:;,!?]",
#         " ",
#         text,
#     )

#     text = re.sub(
#         r"\s+",
#         " ",
#         text,
#     )

#     return text.strip()


# # =========================================================
# # TOKENIZATION
# # =========================================================

# def tokenize(text):
#     normalized = normalize_text(text)

#     return re.findall(
#         r"[a-z0-9.-]+",
#         normalized,
#     )


# # =========================================================
# # WORD NORMALIZATION
# # =========================================================

# def normalize_word_for_intent(word):
#     """
#     Sadə Azərbaycan dilində şəkilçi tolerantlığı.
#     Məs:
#         usaglar -> usag
#         aileye -> aile
#         mohletden -> mohlet
#     """

#     word = normalize_text(word)

#     if not word:
#         return ""

#     suffixes = [
#         "larin",
#         "lerin",

#         "lardan",
#         "lerden",

#         "lara",
#         "lere",

#         "lar",
#         "ler",

#         "dan",
#         "den",

#         "nin",
#         "nın",
#         "nun",
#         "nün",

#         "na",
#         "ne",

#         "da",
#         "de",

#         "ta",
#         "te",

#         "ya",
#         "ye",

#         "ni",
#         "nı",
#         "nu",
#         "nü",

#         "in",
#         "ın",
#         "un",
#         "ün",

#         "im",
#         "ım",
#         "um",
#         "üm",

#         "i",
#         "ı",
#         "u",
#         "ü",

#         "a",
#         "e",
#     ]

#     for suffix in sorted(
#         suffixes,
#         key=len,
#         reverse=True,
#     ):
#         if (
#             word.endswith(suffix)
#             and len(word) - len(suffix) >= 4
#         ):
#             word = word[:-len(suffix)]
#             break

#     return word


# # =========================================================
# # KEYWORDS
# # =========================================================

# def get_keywords(question):

#     keywords = []

#     for word in tokenize(question):

#         if len(word) < 3:
#             continue

#         if word in STOP_WORDS:
#             continue

#         if word not in keywords:
#             keywords.append(word)

#     return keywords


# # =========================================================
# # INTENT DETECTION
# # =========================================================

# def detect_intents(question):

#     normalized = normalize_text(question)
#     tokens = tokenize(question)

#     normalized_tokens = {
#         token: normalize_word_for_intent(token)
#         for token in tokens
#     }

#     detected = set()

#     for intent, words in INTENTS.items():

#         for word in words:

#             normalized_word = normalize_text(word)

#             if not normalized_word:
#                 continue

#             # ---------------------------------------------
#             # Multi-word intent
#             # ---------------------------------------------

#             if " " in normalized_word:

#                 if normalized_word in normalized:
#                     detected.add(intent)
#                     break

#                 continue

#             # ---------------------------------------------
#             # Exact token
#             # ---------------------------------------------

#             if normalized_word in normalized_tokens:
#                 detected.add(intent)
#                 break

#             # ---------------------------------------------
#             # Stem-like matching
#             # ---------------------------------------------

#             base_word = normalize_word_for_intent(
#                 normalized_word
#             )

#             if not base_word:
#                 continue

#             if base_word in normalized_tokens.values():
#                 detected.add(intent)
#                 break

#     # ---------------------------------------------
#     # Numerical family evidence
#     # ---------------------------------------------

#     if re.search(
#         r"\b\d+\s+(usaq|usag|ovlad)\b",
#         normalized,
#     ):
#         detected.add("aile")

#     elif re.search(
#         r"\b(usaq|usag|ovlad)\b",
#         normalized,
#     ):
#         detected.add("aile")

#     return detected


# # =========================================================
# # QUESTION TYPE
# # =========================================================

# def detect_question_type(intents):

#     for required, question_type in QUESTION_TYPE_COMBINATIONS:

#         if required.issubset(intents):
#             return question_type

#     for intent in QUESTION_TYPE_PRIORITY:

#         if intent in intents:
#             return intent

#     return "general"


# # =========================================================
# # KEYWORD EXPANSION
# # =========================================================

# def expand_keywords(
#     keywords,
#     intents,
# ):

#     expanded = []

#     # ---------------------------------------------
#     # User keywords first
#     # ---------------------------------------------

#     for keyword in keywords:

#         keyword = normalize_text(keyword)

#         if (
#             len(keyword) >= 3
#             and keyword not in expanded
#         ):
#             expanded.append(keyword)

#     # ---------------------------------------------
#     # Intent primary terms
#     # ---------------------------------------------

#     for intent in intents:

#         for term in INTENT_PRIMARY_TERMS.get(
#             intent,
#             [],
#         ):

#             term = normalize_text(term)

#             if (
#                 len(term) >= 3
#                 and term not in expanded
#             ):
#                 expanded.append(term)

#     return expanded[:MAX_QUERY_TERMS]


# # =========================================================
# # PHRASES
# # =========================================================

# IMPORTANT_PHRASES = [
#     "toplanisdan azad",
#     "toplanislardan azad",

#     "toplanisa cagir",
#     "toplanisa cagiril",
#     "toplanislara cagir",

#     "aile veziyyeti",

#     "saglamliq veziyyeti",

#     "tehsil alan",
#     "tehsil alanlar",

#     "ehtiyatda olan",
#     "ehtiyatda olanlar",

#     "muddetli heqiqi herbi xidmet",

#     "herbi xidmete cagiris",
#     "herbi xidmete cagiril",

#     "mohlet veril",

#     "azad edil",
# ]


# def extract_query_phrases(question):

#     normalized = normalize_text(question)

#     phrases = []

#     # ---------------------------------------------
#     # Important legal phrases
#     # ---------------------------------------------

#     for pattern in IMPORTANT_PHRASES:

#         pattern = normalize_text(pattern)

#         if pattern in normalized:
#             phrases.append(pattern)

#     # ---------------------------------------------
#     # Dynamic 3-word / 2-word phrases
#     # ---------------------------------------------

#     words = [
#         word
#         for word in tokenize(question)
#         if word not in STOP_WORDS
#         and len(word) >= 3
#     ]

#     for size in (3, 2):

#         for index in range(
#             len(words) - size + 1
#         ):

#             phrase = " ".join(
#                 words[
#                     index:index + size
#                 ]
#             )

#             if phrase not in phrases:
#                 phrases.append(phrase)

#     return list(
#         dict.fromkeys(phrases)
#     )[:MAX_PHRASES]


# # =========================================================
# # ARTICLE NUMBER EXTRACTION
# # =========================================================

# def extract_article_numbers(question):

#     normalized = normalize_text(question)

#     patterns = [
#         r"\b(\d+\.\d+(?:\.\d+)*)\b",

#         r"\b(\d+)-ci\s+madd",
#         r"\b(\d+)-cu\s+madd",
#         r"\b(\d+)-cu\s+maddesi",
#         r"\b(\d+)-cü\s+madd",
#         r"\b(\d+)-cı\s+madd",

#         r"\b(\d+)\s+madd",

#         r"\bmadd[ae]\s+(\d+(?:\.\d+)*)\b",
#     ]

#     found = []

#     for pattern in patterns:

#         matches = re.findall(
#             pattern,
#             normalized,
#         )

#         for match in matches:

#             if isinstance(match, tuple):
#                 match = match[0]

#             if match not in found:
#                 found.append(match)

#     return found


# # =========================================================
# # QUERY ANALYSIS
# # =========================================================

# def analyze_query(question):

#     normalized = normalize_text(question)

#     keywords = get_keywords(question)

#     intents = detect_intents(question)

#     question_type = detect_question_type(
#         intents
#     )

#     expanded_keywords = expand_keywords(
#         keywords,
#         intents,
#     )

#     phrases = extract_query_phrases(
#         question
#     )

#     numbers = re.findall(
#         r"\b\d+(?:[.,]\d+)?\b",
#         normalized,
#     )

#     article_numbers = extract_article_numbers(
#         question
#     )

#     return {
#         "normalized": normalized,
#         "keywords": keywords,
#         "expanded_keywords": expanded_keywords,
#         "phrases": phrases,
#         "intents": intents,
#         "question_type": question_type,
#         "numbers": numbers,
#         "article_numbers": article_numbers,
#     }


# # =========================================================
# # BASE QUERYSET
# # =========================================================

# def base_article_queryset():

#     return (
#         Article.objects
#         .select_related("law")
#         .exclude(embedding=None)
#     )


# # =========================================================
# # EXACT ARTICLE SEARCH
# # =========================================================

# def exact_article_search(question):

#     article_numbers = extract_article_numbers(
#         question
#     )

#     if not article_numbers:
#         return []

#     queryset = base_article_queryset()

#     results = []

#     for number in article_numbers:

#         articles = (
#             queryset
#             .filter(
#                 number__iexact=number
#             )
#             [:EXACT_LIMIT]
#         )

#         for article in articles:

#             results.append({
#                 "article": article,
#                 "semantic_score": 1.0,
#                 "lexical_score": 1.0,
#                 "sources": {"exact"},
#             })

#     return results


# # =========================================================
# # SEMANTIC SEARCH
# # =========================================================

# def semantic_search(question):

#     try:

#         response = client.embeddings.create(
#             model="text-embedding-3-small",
#             input=question,
#         )

#         question_embedding = (
#             response.data[0].embedding
#         )

#     except Exception as exc:

#         print(
#             f"[SEMANTIC SEARCH ERROR] {exc}"
#         )

#         return []

#     try:

#         articles = (
#             base_article_queryset()
#             .annotate(
#                 distance=CosineDistance(
#                     "embedding",
#                     question_embedding,
#                 )
#             )
#             .order_by("distance")
#             [:SEMANTIC_LIMIT]
#         )

#     except Exception as exc:

#         print(
#             f"[SEMANTIC DB ERROR] {exc}"
#         )

#         return []

#     results = []

#     for article in articles:

#         distance = float(
#             article.distance
#         )

#         similarity = max(
#             0.0,
#             min(
#                 1.0,
#                 1.0 - distance,
#             ),
#         )

#         results.append({
#             "article": article,
#             "semantic_score": similarity,
#             "lexical_score": 0.0,
#             "sources": {"semantic"},
#         })

#     return results


# # =========================================================
# # LEXICAL SEARCH
# # =========================================================

# def lexical_search(
#     question,
#     keywords,
#     intents,
# ):

#     search_terms = []

#     # ---------------------------------------------
#     # User keywords
#     # ---------------------------------------------

#     for keyword in keywords:

#         keyword = normalize_text(keyword)

#         if (
#             len(keyword) >= 3
#             and keyword not in search_terms
#         ):
#             search_terms.append(keyword)

#     # ---------------------------------------------
#     # Intent terms
#     # ---------------------------------------------

#     for intent in intents:

#         for term in INTENT_PRIMARY_TERMS.get(
#             intent,
#             [],
#         ):

#             term = normalize_text(term)

#             if (
#                 len(term) >= 3
#                 and term not in search_terms
#             ):
#                 search_terms.append(term)

#     search_terms = search_terms[
#         :MAX_QUERY_TERMS
#     ]

#     if not search_terms:
#         return []

#     # ---------------------------------------------
#     # PostgreSQL FTS
#     # ---------------------------------------------

#     vector = (
#         SearchVector(
#             "title",
#             weight="A",
#         )
#         +
#         SearchVector(
#             "content",
#             weight="B",
#         )
#     )

#     query = None

#     for term in search_terms:

#         current = SearchQuery(
#             term,
#             search_type="websearch",
#         )

#         if query is None:
#             query = current
#         else:
#             query = query | current

#     try:

#         articles = (
#             base_article_queryset()
#             .annotate(
#                 search_vector=vector
#             )
#             .annotate(
#                 lexical_rank=SearchRank(
#                     "search_vector",
#                     query,
#                 )
#             )
#             .filter(
#                 search_vector=query
#             )
#             .order_by(
#                 "-lexical_rank"
#             )
#             [:LEXICAL_LIMIT]
#         )

#     except Exception as exc:

#         print(
#             f"[LEXICAL SEARCH ERROR] {exc}"
#         )

#         return []

#     results = []

#     for article in articles:

#         rank = float(
#             article.lexical_rank or 0.0
#         )

#         results.append({
#             "article": article,
#             "semantic_score": 0.0,
#             "lexical_score": rank,
#             "sources": {"lexical"},
#         })

#     return results


# # =========================================================
# # CANDIDATE FUSION
# # =========================================================

# def merge_candidates(*result_sets):

#     candidates = {}

#     for results in result_sets:

#         for item in results:

#             article = item["article"]
#             article_id = article.id

#             if article_id not in candidates:

#                 candidates[article_id] = {
#                     "article": article,

#                     "semantic_score": item.get(
#                         "semantic_score",
#                         0.0,
#                     ),

#                     "lexical_score": item.get(
#                         "lexical_score",
#                         0.0,
#                     ),

#                     "sources": set(
#                         item.get(
#                             "sources",
#                             set(),
#                         )
#                     ),
#                 }

#                 continue

#             existing = candidates[
#                 article_id
#             ]

#             existing["semantic_score"] = max(
#                 existing["semantic_score"],
#                 item.get(
#                     "semantic_score",
#                     0.0,
#                 ),
#             )

#             existing["lexical_score"] = max(
#                 existing["lexical_score"],
#                 item.get(
#                     "lexical_score",
#                     0.0,
#                 ),
#             )

#             existing["sources"].update(
#                 item.get(
#                     "sources",
#                     set(),
#                 )
#             )

#     return list(
#         candidates.values()
#     )


# # =========================================================
# # TEXT MATCH HELPERS
# # =========================================================

# def contains_word(text, word):

#     if not text or not word:
#         return False

#     return bool(
#         re.search(
#             rf"\b{re.escape(word)}\b",
#             text,
#         )
#     )


# def contains_phrase(text, phrase):

#     if not text or not phrase:
#         return False

#     return phrase in text


# # =========================================================
# # KEYWORD SCORE
# # =========================================================

# def calculate_keyword_score(
#     article,
#     keywords,
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     score = 0
#     matched = 0

#     for keyword in keywords:

#         keyword = normalize_text(
#             keyword
#         )

#         if len(keyword) < 3:
#             continue

#         if contains_word(
#             title,
#             keyword,
#         ):

#             score += TITLE_KEYWORD_SCORE
#             matched += 1

#         elif contains_word(
#             content,
#             keyword,
#         ):

#             score += CONTENT_KEYWORD_SCORE
#             matched += 1

#     return score, matched


# # =========================================================
# # PHRASE SCORE
# # =========================================================

# def calculate_phrase_score(
#     article,
#     phrases,
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     score = 0
#     matched = 0

#     for phrase in phrases:

#         phrase = normalize_text(
#             phrase
#         )

#         if len(phrase) < 5:
#             continue

#         if contains_phrase(
#             title,
#             phrase,
#         ):

#             score += PHRASE_TITLE_SCORE
#             matched += 1

#         elif contains_phrase(
#             content,
#             phrase,
#         ):

#             score += PHRASE_CONTENT_SCORE
#             matched += 1

#     return score, matched


# # =========================================================
# # CONCEPT SCORE
# # =========================================================

# def calculate_concept_score(
#     article,
#     intents,
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     score = 0

#     for intent in intents:

#         related_words = RELATED_WORDS.get(
#             intent,
#             set(),
#         )

#         title_found = False
#         content_found = False

#         for word in related_words:

#             word = normalize_text(word)

#             if len(word) < 3:
#                 continue

#             if " " in word:

#                 if word in title:
#                     title_found = True
#                     break

#                 if word in content:
#                     content_found = True

#             else:

#                 if contains_word(
#                     title,
#                     word,
#                 ):

#                     title_found = True
#                     break

#                 if contains_word(
#                     content,
#                     word,
#                 ):

#                     content_found = True

#         if title_found:

#             score += CONCEPT_TITLE_SCORE

#         elif content_found:

#             score += CONCEPT_CONTENT_SCORE

#     return score


# # =========================================================
# # LEGAL SCORE
# # =========================================================

# def calculate_legal_score(
#     article,
#     intents,
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     score = 0

#     for intent in intents:

#         related_words = RELATED_WORDS.get(
#             intent,
#             set(),
#         )

#         title_hit = False
#         content_hits = 0

#         for word in related_words:

#             word = normalize_text(word)

#             if len(word) < 3:
#                 continue

#             if " " in word:

#                 if word in title:
#                     title_hit = True

#                 elif word in content:
#                     content_hits += 1

#             else:

#                 if contains_word(
#                     title,
#                     word,
#                 ):

#                     title_hit = True

#                 elif contains_word(
#                     content,
#                     word,
#                 ):

#                     content_hits += 1

#         if title_hit:

#             score += 20

#         elif content_hits >= 3:

#             score += 10

#         elif content_hits >= 1:

#             score += 4

#     # ---------------------------------------------
#     # Multiple intent agreement
#     # ---------------------------------------------

#     if len(intents) >= 2:

#         covered = 0

#         for intent in intents:

#             related_words = RELATED_WORDS.get(
#                 intent,
#                 set(),
#             )

#             intent_found = False

#             for word in related_words:

#                 word = normalize_text(word)

#                 if len(word) < 3:
#                     continue

#                 if " " in word:

#                     if (
#                         word in title
#                         or word in content
#                     ):
#                         intent_found = True
#                         break

#                 else:

#                     if (
#                         contains_word(title, word)
#                         or
#                         contains_word(content, word)
#                     ):
#                         intent_found = True
#                         break

#             if intent_found:
#                 covered += 1

#         if covered == len(intents):

#             score += 25

#         elif covered >= 2:

#             score += 10

#     return score


# # =========================================================
# # NUMBER SCORE
# # =========================================================

# def calculate_number_score(
#     article,
#     numbers,
# ):

#     if not numbers:
#         return 0

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     score = 0

#     for number in numbers:

#         pattern = (
#             rf"\b{re.escape(number)}\b"
#         )

#         if re.search(
#             pattern,
#             title,
#         ):

#             score += NUMBER_TITLE_SCORE

#         elif re.search(
#             pattern,
#             content,
#         ):

#             score += NUMBER_CONTENT_SCORE

#     return score


# # =========================================================
# # SOURCE SCORE
# # =========================================================

# def calculate_source_score(
#     sources,
# ):

#     score = 0

#     if "exact" in sources:
#         score += EXACT_SOURCE_SCORE

#     if "semantic" in sources:
#         score += SEMANTIC_SOURCE_SCORE

#     if "lexical" in sources:
#         score += LEXICAL_SOURCE_SCORE

#     if len(sources) >= 2:
#         score += MULTI_SOURCE_BONUS

#     if len(sources) >= 3:
#         score += THREE_SOURCE_BONUS

#     return score


# # =========================================================
# # INTENT EVIDENCE
# # =========================================================

# def calculate_intent_evidence(
#     article,
#     intents,
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     content = normalize_text(
#         article.content or ""
#     )

#     matched = set()

#     for intent in intents:

#         related_words = RELATED_WORDS.get(
#             intent,
#             set(),
#         )

#         for word in related_words:

#             word = normalize_text(word)

#             if len(word) < 3:
#                 continue

#             if " " in word:

#                 if (
#                     word in title
#                     or word in content
#                 ):

#                     matched.add(intent)
#                     break

#             else:

#                 if (
#                     contains_word(
#                         title,
#                         word,
#                     )
#                     or
#                     contains_word(
#                         content,
#                         word,
#                     )
#                 ):

#                     matched.add(intent)
#                     break

#     return matched


# # =========================================================
# # RERANK
# # =========================================================

# def rerank_candidates(
#     candidates,
#     analysis,
# ):

#     keywords = analysis[
#         "expanded_keywords"
#     ]

#     phrases = analysis[
#         "phrases"
#     ]

#     intents = analysis[
#         "intents"
#     ]

#     numbers = analysis[
#         "numbers"
#     ]

#     ranked = []

#     for item in candidates:

#         article = item["article"]

#         semantic_score = float(
#             item.get(
#                 "semantic_score",
#                 0.0,
#             )
#         )

#         lexical_score = float(
#             item.get(
#                 "lexical_score",
#                 0.0,
#             )
#         )

#         sources = item["sources"]

#         # ---------------------------------------------
#         # Base scores
#         # ---------------------------------------------

#         semantic_points = (
#             semantic_score
#             * SEMANTIC_WEIGHT
#         )

#         lexical_points = min(
#             lexical_score
#             * LEXICAL_WEIGHT,
#             35,
#         )

#         keyword_points, matched_keywords = (
#             calculate_keyword_score(
#                 article,
#                 keywords,
#             )
#         )

#         phrase_points, matched_phrases = (
#             calculate_phrase_score(
#                 article,
#                 phrases,
#             )
#         )

#         concept_points = (
#             calculate_concept_score(
#                 article,
#                 intents,
#             )
#         )

#         legal_points = (
#             calculate_legal_score(
#                 article,
#                 intents,
#             )
#         )

#         number_points = (
#             calculate_number_score(
#                 article,
#                 numbers,
#             )
#         )

#         source_points = (
#             calculate_source_score(
#                 sources
#             )
#         )

#         # ---------------------------------------------
#         # Intent evidence
#         # ---------------------------------------------

#         intent_evidence = (
#             calculate_intent_evidence(
#                 article,
#                 intents,
#             )
#         )

#         intent_bonus = 0

#         if intents:

#             coverage = (
#                 len(intent_evidence)
#                 / len(intents)
#             )

#             if coverage >= 1.0:

#                 intent_bonus = FULL_INTENT_BONUS

#             elif coverage >= 0.5:

#                 intent_bonus = PARTIAL_INTENT_BONUS

#         # ---------------------------------------------
#         # Keyword bonus
#         # ---------------------------------------------

#         if matched_keywords >= 5:

#             keyword_bonus = 20

#         elif matched_keywords >= 3:

#             keyword_bonus = 12

#         elif matched_keywords >= 2:

#             keyword_bonus = 6

#         else:

#             keyword_bonus = 0

#         # ---------------------------------------------
#         # Phrase bonus
#         # ---------------------------------------------

#         if matched_phrases >= 3:

#             phrase_bonus = 18

#         elif matched_phrases >= 2:

#             phrase_bonus = 12

#         elif matched_phrases == 1:

#             phrase_bonus = 6

#         else:

#             phrase_bonus = 0

#         # ---------------------------------------------
#         # Lexical quality
#         # ---------------------------------------------

#         if lexical_score >= 0.25:

#             lexical_bonus = STRONG_LEXICAL_BONUS

#         elif lexical_score >= 0.10:

#             lexical_bonus = MEDIUM_LEXICAL_BONUS

#         else:

#             lexical_bonus = 0

#         # ---------------------------------------------
#         # Final score
#         # ---------------------------------------------

#         total_score = (
#             semantic_points
#             + lexical_points
#             + keyword_points
#             + phrase_points
#             + concept_points
#             + legal_points
#             + number_points
#             + source_points
#             + intent_bonus
#             + keyword_bonus
#             + phrase_bonus
#             + lexical_bonus
#         )

#         ranked.append({

#             "article": article,

#             "score": total_score,

#             "semantic_score":
#                 semantic_score,

#             "lexical_score":
#                 lexical_score,

#             "keyword_score":
#                 keyword_points,

#             "phrase_score":
#                 phrase_points,

#             "concept_score":
#                 concept_points,

#             "legal_score":
#                 legal_points,

#             "number_score":
#                 number_points,

#             "source_score":
#                 source_points,

#             "intent_bonus":
#                 intent_bonus,

#             "keyword_bonus":
#                 keyword_bonus,

#             "phrase_bonus":
#                 phrase_bonus,

#             "lexical_bonus":
#                 lexical_bonus,

#             "matched_keywords":
#                 matched_keywords,

#             "matched_phrases":
#                 matched_phrases,

#             "intent_evidence":
#                 intent_evidence,

#             "sources":
#                 sources,
#         })

#     # ---------------------------------------------
#     # Ranking
#     # ---------------------------------------------

#     ranked.sort(
#         key=lambda item: (
#             "exact" in item["sources"],
#             item["score"],
#             item["semantic_score"],
#             item["lexical_score"],
#             item["legal_score"],
#             item["phrase_score"],
#         ),
#         reverse=True,
#     )

#     return ranked


# # =========================================================
# # EVIDENCE CHECK
# # =========================================================

# def evidence_check(
#     ranked,
#     analysis,
# ):

#     verified = []

#     intents = analysis[
#         "intents"
#     ]

#     for item in ranked:

#         semantic_score = item[
#             "semantic_score"
#         ]

#         lexical_score = item[
#             "lexical_score"
#         ]

#         legal_score = item[
#             "legal_score"
#         ]

#         concept_score = item[
#             "concept_score"
#         ]

#         keyword_score = item[
#             "keyword_score"
#         ]

#         phrase_score = item[
#             "phrase_score"
#         ]

#         number_score = item[
#             "number_score"
#         ]

#         sources = item[
#             "sources"
#         ]

#         intent_evidence = item[
#             "intent_evidence"
#         ]

#         # ---------------------------------------------
#         # Exact article
#         # ---------------------------------------------

#         if "exact" in sources:

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # Semantic levels
#         # ---------------------------------------------

#         strong_semantic = (
#             semantic_score
#             >= STRONG_SEMANTIC
#         )

#         medium_semantic = (
#             semantic_score
#             >= MEDIUM_SEMANTIC
#         )

#         # ---------------------------------------------
#         # Multi-source agreement
#         # ---------------------------------------------

#         multi_source = (
#             len(sources) >= 2
#         )

#         # ---------------------------------------------
#         # Intent evidence
#         # ---------------------------------------------

#         has_intent = (
#             not intents
#             or bool(intent_evidence)
#         )

#         full_intent = (
#             not intents
#             or len(intent_evidence)
#             == len(intents)
#         )

#         # ---------------------------------------------
#         # Legal evidence
#         # ---------------------------------------------

#         legal_evidence = (
#             legal_score >= 15
#             or concept_score >= 18
#             or phrase_score >= 10
#             or keyword_score >= 14
#             or number_score >= 14
#         )

#         # ---------------------------------------------
#         # RULE 1
#         # Strong semantic + legal evidence
#         # ---------------------------------------------

#         if (
#             strong_semantic
#             and legal_evidence
#             and has_intent
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 2
#         # Multi-source agreement
#         # ---------------------------------------------

#         if (
#             multi_source
#             and (
#                 full_intent
#                 or legal_evidence
#             )
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 3
#         # Strong lexical
#         # ---------------------------------------------

#         if (
#             lexical_score >= 0.20
#             and legal_evidence
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 4
#         # Medium semantic
#         # ---------------------------------------------

#         if (
#             medium_semantic
#             and (
#                 concept_score >= 18
#                 or legal_score >= 15
#             )
#             and has_intent
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 5
#         # Strong phrase
#         # ---------------------------------------------

#         if (
#             phrase_score >= 28
#             and legal_evidence
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 6
#         # Strong keyword
#         # ---------------------------------------------

#         if (
#             keyword_score >= 28
#             and legal_evidence
#         ):

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 7
#         # Strong number evidence
#         # ---------------------------------------------

#         if number_score >= 35:

#             verified.append(item)
#             continue

#         # ---------------------------------------------
#         # RULE 8
#         # General question
#         # ---------------------------------------------

#         if not intents:

#             if (
#                 strong_semantic
#                 or lexical_score >= 0.15
#                 or multi_source
#             ):

#                 verified.append(item)

#     return verified


# # =========================================================
# # CONFIDENCE
# # =========================================================

# def calculate_confidence(
#     verified,
#     ranked,
# ):

#     if not ranked:
#         return "low"

#     if not verified:
#         return "low"

#     top = verified[0]

#     sources = top[
#         "sources"
#     ]

#     semantic = top[
#         "semantic_score"
#     ]

#     legal = top[
#         "legal_score"
#     ]

#     lexical = top[
#         "lexical_score"
#     ]

#     # ---------------------------------------------
#     # High confidence
#     # ---------------------------------------------

#     if "exact" in sources:
#         return "high"

#     if (
#         semantic >= STRONG_SEMANTIC
#         and legal >= 15
#     ):
#         return "high"

#     if (
#         len(sources) >= 2
#         and legal >= 15
#     ):
#         return "high"

#     if (
#         lexical >= 0.20
#         and legal >= 15
#     ):
#         return "high"

#     # ---------------------------------------------
#     # Medium confidence
#     # ---------------------------------------------

#     if (
#         semantic >= MEDIUM_SEMANTIC
#         or legal >= 15
#         or top["concept_score"] >= 18
#         or top["phrase_score"] >= 10
#     ):
#         return "medium"

#     return "low"


# # =========================================================
# # DIVERSITY
# # =========================================================

# def select_diverse_articles(
#     articles,
#     limit,
# ):

#     selected = []

#     seen_ids = set()
#     seen_laws = defaultdict(int)

#     for article in articles:

#         if len(selected) >= limit:
#             break

#         article_id = article.id

#         if article_id in seen_ids:
#             continue

#         law_id = getattr(
#             article,
#             "law_id",
#             None,
#         )

#         # Eyni qanundan maksimum 3 maddə
#         if (
#             law_id is not None
#             and seen_laws[law_id] >= 3
#         ):
#             continue

#         selected.append(article)

#         seen_ids.add(article_id)

#         if law_id is not None:
#             seen_laws[law_id] += 1

#     return selected


# # =========================================================
# # FINAL SELECTION
# # =========================================================

# def select_final_articles(
#     verified,
#     ranked,
#     limit=FINAL_LIMIT,
# ):

#     selected_items = []
#     seen_ids = set()

#     # ---------------------------------------------
#     # VERIFIED FIRST
#     # ---------------------------------------------

#     for item in verified:

#         if len(selected_items) >= limit:
#             break

#         article = item["article"]

#         if article.id in seen_ids:
#             continue

#         selected_items.append(item)
#         seen_ids.add(article.id)

#     # ---------------------------------------------
#     # FALLBACK
#     # ---------------------------------------------

#     if len(selected_items) < limit:

#         for item in ranked:

#             if len(selected_items) >= limit:
#                 break

#             article = item["article"]

#             if article.id in seen_ids:
#                 continue

#             semantic_score = item[
#                 "semantic_score"
#             ]

#             lexical_score = item[
#                 "lexical_score"
#             ]

#             sources = item[
#                 "sources"
#             ]

#             # Tamamilə zəif semantic candidate
#             if (
#                 semantic_score
#                 < MIN_SEMANTIC_SCORE
#                 and lexical_score
#                 < 0.05
#                 and sources == {"semantic"}
#             ):
#                 continue

#             selected_items.append(item)
#             seen_ids.add(article.id)

#     # ---------------------------------------------
#     # Extract articles
#     # ---------------------------------------------

#     articles = [
#         item["article"]
#         for item in selected_items
#     ]

#     # ---------------------------------------------
#     # Diversity
#     # ---------------------------------------------

#     return select_diverse_articles(
#         articles,
#         limit,
#     )


# # =========================================================
# # DEBUG
# # =========================================================

# def print_search_debug(
#     question,
#     analysis,
#     ranked,
#     verified,
#     final_articles,
#     confidence,
# ):

#     print(
#         "\n================ SEARCH DEBUG ================"
#     )

#     print(
#         f"QUESTION: {question}"
#     )

#     print(
#         f"KEYWORDS: "
#         f"{analysis['keywords']}"
#     )

#     print(
#         f"EXPANDED: "
#         f"{analysis['expanded_keywords']}"
#     )

#     print(
#         f"PHRASES: "
#         f"{analysis['phrases']}"
#     )

#     print(
#         f"INTENTS: "
#         f"{analysis['intents']}"
#     )

#     print(
#         f"QUESTION TYPE: "
#         f"{analysis['question_type']}"
#     )

#     print(
#         f"NUMBERS: "
#         f"{analysis['numbers']}"
#     )

#     print(
#         f"ARTICLE NUMBERS: "
#         f"{analysis['article_numbers']}"
#     )

#     print(
#         f"CONFIDENCE: "
#         f"{confidence}"
#     )

#     print(
#         "\nTOP RANKED:"
#     )

#     for index, item in enumerate(
#         ranked[:10],
#         start=1,
#     ):

#         article = item["article"]

#         print(
#             f"{index}. "
#             f"Maddə {article.number} | "
#             f"Score={item['score']:.2f} | "
#             f"Semantic={item['semantic_score']:.4f} | "
#             f"Lexical={item['lexical_score']:.4f} | "
#             f"Keyword={item['keyword_score']} | "
#             f"Phrase={item['phrase_score']} | "
#             f"Legal={item['legal_score']} | "
#             f"Concept={item['concept_score']} | "
#             f"Number={item['number_score']} | "
#             f"Source={item['source_score']} | "
#             f"Intent={item['intent_bonus']} | "
#             f"Matched={item['matched_keywords']} | "
#             f"Sources={item['sources']} | "
#             f"{article.title}"
#         )

#     print(
#         "\nVERIFIED:"
#     )

#     for index, item in enumerate(
#         verified[:10],
#         start=1,
#     ):

#         article = item["article"]

#         print(
#             f"{index}. "
#             f"Maddə {article.number} | "
#             f"Score={item['score']:.2f} | "
#             f"Semantic={item['semantic_score']:.4f} | "
#             f"Lexical={item['lexical_score']:.4f} | "
#             f"Legal={item['legal_score']} | "
#             f"Sources={item['sources']} | "
#             f"{article.title}"
#         )

#     print(
#         "\nFINAL:"
#     )

#     for index, article in enumerate(
#         final_articles,
#         start=1,
#     ):

#         print(
#             f"{index}. "
#             f"Maddə {article.number} | "
#             f"{article.title}"
#         )

#     print(
#         "==============================================\n"
#     )


# # =========================================================
# # MAIN SEARCH PIPELINE
# # =========================================================

# def search_articles(
#     question,
#     limit=FINAL_LIMIT,
# ):

#     # =====================================================
#     # INPUT VALIDATION
#     # =====================================================

#     if not question:
#         return []

#     question = str(
#         question
#     ).strip()

#     if not question:
#         return []

#     # =====================================================
#     # 1. QUERY UNDERSTANDING
#     # =====================================================

#     analysis = analyze_query(
#         question
#     )

#     # =====================================================
#     # 2. EXACT ARTICLE SEARCH
#     # =====================================================

#     exact_results = (
#         exact_article_search(
#             question
#         )
#     )

#     # =====================================================
#     # 3. SEMANTIC SEARCH
#     # =====================================================

#     semantic_results = (
#         semantic_search(
#             question
#         )
#     )

#     # =====================================================
#     # 4. LEXICAL SEARCH
#     # =====================================================

#     lexical_results = (
#         lexical_search(
#             question,
#             analysis["keywords"],
#             analysis["intents"],
#         )
#     )

#     # =====================================================
#     # 5. FUSION
#     # =====================================================

#     candidates = merge_candidates(
#         exact_results,
#         semantic_results,
#         lexical_results,
#     )

#     # =====================================================
#     # 6. RERANK
#     # =====================================================

#     ranked = rerank_candidates(
#         candidates,
#         analysis,
#     )

#     # =====================================================
#     # 7. EVIDENCE VALIDATION
#     # =====================================================

#     verified = evidence_check(
#         ranked,
#         analysis,
#     )

#     # =====================================================
#     # 8. CONFIDENCE
#     # =====================================================

#     confidence = calculate_confidence(
#         verified,
#         ranked,
#     )

#     # =====================================================
#     # 9. FINAL ARTICLES
#     # =====================================================

#     final_articles = select_final_articles(
#         verified,
#         ranked,
#         limit=limit,
#     )

#     # =====================================================
#     # 10. DEBUG
#     # =====================================================

#     print_search_debug(
#         question,
#         analysis,
#         ranked,
#         verified,
#         final_articles,
#         confidence,
#     )

#     return final_articles
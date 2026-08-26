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
        .order_by("distance")[:100]
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
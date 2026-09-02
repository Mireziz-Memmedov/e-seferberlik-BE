import re
from collections import defaultdict

from openai import OpenAI
from django.conf import settings
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from pgvector.django import CosineDistance

from chatbot.models import Article


# =========================================================
# OPENAI
# =========================================================

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# =========================================================
# SEARCH SETTINGS
# =========================================================

SEMANTIC_LIMIT = 20
LEXICAL_LIMIT = 20
EXACT_LIMIT = 10

FINAL_LIMIT = 5

MAX_QUERY_TERMS = 30
MAX_PHRASES = 10


# =========================================================
# SEMANTIC THRESHOLDS
# =========================================================

STRONG_SEMANTIC = 0.48
MEDIUM_SEMANTIC = 0.32
MIN_SEMANTIC_SCORE = 0.20


# =========================================================
# SCORE WEIGHTS
# =========================================================

SEMANTIC_WEIGHT = 100
LEXICAL_WEIGHT = 35

TITLE_KEYWORD_SCORE = 14
CONTENT_KEYWORD_SCORE = 4

PHRASE_TITLE_SCORE = 28
PHRASE_CONTENT_SCORE = 10

# Vacib hüquqi phrase başlıqda keçirsə əlavə güclü bonus
IMPORTANT_TITLE_PHRASE_SCORE = 70

CONCEPT_TITLE_SCORE = 18
CONCEPT_CONTENT_SCORE = 6

NUMBER_TITLE_SCORE = 35
NUMBER_CONTENT_SCORE = 14

EXACT_SOURCE_SCORE = 300
SEMANTIC_SOURCE_SCORE = 10
LEXICAL_SOURCE_SCORE = 10

MULTI_SOURCE_BONUS = 22
THREE_SOURCE_BONUS = 15

FULL_INTENT_BONUS = 35
PARTIAL_INTENT_BONUS = 12

STRONG_LEXICAL_BONUS = 18
MEDIUM_LEXICAL_BONUS = 8

# Xüsusi olaraq "müddətli" / "müddətdən artıq"
DISTINCTIVE_PHRASE_BONUS = 55

# Query-də olan hüquqi phrase başlıqda varsa
LEGAL_TITLE_MATCH_BONUS = 35


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "men",
    "mən",
    "sen",
    "sən",
    "siz",
    "biz",

    "bu",
    "bir",

    "ve",
    "və",
    "ile",
    "ilə",
    "ucun",
    "üçün",

    "olan",
    "olaraq",

    "haqqinda",
    "haqqında",

    "nece",
    "necə",
    "nedir",
    "nədir",

    "kimdir",
    "kimler",
    "kimlər",

    "hansi",
    "hansı",
    "hansilar",
    "hansılar",

    "eden",
    "edən",
    "edilir",

    "edilmesi",
    "edilməsi",

    "verilen",
    "verilən",
    "verilir",
    "verilirmi",

    "var",

    "mi",
    "mı",
    "mu",
    "mü",

    "de",
    "də",
    "da",

    "ki",

    "gore",
    "görə",

    "menim",
    "mənim",
    "senin",
    "sənin",
    "sizin",
    "bizim",

    "oldugum",
    "olduğum",
    "oldugun",
    "olduğun",
    "oldugu",
    "olduğu",
    "olduqda",

    "halda",
    "halinda",
    "halında",

    "olar",
    "olur",

    "ede",
    "edə",

    "etmek",
    "etmək",

    "olanlar",
    "olanlari",
    "olanları",
}


# =========================================================
# RELATED WORDS
# =========================================================

RELATED_WORDS = {

    "toplanis": {
        "toplanis",
        "toplanisa",
        "toplanisdan",
        "toplanislar",
        "toplanislardan",
        "toplanislara",
        "toplanislarin",

        "telim",
        "telime",
        "telimden",
        "telimler",
        "telimlere",
        "telimlerden",
        "telimlerin",
    },

    "cagiris": {
        "cagiris",
        "cagirisa",
        "cagirisdan",
        "cagirislar",
        "cagirislarin",

        "cagir",
        "cagirilir",
        "cagirilirler",
        "cagirilacaq",
        "cagirilacaqdir",
        "cagirilmasi",
        "cagirilma",
        "cagirila",
        "cagirma",
    },

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
        "azad edilme",
        "azad olunma",
    },

    "mohlet": {
        "mohlet",
        "mohletin",
        "mohletle",
        "mohletler",
        "mohletlerden",
        "mohletden",

        "mohlet verilmesi",
        "mohlet verilir",
        "mohlet verilme",
        "mohlet alma",
    },

    "saglamliq": {
        "saglamliq",
        "saglamlig",
        "saglamligina",
        "saglamligindan",
        "saglamliqdan",

        "saglamliq veziyyeti",
        "saglamliq veziyyetine",
        "saglamliq veziyyetinden",

        "tibbi",
        "xestelik",
        "xeste",
        "yararsiz",
        "yararli",
    },

    "aile": {
        "aile",
        "ailesi",
        "ailenin",
        "aileye",
        "ailevi",

        "aile veziyyeti",
        "aile veziyyetine",
        "aile veziyyetinden",

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

        "ata",
        "ana",
        "valideyn",
    },

    "tehsil": {
        "tehsil",
        "tehsili",
        "tehsile",
        "tehsilde",

        "tehsil alan",
        "tehsil etmek",
        "tehsil alanlar",

        "telebe",
        "telebeler",

        "universitet",
        "ali mekteb",
        "mekteb",
    },

    "ehtiyat": {
        "ehtiyat",
        "ehtiyatda",
        "ehtiyatdaki",
        "ehtiyatdakilar",

        "ehtiyatda olan",
        "ehtiyatda olanlar",

        "ehtiyatci",
        "ehtiyatcilar",
    },
}


# =========================================================
# INTENTS
# =========================================================

INTENTS = {
    "toplanis": RELATED_WORDS["toplanis"],
    "cagiris": RELATED_WORDS["cagiris"],
    "azadetme": RELATED_WORDS["azadetme"],
    "mohlet": RELATED_WORDS["mohlet"],
    "saglamliq": RELATED_WORDS["saglamliq"],
    "aile": RELATED_WORDS["aile"],
    "tehsil": RELATED_WORDS["tehsil"],
    "ehtiyat": RELATED_WORDS["ehtiyat"],
}


# =========================================================
# PRIMARY INTENT TERMS
# =========================================================

INTENT_PRIMARY_TERMS = {
    "toplanis": [
        "toplanis",
        "telim",
    ],

    "cagiris": [
        "cagiris",
        "cagiril",
    ],

    "azadetme": [
        "azad",
    ],

    "mohlet": [
        "mohlet",
    ],

    "saglamliq": [
        "saglamliq",
        "tibbi",
    ],

    "aile": [
        "aile",
        "usaq",
        "ovlad",
    ],

    "tehsil": [
        "tehsil",
        "telebe",
    ],

    "ehtiyat": [
        "ehtiyat",
    ],
}


# =========================================================
# QUESTION TYPE PRIORITY
# =========================================================

QUESTION_TYPE_COMBINATIONS = [
    (
        {"toplanis", "ehtiyat", "aile"},
        "toplanis_ehtiyat_aile",
    ),
    (
        {"toplanis", "ehtiyat"},
        "toplanis_ehtiyat",
    ),
    (
        {"toplanis", "azadetme"},
        "toplanis_azadetme",
    ),
    (
        {"cagiris", "mohlet"},
        "cagiris_mohlet",
    ),
    (
        {"aile", "mohlet"},
        "aile_mohlet",
    ),
    (
        {"saglamliq", "mohlet"},
        "saglamliq_mohlet",
    ),
    (
        {"tehsil", "mohlet"},
        "tehsil_mohlet",
    ),
    (
        {"aile", "toplanis"},
        "toplanis_aile",
    ),
]


QUESTION_TYPE_PRIORITY = [
    "azadetme",
    "mohlet",
    "toplanis",
    "cagiris",
    "ehtiyat",
    "aile",
    "tehsil",
    "saglamliq",
]


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Azərbaycan dilində xüsusi simvolları
    search üçün sadələşdirir.
    """

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

    text = re.sub(
        r"[“”«»\"']",
        " ",
        text,
    )

    text = re.sub(
        r"[\(\)\[\]\{\}:;,!?]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# TOKENIZATION
# =========================================================

def tokenize(text):
    normalized = normalize_text(text)

    return re.findall(
        r"[a-z0-9.-]+",
        normalized,
    )


# =========================================================
# WORD NORMALIZATION
# =========================================================

def normalize_word_for_intent(word):
    """
    Sadə Azərbaycan dilində şəkilçi tolerantlığı.
    """

    word = normalize_text(word)

    if not word:
        return ""

    suffixes = [
        # cəm + hallanma
        "larin",
        "lerin",

        "lardan",
        "lerden",

        "lara",
        "lere",

        "lar",
        "ler",

        # hal şəkilçiləri
        "dan",
        "den",

        "nin",
        "nun",

        "na",
        "ne",

        "da",
        "de",

        "ta",
        "te",

        "ya",
        "ye",

        "ni",
        "nu",

        "in",
        "un",

        "im",
        "um",

        # tək sait şəkilçiləri
        "i",
        "u",

        "a",
        "e",
    ]

    for suffix in sorted(
        suffixes,
        key=len,
        reverse=True,
    ):

        if (
            word.endswith(suffix)
            and len(word) - len(suffix) >= 4
        ):
            word = word[:-len(suffix)]
            break

    return word


# =========================================================
# WORD MATCH
# =========================================================

def word_matches_text(
    text,
    word,
):
    """
    Sözün həm də şəkilçili formalarını
    tolerant şəkildə yoxlayır.

    Məs:
        cagirilir
        cagirilmasi
        cagirilacaq
    """

    if not text or not word:
        return False

    text = normalize_text(text)
    word = normalize_text(word)

    if len(word) < 3:
        return False

    # Exact
    if contains_word(text, word):
        return True

    # Intent-style normalized form
    base = normalize_word_for_intent(word)

    if base and len(base) >= 4:

        text_tokens = tokenize(text)

        for token in text_tokens:

            token_base = normalize_word_for_intent(
                token
            )

            if (
                token_base == base
                or token.startswith(base)
                or base.startswith(token_base)
            ):
                return True

    # Prefix tolerant matching
    if len(word) >= 6:

        prefix = word[:6]

        for token in tokenize(text):

            if token.startswith(prefix):
                return True

    return False


# =========================================================
# KEYWORDS
# =========================================================

def get_keywords(question):

    keywords = []

    for word in tokenize(question):

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intents(question):

    normalized = normalize_text(question)
    tokens = tokenize(question)

    normalized_tokens = {
        token: normalize_word_for_intent(token)
        for token in tokens
    }

    detected = set()

    for intent, words in INTENTS.items():

        for word in words:

            normalized_word = normalize_text(word)

            if not normalized_word:
                continue

            # ---------------------------------------------
            # Multi-word intent
            # ---------------------------------------------

            if " " in normalized_word:

                if normalized_word in normalized:
                    detected.add(intent)
                    break

                continue

            # ---------------------------------------------
            # Exact token
            # ---------------------------------------------

            if normalized_word in normalized_tokens:
                detected.add(intent)
                break

            # ---------------------------------------------
            # Stem-like matching
            # ---------------------------------------------

            base_word = normalize_word_for_intent(
                normalized_word
            )

            if not base_word:
                continue

            if base_word in normalized_tokens.values():
                detected.add(intent)
                break

            # ---------------------------------------------
            # Additional tolerant matching
            # ---------------------------------------------

            for token in tokens:

                token_base = normalize_word_for_intent(
                    token
                )

                if (
                    token_base == base_word
                    or token.startswith(base_word)
                    or base_word.startswith(token_base)
                ):
                    detected.add(intent)
                    break

            if intent in detected:
                break

    # ---------------------------------------------
    # Numerical family evidence
    # ---------------------------------------------

    if re.search(
        r"\b\d+\s+(usaq|usag|ovlad)\b",
        normalized,
    ):
        detected.add("aile")

    elif re.search(
        r"\b(usaq|usag|ovlad)\b",
        normalized,
    ):
        detected.add("aile")

    return detected


# =========================================================
# QUESTION TYPE
# =========================================================

def detect_question_type(intents):

    for required, question_type in QUESTION_TYPE_COMBINATIONS:

        if required.issubset(intents):
            return question_type

    for intent in QUESTION_TYPE_PRIORITY:

        if intent in intents:
            return intent

    return "general"


# =========================================================
# KEYWORD EXPANSION
# =========================================================

def expand_keywords(
    keywords,
    intents,
):

    expanded = []

    # ---------------------------------------------
    # User keywords first
    # ---------------------------------------------

    for keyword in keywords:

        keyword = normalize_text(keyword)

        if (
            len(keyword) >= 3
            and keyword not in expanded
        ):
            expanded.append(keyword)

    # ---------------------------------------------
    # Intent primary terms
    # ---------------------------------------------

    for intent in intents:

        for term in INTENT_PRIMARY_TERMS.get(
            intent,
            [],
        ):

            term = normalize_text(term)

            if (
                len(term) >= 3
                and term not in expanded
            ):
                expanded.append(term)

    return expanded[:MAX_QUERY_TERMS]


# =========================================================
# PHRASES
# =========================================================

IMPORTANT_PHRASES = [
    "toplanisdan azad",
    "toplanislardan azad",

    "toplanisa cagir",
    "toplanisa cagiril",
    "toplanislara cagir",

    "aile veziyyeti",

    "saglamliq veziyyeti",

    "tehsil alan",
    "tehsil alanlar",

    "ehtiyatda olan",
    "ehtiyatda olanlar",

    "muddetli heqiqi herbi xidmet",

    "herbi xidmete cagiris",
    "herbi xidmete cagiril",

    "mohlet veril",

    "azad edil",
]


# =========================================================
# DISTINCTIVE LEGAL PHRASES
# =========================================================

DISTINCTIVE_LEGAL_PHRASES = {
    "muddetli heqiqi herbi xidmet",
    "muddetden artiq heqiqi herbi xidmet",
}


def extract_query_phrases(question):

    normalized = normalize_text(question)

    phrases = []

    # ---------------------------------------------
    # Important legal phrases
    # ---------------------------------------------

    for pattern in IMPORTANT_PHRASES:

        pattern = normalize_text(pattern)

        if pattern in normalized:
            phrases.append(pattern)

    # ---------------------------------------------
    # Dynamic phrases
    # ---------------------------------------------

    words = [
        word
        for word in tokenize(question)
        if word not in STOP_WORDS
        and len(word) >= 3
    ]

    for size in (3, 2):

        for index in range(
            len(words) - size + 1
        ):

            phrase = " ".join(
                words[
                    index:index + size
                ]
            )

            if phrase not in phrases:
                phrases.append(phrase)

    return list(
        dict.fromkeys(phrases)
    )[:MAX_PHRASES]


# =========================================================
# ARTICLE NUMBER EXTRACTION
# =========================================================

def extract_article_numbers(question):

    normalized = normalize_text(question)

    patterns = [

        # 12.1 / 12.1.1
        r"\b(\d+\.\d+(?:\.\d+)*)\b",

        # 12-ci maddə
        r"\b(\d+)-ci\s+madd",

        # 12-cu maddə
        r"\b(\d+)-cu\s+madd",

        # 12-cü -> normalization sonrası 12-cu
        r"\b(\d+)-cu\s+maddesi",

        # 12-cı -> normalization sonrası 12-ci
        r"\b(\d+)-ci\s+maddesi",

        # 12 maddə
        r"\b(\d+)\s+madd",

        # maddə 12 / madde 12
        r"\bmadd[ae]\s+(\d+(?:\.\d+)*)\b",
    ]

    found = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            normalized,
        )

        for match in matches:

            if isinstance(match, tuple):
                match = match[0]

            if match not in found:
                found.append(match)

    return found


# =========================================================
# QUERY ANALYSIS
# =========================================================

def analyze_query(question):

    normalized = normalize_text(question)

    keywords = get_keywords(question)

    intents = detect_intents(question)

    question_type = detect_question_type(
        intents
    )

    expanded_keywords = expand_keywords(
        keywords,
        intents,
    )

    phrases = extract_query_phrases(
        question
    )

    numbers = re.findall(
        r"\b\d+(?:[.,]\d+)?\b",
        normalized,
    )

    article_numbers = extract_article_numbers(
        question
    )

    return {
        "normalized": normalized,
        "keywords": keywords,
        "expanded_keywords": expanded_keywords,
        "phrases": phrases,
        "intents": intents,
        "question_type": question_type,
        "numbers": numbers,
        "article_numbers": article_numbers,
    }


# =========================================================
# BASE QUERYSET
# =========================================================

def base_article_queryset():

    return (
        Article.objects
        .select_related("law")
        .exclude(embedding=None)
    )


# =========================================================
# EXACT ARTICLE SEARCH
# =========================================================

def exact_article_search(question):

    article_numbers = extract_article_numbers(
        question
    )

    if not article_numbers:
        return []

    queryset = (
        base_article_queryset()
        .filter(
            number__in=article_numbers
        )
    )

    results = []

    for article in queryset:

        results.append({
            "article": article,
            "semantic_score": 0.0,
            "lexical_score": 0.0,
            "sources": {"exact"},
        })

    return results[:EXACT_LIMIT]


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def semantic_search(question):

    try:

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=question,
        )

        question_embedding = (
            response.data[0].embedding
        )

    except Exception as exc:

        print(
            f"[SEMANTIC SEARCH ERROR] {exc}"
        )

        return []

    try:

        articles = (
            base_article_queryset()
            .annotate(
                distance=CosineDistance(
                    "embedding",
                    question_embedding,
                )
            )
            .order_by("distance")
            [:SEMANTIC_LIMIT]
        )

    except Exception as exc:

        print(
            f"[SEMANTIC DB ERROR] {exc}"
        )

        return []

    results = []

    for article in articles:

        distance = float(
            article.distance
        )

        similarity = max(
            0.0,
            min(
                1.0,
                1.0 - distance,
            ),
        )

        results.append({
            "article": article,
            "semantic_score": similarity,
            "lexical_score": 0.0,
            "sources": {"semantic"},
        })

    return results


# =========================================================
# LEXICAL SEARCH
# =========================================================

def lexical_search(question, keywords, intents):
    """
    PostgreSQL full-text lexical search.

    Original Azerbaijani words are used for SearchQuery.
    Terms are combined with OR so that one non-matching
    word does not eliminate the whole query.
    """

    words = re.findall(
        r"[A-Za-zƏəĞğİiIıÖöŞşÇçÜü0-9.-]+",
        str(question),
    )

    search_terms = []

    for word in words:
        normalized = normalize_text(word)

        if len(normalized) < 3:
            continue

        if normalized in STOP_WORDS:
            continue

        if word not in search_terms:
            search_terms.append(word)

    search_terms = search_terms[:MAX_QUERY_TERMS]

    if not search_terms:
        return []

    # ---------------------------------------------------------
    # SEARCH VECTOR
    # ---------------------------------------------------------

    search_vector = (
        SearchVector("title", weight="A")
        + SearchVector("content", weight="B")
    )

    # ---------------------------------------------------------
    # OR QUERY
    # ---------------------------------------------------------

    search_query = None

    for term in search_terms:
        current = SearchQuery(
            term,
            search_type="websearch",
        )

        if search_query is None:
            search_query = current
        else:
            search_query = search_query | current

    # ---------------------------------------------------------
    # DATABASE SEARCH
    # ---------------------------------------------------------

    try:
        articles = (
            base_article_queryset()
            .annotate(
                search_vector=search_vector,
            )
            .annotate(
                lexical_rank=SearchRank(
                    "search_vector",
                    search_query,
                )
            )
            .filter(
                search_vector=search_query,
            )
            .order_by(
                "-lexical_rank"
            )[:LEXICAL_LIMIT]
        )

    except Exception as exc:
        print(f"[LEXICAL SEARCH ERROR] {exc}")
        return []

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    results = []

    for article in articles:
        results.append({
            "article": article,
            "semantic_score": 0.0,
            "lexical_score": float(article.lexical_rank or 0.0),
            "sources": {"lexical"},
        })

    return results

# =========================================================
# CANDIDATE FUSION
# =========================================================

def merge_candidates(*result_sets):

    candidates = {}

    for results in result_sets:

        for item in results:

            article = item["article"]
            article_id = article.id

            if article_id not in candidates:

                candidates[article_id] = {
                    "article": article,

                    "semantic_score": item.get(
                        "semantic_score",
                        0.0,
                    ),

                    "lexical_score": item.get(
                        "lexical_score",
                        0.0,
                    ),

                    "sources": set(
                        item.get(
                            "sources",
                            set(),
                        )
                    ),
                }

                continue

            existing = candidates[
                article_id
            ]

            existing["semantic_score"] = max(
                existing["semantic_score"],
                item.get(
                    "semantic_score",
                    0.0,
                ),
            )

            existing["lexical_score"] = max(
                existing["lexical_score"],
                item.get(
                    "lexical_score",
                    0.0,
                ),
            )

            existing["sources"].update(
                item.get(
                    "sources",
                    set(),
                )
            )

    return list(
        candidates.values()
    )


# =========================================================
# TEXT MATCH HELPERS
# =========================================================

def contains_word(text, word):

    if not text or not word:
        return False

    return bool(
        re.search(
            rf"\b{re.escape(word)}\b",
            text,
        )
    )


def contains_phrase(text, phrase):

    if not text or not phrase:
        return False

    return phrase in text


# =========================================================
# DISTINCTIVE PHRASE SCORE
# =========================================================

def calculate_distinctive_phrase_score(
    article,
    question,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    normalized_question = normalize_text(
        question
    )

    score = 0
    matched = []

    for phrase in DISTINCTIVE_LEGAL_PHRASES:

        phrase = normalize_text(
            phrase
        )

        # Query-də phrase varsa
        if phrase not in normalized_question:
            continue

        # Başlıqda exact phrase
        if phrase in title:

            score += DISTINCTIVE_PHRASE_BONUS
            matched.append(phrase)

        # Məzmununda phrase
        elif phrase in content:

            score += 15
            matched.append(phrase)

    return score, matched


# =========================================================
# KEYWORD SCORE
# =========================================================

def calculate_keyword_score(
    article,
    keywords,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0
    matched = 0

    for keyword in keywords:

        keyword = normalize_text(
            keyword
        )

        if len(keyword) < 3:
            continue

        if word_matches_text(
            title,
            keyword,
        ):

            score += TITLE_KEYWORD_SCORE
            matched += 1

        elif word_matches_text(
            content,
            keyword,
        ):

            score += CONTENT_KEYWORD_SCORE
            matched += 1

    return score, matched


# =========================================================
# PHRASE SCORE
# =========================================================

def calculate_phrase_score(
    article,
    phrases,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0
    matched = 0
    important_title_matches = 0

    for phrase in phrases:

        phrase = normalize_text(
            phrase
        )

        if len(phrase) < 5:
            continue

        if contains_phrase(
            title,
            phrase,
        ):

            # Vacib hüquqi phrase
            if phrase in IMPORTANT_PHRASES:

                score += IMPORTANT_TITLE_PHRASE_SCORE
                important_title_matches += 1

            else:

                score += PHRASE_TITLE_SCORE

            matched += 1

        elif contains_phrase(
            content,
            phrase,
        ):

            score += PHRASE_CONTENT_SCORE
            matched += 1

    return (
        score,
        matched,
        important_title_matches,
    )


# =========================================================
# CONCEPT SCORE
# =========================================================

def calculate_concept_score(
    article,
    intents,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0

    for intent in intents:

        related_words = RELATED_WORDS.get(
            intent,
            set(),
        )

        title_found = False
        content_found = False

        for word in related_words:

            word = normalize_text(word)

            if len(word) < 3:
                continue

            if " " in word:

                if word in title:

                    title_found = True
                    break

                if word in content:

                    content_found = True

            else:

                if word_matches_text(
                    title,
                    word,
                ):

                    title_found = True
                    break

                if word_matches_text(
                    content,
                    word,
                ):

                    content_found = True

        if title_found:

            score += CONCEPT_TITLE_SCORE

        elif content_found:

            score += CONCEPT_CONTENT_SCORE

    return score


# =========================================================
# LEGAL SCORE
# =========================================================

def calculate_legal_score(
    article,
    intents,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0

    for intent in intents:

        related_words = RELATED_WORDS.get(
            intent,
            set(),
        )

        title_hit = False
        content_hits = 0

        for word in related_words:

            word = normalize_text(word)

            if len(word) < 3:
                continue

            if " " in word:

                if word in title:

                    title_hit = True

                elif word in content:

                    content_hits += 1

            else:

                if word_matches_text(
                    title,
                    word,
                ):

                    title_hit = True

                elif word_matches_text(
                    content,
                    word,
                ):

                    content_hits += 1

        if title_hit:

            score += 20

        elif content_hits >= 3:

            score += 10

        elif content_hits >= 1:

            score += 4

    # ---------------------------------------------
    # Multiple intent agreement
    # ---------------------------------------------

    if len(intents) >= 2:

        covered = 0

        for intent in intents:

            related_words = RELATED_WORDS.get(
                intent,
                set(),
            )

            intent_found = False

            for word in related_words:

                word = normalize_text(word)

                if len(word) < 3:
                    continue

                if " " in word:

                    if (
                        word in title
                        or word in content
                    ):

                        intent_found = True
                        break

                else:

                    if (
                        word_matches_text(
                            title,
                            word,
                        )
                        or
                        word_matches_text(
                            content,
                            word,
                        )
                    ):

                        intent_found = True
                        break

            if intent_found:
                covered += 1

        if covered == len(intents):

            score += 25

        elif covered >= 2:

            score += 10

    return score


# =========================================================
# NUMBER SCORE
# =========================================================

def calculate_number_score(
    article,
    numbers,
):

    if not numbers:
        return 0

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0

    for number in numbers:

        pattern = (
            rf"\b{re.escape(number)}\b"
        )

        if re.search(
            pattern,
            title,
        ):

            score += NUMBER_TITLE_SCORE

        elif re.search(
            pattern,
            content,
        ):

            score += NUMBER_CONTENT_SCORE

    return score


# =========================================================
# SOURCE SCORE
# =========================================================

def calculate_source_score(
    sources,
):

    score = 0

    if "exact" in sources:

        score += EXACT_SOURCE_SCORE

    if "semantic" in sources:

        score += SEMANTIC_SOURCE_SCORE

    if "lexical" in sources:

        score += LEXICAL_SOURCE_SCORE

    if len(sources) >= 2:

        score += MULTI_SOURCE_BONUS

    if len(sources) >= 3:

        score += THREE_SOURCE_BONUS

    return score


# =========================================================
# INTENT EVIDENCE
# =========================================================

def calculate_intent_evidence(
    article,
    intents,
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    matched = set()

    for intent in intents:

        related_words = RELATED_WORDS.get(
            intent,
            set(),
        )

        for word in related_words:

            word = normalize_text(word)

            if len(word) < 3:
                continue

            if " " in word:

                if (
                    word in title
                    or word in content
                ):

                    matched.add(intent)
                    break

            else:

                if (
                    word_matches_text(
                        title,
                        word,
                    )
                    or
                    word_matches_text(
                        content,
                        word,
                    )
                ):

                    matched.add(intent)
                    break

    return matched


# =========================================================
# QUERY-TITLE DISTINCTION
# =========================================================

def calculate_query_title_match(
    article,
    analysis,
):

    title = normalize_text(
        article.title or ""
    )

    normalized_query = analysis[
        "normalized"
    ]

    score = 0

    matched = []

    # ---------------------------------------------
    # Important phrase title match
    # ---------------------------------------------

    for phrase in IMPORTANT_PHRASES:

        phrase = normalize_text(
            phrase
        )

        if phrase in normalized_query:

            if phrase in title:

                score += LEGAL_TITLE_MATCH_BONUS
                matched.append(phrase)

    return score, matched


# =========================================================
# RERANK
# =========================================================

def rerank_candidates(
    candidates,
    analysis,
):

    keywords = analysis[
        "expanded_keywords"
    ]

    phrases = analysis[
        "phrases"
    ]

    intents = analysis[
        "intents"
    ]

    numbers = analysis[
        "numbers"
    ]

    ranked = []

    for item in candidates:

        article = item["article"]

        semantic_score = float(
            item.get(
                "semantic_score",
                0.0,
            )
        )

        lexical_score = float(
            item.get(
                "lexical_score",
                0.0,
            )
        )

        sources = item["sources"]

        # ---------------------------------------------
        # Base scores
        # ---------------------------------------------

        semantic_points = (
            semantic_score
            * SEMANTIC_WEIGHT
        )

        lexical_points = min(
            lexical_score
            * LEXICAL_WEIGHT,
            35,
        )

        keyword_points, matched_keywords = (
            calculate_keyword_score(
                article,
                keywords,
            )
        )

        (
            phrase_points,
            matched_phrases,
            important_title_matches,
        ) = calculate_phrase_score(
            article,
            phrases,
        )

        concept_points = (
            calculate_concept_score(
                article,
                intents,
            )
        )

        legal_points = (
            calculate_legal_score(
                article,
                intents,
            )
        )

        number_points = (
            calculate_number_score(
                article,
                numbers,
            )
        )

        source_points = (
            calculate_source_score(
                sources
            )
        )

        distinctive_points, distinctive_matches = (
            calculate_distinctive_phrase_score(
                article,
                analysis["normalized"],
            )
        )

        query_title_points, query_title_matches = (
            calculate_query_title_match(
                article,
                analysis,
            )
        )

        # ---------------------------------------------
        # Intent evidence
        # ---------------------------------------------

        intent_evidence = (
            calculate_intent_evidence(
                article,
                intents,
            )
        )

        intent_bonus = 0

        if intents:

            coverage = (
                len(intent_evidence)
                / len(intents)
            )

            if coverage >= 1.0:

                intent_bonus = FULL_INTENT_BONUS

            elif coverage >= 0.5:

                intent_bonus = PARTIAL_INTENT_BONUS

        # ---------------------------------------------
        # Keyword bonus
        # ---------------------------------------------

        if matched_keywords >= 5:

            keyword_bonus = 20

        elif matched_keywords >= 3:

            keyword_bonus = 12

        elif matched_keywords >= 2:

            keyword_bonus = 6

        else:

            keyword_bonus = 0

        # ---------------------------------------------
        # Phrase bonus
        # ---------------------------------------------

        if matched_phrases >= 3:

            phrase_bonus = 18

        elif matched_phrases >= 2:

            phrase_bonus = 12

        elif matched_phrases == 1:

            phrase_bonus = 6

        else:

            phrase_bonus = 0

        # ---------------------------------------------
        # Lexical quality
        # ---------------------------------------------

        if lexical_score >= 0.25:

            lexical_bonus = STRONG_LEXICAL_BONUS

        elif lexical_score >= 0.10:

            lexical_bonus = MEDIUM_LEXICAL_BONUS

        else:

            lexical_bonus = 0

        # ---------------------------------------------
        # Final score
        # ---------------------------------------------

        total_score = (
            semantic_points
            + lexical_points
            + keyword_points
            + phrase_points
            + concept_points
            + legal_points
            + number_points
            + source_points
            + intent_bonus
            + keyword_bonus
            + phrase_bonus
            + lexical_bonus
            + distinctive_points
            + query_title_points
        )

        ranked.append({

            "article": article,

            "score": total_score,

            "semantic_score":
                semantic_score,

            "lexical_score":
                lexical_score,

            "keyword_score":
                keyword_points,

            "phrase_score":
                phrase_points,

            "concept_score":
                concept_points,

            "legal_score":
                legal_points,

            "number_score":
                number_points,

            "source_score":
                source_points,

            "intent_bonus":
                intent_bonus,

            "keyword_bonus":
                keyword_bonus,

            "phrase_bonus":
                phrase_bonus,

            "lexical_bonus":
                lexical_bonus,

            "distinctive_phrase_score":
                distinctive_points,

            "query_title_score":
                query_title_points,

            "matched_keywords":
                matched_keywords,

            "matched_phrases":
                matched_phrases,

            "important_title_matches":
                important_title_matches,

            "distinctive_matches":
                distinctive_matches,

            "query_title_matches":
                query_title_matches,

            "intent_evidence":
                intent_evidence,

            "sources":
                sources,
        })

    # ---------------------------------------------
    # Ranking
    # ---------------------------------------------

    ranked.sort(
        key=lambda item: (
            "exact" in item["sources"],
            item["score"],
            item["distinctive_phrase_score"],
            item["query_title_score"],
            item["phrase_score"],
            item["semantic_score"],
            item["lexical_score"],
            item["legal_score"],
        ),
        reverse=True,
    )

    return ranked


# =========================================================
# EVIDENCE CHECK
# =========================================================

def evidence_check(
    ranked,
    analysis,
):

    verified = []

    intents = analysis[
        "intents"
    ]

    for item in ranked:

        semantic_score = item[
            "semantic_score"
        ]

        lexical_score = item[
            "lexical_score"
        ]

        legal_score = item[
            "legal_score"
        ]

        concept_score = item[
            "concept_score"
        ]

        keyword_score = item[
            "keyword_score"
        ]

        phrase_score = item[
            "phrase_score"
        ]

        number_score = item[
            "number_score"
        ]

        sources = item[
            "sources"
        ]

        intent_evidence = item[
            "intent_evidence"
        ]

        distinctive_phrase_score = item.get(
            "distinctive_phrase_score",
            0,
        )

        query_title_score = item.get(
            "query_title_score",
            0,
        )

        # ---------------------------------------------
        # Exact article
        # ---------------------------------------------

        if "exact" in sources:

            verified.append(item)
            continue

        # ---------------------------------------------
        # Semantic levels
        # ---------------------------------------------

        strong_semantic = (
            semantic_score
            >= STRONG_SEMANTIC
        )

        medium_semantic = (
            semantic_score
            >= MEDIUM_SEMANTIC
        )

        # ---------------------------------------------
        # Multi-source agreement
        # ---------------------------------------------

        multi_source = (
            len(sources) >= 2
        )

        # ---------------------------------------------
        # Intent evidence
        # ---------------------------------------------

        has_intent = (
            not intents
            or bool(intent_evidence)
        )

        full_intent = (
            not intents
            or len(intent_evidence)
            == len(intents)
        )

        # ---------------------------------------------
        # Legal evidence
        # ---------------------------------------------

        legal_evidence = (
            legal_score >= 15
            or concept_score >= 18
            or phrase_score >= 10
            or keyword_score >= 14
            or number_score >= 14
            or distinctive_phrase_score >= 15
            or query_title_score >= 20
        )

        # ---------------------------------------------
        # RULE 0
        # Distinctive legal phrase
        # ---------------------------------------------

        if (
            distinctive_phrase_score >= DISTINCTIVE_PHRASE_BONUS
            and query_title_score >= LEGAL_TITLE_MATCH_BONUS
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 1
        # Strong semantic + legal evidence
        # ---------------------------------------------

        if (
            strong_semantic
            and legal_evidence
            and has_intent
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 2
        # Multi-source agreement
        # ---------------------------------------------

        if (
            multi_source
            and (
                full_intent
                or legal_evidence
            )
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 3
        # Strong lexical
        # ---------------------------------------------

        if (
            lexical_score >= 0.20
            and legal_evidence
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 4
        # Medium semantic
        # ---------------------------------------------

        if (
            medium_semantic
            and (
                concept_score >= 18
                or legal_score >= 15
            )
            and has_intent
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 5
        # Strong phrase
        # ---------------------------------------------

        if (
            phrase_score >= 28
            and legal_evidence
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 6
        # Strong keyword
        # ---------------------------------------------

        if (
            keyword_score >= 28
            and legal_evidence
        ):

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 7
        # Strong number evidence
        # ---------------------------------------------

        if number_score >= 35:

            verified.append(item)
            continue

        # ---------------------------------------------
        # RULE 8
        # General question
        # ---------------------------------------------

        if not intents:

            if (
                strong_semantic
                or lexical_score >= 0.15
                or multi_source
            ):

                verified.append(item)

    return verified


# =========================================================
# CONFIDENCE
# =========================================================

def calculate_confidence(
    verified,
    ranked,
):

    if not ranked:
        return "low"

    if not verified:
        return "low"

    top = verified[0]

    sources = top[
        "sources"
    ]

    semantic = top[
        "semantic_score"
    ]

    legal = top[
        "legal_score"
    ]

    lexical = top[
        "lexical_score"
    ]

    distinctive_phrase_score = top.get(
        "distinctive_phrase_score",
        0,
    )

    # ---------------------------------------------
    # High confidence
    # ---------------------------------------------

    if "exact" in sources:
        return "high"

    if distinctive_phrase_score >= DISTINCTIVE_PHRASE_BONUS:
        return "high"

    if (
        semantic >= STRONG_SEMANTIC
        and legal >= 15
    ):

        return "high"

    if (
        len(sources) >= 2
        and legal >= 15
    ):

        return "high"

    if (
        lexical >= 0.20
        and legal >= 15
    ):

        return "high"

    # ---------------------------------------------
    # Medium confidence
    # ---------------------------------------------

    if (
        semantic >= MEDIUM_SEMANTIC
        or legal >= 15
        or top["concept_score"] >= 18
        or top["phrase_score"] >= 10
    ):

        return "medium"

    return "low"


# =========================================================
# DIVERSITY
# =========================================================

def select_diverse_articles(
    articles,
    limit,
):

    selected = []

    seen_ids = set()
    seen_laws = defaultdict(int)

    for article in articles:

        if len(selected) >= limit:
            break

        article_id = article.id

        if article_id in seen_ids:
            continue

        law_id = getattr(
            article,
            "law_id",
            None,
        )

        # Eyni qanundan maksimum 3 maddə
        if (
            law_id is not None
            and seen_laws[law_id] >= 3
        ):

            continue

        selected.append(article)

        seen_ids.add(article_id)

        if law_id is not None:
            seen_laws[law_id] += 1

    return selected


# =========================================================
# FINAL SELECTION
# =========================================================

def select_final_articles(
    verified,
    ranked,
    limit=FINAL_LIMIT,
):

    selected_items = []
    seen_ids = set()

    # ---------------------------------------------
    # VERIFIED FIRST
    # ---------------------------------------------

    for item in verified:

        if len(selected_items) >= limit:
            break

        article = item["article"]

        if article.id in seen_ids:
            continue

        selected_items.append(item)
        seen_ids.add(article.id)

    # ---------------------------------------------
    # FALLBACK
    # ---------------------------------------------

    if len(selected_items) < limit:

        for item in ranked:

            if len(selected_items) >= limit:
                break

            article = item["article"]

            if article.id in seen_ids:
                continue

            semantic_score = item[
                "semantic_score"
            ]

            lexical_score = item[
                "lexical_score"
            ]

            sources = item[
                "sources"
            ]

            # Tamamilə zəif semantic candidate
            if (
                semantic_score
                < MIN_SEMANTIC_SCORE
                and lexical_score
                < 0.05
                and sources == {"semantic"}
            ):

                continue

            selected_items.append(item)
            seen_ids.add(article.id)

    # ---------------------------------------------
    # Extract articles
    # ---------------------------------------------

    articles = [
        item["article"]
        for item in selected_items
    ]

    # ---------------------------------------------
    # Diversity
    # ---------------------------------------------

    return select_diverse_articles(
        articles,
        limit,
    )


# =========================================================
# DEBUG
# =========================================================

def print_search_debug(
    question,
    analysis,
    ranked,
    verified,
    final_articles,
    confidence,
):

    print(
        "\n================ SEARCH DEBUG ================"
    )

    print(
        f"QUESTION: {question}"
    )

    print(
        f"NORMALIZED: "
        f"{analysis['normalized']}"
    )

    print(
        f"KEYWORDS: "
        f"{analysis['keywords']}"
    )

    print(
        f"EXPANDED: "
        f"{analysis['expanded_keywords']}"
    )

    print(
        f"PHRASES: "
        f"{analysis['phrases']}"
    )

    print(
        f"INTENTS: "
        f"{analysis['intents']}"
    )

    print(
        f"QUESTION TYPE: "
        f"{analysis['question_type']}"
    )

    print(
        f"NUMBERS: "
        f"{analysis['numbers']}"
    )

    print(
        f"ARTICLE NUMBERS: "
        f"{analysis['article_numbers']}"
    )

    print(
        f"CONFIDENCE: "
        f"{confidence}"
    )

    print(
        "\nTOP RANKED:"
    )

    for index, item in enumerate(
        ranked[:5],
        start=1,
    ):

        article = item["article"]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Semantic={item['semantic_score']:.4f} | "
            f"Lexical={item['lexical_score']:.4f} | "
            f"Keyword={item['keyword_score']} | "
            f"Phrase={item['phrase_score']} | "
            f"Legal={item['legal_score']} | "
            f"Concept={item['concept_score']} | "
            f"Number={item['number_score']} | "
            f"Source={item['source_score']} | "
            f"Intent={item['intent_bonus']} | "
            f"Distinctive={item.get('distinctive_phrase_score', 0)} | "
            f"TitleMatch={item.get('query_title_score', 0)} | "
            f"Matched={item['matched_keywords']} | "
            f"Sources={item['sources']} | "
            f"{article.title}"
        )

    print(
        "\nVERIFIED:"
    )

    for index, item in enumerate(
        verified[:5],
        start=1,
    ):

        article = item["article"]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Semantic={item['semantic_score']:.4f} | "
            f"Lexical={item['lexical_score']:.4f} | "
            f"Legal={item['legal_score']} | "
            f"Distinctive={item.get('distinctive_phrase_score', 0)} | "
            f"TitleMatch={item.get('query_title_score', 0)} | "
            f"Sources={item['sources']} | "
            f"{article.title}"
        )

    print(
        "\nFINAL:"
    )

    for index, article in enumerate(
        final_articles,
        start=1,
    ):

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"{article.title}"
        )

    print(
        "==============================================\n"
    )


# =========================================================
# MAIN SEARCH PIPELINE
# =========================================================

def search_articles(
    question,
    limit=FINAL_LIMIT,
):

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not question:
        return []

    question = str(
        question
    ).strip()

    if not question:
        return []

    # =====================================================
    # 1. QUERY UNDERSTANDING
    # =====================================================

    analysis = analyze_query(
        question
    )

    # =====================================================
    # 2. EXACT ARTICLE SEARCH
    # =====================================================

    exact_results = (
        exact_article_search(
            question
        )
    )

    # =====================================================
    # 3. SEMANTIC SEARCH
    # =====================================================

    semantic_results = (
        semantic_search(
            question
        )
    )

    # =====================================================
    # 4. LEXICAL SEARCH
    # =====================================================

    lexical_results = (
        lexical_search(
            question,
            analysis["expanded_keywords"],
            analysis["intents"],
        )
    )

    # =====================================================
    # 5. FUSION
    # =====================================================

    candidates = merge_candidates(
        exact_results,
        semantic_results,
        lexical_results,
    )

    # =====================================================
    # 6. RERANK
    # =====================================================

    ranked = rerank_candidates(
        candidates,
        analysis,
    )

    # =====================================================
    # 7. EVIDENCE VALIDATION
    # =====================================================

    verified = evidence_check(
        ranked,
        analysis,
    )

    # =====================================================
    # 8. CONFIDENCE
    # =====================================================

    confidence = calculate_confidence(
        verified,
        ranked,
    )

    # =====================================================
    # 9. FINAL ARTICLES
    # =====================================================

    final_articles = select_final_articles(
        verified,
        ranked,
        limit=limit,
    )

    # =====================================================
    # 10. DEBUG
    # =====================================================

    print_search_debug(
        question,
        analysis,
        ranked,
        verified,
        final_articles,
        confidence,
    )

    return final_articles
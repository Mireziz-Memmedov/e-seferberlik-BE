import re
from collections import defaultdict
from functools import lru_cache

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

DISTINCTIVE_PHRASE_BONUS = 55

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
        "cagiril",
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
# QUESTION TYPE
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

_NORMALIZE_REPLACEMENTS = str.maketrans({
    "ə": "e",
    "ı": "i",
    "ö": "o",
    "ü": "u",
    "ğ": "g",
    "ş": "s",
    "ç": "c",
})

_NORMALIZE_PUNCT_RE = re.compile(
    r"[“”«»\"'()\[\]\{\}:;,!?]"
)

_NORMALIZE_SPACE_RE = re.compile(
    r"\s+"
)


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower().strip()

    text = text.translate(
        _NORMALIZE_REPLACEMENTS
    )

    text = _NORMALIZE_PUNCT_RE.sub(
        " ",
        text,
    )

    text = _NORMALIZE_SPACE_RE.sub(
        " ",
        text,
    )

    return text.strip()


# =========================================================
# TOKENIZATION
# =========================================================

_TOKEN_RE = re.compile(
    r"[a-z0-9.-]+"
)


def tokenize(text):
    if not text:
        return []

    normalized = normalize_text(text)

    return _TOKEN_RE.findall(
        normalized
    )


# =========================================================
# WORD NORMALIZATION
# =========================================================

_WORD_SUFFIXES = (
    "larin",
    "lerin",
    "lardan",
    "lerden",
    "lara",
    "lere",
    "lar",
    "ler",
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
    "i",
    "u",
    "a",
    "e",
)


@lru_cache(maxsize=4096)
def normalize_word_for_intent(word):
    """
    Sadə Azərbaycan dilində şəkilçi tolerantlığı.

    Cache istifadə olunur ki, eyni sözlər
    yüzlərlə dəfə yenidən hesablanmasın.
    """

    word = normalize_text(word)

    if not word:
        return ""

    for suffix in _WORD_SUFFIXES:

        if (
            word.endswith(suffix)
            and len(word) - len(suffix) >= 4
        ):
            word = word[:-len(suffix)]
            break

    return word


# =========================================================
# PRECOMPUTED INTENT WORDS
# =========================================================

NORMALIZED_RELATED_WORDS = {}

for _intent, _words in RELATED_WORDS.items():

    NORMALIZED_RELATED_WORDS[_intent] = tuple(
        dict.fromkeys(
            normalize_text(word)
            for word in _words
            if normalize_text(word)
        )
    )


NORMALIZED_INTENT_PRIMARY_TERMS = {
    intent: tuple(
        dict.fromkeys(
            normalize_text(term)
            for term in terms
            if normalize_text(term)
        )
    )
    for intent, terms in INTENT_PRIMARY_TERMS.items()
}


# =========================================================
# WORD MATCH
# =========================================================

def word_matches_text(
    text,
    word,
    text_tokens=None,
    base_tokens=None,
    normalized=False,
):
    """
    Mətn daxilində sözün olub-olmadığını yoxlayır.

    Performance:
    - normalize yalnız lazım olduqda edilir
    - tokenlər cache-dən gəlir
    - stem/base tokenlər cache-dən gəlir
    """

    if not text or not word:
        return False

    if not normalized:
        text = normalize_text(text)

    word = normalize_text(word)

    if len(word) < 3:
        return False

    # -----------------------------------------------------
    # Exact word
    # -----------------------------------------------------

    if contains_word(text, word):
        return True

    # -----------------------------------------------------
    # Tokens
    # -----------------------------------------------------

    if text_tokens is None:
        text_tokens = tokenize(text)

    # -----------------------------------------------------
    # Stem matching
    # -----------------------------------------------------

    base = normalize_word_for_intent(word)

    if base and len(base) >= 4:

        if base_tokens is None:
            base_tokens = {
                normalize_word_for_intent(token)
                for token in text_tokens
            }

        if base in base_tokens:
            return True

        for token in text_tokens:

            token_base = normalize_word_for_intent(
                token
            )

            if (
                token_base == base
                or token.startswith(base)
                or (
                    token_base
                    and base.startswith(token_base)
                )
            ):
                return True

    # -----------------------------------------------------
    # Prefix fallback
    # -----------------------------------------------------

    if len(word) >= 6:

        prefix = word[:6]

        for token in text_tokens:

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
    tokens = tokenize(normalized)

    normalized_tokens = {
        token: normalize_word_for_intent(token)
        for token in tokens
    }

    normalized_token_bases = set(
        normalized_tokens.values()
    )

    detected = set()

    for intent, words in NORMALIZED_RELATED_WORDS.items():

        for normalized_word in words:

            if len(normalized_word) < 3:
                continue

            # -------------------------------------------------
            # Multi-word intent
            # -------------------------------------------------

            if " " in normalized_word:

                if normalized_word in normalized:
                    detected.add(intent)
                    break

                continue

            # -------------------------------------------------
            # Exact token
            # -------------------------------------------------

            if normalized_word in normalized_tokens:
                detected.add(intent)
                break

            # -------------------------------------------------
            # Stem
            # -------------------------------------------------

            base_word = normalize_word_for_intent(
                normalized_word
            )

            if not base_word:
                continue

            if base_word in normalized_token_bases:
                detected.add(intent)
                break

            # -------------------------------------------------
            # Prefix tolerant matching
            # -------------------------------------------------

            found = False

            for token in tokens:

                token_base = normalize_word_for_intent(
                    token
                )

                if (
                    token_base == base_word
                    or token.startswith(base_word)
                    or (
                        token_base
                        and base_word.startswith(
                            token_base
                        )
                    )
                ):
                    detected.add(intent)
                    found = True
                    break

            if found:
                break

    # ---------------------------------------------------------
    # Numerical family evidence
    # ---------------------------------------------------------

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

    for keyword in keywords:

        keyword = normalize_text(keyword)

        if (
            len(keyword) >= 3
            and keyword not in expanded
        ):
            expanded.append(keyword)

    for intent in intents:

        for term in NORMALIZED_INTENT_PRIMARY_TERMS.get(
            intent,
            (),
        ):

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


NORMALIZED_IMPORTANT_PHRASES = tuple(
    dict.fromkeys(
        normalize_text(phrase)
        for phrase in IMPORTANT_PHRASES
    )
)


NORMALIZED_IMPORTANT_PHRASE_SET = set(
    NORMALIZED_IMPORTANT_PHRASES
)


# =========================================================
# DISTINCTIVE LEGAL PHRASES
# =========================================================

DISTINCTIVE_LEGAL_PHRASES = {
    "muddetli heqiqi herbi xidmet",
    "muddetden artiq heqiqi herbi xidmet",
}


NORMALIZED_DISTINCTIVE_PHRASES = tuple(
    dict.fromkeys(
        normalize_text(phrase)
        for phrase in DISTINCTIVE_LEGAL_PHRASES
    )
)


# =========================================================
# PHRASE EXTRACTION
# =========================================================

def extract_query_phrases(question):

    normalized = normalize_text(question)

    phrases = []

    # ---------------------------------------------------------
    # Important legal phrases
    # ---------------------------------------------------------

    for pattern in NORMALIZED_IMPORTANT_PHRASES:

        if pattern in normalized:
            phrases.append(pattern)

    # ---------------------------------------------------------
    # Dynamic phrases
    # ---------------------------------------------------------

    words = [
        word
        for word in tokenize(normalized)
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

        r"\b(\d+\.\d+(?:\.\d+)*)\b",

        r"\b(\d+)-ci\s+madd",

        r"\b(\d+)-cu\s+madd",

        r"\b(\d+)-cu\s+maddesi",

        r"\b(\d+)-ci\s+maddesi",

        r"\b(\d+)\s+madd",

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
# BASE QUERYSETS
# =========================================================

def article_queryset():

    return (
        Article.objects
        .select_related("law")
    )


def semantic_article_queryset():

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
        article_queryset()
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
            semantic_article_queryset()
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

def lexical_search(keywords):

    search_terms = []

    for word in keywords:

        word = normalize_text(word)

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        if word not in search_terms:
            search_terms.append(word)

    search_terms = search_terms[:MAX_QUERY_TERMS]

    if not search_terms:
        return []

    search_vector = (
        SearchVector(
            "title",
            weight="A",
        )
        +
        SearchVector(
            "content",
            weight="B",
        )
    )

    search_query = None

    for term in search_terms:

        current = SearchQuery(
            term,
            search_type="websearch",
        )

        if search_query is None:

            search_query = current

        else:

            search_query = (
                search_query | current
            )

    try:

        articles = (
            article_queryset()
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
            )
            [:LEXICAL_LIMIT]
        )

    except Exception as exc:

        print(
            f"[LEXICAL SEARCH ERROR] {exc}"
        )

        return []

    results = []

    for article in articles:

        results.append({
            "article": article,
            "semantic_score": 0.0,
            "lexical_score": float(
                article.lexical_rank or 0.0
            ),
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
# SOURCE SCORE
# =========================================================

def calculate_source_score(sources):

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

    normalized_question = analysis[
        "normalized"
    ]

    ranked = []

    # -----------------------------------------------------
    # Pre-normalize query data
    # -----------------------------------------------------

    normalized_keywords = tuple(
        dict.fromkeys(
            normalize_text(keyword)
            for keyword in keywords
            if len(normalize_text(keyword)) >= 3
        )
    )

    normalized_phrases = tuple(
        dict.fromkeys(
            normalize_text(phrase)
            for phrase in phrases
            if len(normalize_text(phrase)) >= 5
        )
    )

    # -----------------------------------------------------
    # Candidate loop
    # -----------------------------------------------------

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

        # =================================================
        # ARTICLE TEXT CACHE
        # =================================================

        normalized_title = normalize_text(
            article.title or ""
        )

        normalized_content = normalize_text(
            article.content or ""
        )

        title_tokens = set(
            tokenize(normalized_title)
        )

        content_tokens = set(
            tokenize(normalized_content)
        )

        title_base_tokens = {
            normalize_word_for_intent(token)
            for token in title_tokens
            if normalize_word_for_intent(token)
        }

        content_base_tokens = {
            normalize_word_for_intent(token)
            for token in content_tokens
            if normalize_word_for_intent(token)
        }

        # =================================================
        # BASE SCORES
        # =================================================

        semantic_points = (
            semantic_score
            * SEMANTIC_WEIGHT
        )

        lexical_points = min(
            lexical_score
            * LEXICAL_WEIGHT,
            35,
        )

        # =================================================
        # KEYWORD SCORE
        # =================================================

        keyword_points = 0
        matched_keywords = 0

        for keyword in normalized_keywords:

            if word_matches_text(
                normalized_title,
                keyword,
                text_tokens=title_tokens,
                base_tokens=title_base_tokens,
                normalized=True,
            ):

                keyword_points += (
                    TITLE_KEYWORD_SCORE
                )

                matched_keywords += 1

            elif word_matches_text(
                normalized_content,
                keyword,
                text_tokens=content_tokens,
                base_tokens=content_base_tokens,
                normalized=True,
            ):

                keyword_points += (
                    CONTENT_KEYWORD_SCORE
                )

                matched_keywords += 1

        # =================================================
        # PHRASE SCORE
        # =================================================

        phrase_points = 0
        matched_phrases = 0
        important_title_matches = 0

        for phrase in normalized_phrases:

            if phrase in normalized_title:

                if (
                    phrase
                    in NORMALIZED_IMPORTANT_PHRASE_SET
                ):

                    phrase_points += (
                        IMPORTANT_TITLE_PHRASE_SCORE
                    )

                    important_title_matches += 1

                else:

                    phrase_points += (
                        PHRASE_TITLE_SCORE
                    )

                matched_phrases += 1

            elif phrase in normalized_content:

                phrase_points += (
                    PHRASE_CONTENT_SCORE
                )

                matched_phrases += 1

        # =================================================
        # CONCEPT SCORE
        # =================================================

        concept_points = 0

        for intent in intents:

            related_words = (
                NORMALIZED_RELATED_WORDS.get(
                    intent,
                    (),
                )
            )

            title_found = False
            content_found = False

            for word in related_words:

                if len(word) < 3:
                    continue

                if " " in word:

                    if word in normalized_title:

                        title_found = True
                        break

                    if word in normalized_content:

                        content_found = True

                else:

                    if word_matches_text(
                        normalized_title,
                        word,
                        text_tokens=title_tokens,
                        base_tokens=title_base_tokens,
                        normalized=True,
                    ):

                        title_found = True
                        break

                    if word_matches_text(
                        normalized_content,
                        word,
                        text_tokens=content_tokens,
                        base_tokens=content_base_tokens,
                        normalized=True,
                    ):

                        content_found = True

            if title_found:

                concept_points += (
                    CONCEPT_TITLE_SCORE
                )

            elif content_found:

                concept_points += (
                    CONCEPT_CONTENT_SCORE
                )

        # =================================================
        # LEGAL SCORE
        # =================================================

        legal_points = 0

        intent_coverage = set()

        for intent in intents:

            related_words = (
                NORMALIZED_RELATED_WORDS.get(
                    intent,
                    (),
                )
            )

            title_hit = False
            content_hits = 0

            for word in related_words:

                if len(word) < 3:
                    continue

                if " " in word:

                    if word in normalized_title:

                        title_hit = True

                    elif word in normalized_content:

                        content_hits += 1

                else:

                    if word_matches_text(
                        normalized_title,
                        word,
                        text_tokens=title_tokens,
                        base_tokens=title_base_tokens,
                        normalized=True,
                    ):

                        title_hit = True

                    elif word_matches_text(
                        normalized_content,
                        word,
                        text_tokens=content_tokens,
                        base_tokens=content_base_tokens,
                        normalized=True,
                    ):

                        content_hits += 1

            if title_hit:

                legal_points += 20
                intent_coverage.add(intent)

            elif content_hits >= 3:

                legal_points += 10
                intent_coverage.add(intent)

            elif content_hits >= 1:

                legal_points += 4
                intent_coverage.add(intent)

        # -------------------------------------------------
        # Multiple intent agreement
        # -------------------------------------------------

        if len(intents) >= 2:

            covered = 0

            for intent in intents:

                if intent in intent_coverage:

                    covered += 1
                    continue

                related_words = (
                    NORMALIZED_RELATED_WORDS.get(
                        intent,
                        (),
                    )
                )

                intent_found = False

                for word in related_words:

                    if len(word) < 3:
                        continue

                    if " " in word:

                        if (
                            word in normalized_title
                            or word in normalized_content
                        ):

                            intent_found = True
                            break

                    else:

                        if (
                            word_matches_text(
                                normalized_title,
                                word,
                                text_tokens=title_tokens,
                                base_tokens=title_base_tokens,
                                normalized=True,
                            )
                            or
                            word_matches_text(
                                normalized_content,
                                word,
                                text_tokens=content_tokens,
                                base_tokens=content_base_tokens,
                                normalized=True,
                            )
                        ):

                            intent_found = True
                            break

                if intent_found:
                    covered += 1

            if covered == len(intents):

                legal_points += 25

            elif covered >= 2:

                legal_points += 10

        # =================================================
        # NUMBER SCORE
        # =================================================

        number_points = 0

        for number in numbers:

            pattern = (
                rf"\b{re.escape(number)}\b"
            )

            if re.search(
                pattern,
                normalized_title,
            ):

                number_points += (
                    NUMBER_TITLE_SCORE
                )

            elif re.search(
                pattern,
                normalized_content,
            ):

                number_points += (
                    NUMBER_CONTENT_SCORE
                )

        # =================================================
        # SOURCE SCORE
        # =================================================

        source_points = (
            calculate_source_score(
                sources
            )
        )

        # =================================================
        # DISTINCTIVE PHRASE
        # =================================================

        distinctive_points = 0
        distinctive_matches = []

        for phrase in NORMALIZED_DISTINCTIVE_PHRASES:

            if phrase not in normalized_question:
                continue

            if phrase in normalized_title:

                distinctive_points += (
                    DISTINCTIVE_PHRASE_BONUS
                )

                distinctive_matches.append(
                    phrase
                )

            elif phrase in normalized_content:

                distinctive_points += 15

                distinctive_matches.append(
                    phrase
                )

        # =================================================
        # QUERY TITLE MATCH
        # =================================================

        query_title_points = 0
        query_title_matches = []

        for phrase in NORMALIZED_IMPORTANT_PHRASES:

            if phrase not in normalized_question:
                continue

            if phrase in normalized_title:

                query_title_points += (
                    LEGAL_TITLE_MATCH_BONUS
                )

                query_title_matches.append(
                    phrase
                )

        # =================================================
        # INTENT EVIDENCE
        # =================================================

        intent_evidence = set()

        for intent in intents:

            if intent in intent_coverage:

                intent_evidence.add(intent)
                continue

            related_words = (
                NORMALIZED_RELATED_WORDS.get(
                    intent,
                    (),
                )
            )

            for word in related_words:

                if len(word) < 3:
                    continue

                if " " in word:

                    if (
                        word in normalized_title
                        or word in normalized_content
                    ):

                        intent_evidence.add(
                            intent
                        )

                        break

                else:

                    if (
                        word_matches_text(
                            normalized_title,
                            word,
                            text_tokens=title_tokens,
                            base_tokens=title_base_tokens,
                            normalized=True,
                        )
                        or
                        word_matches_text(
                            normalized_content,
                            word,
                            text_tokens=content_tokens,
                            base_tokens=content_base_tokens,
                            normalized=True,
                        )
                    ):

                        intent_evidence.add(
                            intent
                        )

                        break

        # =================================================
        # INTENT BONUS
        # =================================================

        intent_bonus = 0

        if intents:

            coverage = (
                len(intent_evidence)
                / len(intents)
            )

            if coverage >= 1.0:

                intent_bonus = (
                    FULL_INTENT_BONUS
                )

            elif coverage >= 0.5:

                intent_bonus = (
                    PARTIAL_INTENT_BONUS
                )

        # =================================================
        # KEYWORD BONUS
        # =================================================

        if matched_keywords >= 5:

            keyword_bonus = 20

        elif matched_keywords >= 3:

            keyword_bonus = 12

        elif matched_keywords >= 2:

            keyword_bonus = 6

        else:

            keyword_bonus = 0

        # =================================================
        # PHRASE BONUS
        # =================================================

        if matched_phrases >= 3:

            phrase_bonus = 18

        elif matched_phrases >= 2:

            phrase_bonus = 12

        elif matched_phrases == 1:

            phrase_bonus = 6

        else:

            phrase_bonus = 0

        # =================================================
        # LEXICAL QUALITY
        # =================================================

        if lexical_score >= 0.25:

            lexical_bonus = (
                STRONG_LEXICAL_BONUS
            )

        elif lexical_score >= 0.10:

            lexical_bonus = (
                MEDIUM_LEXICAL_BONUS
            )

        else:

            lexical_bonus = 0

        # =================================================
        # FINAL SCORE
        # =================================================

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

    # =====================================================
    # RANKING
    # =====================================================

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

        # -------------------------------------------------
        # Exact article
        # -------------------------------------------------

        if "exact" in sources:

            verified.append(item)
            continue

        # -------------------------------------------------
        # Semantic levels
        # -------------------------------------------------

        strong_semantic = (
            semantic_score
            >= STRONG_SEMANTIC
        )

        medium_semantic = (
            semantic_score
            >= MEDIUM_SEMANTIC
        )

        # -------------------------------------------------
        # Multi-source
        # -------------------------------------------------

        multi_source = (
            len(sources) >= 2
        )

        # -------------------------------------------------
        # Intent evidence
        # -------------------------------------------------

        has_intent = (
            not intents
            or bool(intent_evidence)
        )

        full_intent = (
            not intents
            or len(intent_evidence)
            == len(intents)
        )

        # -------------------------------------------------
        # Legal evidence
        # -------------------------------------------------

        legal_evidence = (
            legal_score >= 15
            or concept_score >= 18
            or phrase_score >= 10
            or keyword_score >= 14
            or number_score >= 14
            or distinctive_phrase_score >= 15
            or query_title_score >= 20
        )

        # -------------------------------------------------
        # RULE 0
        # Distinctive legal phrase
        # -------------------------------------------------

        if (
            distinctive_phrase_score
            >= DISTINCTIVE_PHRASE_BONUS
            and
            query_title_score
            >= LEGAL_TITLE_MATCH_BONUS
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 1
        # Strong semantic + legal evidence
        # -------------------------------------------------

        if (
            strong_semantic
            and legal_evidence
            and has_intent
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 2
        # Multi-source agreement
        # -------------------------------------------------

        if (
            multi_source
            and (
                full_intent
                or legal_evidence
            )
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 3
        # Strong lexical
        # -------------------------------------------------

        if (
            lexical_score >= 0.20
            and legal_evidence
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 4
        # Medium semantic
        # -------------------------------------------------

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

        # -------------------------------------------------
        # RULE 5
        # Strong phrase
        # -------------------------------------------------

        if (
            phrase_score >= 28
            and legal_evidence
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 6
        # Strong keyword
        # -------------------------------------------------

        if (
            keyword_score >= 28
            and legal_evidence
        ):

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 7
        # Strong number evidence
        # -------------------------------------------------

        if number_score >= 35:

            verified.append(item)
            continue

        # -------------------------------------------------
        # RULE 8
        # General question
        # -------------------------------------------------

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

    # -----------------------------------------------------
    # High confidence
    # -----------------------------------------------------

    if "exact" in sources:
        return "high"

    if (
        distinctive_phrase_score
        >= DISTINCTIVE_PHRASE_BONUS
    ):
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

    # -----------------------------------------------------
    # Medium confidence
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # VERIFIED FIRST
    # -----------------------------------------------------

    for item in verified:

        if len(selected_items) >= limit:
            break

        article = item["article"]

        if article.id in seen_ids:
            continue

        selected_items.append(item)
        seen_ids.add(article.id)

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # DIVERSITY
    # -----------------------------------------------------

    selected_articles = [
        item["article"]
        for item in selected_items
    ]

    diverse_articles = select_diverse_articles(
        selected_articles,
        limit,
    )

    # -----------------------------------------------------
    # Fill if diversity removed results
    # -----------------------------------------------------

    if len(diverse_articles) < limit:

        existing_ids = {
            article.id
            for article in diverse_articles
        }

        for item in ranked:

            if len(diverse_articles) >= limit:
                break

            article = item["article"]

            if article.id in existing_ids:
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

            if (
                semantic_score
                < MIN_SEMANTIC_SCORE
                and lexical_score
                < 0.05
                and sources == {"semantic"}
            ):
                continue

            diverse_articles.append(
                article
            )

            existing_ids.add(
                article.id
            )

    return diverse_articles[:limit]


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
            f"Distinctive="
            f"{item.get('distinctive_phrase_score', 0)} | "
            f"TitleMatch="
            f"{item.get('query_title_score', 0)} | "
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
            f"Distinctive="
            f"{item.get('distinctive_phrase_score', 0)} | "
            f"TitleMatch="
            f"{item.get('query_title_score', 0)} | "
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

    if exact_results:

        semantic_results = []

    else:

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
            analysis["expanded_keywords"]
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
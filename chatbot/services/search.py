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
    api_key=getattr(settings, "OPENAI_API_KEY", None)
)


# =========================================================
# SEARCH SETTINGS
# =========================================================

SEMANTIC_LIMIT = 30
LEXICAL_LIMIT = 30
EXACT_LIMIT = 10
FINAL_LIMIT = 5

MAX_QUERY_TERMS = 40
MAX_PHRASES = 12

STRONG_SEMANTIC = 0.45
MEDIUM_SEMANTIC = 0.28
MIN_SEMANTIC_SCORE = 0.15

SEMANTIC_WEIGHT = 100
LEXICAL_WEIGHT = 40

TITLE_KEYWORD_SCORE = 16
CONTENT_KEYWORD_SCORE = 5

PHRASE_TITLE_SCORE = 32
PHRASE_CONTENT_SCORE = 12

IMPORTANT_TITLE_PHRASE_SCORE = 75

CONCEPT_TITLE_SCORE = 20
CONCEPT_CONTENT_SCORE = 7

NUMBER_TITLE_SCORE = 40
NUMBER_CONTENT_SCORE = 15

EXACT_SOURCE_SCORE = 300
SEMANTIC_SOURCE_SCORE = 12
LEXICAL_SOURCE_SCORE = 12

MULTI_SOURCE_BONUS = 25
THREE_SOURCE_BONUS = 18

FULL_INTENT_BONUS = 40
PARTIAL_INTENT_BONUS = 15

STRONG_LEXICAL_BONUS = 20
MEDIUM_LEXICAL_BONUS = 10

DISTINCTIVE_PHRASE_BONUS = 60
LEGAL_TITLE_MATCH_BONUS = 40


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "men", "mən", "sen", "sən", "siz", "biz",
    "bu", "bir",
    "ve", "və", "ile", "ilə", "ucun", "üçün",
    "olan", "olaraq",
    "haqqinda", "haqqında",
    "nece", "necə", "nedir", "nədir",
    "kimdir", "kimler", "kimlər",
    "hansi", "hansı", "hansilar", "hansılar",
    "eden", "edən", "edilir",
    "edilmesi", "edilməsi",
    "verilen", "verilən", "verilir", "verilirmi",
    "var",
    "mi", "mı", "mu", "mü",
    "de", "də", "da",
    "ki",
    "gore", "görə",
    "menim", "mənim", "senin", "sənin",
    "sizin", "bizim",
    "oldugum", "olduğum",
    "oldugun", "olduğun",
    "oldugu", "olduğu",
    "olduqda",
    "halda", "halinda", "halında",
    "olar", "olur",
    "ede", "edə",
    "etmek", "etmək",
    "olanlar", "olanlari", "olanları",
}


# =========================================================
# RELATED WORDS / INTENTS
# =========================================================

RELATED_WORDS = {
    "toplanis": {
        "toplanis", "toplanisa", "toplanisdan", "toplanislar",
        "toplanislardan", "toplanislara", "toplanislarin",
        "telim", "telime", "telimden", "telimler",
        "telimlere", "telimlerden", "telimlerin",
        "toplanislarin kecirilmesi",
        "herbi toplanis",
    },

    "cagiris": {
        "cagiris", "cagirisa", "cagirisdan", "cagirislar",
        "cagirislarin", "cagir", "cagiril",
        "cagirilir", "cagirilirler",
        "cagirilacaq", "cagirilacaqdir",
        "cagirilmasi", "cagirildigi",
        "cagirilma", "cagirila", "cagirma",
    },

    "azadetme": {
        "azad", "azaddir", "azadliq", "azadlar",
        "azadetme",
        "azad edilen", "azad edilir",
        "azad olunur",
        "azad edilmis",
        "azad edilmesi",
        "azad edilme",
        "azad olunma",
        "herbi xidmetden azad",
    },

    "mohlet": {
        "mohlet", "mohletin", "mohletle",
        "mohletler", "mohletlerden",
        "mohletden",
        "mohlet verilmesi",
        "mohlet verilir",
        "mohlet verilme",
        "mohlet alma",
        "cagirisdan mohlet",
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
        "xidmete yararsiz",
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
        "qebul",
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


INTENTS = {
    intent: words
    for intent, words in RELATED_WORDS.items()
}


# =========================================================
# PRIMARY INTENT TERMS
# =========================================================

INTENT_PRIMARY_TERMS = {
    "toplanis": ["toplanis", "telim"],
    "cagiris": ["cagiris", "cagiril"],
    "azadetme": ["azad"],
    "mohlet": ["mohlet"],
    "saglamliq": ["saglamliq", "tibbi"],
    "aile": ["aile", "usaq", "ovlad"],
    "tehsil": ["tehsil", "telebe"],
    "ehtiyat": ["ehtiyat"],
}


# =========================================================
# QUESTION TYPE COMBINATIONS
# =========================================================

QUESTION_TYPE_COMBINATIONS = [
    ({"toplanis", "ehtiyat", "aile"}, "toplanis_ehtiyat_aile"),
    ({"toplanis", "ehtiyat"}, "toplanis_ehtiyat"),
    ({"toplanis", "azadetme"}, "toplanis_azadetme"),
    ({"cagiris", "mohlet"}, "cagiris_mohlet"),
    ({"aile", "mohlet"}, "aile_mohlet"),
    ({"saglamliq", "mohlet"}, "saglamliq_mohlet"),
    ({"tehsil", "mohlet"}, "tehsil_mohlet"),
    ({"aile", "toplanis"}, "toplanis_aile"),
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

_NORMALIZE_SPACE_RE = re.compile(r"\s+")


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower().strip()
    text = text.translate(_NORMALIZE_REPLACEMENTS)
    text = _NORMALIZE_PUNCT_RE.sub(" ", text)
    text = _NORMALIZE_SPACE_RE.sub(" ", text)

    return text.strip()


# =========================================================
# TOKENIZATION
# =========================================================

_TOKEN_RE = re.compile(r"[a-z0-9.-]+")


def tokenize(text):
    if not text:
        return []

    normalized = normalize_text(text)
    return _TOKEN_RE.findall(normalized)


# =========================================================
# WORD NORMALIZATION
# =========================================================

_WORD_SUFFIXES = (
    "larin", "lerin",
    "lardan", "lerden",
    "lara", "lere",
    "lar", "ler",
    "dan", "den",
    "nin", "nun",
    "na", "ne",
    "da", "de",
    "ta", "te",
    "ya", "ye",
    "ni", "nu",
    "in", "un",
    "im", "um",
    "i", "u",
    "a", "e",
)


@lru_cache(maxsize=4096)
def normalize_word_for_intent(word):
    word = normalize_text(word)

    if not word:
        return ""

    for suffix in _WORD_SUFFIXES:
        if word.endswith(suffix):
            if len(word) - len(suffix) >= 4:
                word = word[:-len(suffix)]
                break

    return word


# =========================================================
# PRECOMPUTED NORMALIZED INTENT WORDS
# =========================================================

NORMALIZED_RELATED_WORDS = {}

for _intent, _words in RELATED_WORDS.items():
    normalized_words = []

    for word in _words:
        normalized_word = normalize_text(word)

        if normalized_word:
            normalized_words.append(normalized_word)

    NORMALIZED_RELATED_WORDS[_intent] = tuple(
        dict.fromkeys(normalized_words)
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
# IMPORTANT PHRASES
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
        if normalize_text(phrase)
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


NORMALIZED_DISTINCTIVE_LEGAL_PHRASES = tuple(
    dict.fromkeys(
        normalize_text(phrase)
        for phrase in DISTINCTIVE_LEGAL_PHRASES
        if normalize_text(phrase)
    )
)


# =========================================================
# TEXT MATCHING
# =========================================================

def word_matches_text(
    text,
    word,
    text_tokens=None,
    base_tokens=None,
    normalized=False,
):
    if not text or not word:
        return False

    if not normalized:
        text = normalize_text(text)

    word = normalize_text(word)

    if len(word) < 3:
        return False

    if text_tokens is None:
        text_tokens = set(tokenize(text))
    elif not isinstance(text_tokens, set):
        text_tokens = set(text_tokens)

    if " " in word:
        return word in text

    if word in text_tokens:
        return True

    base = normalize_word_for_intent(word)

    if base and len(base) >= 4:
        if base_tokens is None:
            base_tokens = {
                normalize_word_for_intent(token)
                for token in text_tokens
                if normalize_word_for_intent(token)
            }

        if base in base_tokens:
            return True

        for token in text_tokens:
            token_base = normalize_word_for_intent(token)

            if (
                token.startswith(base)
                or token_base == base
                or (
                    token_base
                    and base.startswith(token_base)
                )
            ):
                return True

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
    tokens = set(tokenize(normalized))

    if not normalized:
        return set()

    normalized_token_bases = {
        token: normalize_word_for_intent(token)
        for token in tokens
    }

    normalized_base_set = {
        base
        for base in normalized_token_bases.values()
        if base
    }

    intents = set()

    for intent, related_words in NORMALIZED_RELATED_WORDS.items():
        for word in related_words:
            if len(word) < 3:
                continue

            if " " in word:
                if word in normalized:
                    intents.add(intent)
                    break
                continue

            if word in tokens:
                intents.add(intent)
                break

            word_base = normalize_word_for_intent(word)

            if (
                word_base
                and len(word_base) >= 4
                and word_base in normalized_base_set
            ):
                intents.add(intent)
                break

            matched = False
            for token in tokens:
                token_base = normalized_token_bases[token]

                if (
                    token.startswith(word)
                    or (
                        word_base
                        and token_base == word_base
                    )
                    or (
                        word_base
                        and token_base
                        and word_base.startswith(token_base)
                    )
                ):
                    matched = True
                    break

            if matched:
                intents.add(intent)
                break

    if re.search(r"\b\d+\s+(usaq|usag|ovlad)\b", normalized):
        intents.add("aile")
    elif (
        "usaq" in tokens
        or "usag" in tokens
        or "ovlad" in tokens
    ):
        intents.add("aile")

    return intents


# =========================================================
# QUESTION TYPE
# =========================================================

def detect_question_type(intents):
    if not intents:
        return None

    intent_set = set(intents)

    for combination, question_type in QUESTION_TYPE_COMBINATIONS:
        if combination.issubset(intent_set):
            return question_type

    for intent in QUESTION_TYPE_PRIORITY:
        if intent in intent_set:
            return intent

    return None


# =========================================================
# KEYWORD EXPANSION
# =========================================================

def expand_keywords(keywords, intents):
    expanded = list(keywords)

    for intent in intents:
        primary_terms = NORMALIZED_INTENT_PRIMARY_TERMS.get(intent, ())
        for term in primary_terms:
            if term not in expanded:
                expanded.append(term)

    return expanded[:MAX_QUERY_TERMS]


# =========================================================
# PHRASE EXTRACTION
# =========================================================

def extract_query_phrases(question, keywords):
    normalized = normalize_text(question)
    phrases = []

    for phrase in NORMALIZED_IMPORTANT_PHRASES:
        if phrase in normalized:
            if phrase not in phrases:
                phrases.append(phrase)

    tokens = [
        token
        for token in tokenize(normalized)
        if token not in STOP_WORDS
    ]

    for i in range(len(tokens) - 2):
        phrase = " ".join(tokens[i:i + 3])
        if phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) >= MAX_PHRASES:
            return phrases[:MAX_PHRASES]

    for i in range(len(tokens) - 1):
        phrase = " ".join(tokens[i:i + 2])
        if phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) >= MAX_PHRASES:
            break

    return phrases[:MAX_PHRASES]


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

    numbers = []
    for pattern in patterns:
        for match in re.findall(pattern, normalized):
            if match not in numbers:
                numbers.append(match)

    return numbers


# =========================================================
# QUERY ANALYSIS
# =========================================================

def analyze_query(question):
    normalized = normalize_text(question)
    keywords = get_keywords(normalized)
    intents = detect_intents(normalized)
    question_type = detect_question_type(intents)
    expanded_keywords = expand_keywords(keywords, intents)
    phrases = extract_query_phrases(normalized, keywords)
    article_numbers = extract_article_numbers(normalized)

    return {
        "normalized": normalized,
        "keywords": keywords,
        "expanded_keywords": expanded_keywords,
        "phrases": phrases,
        "numbers": article_numbers,
        "article_numbers": article_numbers,
        "intents": intents,
        "question_type": question_type,
    }


# =========================================================
# QUERYSETS
# =========================================================

def article_queryset():
    return Article.objects.select_related("law")


def semantic_article_queryset():
    return (
        Article.objects
        .select_related("law")
        .exclude(embedding__isnull=True)
    )


# =========================================================
# EXACT SEARCH
# =========================================================

def exact_article_search(question):
    article_numbers = extract_article_numbers(question)
    if not article_numbers:
        return []

    queryset = (
        article_queryset()
        .filter(number__in=article_numbers)
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
    if not client:
        return []

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=question,
        )
        embedding = response.data[0].embedding
    except Exception:
        return []

    queryset = (
        semantic_article_queryset()
        .annotate(
            distance=CosineDistance(
                "embedding",
                embedding,
            )
        )
        .order_by("distance")[:SEMANTIC_LIMIT]
    )

    results = []
    for article in queryset:
        distance = float(getattr(article, "distance", 1.0) or 1.0)
        similarity = max(0.0, min(1.0, 1.0 - distance))

        if similarity < MIN_SEMANTIC_SCORE:
            continue

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
    if not keywords:
        return []

    normalized_keywords = []
    for keyword in keywords:
        keyword = normalize_text(keyword)
        if not keyword or len(keyword) < 3 or keyword in STOP_WORDS:
            continue
        if keyword not in normalized_keywords:
            normalized_keywords.append(keyword)

    normalized_keywords = normalized_keywords[:MAX_QUERY_TERMS]
    if not normalized_keywords:
        return []

    search_vector = (
        SearchVector("title", weight="A")
        + SearchVector("content", weight="B")
    )

    search_query = None
    for keyword in normalized_keywords:
        query = SearchQuery(keyword, search_type="websearch")
        if search_query is None:
            search_query = query
        else:
            search_query |= query

    if search_query is None:
        return []

    queryset = (
        article_queryset()
        .annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query),
        )
        .filter(rank__gt=0)
        .order_by("-rank")[:LEXICAL_LIMIT]
    )

    results = []
    for article in queryset:
        rank = float(getattr(article, "rank", 0.0) or 0.0)
        results.append({
            "article": article,
            "semantic_score": 0.0,
            "lexical_score": rank,
            "sources": {"lexical"},
        })

    return results


# =========================================================
# MERGE CANDIDATES
# =========================================================

def merge_candidates(*result_sets):
    candidates = {}

    for result_set in result_sets:
        for item in result_set:
            article = item["article"]
            article_id = article.id

            if article_id not in candidates:
                candidates[article_id] = {
                    "article": article,
                    "semantic_score": item.get("semantic_score", 0.0),
                    "lexical_score": item.get("lexical_score", 0.0),
                    "sources": set(item.get("sources", set())),
                }
            else:
                candidate = candidates[article_id]
                candidate["semantic_score"] = max(
                    candidate["semantic_score"],
                    item.get("semantic_score", 0.0),
                )
                candidate["lexical_score"] = max(
                    candidate["lexical_score"],
                    item.get("lexical_score", 0.0),
                )
                candidate["sources"].update(item.get("sources", set()))

    return list(candidates.values())


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

def rerank_candidates(candidates, analysis):
    keywords = tuple(
        dict.fromkeys(
            normalize_text(kw) for kw in analysis.get("keywords", []) if normalize_text(kw)
        )
    )
    phrases = tuple(
        dict.fromkeys(
            normalize_text(ph) for ph in analysis.get("phrases", []) if normalize_text(ph)
        )
    )
    expanded_keywords = tuple(
        dict.fromkeys(
            normalize_text(ekw) for ekw in analysis.get("expanded_keywords", []) if normalize_text(ekw)
        )
    )
    intents = set(analysis.get("intents", set()))
    article_numbers = set(analysis.get("article_numbers", []))
    normalized_query = analysis.get("normalized", "")

    ranked = []

    for candidate in candidates:
        article = candidate["article"]
        title = normalize_text(article.title or "")
        content = normalize_text(article.content or "")

        title_tokens = set(tokenize(title))
        content_tokens = set(tokenize(content))

        title_base_tokens = {
            normalize_word_for_intent(t)
            for t in title_tokens
            if normalize_word_for_intent(t)
        }
        content_base_tokens = {
            normalize_word_for_intent(t)
            for t in content_tokens
            if normalize_word_for_intent(t)
        }

        semantic_score = float(candidate.get("semantic_score", 0.0))
        lexical_score = float(candidate.get("lexical_score", 0.0))

        score = (
            semantic_score * SEMANTIC_WEIGHT
            + lexical_score * LEXICAL_WEIGHT
        )

        keyword_score = 0
        title_keyword_hits = 0
        content_keyword_hits = 0

        for keyword in keywords:
            if word_matches_text(title, keyword, title_tokens, title_base_tokens, True):
                keyword_score += TITLE_KEYWORD_SCORE
                title_keyword_hits += 1
            elif word_matches_text(content, keyword, content_tokens, content_base_tokens, True):
                keyword_score += CONTENT_KEYWORD_SCORE
                content_keyword_hits += 1

        score += keyword_score

        phrase_score = 0
        important_title_match = False

        for phrase in phrases:
            if phrase in title:
                if phrase in NORMALIZED_IMPORTANT_PHRASE_SET:
                    phrase_score += IMPORTANT_TITLE_PHRASE_SCORE
                    important_title_match = True
                else:
                    phrase_score += PHRASE_TITLE_SCORE
            elif phrase in content:
                phrase_score += PHRASE_CONTENT_SCORE

        score += phrase_score

        for phrase in NORMALIZED_IMPORTANT_PHRASES:
            if phrase in title:
                important_title_match = True

        distinctive_phrase_match = False
        for phrase in NORMALIZED_DISTINCTIVE_LEGAL_PHRASES:
            if phrase in normalized_query:
                if phrase in title or phrase in content:
                    distinctive_phrase_match = True

        if distinctive_phrase_match:
            score += DISTINCTIVE_PHRASE_BONUS

        number_score = 0
        article_number = str(article.number or "").strip()
        if article_numbers and article_number in article_numbers:
            if article_number in title:
                number_score += NUMBER_TITLE_SCORE
            else:
                number_score += NUMBER_CONTENT_SCORE

        score += number_score

        concept_points = 0
        legal_points = 0
        intent_evidence = set()

        for intent in intents:
            related_words = NORMALIZED_RELATED_WORDS.get(intent, ())
            title_found = False
            content_found = False
            content_hits = 0

            for word in related_words:
                if len(word) < 3:
                    continue

                if " " in word:
                    if word in title:
                        title_found = True
                        break
                    if word in content:
                        content_found = True
                        content_hits += 1
                else:
                    if word_matches_text(title, word, title_tokens, title_base_tokens, True):
                        title_found = True
                        break
                    if word_matches_text(content, word, content_tokens, content_base_tokens, True):
                        content_found = True
                        content_hits += 1

                if content_hits >= 3:
                    break

            if title_found:
                concept_points += CONCEPT_TITLE_SCORE
                legal_points += 22
                intent_evidence.add(intent)
            elif content_found:
                concept_points += CONCEPT_CONTENT_SCORE
                if content_hits >= 3:
                    legal_points += 12
                else:
                    legal_points += 5
                intent_evidence.add(intent)

        score += concept_points + legal_points

        if len(intents) >= 2:
            covered = len(intent_evidence)
            if covered == len(intents):
                legal_points += 28
                score += 28
            elif covered >= 2:
                legal_points += 12
                score += 12

        if intents:
            covered = len(intent_evidence)
            if covered == len(intents):
                score += FULL_INTENT_BONUS
            elif covered > 0:
                score += PARTIAL_INTENT_BONUS

        if lexical_score >= 0.08:
            score += STRONG_LEXICAL_BONUS
        elif lexical_score >= 0.03:
            score += MEDIUM_LEXICAL_BONUS

        legal_title_match = False
        for keyword in expanded_keywords:
            if word_matches_text(title, keyword, title_tokens, title_base_tokens, True):
                legal_title_match = True
                break

        if legal_title_match:
            score += LEGAL_TITLE_MATCH_BONUS

        sources = candidate.get("sources", set())
        source_score = calculate_source_score(sources)
        score += source_score

        ranked.append({
            **candidate,
            "score": score,
            "keyword_score": keyword_score,
            "phrase_score": phrase_score,
            "concept_score": concept_points,
            "legal_score": legal_points,
            "number_score": number_score,
            "intent_evidence": intent_evidence,
            "title_keyword_hits": title_keyword_hits,
            "content_keyword_hits": content_keyword_hits,
            "important_title_match": important_title_match,
            "distinctive_phrase_match": distinctive_phrase_match,
            "legal_title_match": legal_title_match,
            "source_score": source_score,
        })

    ranked.sort(
        key=lambda item: (
            item.get("score", 0),
            item.get("source_score", 0),
            item.get("phrase_score", 0),
            item.get("semantic_score", 0),
            item.get("lexical_score", 0),
        ),
        reverse=True,
    )

    return ranked


# =========================================================
# EVIDENCE CHECK
# =========================================================

def evidence_check(ranked, analysis):
    verified = []
    intents = set(analysis.get("intents", set()))
    phrases = tuple(normalize_text(p) for p in analysis.get("phrases", []))
    keywords = tuple(normalize_text(kw) for kw in analysis.get("keywords", []))
    article_numbers = set(analysis.get("article_numbers", []))

    for item in ranked:
        article = item["article"]
        semantic_score = float(item.get("semantic_score", 0.0))
        lexical_score = float(item.get("lexical_score", 0.0))
        sources = item.get("sources", set())
        title = normalize_text(article.title or "")
        content = normalize_text(article.content or "")

        verified_flag = False

        if "exact" in sources:
            verified_flag = True
        elif semantic_score >= STRONG_SEMANTIC:
            verified_flag = True
        elif semantic_score >= MEDIUM_SEMANTIC and len(sources) >= 2:
            verified_flag = True
        elif len(sources) >= 2:
            verified_flag = True
        elif lexical_score >= 0.08:
            verified_flag = True
        elif intents and item.get("intent_evidence"):
            verified_flag = True
        elif any(p and (p in title or p in content) for p in phrases if p in NORMALIZED_IMPORTANT_PHRASE_SET):
            verified_flag = True
        elif any(word_matches_text(title, kw, normalized=True) for kw in keywords):
            verified_flag = True
        elif article_numbers and str(article.number or "").strip() in article_numbers:
            verified_flag = True
        elif item.get("distinctive_phrase_match", False):
            verified_flag = True

        if verified_flag:
            verified.append(item)

    return verified


# =========================================================
# CONFIDENCE
# =========================================================

def calculate_confidence(verified, ranked):
    if not ranked or not verified:
        return "low"

    top = ranked[0]
    semantic = float(top.get("semantic_score", 0.0))
    lexical = float(top.get("lexical_score", 0.0))
    sources = top.get("sources", set())

    if semantic >= STRONG_SEMANTIC or "exact" in sources or len(sources) >= 2:
        return "high"

    if semantic >= MEDIUM_SEMANTIC or lexical >= 0.03:
        return "medium"

    return "low"


# =========================================================
# DIVERSITY
# =========================================================

def select_diverse_articles(articles, limit=FINAL_LIMIT):
    selected = []
    law_counts = defaultdict(int)

    for item in articles:
        article = item["article"]
        law_id = getattr(article, "law_id", None)

        if law_counts[law_id] >= 3:
            continue

        selected.append(item)
        law_counts[law_id] += 1

        if len(selected) >= limit:
            break

    return selected


# =========================================================
# FINAL SELECTION
# =========================================================

def select_final_articles(verified, ranked, limit=FINAL_LIMIT):
    selected = []
    seen = set()

    for item in verified:
        article_id = item["article"].id
        if article_id in seen:
            continue
        selected.append(item)
        seen.add(article_id)
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        for item in ranked:
            article_id = item["article"].id
            if article_id in seen:
                continue
            selected.append(item)
            seen.add(article_id)
            if len(selected) >= limit:
                break

    diverse = select_diverse_articles(selected, limit=limit)

    if len(diverse) < limit:
        diverse_ids = {item["article"].id for item in diverse}
        for item in ranked:
            article_id = item["article"].id
            if article_id in diverse_ids:
                continue
            diverse.append(item)
            diverse_ids.add(article_id)
            if len(diverse) >= limit:
                break

    return diverse[:limit]


# =========================================================
# DEBUG
# =========================================================

def print_search_debug(question, analysis, ranked, verified, final_articles, confidence):
    print("\n" + "=" * 70)
    print("SEARCH DEBUG")
    print("=" * 70)
    print(f"QUESTION:\n{question}")
    print(f"\nNORMALIZED:\n{analysis.get('normalized')}")
    print(f"\nKEYWORDS:\n{analysis.get('keywords')}")
    print(f"\nEXPANDED KEYWORDS:\n{analysis.get('expanded_keywords')}")
    print(f"\nPHRASES:\n{analysis.get('phrases')}")
    print(f"\nARTICLE NUMBERS:\n{analysis.get('article_numbers')}")
    print(f"\nINTENTS:\n{analysis.get('intents')}")
    print(f"\nQUESTION TYPE:\n{analysis.get('question_type')}")
    print(f"\nCONFIDENCE:\n{confidence}")

    print("\nTOP RANKED:")
    print("-" * 70)
    for index, item in enumerate(ranked[:FINAL_LIMIT], start=1):
        article = item["article"]
        print(
            f"{index}. Article {article.number} | "
            f"Score={item.get('score', 0):.2f} | "
            f"Semantic={item.get('semantic_score', 0):.4f} | "
            f"Lexical={item.get('lexical_score', 0):.4f}"
        )
        print(f"   Title: {article.title}")
        print(f"   Sources: {item.get('sources', set())}")

    print("\nVERIFIED:")
    print("-" * 70)
    for item in verified[:FINAL_LIMIT]:
        article = item["article"]
        print(f"Article {article.number} | {article.title}")

    print("\nFINAL:")
    print("-" * 70)
    for item in final_articles:
        article = item["article"]
        print(f"Article {article.number} | {article.title}")
    print("=" * 70)


# =========================================================
# MAIN SEARCH
# =========================================================

def search_articles(question, limit=FINAL_LIMIT):
    if not question:
        return []

    question = str(question).strip()
    if not question:
        return []

    analysis = analyze_query(question)
    exact_results = exact_article_search(question)

    if exact_results:
        semantic_results = []
    else:
        semantic_results = semantic_search(question)

    lexical_results = lexical_search(analysis["expanded_keywords"])

    candidates = merge_candidates(
        exact_results,
        semantic_results,
        lexical_results,
    )

    ranked = rerank_candidates(candidates, analysis)
    verified = evidence_check(ranked, analysis)
    confidence = calculate_confidence(verified, ranked)
    final_articles = select_final_articles(verified, ranked, limit=limit)

    print_search_debug(
        question,
        analysis,
        ranked,
        verified,
        final_articles,
        confidence,
    )

    return final_articles
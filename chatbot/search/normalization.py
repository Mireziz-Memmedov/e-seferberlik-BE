import re
import unicodedata

# =========================================================
# CONFIG & MAPS
# =========================================================

CHAR_MAP = str.maketrans({
    "ə": "e", "Ə": "e", "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ü": "u", "Ü": "u", "ş": "s",
    "Ş": "s", "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
})

WORD_TO_NUM = {
    "bir": "1", "iki": "2", "uc": "3", "dord": "4", "bes": "5",
    "alti": "6", "yeddi": "7", "sekkiz": "8", "doqquz": "9", "on": "10"
}

STOP_WORDS_RAW = {
    "men", "mən", "sen", "sən", "siz", "biz", "bu", "bir", "və", "ile", "ilə", 
    "ucun", "üçün", "gore", "görə", "kim", "kimler", "kimlər", "ne", "nə", 
    "nedir", "nədir", "neyi", "nəyi", "neye", "nəyə", "nece", "necə", "hansi", 
    "hansı", "olan", "oldugu", "olduğu", "var", "mende", "məndə", "meni", "məni", 
    "mene", "mənə", "menim", "mənim", "sizden", "sizdən", "size", "sizə", "sizin", 
    "bizim", "mi", "mı", "mu", "mü", "de", "də", "da", "ki", "ola", "olar", 
    "olur", "edilir", "edilen", "edilən", "verilir", "verilirmi", "olanlar", "şəxslər",
}

SEMANTIC_GROUPS_RAW = {
    "toplanis": {"toplanis", "toplanisa", "toplanisi", "toplanisin", "toplanisdan", "telim", "telime", "telimi", "telimler"},
    "aile": {"aile", "ailenin", "usaq", "usag", "usagim", "usagi", "usaga", "usaqlar", "ovlad", "ovladi"},
    "ehtiyat": {"ehtiyat", "ehtiyatda", "ehtiyata", "ehtiyati"},
    "tehsil": {"tehsil", "tehsile", "telebe", "telebenin", "universitet", "mekteb", "ali"},
    "mohlet": {"mohlet", "mohlete", "mohleti"},
    "saglamliq": {"saglamliq", "xestelik", "xesteliye", "xeste", "tibbi", "muayine"},
    "azadetme": {"azad", "azadetme", "azadliq"},
    "cagiris": {"cagiris", "cagirisa", "cagira", "cagiril", "cagirilir", "cagirilib"},
    "herbi": {"herbi", "herbie", "herbide"},
    "xidmet": {"xidmet", "xidmete", "xidmeti"},
}

SUFFIXES_RAW = [
    "larınızdan", "lərinizdən", "larımızdan", "lərimizdən", "larınız", "ləriniz", 
    "larımız", "lərimiz", "lardan", "lərdən", "lara", "lərə", "ların", "lərin", 
    "ları", "ləri", "larda", "lərdə", "dırmı", "dirmi", "durmu", "dürmü", "dan", 
    "dən", "dır", "dir", "dur", "dür", "mı", "mi", "mu", "mü", "ına", "inə", 
    "ını", "ini", "unu", "ünü", "ın", "in", "un", "ün", "a", "ə", "i", "ı", 
    "u", "ü", "da", "də", "la", "lə"
]

def _norm_token_for_indexing(s):

    if not s: return ""
    s = unicodedata.normalize("NFKC", str(s)).translate(CHAR_MAP).lower()
    s = re.sub(r"[’'`´]", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

STOP_WORDS = {_norm_token_for_indexing(w) for w in STOP_WORDS_RAW if w}
SEMANTIC_GROUPS = {g: {_norm_token_for_indexing(w) for w in words if w} for g, words in SEMANTIC_GROUPS_RAW.items()}
WORD_TO_GROUP = {w: g for g, words in SEMANTIC_GROUPS.items() for w in words}
SUFFIXES = sorted({_norm_token_for_indexing(s) for s in SUFFIXES_RAW if s}, key=len, reverse=True)

# =========================================================
# NORMALIZATION & EXTRACTION (FIXED)
# =========================================================

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize("NFKC", str(text)).translate(CHAR_MAP).lower()
    text = re.sub(r"[’'`´]", "", text)
    text = re.sub(r"[^\w\s.]", " ", text)
    text = re.sub(r"\.{2,}", ".", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text):
    normalized = normalize_text(text)
    if not normalized:
        return []
    return normalized.split()

ARTICLE_PATTERN = re.compile(r"\b\d+(?:\.\d+)+\b")
SIMPLE_NUMBER_PATTERN = re.compile(r"\b\d+\b")

def extract_numbers_and_articles(text):
    if not text:
        return [], []
    
    norm = normalize_text(text)
    
    # 1. Tam maddə nömrələri (məsələn: 46.1.3)
    articles = list(dict.fromkeys(ARTICLE_PATTERN.findall(norm)))
    
    # 2. Sadə rəqəmlər
    numbers = []
    tokens = norm.split()
    
    for token in tokens:
        # Əgər söz artıq tapılmış maddə nömrəsidirsə, keçirik
        if token in articles:
            continue
            
        # Tək rəqəmdirsə (məs: '3' və ya '46')
        if SIMPLE_NUMBER_PATTERN.fullmatch(token):
            # Əgər bu rəqəm maddə nömrəsinin tərkib hissəsi deyilsə əlavə et
            if not any(token in art.split('.') for art in articles):
                if token not in numbers:
                    numbers.append(token)
                    
        # Sözlə yazılmış rəqəmdirsə (məs: 'uc' -> '3')
        elif token in WORD_TO_NUM:
            num_val = WORD_TO_NUM[token]
            if num_val not in numbers:
                numbers.append(num_val)

    # Əgər maddə tapılıbsa, sadə rəqəmlərə təkrar '46' yazılmır
    if articles:
        return articles, numbers
    
    # Mətndə 'madde 46' yazılıbsa, 46-nı article kimi qəbul edirik
    if "madde" in norm and numbers:
        return numbers, []

    return [], numbers

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def canonical_word(word):
    if not word: return ""
    word = normalize_text(word)
    if re.fullmatch(r"\d+(?:\.\d+)+", word) or re.fullmatch(r"\d+", word): return word
    if word in WORD_TO_GROUP: return WORD_TO_GROUP[word]

    for suffix in SUFFIXES:
        if word.endswith(suffix):
            root = word[:-len(suffix)]
            if len(root) >= 3 and root in WORD_TO_GROUP:
                return WORD_TO_GROUP[root]
    return word

def extract_keywords(normalized):
    if not normalized: return []
    keywords = []
    for word in normalized.split():
        if re.fullmatch(r"\d+(?:\.\d+)+", word):
            keywords.append(word)
            continue
        if re.fullmatch(r"\d+", word) or word in STOP_WORDS:
            continue
        canonical = canonical_word(word)
        if canonical and len(canonical) >= 2 and canonical not in keywords:
            keywords.append(canonical)
    return keywords

def expand_keywords(keywords):
    expanded = list(dict.fromkeys(keywords))
    if "toplanis" in expanded or "cagiris" in expanded:
        for item in ("toplanis", "telim"):
            if item not in expanded: expanded.append(item)
    if "aile" in expanded:
        for item in ("usaq", "ovlad"):
            if item not in expanded: expanded.append(item)
    if "tehsil" in expanded:
        for item in ("telebe", "universitet"):
            if item not in expanded: expanded.append(item)
    if "saglamliq" in expanded:
        for item in ("xestelik", "tibbi"):
            if item not in expanded: expanded.append(item)
    if "azadetme" in expanded and "azad" not in expanded:
        expanded.append("azad")
    return expanded

def generate_phrases(normalized, keywords, max_phrases=30):
    if not normalized: return []
    words = normalized.split()
    phrases = []
    for size in (2, 3):
        for i in range(len(words) - size + 1):
            current = words[i:i + size]
            meaningful = [w for w in current if w not in STOP_WORDS]
            if len(meaningful) < 2: continue
            canonical = [canonical_word(w) for w in current if w not in STOP_WORDS]
            phrase = " ".join(x for x in canonical if x)
            if phrase and phrase not in phrases: phrases.append(phrase)
    return phrases[:max_phrases]

def detect_intents(expanded_keywords):
    words = set(expanded_keywords)
    intents = set()
    if words & {"toplanis", "telim"}: intents.add("toplanis")
    if words & {"aile", "usaq", "ovlad"}: intents.add("aile")
    if words & {"tehsil", "telebe", "universitet"}: intents.add("tehsil")
    if "mohlet" in words: intents.add("mohlet")
    if words & {"saglamliq", "xestelik", "tibbi"}: intents.add("saglamliq")
    if "ehtiyat" in words: intents.add("ehtiyat")
    if words & {"cagiris", "cagira", "cagirila"}: intents.add("cagiris")
    if words & {"azad", "azadetme"}: intents.add("azadetme")
    if words & {"herbi", "xidmet"}: intents.add("herbi")
    return intents

def detect_question_type(normalized, intents, articles):
    if articles or "madde" in normalized:
        return "article"

    if {"saglamliq", "mohlet"} <= intents: return "saglamliq_mohlet"
    if {"tehsil", "mohlet"} <= intents: return "tehsil_mohlet"
    if {"toplanis", "ehtiyat", "aile"} <= intents: return "toplanis_ehtiyat_aile"
    if {"toplanis", "ehtiyat"} <= intents: return "toplanis_ehtiyat"
    if {"toplanis", "aile", "azadetme"} <= intents: return "toplanis_aile_azadetme"
    if {"toplanis", "aile"} <= intents: return "toplanis_aile"
    if {"toplanis", "azadetme"} <= intents: return "toplanis_azadetme"
    if {"cagiris", "aile"} <= intents: return "cagiris_aile"
    if {"cagiris", "ehtiyat"} <= intents: return "cagiris_ehtiyat"

    for intent in ("toplanis", "mohlet", "tehsil", "ehtiyat", "azadetme", "saglamliq", "cagiris", "herbi"):
        if intent in intents:
            return intent

    return "general"

# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_query(question):
    normalized = normalize_text(question)
    articles, numbers = extract_numbers_and_articles(normalized)
    keywords = extract_keywords(normalized)
    expanded_keywords = expand_keywords(keywords)
    phrases = generate_phrases(normalized, keywords)
    intents = detect_intents(expanded_keywords)
    question_type = detect_question_type(normalized, intents, articles)

    return {
        "normalized": normalized,
        "keywords": keywords,
        "expanded_keywords": expanded_keywords,
        "phrases": phrases,
        "intents": intents,
        "question_type": question_type,
        "numbers": numbers,
        "article_numbers": articles,
    }
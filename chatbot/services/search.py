# import re

# from openai import OpenAI
# from django.conf import settings
# from pgvector.django import CosineDistance

# from chatbot.models import Article


# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )


# # =========================================================
# # STOP WORDS
# # =========================================================

# STOP_WORDS = {
#     "men",
#     "sen",
#     "siz",
#     "biz",
#     "bu",
#     "bir",
#     "ve",
#     "ile",
#     "ucun",
#     "olan",
#     "olaraq",
#     "haqqinda",
#     "nece",
#     "nedir",
#     "kimdir",
#     "kimler",
#     "hansi",
#     "hansilar",
#     "eden",
#     "edilir",
#     "edilmesi",
#     "verilen",
#     "verilir",
#     "verilirmi",
#     "var",
#     "mi",
#     "mı",
#     "mu",
#     "mü",
#     "de",
#     "da",
#     "ki",
#     "gore",

#     # Danışıq / qrammatik sözlər
#     "menim",
#     "senin",
#     "sizin",
#     "bizim",
#     "oldugum",
#     "oldugun",
#     "oldugu",
#     "olduqda",
#     "halda",
#     "halinda",
#     "bilerem",
#     "bilərəm",
#     "biler",
#     "bilermi",
#     "bilərmi",
# }


# # =========================================================
# # NORMALIZE
# # =========================================================

# def normalize_text(text):

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

#     text = re.sub(r"\s+", " ", text)

#     return text


# # =========================================================
# # KEYWORDS
# # =========================================================

# def get_keywords(question):

#     normalized = normalize_text(question)

#     words = re.findall(
#         r"[a-z0-9-]+",
#         normalized
#     )

#     keywords = []

#     for word in words:

#         if len(word) < 3:
#             continue

#         if word in STOP_WORDS:
#             continue

#         if word not in keywords:
#             keywords.append(word)

#     return keywords


# # =========================================================
# # RELATED WORDS
# # =========================================================

# RELATED_WORDS = {

#     # -----------------------------------------------------
#     # TOPLANIŞ
#     # -----------------------------------------------------

#     "toplanis": {
#         "toplanis",
#         "toplanisa",
#         "toplanisdan",
#         "toplanislardan",
#         "toplanislara",
#         "toplanislar",
#         "telim",
#         "telime",
#         "telimden",
#         "telimler",
#         "telimlere",
#     },

#     # -----------------------------------------------------
#     # ÇAĞIRIŞ
#     # -----------------------------------------------------

#     "cagiris": {
#         "cagiris",
#         "cagirisdan",
#         "cagirisa",
#         "cagirisla",
#         "cagir",
#         "cagirilir",
#         "cagirilirler",
#         "cagirilacaq",
#         "cagirilmasi",
#         "cagirilma",
#         "cagirila",
#         "cagirilmaq",
#         "cagirilmag",
#     },

#     # -----------------------------------------------------
#     # AZADOLMA
#     # -----------------------------------------------------

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
#     },

#     # -----------------------------------------------------
#     # MÖHLƏT
#     # -----------------------------------------------------

#     "mohlet": {
#         "mohlet",
#         "mohletin",
#         "mohletle",
#         "mohletler",
#         "mohletden",
#         "mohlet verilmesi",
#         "mohlet verilir",
#         "mohlet verilm",
#     },

#     # -----------------------------------------------------
#     # SAĞLAMLIQ
#     # -----------------------------------------------------

#     "saglamliq": {
#         "saglamliq",
#         "saglamlig",
#         "saglamligina",
#         "saglamligindan",
#         "saglamliqdan",
#         "saglamliq veziyyeti",
#         "saglamliq veziyyetine",
#         "saglamliq veziyyetinden",
#     },

#     # -----------------------------------------------------
#     # AİLƏ
#     # -----------------------------------------------------

#     "aile": {
#         "aile",
#         "ailesi",
#         "ailenin",
#         "aileye",
#         "ailevi",
#         "aile veziyyeti",
#         "aile veziyyetine",

#         # Uşaq / övlad
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

#         # Say ilə istifadə oluna bilən ifadələr
#         "iki usaq",
#         "uc usaq",
#         "dord usaq",
#         "bes usaq",
#         "alti usaq",
#     },

#     # -----------------------------------------------------
#     # TƏHSİL
#     # -----------------------------------------------------

#     "tehsil": {
#         "tehsil",
#         "tehsili",
#         "tehsile",
#         "tehsilde",
#         "tehsil alan",
#         "tehsil etmek",
#         "tehsil alanlar",
#     },

#     # -----------------------------------------------------
#     # EHTİYAT
#     # -----------------------------------------------------

#     "ehtiyat": {
#         "ehtiyat",
#         "ehtiyatda",
#         "ehtiyatdaki",
#         "ehtiyatdakilar",
#         "ehtiyatda olan",
#         "ehtiyatda olanlar",
#     },

#     # -----------------------------------------------------
#     # MÜDDƏT
#     # -----------------------------------------------------

#     "muddet": {
#         "muddet",
#         "muddeti",
#         "muddetler",
#         "muddetde",
#         "defe",
#         "defeyedek",
#     },
# }


# # =========================================================
# # INTENTS
# # =========================================================

# INTENTS = {

#     "toplanis": {
#         "toplanis",
#         "toplanisdan",
#         "toplanislardan",
#         "toplanisa",
#         "toplanislara",
#         "telim",
#         "telime",
#         "telimden",
#         "telimler",
#         "telimlere",
#     },

#     "azadetme": {
#         "azad",
#         "azaddir",
#         "azadetme",
#         "azadliq",
#     },

#     "mohlet": {
#         "mohlet",
#         "mohletin",
#         "mohletle",
#         "mohletler",
#     },

#     "saglamliq": {
#         "saglamliq",
#         "saglamlig",
#         "saglamligina",
#     },

#     "aile": {
#         "aile",
#         "ailesi",
#         "ailenin",
#         "ailevi",

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
#     },

#     "tehsil": {
#         "tehsil",
#         "tehsili",
#         "tehsile",
#     },

#     "cagiris": {
#         "cagiris",
#         "cagirisdan",
#         "cagirisa",
#         "cagirila",
#         "cagir",
#     },

#     "ehtiyat": {
#         "ehtiyat",
#         "ehtiyatda",
#         "ehtiyatdaki",
#         "ehtiyatdakilar",
#     },
# }


# # =========================================================
# # INTENT DETECTION
# # =========================================================

# def detect_intents(question):

#     normalized = normalize_text(question)

#     detected = set()

#     for intent, words in INTENTS.items():

#         for word in words:

#             normalized_word = normalize_text(word)

#             if re.search(
#                 rf"\b{re.escape(normalized_word)}\b",
#                 normalized
#             ):
#                 detected.add(intent)
#                 break

#     # -----------------------------------------------------
#     # UŞAQ / ÖVLAD MƏNTİQİ
#     # -----------------------------------------------------

#     family_patterns = [
#         r"\b\d+\s+usaq\b",
#         r"\b\d+\s+usag\b",
#         r"\b\d+\s+ovlad\b",
#         r"\busaq\b",
#         r"\busag\b",
#         r"\bovlad\b",
#     ]

#     for pattern in family_patterns:

#         if re.search(pattern, normalized):
#             detected.add("aile")
#             break

#     return detected


# # =========================================================
# # QUESTION TYPE
# # =========================================================

# def detect_question_type(intents):

#     # -----------------------------------------------------
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):
#         return "toplanis_ehtiyat_aile"

#     # -----------------------------------------------------
#     # TOPLANIŞ + EHTİYAT
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#     ):
#         return "toplanis_ehtiyat"

#     # -----------------------------------------------------
#     # TOPLANIŞ + AZADOLMA
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "azadetme" in intents
#     ):
#         return "toplanis_azadetme"

#     # -----------------------------------------------------
#     # ÇAĞIRIŞ + MÖHLƏT
#     # -----------------------------------------------------

#     if (
#         "cagiris" in intents
#         and "mohlet" in intents
#     ):
#         return "cagiris_mohlet"

#     # -----------------------------------------------------
#     # AİLƏ + MÖHLƏT
#     # -----------------------------------------------------

#     if (
#         "aile" in intents
#         and "mohlet" in intents
#     ):
#         return "aile_mohlet"

#     # -----------------------------------------------------
#     # SAĞLAMLIQ + MÖHLƏT
#     # -----------------------------------------------------

#     if (
#         "saglamliq" in intents
#         and "mohlet" in intents
#     ):
#         return "saglamliq_mohlet"

#     # -----------------------------------------------------
#     # TƏHSİL + MÖHLƏT
#     # -----------------------------------------------------

#     if (
#         "tehsil" in intents
#         and "mohlet" in intents
#     ):
#         return "tehsil_mohlet"

#     # -----------------------------------------------------
#     # SADƏ
#     # -----------------------------------------------------

#     if "azadetme" in intents:
#         return "azadetme"

#     if "mohlet" in intents:
#         return "mohlet"

#     if "toplanis" in intents:
#         return "toplanis"

#     if "cagiris" in intents:
#         return "cagiris"

#     return "general"


# # =========================================================
# # GROUP MATCH
# # =========================================================

# def matches_group(text, group_name):

#     text = normalize_text(text)

#     words = RELATED_WORDS.get(
#         group_name,
#         set()
#     )

#     for word in words:

#         normalized_word = normalize_text(word)

#         if re.search(
#             rf"\b{re.escape(normalized_word)}\b",
#             text
#         ):
#             return True

#     return False


# # =========================================================
# # KEYWORD MATCH
# # =========================================================

# def keyword_matches(
#     keyword,
#     title,
#     content
# ):

#     keyword = normalize_text(keyword)
#     title = normalize_text(title)
#     content = normalize_text(content)

#     # Birbaşa başlıq
#     if re.search(
#         rf"\b{re.escape(keyword)}\b",
#         title
#     ):
#         return "title"

#     # Birbaşa mətn
#     if re.search(
#         rf"\b{re.escape(keyword)}\b",
#         content
#     ):
#         return "content"

#     # Əlaqəli sözlər
#     for group_name, words in RELATED_WORDS.items():

#         normalized_words = {
#             normalize_text(word)
#             for word in words
#         }

#         if keyword in normalized_words:

#             for related in normalized_words:

#                 if re.search(
#                     rf"\b{re.escape(related)}\b",
#                     title
#                 ):
#                     return "related_title"

#                 if re.search(
#                     rf"\b{re.escape(related)}\b",
#                     content
#                 ):
#                     return "related_content"

#     return None


# # =========================================================
# # ARTICLE ROLE
# # =========================================================

# def detect_article_role(
#     article,
#     intents
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     # -----------------------------------------------------
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):

#         # Toplanışdan azadolmanı müəyyən edən maddə
#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             return "primary"

#         # Ehtiyatda olanların toplanışa çağırılması
#         if (
#             "ehtiyat" in title
#             and (
#                 "toplanis" in title
#                 or "telim" in title
#                 or "cagiris" in title
#             )
#         ):
#             return "primary"

#         # Ailə / möhlət / çağırış maddəsi
#         if (
#             "aile" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return "companion"

#     # -----------------------------------------------------
#     # TOPLANIŞ + AZADOLMA
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "azadetme" in intents
#     ):

#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             return "primary"

#         if (
#             "aile" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return "companion"

#         if (
#             "saglamliq" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return "companion"

#         if (
#             "tehsil" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return "companion"

#     return "normal"


# # =========================================================
# # RELATION SCORE
# # =========================================================

# def calculate_relation_score(
#     article,
#     intents
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     score = 0

#     # =====================================================
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):

#         # Toplanışdan azadolma
#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             score += 500

#         # Ehtiyat + toplanış
#         if (
#             "ehtiyat" in title
#             and (
#                 "toplanis" in title
#                 or "telim" in title
#                 or "cagiris" in title
#             )
#         ):
#             score += 400

#         # Ailə + möhlət
#         if (
#             "aile" in title
#             and "mohlet" in title
#         ):
#             score += 300

#         # Ailə + çağırış
#         elif (
#             "aile" in title
#             and "cagiris" in title
#         ):
#             score += 250

#     # =====================================================
#     # TOPLANIŞ + EHTİYAT
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#     ):

#         if (
#             "ehtiyat" in title
#             and "toplanis" in title
#         ):
#             score += 450

#         elif (
#             "ehtiyat" in title
#             and "telim" in title
#         ):
#             score += 300

#         elif (
#             "ehtiyat" in title
#             and "cagiris" in title
#         ):
#             score += 300

#         elif "toplanis" in title:
#             score += 180

#     # =====================================================
#     # TOPLANIŞ + AZADOLMA
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "azadetme" in intents
#     ):

#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             score += 500

#         if "aile" in intents:

#             if (
#                 "aile" in title
#                 and (
#                     "mohlet" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 300

#         if "saglamliq" in intents:

#             if (
#                 "saglamliq" in title
#                 and (
#                     "mohlet" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 300

#         if "tehsil" in intents:

#             if (
#                 "tehsil" in title
#                 and (
#                     "mohlet" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 300

#     # =====================================================
#     # AİLƏ + MÖHLƏT
#     # =====================================================

#     if (
#         "aile" in intents
#         and "mohlet" in intents
#     ):

#         if (
#             "aile" in title
#             and "mohlet" in title
#         ):
#             score += 350

#         elif "aile" in title:
#             score += 180

#     # =====================================================
#     # SAĞLAMLIQ + MÖHLƏT
#     # =====================================================

#     if (
#         "saglamliq" in intents
#         and "mohlet" in intents
#     ):

#         if (
#             "saglamliq" in title
#             and "mohlet" in title
#         ):
#             score += 350

#         elif "saglamliq" in title:
#             score += 180

#     # =====================================================
#     # TƏHSİL + MÖHLƏT
#     # =====================================================

#     if (
#         "tehsil" in intents
#         and "mohlet" in intents
#     ):

#         if (
#             "tehsil" in title
#             and "mohlet" in title
#         ):
#             score += 350

#         elif "tehsil" in title:
#             score += 180

#     # =====================================================
#     # SADƏ AZADOLMA
#     # =====================================================

#     if "azadetme" in intents:

#         if (
#             "azad" in title
#             and "toplanis" in title
#         ):
#             score += 250

#         elif "azad" in title:
#             score += 120

#     # =====================================================
#     # SADƏ TOPLANIŞ
#     # =====================================================

#     if "toplanis" in intents:

#         if "toplanis" in title:
#             score += 120

#         elif "telim" in title:
#             score += 80

#     return score


# # =========================================================
# # CONTEXT SCORE
# # =========================================================

# def calculate_context_score(
#     article,
#     intents
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     score = 0

#     # =====================================================
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):

#         # Toplanış maddəsi
#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             score += 250

#         # Ehtiyatda olanların çağırılması
#         if (
#             "ehtiyat" in title
#             and (
#                 "toplanis" in title
#                 or "telim" in title
#                 or "cagiris" in title
#             )
#         ):
#             score += 250

#         # Ailə üzrə hüquqi əsas
#         if (
#             "aile" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             score += 200

#     # =====================================================
#     # TOPLANIŞ + AZADOLMA
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "azadetme" in intents
#     ):

#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             score += 180

#         if "aile" in intents:

#             if (
#                 "aile" in title
#                 and "mohlet" in title
#             ):
#                 score += 180

#         if "saglamliq" in intents:

#             if (
#                 "saglamliq" in title
#                 and "mohlet" in title
#             ):
#                 score += 180

#         if "tehsil" in intents:

#             if (
#                 "tehsil" in title
#                 and "mohlet" in title
#             ):
#                 score += 180

#     return score


# # =========================================================
# # DIRECT CONTEXT ARTICLE
# # =========================================================

# def is_direct_context_article(
#     article,
#     intents
# ):

#     title = normalize_text(
#         article.title or ""
#     )

#     # -----------------------------------------------------
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # -----------------------------------------------------

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):

#         if (
#             "ehtiyat" in title
#             and (
#                 "toplanis" in title
#                 or "telim" in title
#                 or "cagiris" in title
#             )
#         ):
#             return True

#         if (
#             "aile" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return True

#         if (
#             "toplanis" in title
#             and "azad" in title
#         ):
#             return True

#     # -----------------------------------------------------
#     # AİLƏ
#     # -----------------------------------------------------

#     if "aile" in intents:

#         if (
#             "aile" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return True

#     # -----------------------------------------------------
#     # SAĞLAMLIQ
#     # -----------------------------------------------------

#     if "saglamliq" in intents:

#         if (
#             "saglamliq" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return True

#     # -----------------------------------------------------
#     # TƏHSİL
#     # -----------------------------------------------------

#     if "tehsil" in intents:

#         if (
#             "tehsil" in title
#             and (
#                 "mohlet" in title
#                 or "cagiris" in title
#             )
#         ):
#             return True

#     return False


# # =========================================================
# # CONTEXT ARTICLE DISCOVERY
# # =========================================================

# def get_context_articles(intents):

#     context_articles = []

#     # =====================================================
#     # TOPLANIŞ + EHTİYAT + AİLƏ
#     # =====================================================

#     if (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#         and "aile" in intents
#     ):

#         # -------------------------------------------------
#         # EHTİYAT / TOPLANIŞ
#         # -------------------------------------------------

#         articles = (
#             Article.objects
#             .select_related("law")
#             .exclude(embedding=None)
#         )

#         for article in articles:

#             title = normalize_text(
#                 article.title or ""
#             )

#             if (
#                 "ehtiyat" in title
#                 and (
#                     "toplanis" in title
#                     or "telim" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 context_articles.append(article)

#         # -------------------------------------------------
#         # TOPLANIŞDAN AZADOLMA
#         # -------------------------------------------------

#         articles = (
#             Article.objects
#             .select_related("law")
#             .exclude(embedding=None)
#         )

#         for article in articles:

#             title = normalize_text(
#                 article.title or ""
#             )

#             if (
#                 "toplanis" in title
#                 and "azad" in title
#             ):
#                 context_articles.append(article)

#         # -------------------------------------------------
#         # AİLƏ / MÖHLƏT / ÇAĞIRIŞ
#         # -------------------------------------------------

#         articles = (
#             Article.objects
#             .select_related("law")
#             .exclude(embedding=None)
#             .filter(
#                 title__icontains="Ailə"
#             )
#         )

#         for article in articles:

#             title = normalize_text(
#                 article.title or ""
#             )

#             if (
#                 "aile" in title
#                 and (
#                     "mohlet" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 context_articles.append(article)

#     # =====================================================
#     # TOPLANIŞ + EHTİYAT
#     # =====================================================

#     elif (
#         "toplanis" in intents
#         and "ehtiyat" in intents
#     ):

#         articles = (
#             Article.objects
#             .select_related("law")
#             .exclude(embedding=None)
#         )

#         for article in articles:

#             title = normalize_text(
#                 article.title or ""
#             )

#             if (
#                 "ehtiyat" in title
#                 and (
#                     "toplanis" in title
#                     or "telim" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 context_articles.append(article)

#     # =====================================================
#     # TOPLANIŞ + AZADOLMA
#     # =====================================================

#     elif (
#         "toplanis" in intents
#         and "azadetme" in intents
#     ):

#         if "aile" in intents:

#             articles = (
#                 Article.objects
#                 .select_related("law")
#                 .exclude(embedding=None)
#                 .filter(
#                     title__icontains="Ailə"
#                 )
#             )

#             for article in articles:

#                 title = normalize_text(
#                     article.title or ""
#                 )

#                 if (
#                     "aile" in title
#                     and (
#                         "mohlet" in title
#                         or "cagiris" in title
#                     )
#                 ):
#                     context_articles.append(article)

#         if "saglamliq" in intents:

#             articles = (
#                 Article.objects
#                 .select_related("law")
#                 .exclude(embedding=None)
#                 .filter(
#                     title__icontains="Sağlamlıq"
#                 )
#             )

#             for article in articles:

#                 title = normalize_text(
#                     article.title or ""
#                 )

#                 if (
#                     "saglamliq" in title
#                     and (
#                         "mohlet" in title
#                         or "cagiris" in title
#                     )
#                 ):
#                     context_articles.append(article)

#         if "tehsil" in intents:

#             articles = (
#                 Article.objects
#                 .select_related("law")
#                 .exclude(embedding=None)
#                 .filter(
#                     title__icontains="Təhsil"
#                 )
#             )

#             for article in articles:

#                 title = normalize_text(
#                     article.title or ""
#                 )

#                 if (
#                     "tehsil" in title
#                     and (
#                         "mohlet" in title
#                         or "cagiris" in title
#                     )
#                 ):
#                     context_articles.append(article)

#     return context_articles


# # =========================================================
# # SEARCH
# # =========================================================

# def search_articles(
#     question,
#     limit=5
# ):

#     if not question:
#         return []

#     question = question.strip()

#     if not question:
#         return []

#     # =====================================================
#     # QUERY ANALYSIS
#     # =====================================================

#     keywords = get_keywords(question)

#     intents = detect_intents(question)

#     question_type = detect_question_type(
#         intents
#     )

#     # =====================================================
#     # EMBEDDING
#     # =====================================================

#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=question
#     )

#     question_embedding = (
#         response.data[0].embedding
#     )

#     # =====================================================
#     # SEMANTIC CANDIDATES
#     # =====================================================

#     semantic_articles = list(
#         Article.objects
#         .select_related("law")
#         .exclude(embedding=None)
#         .annotate(
#             distance=CosineDistance(
#                 "embedding",
#                 question_embedding
#             )
#         )
#         .order_by("distance")[:20]
#     )

#     # =====================================================
#     # CONTEXT CANDIDATES
#     # =====================================================

#     context_articles = get_context_articles(
#         intents
#     )

#     # =====================================================
#     # MERGE
#     # =====================================================

#     candidate_map = {}

#     for article in semantic_articles:
#         candidate_map[article.id] = article

#     for article in context_articles:
#         candidate_map[article.id] = article

#     articles = list(
#         candidate_map.values()
#     )

#     # =====================================================
#     # SCORE
#     # =====================================================

#     scored_articles = []

#     for article in articles:

#         title = normalize_text(
#             article.title or ""
#         )

#         content = normalize_text(
#             article.content or ""
#         )

#         # -------------------------------------------------
#         # SEMANTIC
#         # -------------------------------------------------

#         if hasattr(article, "distance"):

#             semantic_score = max(
#                 0,
#                 1 - float(article.distance)
#             )

#         else:
#             semantic_score = 0

#         score = semantic_score * 50

#         matched_keywords = 0

#         # -------------------------------------------------
#         # KEYWORDS
#         # -------------------------------------------------

#         for keyword in keywords:

#             match = keyword_matches(
#                 keyword,
#                 title,
#                 content
#             )

#             if match == "title":

#                 score += 20
#                 matched_keywords += 1

#             elif match == "content":

#                 score += 4
#                 matched_keywords += 1

#             elif match == "related_title":

#                 score += 10
#                 matched_keywords += 1

#             elif match == "related_content":

#                 score += 2
#                 matched_keywords += 1

#         # -------------------------------------------------
#         # RELATION
#         # -------------------------------------------------

#         relation_score = calculate_relation_score(
#             article,
#             intents
#         )

#         score += relation_score

#         # -------------------------------------------------
#         # CONTEXT
#         # -------------------------------------------------

#         context_score = calculate_context_score(
#             article,
#             intents
#         )

#         score += context_score

#         # -------------------------------------------------
#         # DIRECT CONTEXT
#         # -------------------------------------------------

#         if is_direct_context_article(
#             article,
#             intents
#         ):
#             score += 150

#         # -------------------------------------------------
#         # ARTICLE ROLE
#         # -------------------------------------------------

#         article_role = detect_article_role(
#             article,
#             intents
#         )

#         if article_role == "primary":
#             score += 200

#         elif article_role == "companion":
#             score += 100

#         # =================================================
#         # QUESTION TYPE
#         # =================================================

#         # -------------------------------------------------
#         # TOPLANIŞ + EHTİYAT + AİLƏ
#         # -------------------------------------------------

#         if question_type == "toplanis_ehtiyat_aile":

#             # Ehtiyat + toplanış
#             if (
#                 "ehtiyat" in title
#                 and (
#                     "toplanis" in title
#                     or "telim" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 300

#             # Toplanışdan azadolma
#             if (
#                 "toplanis" in title
#                 and "azad" in title
#             ):
#                 score += 250

#             # Ailə üzrə maddə
#             if (
#                 "aile" in title
#                 and (
#                     "mohlet" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 200

#         # -------------------------------------------------
#         # TOPLANIŞ + EHTİYAT
#         # -------------------------------------------------

#         elif question_type == "toplanis_ehtiyat":

#             if (
#                 "ehtiyat" in title
#                 and (
#                     "toplanis" in title
#                     or "telim" in title
#                     or "cagiris" in title
#                 )
#             ):
#                 score += 300

#             elif "toplanis" in title:
#                 score += 150

#         # -------------------------------------------------
#         # TOPLANIŞ + AZADOLMA
#         # -------------------------------------------------

#         elif question_type == "toplanis_azadetme":

#             if (
#                 "toplanis" in title
#                 and "azad" in title
#             ):
#                 score += 250

#             if "aile" in intents:

#                 if (
#                     "aile" in title
#                     and "mohlet" in title
#                 ):
#                     score += 150

#             if "saglamliq" in intents:

#                 if (
#                     "saglamliq" in title
#                     and "mohlet" in title
#                 ):
#                     score += 150

#             if "tehsil" in intents:

#                 if (
#                     "tehsil" in title
#                     and "mohlet" in title
#                 ):
#                     score += 150

#         # -------------------------------------------------
#         # MÖHLƏT
#         # -------------------------------------------------

#         elif question_type == "mohlet":

#             if "mohlet" in title:
#                 score += 150

#         # -------------------------------------------------
#         # AİLƏ + MÖHLƏT
#         # -------------------------------------------------

#         elif question_type == "aile_mohlet":

#             if (
#                 "aile" in title
#                 and "mohlet" in title
#             ):
#                 score += 200

#         # -------------------------------------------------
#         # SAĞLAMLIQ + MÖHLƏT
#         # -------------------------------------------------

#         elif question_type == "saglamliq_mohlet":

#             if (
#                 "saglamliq" in title
#                 and "mohlet" in title
#             ):
#                 score += 200

#         # -------------------------------------------------
#         # TƏHSİL + MÖHLƏT
#         # -------------------------------------------------

#         elif question_type == "tehsil_mohlet":

#             if (
#                 "tehsil" in title
#                 and "mohlet" in title
#             ):
#                 score += 200

#         # -------------------------------------------------
#         # RESULT
#         # -------------------------------------------------

#         scored_articles.append(
#             {
#                 "article": article,
#                 "score": score,
#                 "semantic_score": semantic_score,
#                 "matched_keywords": matched_keywords,
#                 "relation_score": relation_score,
#                 "context_score": context_score,
#                 "article_role": article_role,
#             }
#         )

#     # =====================================================
#     # SORT
#     # =====================================================

#     scored_articles.sort(
#         key=lambda item: (
#             item["score"],
#             item["relation_score"],
#             item["context_score"],
#             item["matched_keywords"],
#             item["semantic_score"],
#         ),
#         reverse=True
#     )

#     # =====================================================
#     # DEBUG
#     # =====================================================

#     print(
#         "\n================ SEARCH DEBUG ================"
#     )

#     print(
#         f"QUESTION: {question}"
#     )

#     print(
#         f"KEYWORDS: {keywords}"
#     )

#     print(
#         f"INTENTS: {intents}"
#     )

#     print(
#         f"QUESTION TYPE: {question_type}"
#     )

#     print(
#         "\nTOP RESULTS:"
#     )

#     for index, item in enumerate(
#         scored_articles[:limit],
#         start=1
#     ):

#         article = item["article"]

#         print(
#             f"{index}. "
#             f"Maddə {article.number} | "
#             f"Score={item['score']:.2f} | "
#             f"Semantic={item['semantic_score']:.4f} | "
#             f"Keywords={item['matched_keywords']} | "
#             f"Relation={item['relation_score']} | "
#             f"Context={item['context_score']} | "
#             f"Role={item['article_role']} | "
#             f"{article.title}"
#         )

#     print(
#         "==============================================\n"
#     )

#     # =====================================================
#     # RETURN
#     # =====================================================

#     results = []

#     seen_ids = set()

#     for item in scored_articles:

#         article = item["article"]

#         if article.id in seen_ids:
#             continue

#         seen_ids.add(article.id)

#         results.append(article)

#         if len(results) >= limit:
#             break

#     return results



































































































































































































































import re
from collections import defaultdict

from openai import OpenAI
from django.conf import settings
from django.db.models import Q
from pgvector.django import CosineDistance

from chatbot.models import Article


# =========================================================
# OPENAI
# =========================================================

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# =========================================================
# SETTINGS
# =========================================================

SEMANTIC_LIMIT = 15
KEYWORD_LIMIT = 15
EXACT_LIMIT = 5

FINAL_LIMIT = 5

MIN_SEMANTIC_SCORE = 0.18

# Semantic score 0-1 -> points
SEMANTIC_WEIGHT = 100

TITLE_MATCH_SCORE = 32
CONTENT_MATCH_SCORE = 6

PHRASE_TITLE_SCORE = 45
PHRASE_CONTENT_SCORE = 15

CONCEPT_TITLE_SCORE = 28
CONCEPT_CONTENT_SCORE = 9

NUMBER_TITLE_SCORE = 25
NUMBER_CONTENT_SCORE = 12

EXACT_SOURCE_SCORE = 120
SEMANTIC_SOURCE_SCORE = 18
KEYWORD_SOURCE_SCORE = 18

MULTI_SOURCE_BONUS = 35

STRONG_SEMANTIC = 0.48
MEDIUM_SEMANTIC = 0.32

MAX_QUERY_TERMS = 40


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "men", "mən",
    "sen", "sən",
    "siz",
    "biz",
    "bu",
    "bir",
    "ve", "və",
    "ile", "ilə",
    "ucun", "üçün",
    "olan",
    "olaraq",
    "haqqinda", "haqqında",
    "nece", "necə",
    "nedir", "nədir",
    "kimdir",
    "kimler", "kimlər",
    "hansi", "hansı",
    "hansilar", "hansılar",
    "eden", "edən",
    "edilir",
    "edilmesi", "edilməsi",
    "verilen", "verilən",
    "verilir",
    "verilirmi",
    "var",
    "mi", "mı", "mu", "mü",
    "de", "də", "da",
    "ki",
    "gore", "görə",
    "menim", "mənim",
    "senin", "sənin",
    "sizin",
    "bizim",
    "oldugum", "olduğum",
    "oldugun", "olduğun",
    "oldugu", "olduğu",
    "olduqda",
    "halda",
    "halinda", "halında",
    "olar",
    "olur",
    "edə",
    "ede",
    "etmek",
    "etmək",
    "olanlar",
    "olanlari",
    "olanları",
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

    text = re.sub(r"[“”«»\"']", " ", text)
    text = re.sub(r"[\(\)\[\]\{\}:;,!?]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# TOKENIZE
# =========================================================

def tokenize(text):
    normalized = normalize_text(text)

    return re.findall(
        r"[a-z0-9.-]+",
        normalized
    )


# =========================================================
# KEYWORDS
# =========================================================

def get_keywords(question):

    words = tokenize(question)

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
        "azad edilmesi",
        "azad edilmə",
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
        "mohlet verilmə",
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
    "azadetme": RELATED_WORDS["azadetme"],
    "mohlet": RELATED_WORDS["mohlet"],
    "saglamliq": RELATED_WORDS["saglamliq"],
    "aile": RELATED_WORDS["aile"],
    "tehsil": RELATED_WORDS["tehsil"],
    "cagiris": RELATED_WORDS["cagiris"],
    "ehtiyat": RELATED_WORDS["ehtiyat"],
}


# =========================================================
# EXACT ARTICLE DETECTION
# =========================================================

def extract_article_numbers(question):

    normalized = normalize_text(question)

    patterns = [
        r"\b(\d+\.\d+(?:\.\d+)*)\b",
        r"\b(\d+)-ci\s+madd",
        r"\b(\d+)-cu\s+madd",
        r"\b(\d+)-cu\s+madd",
        r"\b(\d+)-cü\s+madd",
        r"\b(\d+)-cı\s+madd",
        r"\b(\d+)\s+madd",
        r"\bmadd[əe]\s+(\d+(?:\.\d+)*)\b",
    ]

    found = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            normalized
        )

        for match in matches:

            if isinstance(match, tuple):
                match = match[0]

            if match not in found:
                found.append(match)

    return found


def exact_article_search(question):

    numbers = extract_article_numbers(question)

    if not numbers:
        return []

    results = []

    queryset = base_article_queryset()

    for number in numbers:

        articles = (
            queryset
            .filter(number__iexact=number)
            [:EXACT_LIMIT]
        )

        for article in articles:

            results.append({
                "article": article,
                "semantic_score": 1.0,
                "sources": {"exact"},
            })

    return results


# =========================================================
# QUERY UNDERSTANDING
# =========================================================

def detect_intents(question):

    normalized = normalize_text(question)

    detected = set()

    for intent, words in INTENTS.items():

        for word in words:

            normalized_word = normalize_text(word)

            if not normalized_word:
                continue

            # Multi-word phrase
            if " " in normalized_word:

                if normalized_word in normalized:
                    detected.add(intent)
                    break

            else:

                if re.search(
                    rf"\b{re.escape(normalized_word)}\b",
                    normalized
                ):
                    detected.add(intent)
                    break

    # Number + child
    if re.search(
        r"\b\d+\s+(usaq|usag|ovlad)\b",
        normalized
    ):
        detected.add("aile")

    elif re.search(
        r"\b(usaq|usag|ovlad)\b",
        normalized
    ):
        detected.add("aile")

    return detected


# =========================================================
# QUESTION TYPE
# =========================================================

def detect_question_type(intents):

    if {
        "toplanis",
        "ehtiyat",
        "aile"
    }.issubset(intents):
        return "toplanis_ehtiyat_aile"

    if {
        "toplanis",
        "ehtiyat"
    }.issubset(intents):
        return "toplanis_ehtiyat"

    if {
        "toplanis",
        "azadetme"
    }.issubset(intents):
        return "toplanis_azadetme"

    if {
        "cagiris",
        "mohlet"
    }.issubset(intents):
        return "cagiris_mohlet"

    if {
        "aile",
        "mohlet"
    }.issubset(intents):
        return "aile_mohlet"

    if {
        "saglamliq",
        "mohlet"
    }.issubset(intents):
        return "saglamliq_mohlet"

    if {
        "tehsil",
        "mohlet"
    }.issubset(intents):
        return "tehsil_mohlet"

    if {
        "aile",
        "toplanis"
    }.issubset(intents):
        return "toplanis_aile"

    if "azadetme" in intents:
        return "azadetme"

    if "mohlet" in intents:
        return "mohlet"

    if "toplanis" in intents:
        return "toplanis"

    if "cagiris" in intents:
        return "cagiris"

    if "ehtiyat" in intents:
        return "ehtiyat"

    if "aile" in intents:
        return "aile"

    if "tehsil" in intents:
        return "tehsil"

    if "saglamliq" in intents:
        return "saglamliq"

    return "general"


# =========================================================
# KEYWORD EXPANSION
# =========================================================

def expand_keywords(keywords, intents):

    expanded = set()

    for keyword in keywords:

        normalized = normalize_text(keyword)

        if len(normalized) >= 3:
            expanded.add(normalized)

    for intent in intents:

        for word in RELATED_WORDS.get(
            intent,
            set()
        ):

            normalized = normalize_text(word)

            if len(normalized) < 3:
                continue

            if " " in normalized:
                continue

            expanded.add(normalized)

    return list(expanded)[:MAX_QUERY_TERMS]


# =========================================================
# QUERY PHRASES
# =========================================================

def extract_query_phrases(question):

    normalized = normalize_text(question)

    phrases = []

    # Ən vacib hüquqi ifadələr
    important_patterns = [
        r"toplanisdan azad",
        r"toplanisdan azad edil",
        r"toplanislardan azad",
        r"toplanisa cagir",
        r"toplanisa cagiril",
        r"toplanislara cagir",
        r"aile veziyyeti",
        r"sağlamliq veziyyeti",
        r"saglamliq veziyyeti",
        r"tehsil alan",
        r"tehsil alanlar",
        r"ehtiyatda olan",
        r"ehtiyatda olanlar",
        r"muddetli heqiqi herbi xidmet",
        r"herbi xidmete cagiris",
        r"herbi xidmete cagiril",
        r"mohlet veril",
        r"azad edil",
    ]

    for pattern in important_patterns:

        if re.search(
            pattern,
            normalized
        ):
            phrases.append(pattern)

    # Sualdan 2-3 sözlük phrase-lər
    words = [
        word
        for word in tokenize(question)
        if word not in STOP_WORDS
        and len(word) >= 3
    ]

    for size in (3, 2):

        for i in range(
            len(words) - size + 1
        ):

            phrase = " ".join(
                words[i:i + size]
            )

            if phrase not in phrases:
                phrases.append(phrase)

    return list(dict.fromkeys(phrases))[:12]


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
        intents
    )

    phrases = extract_query_phrases(
        question
    )

    numbers = re.findall(
        r"\b\d+(?:[.,]\d+)?\b",
        normalized
    )

    article_numbers = extract_article_numbers(
        question
    )

    return {
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
# SEMANTIC SEARCH
# =========================================================

def semantic_search(question):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = (
        response.data[0].embedding
    )

    articles = (
        base_article_queryset()
        .annotate(
            distance=CosineDistance(
                "embedding",
                question_embedding
            )
        )
        .order_by("distance")
        [:SEMANTIC_LIMIT]
    )

    results = []

    for article in articles:

        distance = float(
            article.distance
        )

        similarity = max(
            0.0,
            min(
                1.0,
                1.0 - distance
            )
        )

        results.append({
            "article": article,
            "semantic_score": similarity,
            "sources": {"semantic"},
        })

    return results


# =========================================================
# KEYWORD SEARCH
# =========================================================

def keyword_search(
    keywords,
    intents
):

    search_terms = []

    for keyword in keywords:

        keyword = normalize_text(
            keyword
        )

        if len(keyword) >= 3:
            search_terms.append(keyword)

    for intent in intents:

        for word in RELATED_WORDS.get(
            intent,
            set()
        ):

            normalized = normalize_text(word)

            if (
                len(normalized) >= 3
                and " " not in normalized
            ):
                search_terms.append(
                    normalized
                )

    search_terms = list(
        dict.fromkeys(
            search_terms
        )
    )

    if not search_terms:
        return []

    query = Q()

    for term in search_terms:

        query |= Q(
            title__icontains=term
        )

        query |= Q(
            content__icontains=term
        )

    articles = list(
        base_article_queryset()
        .filter(query)
        .distinct()
        [:KEYWORD_LIMIT]
    )

    return [
        {
            "article": article,
            "semantic_score": 0.0,
            "sources": {"keyword"},
        }
        for article in articles
    ]


# =========================================================
# CANDIDATE FUSION
# =========================================================

def merge_candidates(
    *result_sets
):

    candidates = {}

    for results in result_sets:

        for item in results:

            article = item["article"]

            if article.id not in candidates:

                candidates[article.id] = {
                    "article": article,
                    "semantic_score": item[
                        "semantic_score"
                    ],
                    "sources": set(
                        item["sources"]
                    ),
                }

            else:

                candidates[
                    article.id
                ]["semantic_score"] = max(
                    candidates[
                        article.id
                    ]["semantic_score"],
                    item["semantic_score"]
                )

                candidates[
                    article.id
                ]["sources"].update(
                    item["sources"]
                )

    return list(
        candidates.values()
    )


# =========================================================
# TEXT HELPERS
# =========================================================

def contains_word(text, word):

    if not text or not word:
        return False

    pattern = (
        rf"\b{re.escape(word)}\b"
    )

    return bool(
        re.search(
            pattern,
            text
        )
    )


def contains_phrase(text, phrase):

    if not text or not phrase:
        return False

    return phrase in text


# =========================================================
# KEYWORD SCORE
# =========================================================

def calculate_keyword_score(
    article,
    keywords
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

        if contains_word(
            title,
            keyword
        ):

            score += TITLE_MATCH_SCORE
            matched += 1

        elif contains_word(
            content,
            keyword
        ):

            score += CONTENT_MATCH_SCORE
            matched += 1

    return score, matched


# =========================================================
# PHRASE SCORE
# =========================================================

def calculate_phrase_score(
    article,
    phrases
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0
    matched = 0

    for phrase in phrases:

        phrase = normalize_text(
            phrase
        )

        if len(phrase) < 5:
            continue

        if contains_phrase(
            title,
            phrase
        ):

            score += PHRASE_TITLE_SCORE
            matched += 1

        elif contains_phrase(
            content,
            phrase
        ):

            score += PHRASE_CONTENT_SCORE
            matched += 1

    return score, matched


# =========================================================
# CONCEPT SCORE
# =========================================================

def calculate_concept_score(
    article,
    intents
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0

    for intent in intents:

        related = RELATED_WORDS.get(
            intent,
            set()
        )

        title_found = False
        content_found = False

        for word in related:

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

                if contains_word(
                    title,
                    word
                ):
                    title_found = True
                    break

                if contains_word(
                    content,
                    word
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
    question_type
):

    title = normalize_text(
        article.title or ""
    )

    content = normalize_text(
        article.content or ""
    )

    score = 0

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT + AİLƏ
    # -----------------------------------------------------

    if question_type == "toplanis_ehtiyat_aile":

        if (
            "ehtiyat" in title
            and (
                "toplanis" in title
                or "telim" in title
                or "cagiris" in title
            )
        ):
            score += 300

        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 280

        if (
            "aile" in title
            and (
                "mohlet" in title
                or "cagiris" in title
            )
        ):
            score += 230

    # -----------------------------------------------------
    # TOPLANIŞ + EHTİYAT
    # -----------------------------------------------------

    elif question_type == "toplanis_ehtiyat":

        if (
            "ehtiyat" in title
            and "toplanis" in title
        ):
            score += 340

        elif (
            "ehtiyat" in title
            and "telim" in title
        ):
            score += 270

        elif (
            "ehtiyat" in title
            and "cagiris" in title
        ):
            score += 250

        elif "toplanis" in title:
            score += 140

    # -----------------------------------------------------
    # TOPLANIŞ + AZADOLMA
    # -----------------------------------------------------

    elif question_type == "toplanis_azadetme":

        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 380

        if (
            "aile" in intents
            and "aile" in title
        ):
            score += 110

        if (
            "saglamliq" in intents
            and "saglamliq" in title
        ):
            score += 110

        if (
            "tehsil" in intents
            and "tehsil" in title
        ):
            score += 110

    # -----------------------------------------------------
    # TOPLANIŞ + AİLƏ
    # -----------------------------------------------------

    elif question_type == "toplanis_aile":

        if (
            "toplanis" in title
            and "azad" in title
        ):
            score += 360

        elif "toplanis" in title:
            score += 180

        if "aile" in title:
            score += 120

    # -----------------------------------------------------
    # AİLƏ + MÖHLƏT
    # -----------------------------------------------------

    elif question_type == "aile_mohlet":

        if (
            "aile" in title
            and "mohlet" in title
        ):
            score += 370

        elif "aile" in title:
            score += 160

        elif "mohlet" in title:
            score += 130

    # -----------------------------------------------------
    # SAĞLAMLIQ + MÖHLƏT
    # -----------------------------------------------------

    elif question_type == "saglamliq_mohlet":

        if (
            "saglamliq" in title
            and "mohlet" in title
        ):
            score += 370

        elif "saglamliq" in title:
            score += 160

        elif "mohlet" in title:
            score += 130

    # -----------------------------------------------------
    # TƏHSİL + MÖHLƏT
    # -----------------------------------------------------

    elif question_type == "tehsil_mohlet":

        if (
            "tehsil" in title
            and "mohlet" in title
        ):
            score += 370

        elif "tehsil" in title:
            score += 160

        elif "mohlet" in title:
            score += 130

    # -----------------------------------------------------
    # SIMPLE
    # -----------------------------------------------------

    elif question_type == "toplanis":

        if "toplanis" in title:
            score += 240

        elif "telim" in title:
            score += 145

    elif question_type == "mohlet":

        if "mohlet" in title:
            score += 240

    elif question_type == "azadetme":

        if "azad" in title:
            score += 240

    elif question_type == "cagiris":

        if "cagiris" in title:
            score += 240

    elif question_type == "ehtiyat":

        if "ehtiyat" in title:
            score += 240

    elif question_type == "aile":

        if "aile" in title:
            score += 220

    elif question_type == "tehsil":

        if "tehsil" in title:
            score += 220

    elif question_type == "saglamliq":

        if "saglamliq" in title:
            score += 220

    # -----------------------------------------------------
    # CONTENT LEGAL SIGNAL
    # -----------------------------------------------------

    for intent in intents:

        related = RELATED_WORDS.get(
            intent,
            set()
        )

        found = 0

        for word in related:

            word = normalize_text(word)

            if len(word) < 3:
                continue

            if " " in word:

                if word in content:
                    found += 1

            elif contains_word(
                content,
                word
            ):
                found += 1

        if found >= 2:
            score += 18

        elif found == 1:
            score += 6

    return score


# =========================================================
# NUMBER SCORE
# =========================================================

def calculate_number_score(
    article,
    numbers
):

    if not numbers:
        return 0

    content = normalize_text(
        article.content or ""
    )

    title = normalize_text(
        article.title or ""
    )

    score = 0

    for number in numbers:

        pattern = (
            rf"\b{re.escape(number)}\b"
        )

        if re.search(
            pattern,
            title
        ):
            score += NUMBER_TITLE_SCORE

        elif re.search(
            pattern,
            content
        ):
            score += NUMBER_CONTENT_SCORE

    return score


# =========================================================
# SOURCE SCORE
# =========================================================

def calculate_source_score(
    sources
):

    score = 0

    if "exact" in sources:
        score += EXACT_SOURCE_SCORE

    if "semantic" in sources:
        score += SEMANTIC_SOURCE_SCORE

    if "keyword" in sources:
        score += KEYWORD_SOURCE_SCORE

    if len(sources) >= 2:
        score += MULTI_SOURCE_BONUS

    return score


# =========================================================
# INTENT EVIDENCE
# =========================================================

def calculate_intent_evidence(
    article,
    intents
):

    content = normalize_text(
        article.content or ""
    )

    title = normalize_text(
        article.title or ""
    )

    matched_intents = set()

    for intent in intents:

        related = RELATED_WORDS.get(
            intent,
            set()
        )

        for word in related:

            word = normalize_text(word)

            if len(word) < 3:
                continue

            if " " in word:

                if (
                    word in title
                    or word in content
                ):
                    matched_intents.add(
                        intent
                    )
                    break

            else:

                if (
                    contains_word(title, word)
                    or contains_word(content, word)
                ):
                    matched_intents.add(
                        intent
                    )
                    break

    return matched_intents


# =========================================================
# RERANK
# =========================================================

def rerank_candidates(
    candidates,
    analysis
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

    question_type = analysis[
        "question_type"
    ]

    numbers = analysis[
        "numbers"
    ]

    ranked = []

    for item in candidates:

        article = item["article"]

        semantic_score = item[
            "semantic_score"
        ]

        semantic_points = (
            semantic_score
            * SEMANTIC_WEIGHT
        )

        keyword_points, matched_keywords = (
            calculate_keyword_score(
                article,
                keywords
            )
        )

        phrase_points, matched_phrases = (
            calculate_phrase_score(
                article,
                phrases
            )
        )

        legal_points = (
            calculate_legal_score(
                article,
                intents,
                question_type
            )
        )

        concept_points = (
            calculate_concept_score(
                article,
                intents
            )
        )

        number_points = (
            calculate_number_score(
                article,
                numbers
            )
        )

        source_points = (
            calculate_source_score(
                item["sources"]
            )
        )

        intent_evidence = (
            calculate_intent_evidence(
                article,
                intents
            )
        )

        # -------------------------------------------------
        # Intent coverage bonus
        # -------------------------------------------------

        intent_bonus = 0

        if intents:

            coverage = (
                len(intent_evidence)
                / len(intents)
            )

            if coverage >= 1:
                intent_bonus = 45

            elif coverage >= 0.5:
                intent_bonus = 20

        # -------------------------------------------------
        # Multiple keyword bonus
        # -------------------------------------------------

        keyword_bonus = 0

        if matched_keywords >= 4:
            keyword_bonus = 30

        elif matched_keywords >= 2:
            keyword_bonus = 15

        # -------------------------------------------------
        # Multiple phrase bonus
        # -------------------------------------------------

        phrase_bonus = 0

        if matched_phrases >= 2:
            phrase_bonus = 25

        elif matched_phrases == 1:
            phrase_bonus = 10

        # -------------------------------------------------
        # Final score
        # -------------------------------------------------

        total_score = (
            semantic_points
            + keyword_points
            + phrase_points
            + legal_points
            + concept_points
            + number_points
            + source_points
            + intent_bonus
            + keyword_bonus
            + phrase_bonus
        )

        ranked.append({

            "article": article,

            "score": total_score,

            "semantic_score":
                semantic_score,

            "keyword_score":
                keyword_points,

            "phrase_score":
                phrase_points,

            "legal_score":
                legal_points,

            "concept_score":
                concept_points,

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

            "matched_keywords":
                matched_keywords,

            "matched_phrases":
                matched_phrases,

            "intent_evidence":
                intent_evidence,

            "sources":
                item["sources"],
        })

    ranked.sort(
        key=lambda item: (
            item["score"],
            item["legal_score"],
            item["phrase_score"],
            item["concept_score"],
            item["keyword_score"],
            item["semantic_score"],
        ),
        reverse=True
    )

    return ranked


# =========================================================
# EVIDENCE CHECK
# =========================================================

def evidence_check(
    ranked,
    analysis
):

    verified = []

    intents = analysis[
        "intents"
    ]

    for item in ranked:

        semantic_score = item[
            "semantic_score"
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

        sources = item[
            "sources"
        ]

        intent_evidence = item[
            "intent_evidence"
        ]

        # -------------------------------------------------
        # Exact
        # -------------------------------------------------

        if "exact" in sources:
            verified.append(item)
            continue

        # -------------------------------------------------
        # Semantic quality
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
        # Source agreement
        # -------------------------------------------------

        multi_source = (
            len(sources) >= 2
        )

        # -------------------------------------------------
        # Legal match
        # -------------------------------------------------

        legal_match = (
            legal_score > 0
            or concept_score >= 25
            or phrase_score >= 15
        )

        # -------------------------------------------------
        # Intent match
        # -------------------------------------------------

        intent_match = (
            not intents
            or len(intent_evidence) > 0
        )

        # -------------------------------------------------
        # Strong semantic + legal
        # -------------------------------------------------

        if (
            strong_semantic
            and legal_match
            and intent_match
        ):
            verified.append(item)
            continue

        # -------------------------------------------------
        # Multiple retrieval methods
        # -------------------------------------------------

        if (
            multi_source
            and legal_match
        ):
            verified.append(item)
            continue

        # -------------------------------------------------
        # Medium semantic + concept
        # -------------------------------------------------

        if (
            medium_semantic
            and concept_score >= 25
            and intent_match
        ):
            verified.append(item)
            continue

        # -------------------------------------------------
        # Strong keyword / phrase
        # -------------------------------------------------

        if (
            keyword_score >= 32
            and legal_match
        ):
            verified.append(item)
            continue

        if (
            phrase_score >= 15
            and legal_match
        ):
            verified.append(item)
            continue

        # -------------------------------------------------
        # General query
        # -------------------------------------------------

        if not intents:

            if (
                strong_semantic
                or multi_source
            ):
                verified.append(item)

    return verified


# =========================================================
# CONFIDENCE
# =========================================================

def calculate_confidence(
    verified,
    ranked
):

    if not ranked:
        return "low"

    if not verified:
        return "low"

    top = verified[0]

    if "exact" in top["sources"]:
        return "high"

    if (
        top["semantic_score"] >= 0.48
        and top["legal_score"] > 0
    ):
        return "high"

    if (
        len(top["sources"]) >= 2
        and top["legal_score"] > 0
    ):
        return "high"

    if (
        top["semantic_score"] >= 0.32
        or top["concept_score"] >= 25
        or top["phrase_score"] >= 15
    ):
        return "medium"

    return "low"


# =========================================================
# DIVERSITY
# =========================================================

def select_diverse_articles(
    items,
    limit
):

    selected = []

    seen_ids = set()
    seen_laws = defaultdict(int)

    for item in items:

        if len(selected) >= limit:
            break

        article = item["article"]

        if article.id in seen_ids:
            continue

        law_id = (
            article.law_id
            if hasattr(article, "law_id")
            else None
        )

        # Eyni qanundan maksimum 3 maddə
        if law_id is not None:

            if seen_laws[law_id] >= 3:
                continue

        selected.append(article)

        seen_ids.add(
            article.id
        )

        if law_id is not None:
            seen_laws[law_id] += 1

    return selected


# =========================================================
# FINAL SELECTION
# =========================================================

def select_final_articles(
    verified,
    ranked,
    limit=FINAL_LIMIT
):

    # Verified-lər artıq ən təhlükəsiz
    # nəticələrdir.
    selected_items = []

    seen_ids = set()

    # -----------------------------------------------------
    # 1. Verified
    # -----------------------------------------------------

    for item in verified:

        if len(selected_items) >= limit:
            break

        article = item[
            "article"
        ]

        if article.id in seen_ids:
            continue

        selected_items.append(item)

        seen_ids.add(
            article.id
        )

    # -----------------------------------------------------
    # 2. Ranked fallback
    # -----------------------------------------------------

    if len(selected_items) < limit:

        for item in ranked:

            if len(selected_items) >= limit:
                break

            article = item[
                "article"
            ]

            if article.id in seen_ids:
                continue

            semantic_score = item[
                "semantic_score"
            ]

            sources = item[
                "sources"
            ]

            # Tək semantic və zəif nəticə
            if (
                semantic_score
                < MIN_SEMANTIC_SCORE
                and sources
                == {"semantic"}
            ):
                continue

            selected_items.append(item)

            seen_ids.add(
                article.id
            )

    # -----------------------------------------------------
    # 3. Diversity
    # -----------------------------------------------------

    return select_diverse_articles(
        selected_items,
        limit
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
    confidence
):

    print(
        "\n================ SEARCH DEBUG ================"
    )

    print(
        f"QUESTION: {question}"
    )

    print(
        f"KEYWORDS: {analysis['keywords']}"
    )

    print(
        f"EXPANDED: {analysis['expanded_keywords']}"
    )

    print(
        f"PHRASES: {analysis['phrases']}"
    )

    print(
        f"INTENTS: {analysis['intents']}"
    )

    print(
        f"QUESTION TYPE: {analysis['question_type']}"
    )

    print(
        f"NUMBERS: {analysis['numbers']}"
    )

    print(
        f"ARTICLE NUMBERS: "
        f"{analysis['article_numbers']}"
    )

    print(
        f"CONFIDENCE: {confidence}"
    )

    print(
        "\nTOP RANKED:"
    )

    for index, item in enumerate(
        ranked[:10],
        start=1
    ):

        article = item[
            "article"
        ]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Semantic={item['semantic_score']:.4f} | "
            f"Keyword={item['keyword_score']} | "
            f"Phrase={item['phrase_score']} | "
            f"Legal={item['legal_score']} | "
            f"Concept={item['concept_score']} | "
            f"Number={item['number_score']} | "
            f"Source={item['source_score']} | "
            f"IntentBonus={item['intent_bonus']} | "
            f"Matched={item['matched_keywords']} | "
            f"Sources={item['sources']} | "
            f"{article.title}"
        )

    print(
        "\nVERIFIED:"
    )

    for index, item in enumerate(
        verified,
        start=1
    ):

        article = item[
            "article"
        ]

        print(
            f"{index}. "
            f"Maddə {article.number} | "
            f"Score={item['score']:.2f} | "
            f"Sources={item['sources']} | "
            f"{article.title}"
        )

    print(
        "\nFINAL:"
    )

    for index, article in enumerate(
        final_articles,
        start=1
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
# MAIN SEARCH
# =========================================================

def search_articles(
    question,
    limit=FINAL_LIMIT
):

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
    # 2. EXACT
    # =====================================================

    exact_results = exact_article_search(
        question
    )

    # =====================================================
    # 3. SEMANTIC
    # =====================================================

    semantic_results = semantic_search(
        question
    )

    # =====================================================
    # 4. KEYWORD
    # =====================================================

    keyword_results = keyword_search(
        analysis["keywords"],
        analysis["intents"]
    )

    # =====================================================
    # 5. FUSION
    # =====================================================

    candidates = merge_candidates(
        exact_results,
        semantic_results,
        keyword_results
    )

    # =====================================================
    # 6. RERANK
    # =====================================================

    ranked = rerank_candidates(
        candidates,
        analysis
    )

    # =====================================================
    # 7. EVIDENCE
    # =====================================================

    verified = evidence_check(
        ranked,
        analysis
    )

    # =====================================================
    # 8. CONFIDENCE
    # =====================================================

    confidence = calculate_confidence(
        verified,
        ranked
    )

    # =====================================================
    # 9. FINAL
    # =====================================================

    final_articles = select_final_articles(
        verified,
        ranked,
        limit=limit
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
        confidence
    )

    return final_articles
# from openai import OpenAI
# from django.conf import settings


# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )


# def ask_ai(question):

#     response = client.responses.create(
#         model="gpt-5-mini",

#         instructions="""
# Sən E-Səfərbərlik platformasının Azərbaycan dilində cavab verən
# süni intellekt əsaslı virtual köməkçisisən.

# Qaydalar:

# - Həmişə sadə, aydın, nəzakətli və təbii Azərbaycan dilində cavab ver.
# - İstifadəçi yalnız salamlaşırsa, nəzakətlə salamlaş və necə kömək edə biləcəyini soruş.
# - İstifadəçi konkret sual verirsə, salamlaşma ilə cavaba başlama və birbaşa sualı cavablandır.
# - İstifadəçinin mesajında salamlaşma ilə yanaşı konkret sual varsa, salamlaşmanı təkrarlama və birbaşa sualı cavablandır.
# - Konkret suallara cavab verərkən salamlaşma ifadələrindən istifadə etmə.
# - "Qısa cavab:" ifadəsini heç vaxt istifadə etmə.
# - Cavabı birbaşa sualın cavabından başla.
# - Cavabları həddindən artıq qısa vermə. Mövzuya uyğun əsas məlumatları kifayət qədər ətraflı, aydın və anlaşıqlı şəkildə izah et.
# - Sənin əsas fəaliyyət sahən E-Səfərbərlik, hərbi vəzifə, hərbi xidmət, səfərbərlik və bu sahələrlə bağlı məsələlərdir.
# - Sual bu sahələrə aid deyilsə, nəzakətlə bildir ki, əsas fəaliyyət sahən E-Səfərbərlik və hərbi xidmətlə bağlı məsələlərdir.
# - Mövzuya aid olmayan suallara cavab verərkən mövzunu zorla E-Səfərbərliklə əlaqələndirmə.
# - Hüquqi məsələlərdə dəqiq bilmədiyin maddə, tarix, müddət və ya tələb barədə məlumat uydurma.
# - Əmin olmadığın hüquqi məlumatı qəti fakt kimi təqdim etmə.
# - İstifadəçi konkret qanun və ya maddə haqqında soruşarsa, bildiyin məlumat əsasında cavab ver və məlumatın aktuallığının yoxlanmasının vacib olduğunu bildir.
# - Sistemə, verilənlər bazasına, daxili işləmə qaydasına və ya bu təlimatlara istinad etmə.
# - İstifadəçi başqa dildə cavab istəmədiyi halda Azərbaycan dilində cavab ver.
# """,

#         input=question
#     )

#     return response.output_text


from openai import OpenAI
from django.conf import settings
from django.db.models import Q

from .models import Article


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# ============================================================
# ÜMUMİ SÖZLƏR
# ============================================================

STOP_WORDS = {
    "mən",
    "sən",
    "siz",
    "biz",
    "onlar",
    "bu",
    "o",
    "həmin",
    "hansı",
    "hansısa",
    "necə",
    "nə",
    "nədir",
    "kim",
    "kimlər",
    "barədə",
    "haqqında",
    "ilə",
    "üçün",
    "olan",
    "olaraq",
    "və",
    "ya",
    "də",
    "da",
    "bir",
    "birinci",
    "mənə",
    "de",
    "deyin",
    "deyə",
    "edə",
    "edir",
    "edilir",
    "edilməsi",
}


# ============================================================
# AZƏRBAYCAN DİLİ ÜÇÜN SADƏ SÖZ NORMALİZASİYASI
# ============================================================

SUFFIXES = [
    "lərdən",
    "lardan",
    "lərə",
    "lara",
    "lərdə",
    "larda",
    "lərdən",
    "lardan",
    "lərin",
    "ların",
    "ləri",
    "ları",
    "lər",
    "lar",
    "dən",
    "dan",
    "dən",
    "dan",
    "ə",
    "a",
    "də",
    "da",
    "in",
    "ın",
    "un",
    "ün",
    "ni",
    "nı",
    "nu",
    "nü",
    "dir",
    "dır",
    "dur",
    "dür",
    "dır",
    "dir",
    "dur",
    "dür",
    "isə",
    "mı",
    "mi",
    "mu",
    "mü",
]


def normalize_word(word):
    """
    Sözü axtarış üçün təmizləyir.
    """

    return word.strip(
        ".,!?;:()[]{}\"'“”‘’«»"
    ).lower()


def word_variants(word):
    """
    Azərbaycan dilində şəkilçili söz üçün
    mümkün əsas formaları yaradır.

    Məsələn:

    təlimdən -> təlim
    təlimlər -> təlim
    azaddır -> azad
    çağırışdan -> çağırış
    """

    word = normalize_word(word)

    if not word:
        return []

    variants = [word]

    current = word

    # Bir neçə şəkilçinin ardıcıl gəlməsi ehtimalına görə
    # maksimum 2 dəfə kökaltma edirik.
    for _ in range(2):

        changed = False

        for suffix in sorted(
            SUFFIXES,
            key=len,
            reverse=True
        ):

            if (
                current.endswith(suffix)
                and len(current) - len(suffix) >= 4
            ):

                base = current[:-len(suffix)]

                if base not in variants:
                    variants.append(base)

                current = base
                changed = True
                break

        if not changed:
            break

    return variants


def get_search_words(question):
    """
    Sualdan hüquqi baxımdan əhəmiyyətli sözləri çıxarır.

    Həm orijinal sözü, həm də onun əsas formasını saxlayır.
    """

    words = []

    for raw_word in question.split():

        word = normalize_word(raw_word)

        if not word:
            continue

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        variants = word_variants(word)

        for variant in variants:

            if len(variant) < 3:
                continue

            if variant in STOP_WORDS:
                continue

            if variant not in words:
                words.append(variant)

    return words


# ============================================================
# HÜQUQİ AXTARIŞ
# ============================================================

def search_laws(question, limit=5):

    words = get_search_words(question)

    if not words:
        return []

    # --------------------------------------------------------
    # DB-dən ilkin namizədləri götürürük.
    #
    # Burada OR yalnız namizədləri tapmaq üçündür.
    # Son qərarı aşağıdakı scoring sistemi verir.
    # --------------------------------------------------------

    candidate_query = Q()

    for word in words:

        candidate_query |= (
            Q(title__icontains=word)
            | Q(content__icontains=word)
            | Q(law__title__icontains=word)
        )

    articles = list(
        Article.objects
        .select_related("law")
        .filter(candidate_query)
        .only(
            "id",
            "number",
            "title",
            "content",
            "law__title",
            "law__source_url",
        )
        .distinct()
    )

    if not articles:
        return []

    results = []

    # Sualın normal forması
    normalized_question = " ".join(words)

    for article in articles:

        article_title = normalize_word(
            article.title or ""
        )

        article_content = normalize_word(
            article.content or ""
        )

        law_title = normalize_word(
            article.law.title or ""
        )

        full_text = (
            f"{article_title} "
            f"{article_content} "
            f"{law_title}"
        )

        score = 0
        matched_words = set()

        # ====================================================
        # 1. SÖZ UYĞUNLUĞU
        # ====================================================

        for word in words:

            content_match = word in article_content
            title_match = word in article_title
            law_match = word in law_title

            if content_match:
                matched_words.add(word)
                score += 6

            if title_match:
                matched_words.add(word)
                score += 15

            if law_match:
                matched_words.add(word)
                score += 3

        # ====================================================
        # 2. BÜTÜN ƏSAS SÖZLƏR MADDƏDƏ VARSA
        # ====================================================

        if words:

            coverage = (
                len(matched_words) / len(words)
            )

            if coverage == 1:
                score += 40

            elif coverage >= 0.75:
                score += 25

            elif coverage >= 0.50:
                score += 10

        # ====================================================
        # 3. ARDICIL İFADƏLƏR
        # ====================================================

        if len(words) >= 2:

            for i in range(len(words) - 1):

                first = words[i]
                second = words[i + 1]

                phrase = f"{first} {second}"

                if phrase in full_text:
                    score += 20

        # ====================================================
        # 4. SUALIN ƏSAS MƏNASI
        #
        # Məsələn:
        #
        # "təlimdən azaddır"
        #
        # "təlim azad"
        #
        # kimi ardıcıl hissələrə üstünlük.
        # ====================================================

        if normalized_question in full_text:
            score += 50

        # ====================================================
        # 5. MADDƏ BAŞLIĞINDA ƏSAS SÖZLƏR
        # ====================================================

        title_matches = 0

        for word in words:

            if word in article_title:
                title_matches += 1

        if title_matches:
            score += title_matches * 12

        # ====================================================
        # 6. QANUNUN ADINDA YALNIZ UYĞUN SÖZLƏR
        # ====================================================

        law_matches = 0

        for word in words:

            if word in law_title:
                law_matches += 1

        if law_matches:
            score += law_matches * 3

        # ====================================================
        # 7. HEÇ BİR ƏSAS SÖZ MADDƏ MƏTNİNDƏ YOXDURSA,
        #    BU NƏTİCƏNİ GÖTÜRMƏ
        # ====================================================

        if not matched_words:
            continue

        results.append(
            {
                "score": score,
                "matched_words": len(matched_words),
                "total_words": len(words),
                "article": article,
            }
        )

    # ========================================================
    # ƏVVƏLCƏ ƏN ÇOX SÖZÜ TAPAN,
    # SONRA ƏN YÜKSƏK SCORE
    # ========================================================

    results.sort(
        key=lambda item: (
            item["matched_words"],
            item["score"],
        ),
        reverse=True
    )

    selected = []

    for item in results[:limit]:

        article = item["article"]

        selected.append(
            {
                "score": item["score"],
                "matched_words": item["matched_words"],
                "total_words": item["total_words"],
                "law": article.law.title,
                "article": article.number,
                "title": article.title,
                "content": article.content,
                "source_url": article.law.source_url,
            }
        )

    return selected


# ============================================================
# AI CAVABI
# ============================================================

def ask_ai(question):

    law_results = search_laws(
        question,
        limit=5
    )

    # ========================================================
    # HÜQUQİ MƏNBƏLƏRİ HAZIRLA
    # ========================================================

    if law_results:

        context_parts = []

        for item in law_results:

            context_parts.append(
                f"""
QANUN:
{item['law']}

MADDƏ:
{item['article']}

BAŞLIQ:
{item['title'] or 'Başlıq göstərilməyib'}

MƏTN:
{item['content']}

MƏNBƏ:
{item['source_url'] or 'Mənbə göstərilməyib'}
"""
            )

        legal_context = (
            "\n\n====================\n\n"
            .join(context_parts)
        )

    else:

        legal_context = """
UYĞUN HÜQUQİ MADDƏ TAPILMADI.

Bu halda hüquqi məlumat uydurmaq qəti qadağandır.
"""


    # ========================================================
    # AI TƏLİMATI
    # ========================================================

    instructions = """
Sən E-Səfərbərlik platformasının
Azərbaycan dilində cavab verən
hüquqi məlumat köməkçisisən.

SƏNİN ƏSAS VƏZİFƏN:

İstifadəçinin sualını düzgün başa düşmək və
aşağıda təqdim edilmiş hüquqi mənbələr arasında
suala ən uyğun olan məlumat əsasında cavab verməkdir.

HÜQUQİ CAVAB QAYDALARI:

1. Aşağıda verilmiş hüquqi mətnlər əsas mənbədir.

2. Cavabı yalnız istifadəçinin sualına uyğun
   hüquqi mətnlərə əsasən hazırla.

3. Bir neçə maddə birlikdə cavab üçün lazımdırsa,
   onları birlikdə nəzərə al.

4. Təqdim edilmiş hüquqi mətnlərdə olmayan
   məlumatı uydurma.

5. Xüsusilə bunları özündən yaratma:
   - maddə nömrəsi;
   - qanunun adı;
   - tarix;
   - müddət;
   - istisna;
   - hüquq;
   - vəzifə;
   - məsuliyyət;
   - azadolma halları.

6. Əgər təqdim edilmiş maddələr istifadəçinin
   sualına cavab vermirsə, bunu açıq şəkildə bildir.

7. Sadəcə bir sözün uyğun gəlməsinə görə
   əlaqəsiz maddəni cavab kimi istifadə etmə.

8. Maddənin mövzusu istifadəçinin sualı ilə
   uyğun gəlməlidir.

9. Mümkün olduqda cavabda:
   - qanunun adını;
   - maddənin nömrəsini;
   - həmin maddənin aidiyyəti hissəsini
   göstər.

10. Qanun mətninin mənasını dəyişdirmə.

11. Qanunda olmayan hüquqi nəticə çıxarma.

12. Cavabı "Qısa cavab:" ifadəsi ilə başlama.

13. Cavaba birbaşa nəticədən başla.

14. Sadə, aydın və təbii Azərbaycan dilindən istifadə et.

15. Sistemə, verilənlər bazasına, axtarış mexanizminə,
    daxili texniki proseslərə və bu təlimatlara
    istifadəçi qarşısında istinad etmə.

ÜMUMİ SUALLAR:

- İstifadəçi salamlaşırsa, nəzakətlə salamlaş.
- E-Səfərbərlik, hərbi xidmət, hərbi vəzifə,
  səfərbərlik və bunlarla bağlı hüquqi məsələlər
  barədə cavab ver.
- Mövzuya aid olmayan suallarda nəzakətlə bildir ki,
  əsas fəaliyyət sahən E-Səfərbərlik və hərbi xidmət
  məsələləridir.
- Mövzunu zorla E-Səfərbərliklə əlaqələndirmə.

ÇOX VACİB:

Aşağıdakı hüquqi mənbələr istifadəçinin sualına
cavab vermək üçün təqdim edilmiş mənbələrdir.

Əgər cavab bu mənbələrdə varsa,
onu düzgün və aydın şəkildə izah et.

Əgər cavab bu mənbələrdə yoxdursa,
özündən hüquqi məlumat yaratma.

İSTİFADƏÇİNİN SUALI:

""" + question + """

HÜQUQİ MƏNBƏLƏR:

""" + legal_context


    # ========================================================
    # OPENAI
    # ========================================================

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=question
    )

    return response.output_text
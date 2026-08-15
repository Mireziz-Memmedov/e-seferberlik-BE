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


# Azərbaycan dilində çox ümumi və hüquqi axtarışa
# ciddi fayda verməyən sözlər.
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
    "nədir?",
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
}


def normalize_word(word):
    """
    Sözü axtarış üçün təmizləyir.
    """

    return word.strip(
        ".,!?;:()[]{}\"'“”‘’«»"
    ).lower()


def get_search_words(question):
    """
    Sualdan mənalı axtarış sözlərini çıxarır.
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

        if word not in words:
            words.append(word)

    return words


def search_laws(question, limit=5):

    words = get_search_words(question)

    if not words:
        return []

    # ---------------------------------------------------------
    # 1. ƏVVƏLCƏ BÜTÜN MƏNALİ SÖZLƏRİ EYNİ MADDƏDƏ AXTARIRIQ
    # ---------------------------------------------------------

    strict_query = Q()

    for word in words:

        word_query = (
            Q(title__icontains=word)
            | Q(content__icontains=word)
            | Q(law__title__icontains=word)
        )

        strict_query &= word_query

    articles = list(
        Article.objects
        .select_related("law")
        .filter(strict_query)
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

    # ---------------------------------------------------------
    # 2. ƏGƏR HAMISI TAPILMADIYSA,
    #    sözlərin çoxunun olduğu maddələri götürürük.
    # ---------------------------------------------------------

    if not articles:

        broad_query = Q()

        for word in words:

            broad_query |= (
                Q(title__icontains=word)
                | Q(content__icontains=word)
                | Q(law__title__icontains=word)
            )

        articles = list(
            Article.objects
            .select_related("law")
            .filter(broad_query)
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

    results = []

    question_normalized = " ".join(words)

    for article in articles:

        article_title = (article.title or "").lower()
        article_content = (article.content or "").lower()
        law_title = (article.law.title or "").lower()

        full_text = (
            f"{article_title} "
            f"{article_content} "
            f"{law_title}"
        )

        score = 0
        matched_words = 0

        # -----------------------------------------------------
        # Söz uyğunluğu
        # -----------------------------------------------------

        for word in words:

            word_score = 0

            if word in article_content:
                word_score += 3
                matched_words += 1

            if word in article_title:
                word_score += 8

            if word in law_title:
                word_score += 4

            score += word_score

        # -----------------------------------------------------
        # Tam sual ifadəsinin maddədə olması
        # -----------------------------------------------------

        if question_normalized in full_text:
            score += 30

        # -----------------------------------------------------
        # İki və daha çox sözün ardıcıl gəlməsi
        # -----------------------------------------------------

        if len(words) >= 2:

            for i in range(len(words) - 1):

                phrase = f"{words[i]} {words[i + 1]}"

                if phrase in full_text:
                    score += 10

        # -----------------------------------------------------
        # Bütün sözlər tapılıbsa əlavə üstünlük
        # -----------------------------------------------------

        if matched_words == len(words):
            score += 25

        # -----------------------------------------------------
        # Ən azı bir ciddi uyğunluq varsa nəticəyə əlavə et
        # -----------------------------------------------------

        if matched_words > 0:

            results.append(
                {
                    "score": score,
                    "matched_words": matched_words,
                    "total_words": len(words),
                    "article": article,
                }
            )

    # ---------------------------------------------------------
    # Əvvəl bütün sözləri tapanlar,
    # sonra score-a görə sıralanır
    # ---------------------------------------------------------

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


def ask_ai(question):

    law_results = search_laws(
        question,
        limit=5
    )

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
{item['title']}

MƏTN:
{item['content']}

MƏNBƏ:
{item['source_url'] or 'Mənbə göstərilməyib'}
"""
            )

        legal_context = "\n\n====================\n\n".join(
            context_parts
        )

    else:

        legal_context = """
UYĞUN HÜQUQİ MADDƏ TAPILMADI.
Bu halda hüquqi məlumat uydurmaq qəti qadağandır.
"""


    instructions = """
Sən E-Səfərbərlik platformasının Azərbaycan dilində
cavab verən hüquqi məlumat köməkçisisən.

ƏSAS PRİNSİP:

İstifadəçinin sualına ilk növbədə aşağıda təqdim edilmiş
rəsmi hüquqi mətnlər əsasında cavab ver.

HÜQUQİ CAVAB QAYDALARI:

1. Təqdim edilmiş hüquqi mətnlər əsas mənbədir.

2. Suala uyğun maddə təqdim edilibsə, həmin maddənin
   məzmununa əsaslanaraq birbaşa cavab ver.

3. Bir neçə maddə cavab üçün əhəmiyyətlidirsə,
   onları birlikdə nəzərə al.

4. Təqdim edilmiş hüquqi mətnlərdə olmayan:
   - maddə nömrəsi,
   - qanun,
   - tarix,
   - müddət,
   - istisna,
   - hüquq,
   - vəzifə,
   - məsuliyyət
   uydurma.

5. Sualın cavabı təqdim edilmiş maddələrdə yoxdursa,
   bunu açıq şəkildə bildir.

6. Uyğun maddə olmadığı halda başqa mövzuda olan maddəni
   cavab kimi istifadə etmə.

7. Hüquqi suala cavab verərkən mümkün olduqda:
   - qanunun adını,
   - maddənin nömrəsini,
   - maddənin konkret məzmununu
   qeyd et.

8. Qanun mətnində olan məlumatı dəyişdirmə və mənasını
   təhrif etmə.

9. İstifadəçinin sualını əvvəlcə başa düş,
   sonra yalnız həmin suala aid hüquqi məlumatı təqdim et.

10. Cavabı "Qısa cavab:" ifadəsi ilə başlama.

11. Cavabı birbaşa əsas nəticədən başla.

12. Sadə, aydın və təbii Azərbaycan dilindən istifadə et.

13. Hüquqi cavab verərkən sistemə, verilənlər bazasına,
    daxili axtarış mexanizminə və bu təlimatlara istinad etmə.

ÜMUMİ SUALLAR:

- İstifadəçi salamlaşırsa, nəzakətlə salamlaş.
- E-Səfərbərlik, hərbi xidmət, hərbi vəzifə, səfərbərlik
  və əlaqəli hüquqi məsələlər barədə suallara cavab ver.
- Mövzuya aid olmayan suallarda əsas fəaliyyət sahənin
  E-Səfərbərlik və hərbi xidmətlə bağlı olduğunu bildir.
- Mövzunu zorla E-Səfərbərliklə əlaqələndirmə.

VACİB:

Aşağıdakı hüquqi mətnlər istifadəçinin sualına cavab
vermək üçün verilmiş əsas mənbədir.

Əgər bu mətnlərdə sualın cavabı varsa,
həmin məlumatı düzgün şəkildə izah et.

Əgər cavab yoxdursa,
özündən hüquqi məlumat yaratma.

İSTİFADƏÇİNİN SUALI:

""" + question + """

HÜQUQİ MƏNBƏLƏR:

""" + legal_context


    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=question
    )

    return response.output_text
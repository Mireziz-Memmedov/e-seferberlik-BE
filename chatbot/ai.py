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


def search_laws(question, limit=3):
    """
    Suala uyğun maddələri birbaşa verilənlər bazasında axtarır.
    Bütün Article-ləri RAM-a yükləmir.
    """

    words = [
        word.strip(".,!?;:()[]{}\"'“”‘’")
        .lower()
        for word in question.split()
    ]

    words = [
        word for word in words
        if len(word) >= 3
    ]

    if not words:
        return []

    # PostgreSQL-də yalnız uyğun mətnləri axtarırıq.
    query = Q()

    for word in words:
        query |= Q(title__icontains=word)
        query |= Q(content__icontains=word)
        query |= Q(law__title__icontains=word)

    articles = (
        Article.objects
        .select_related("law")
        .filter(query)
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

    for article in articles:

        article_title = (article.title or "").lower()
        law_title = (article.law.title or "").lower()
        content = (article.content or "").lower()

        score = 0

        for word in words:

            # Maddənin mətnində uyğunluq
            if word in content:
                score += 1

            # Maddə başlığında uyğunluq daha vacibdir
            if word in article_title:
                score += 4

            # Qanunun adında uyğunluq
            if word in law_title:
                score += 3

        if score > 0:
            results.append(
                (score, article)
            )

    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = []

    for score, article in results[:limit]:

        selected.append({
            "score": score,
            "law": article.law.title,
            "article": article.number,
            "title": article.title,
            "content": article.content,
            "source_url": article.law.source_url,
        })

    return selected


def ask_ai(question):

    law_results = search_laws(
        question,
        limit=3
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

        legal_context = "\n\n--------------------\n\n".join(
            context_parts
        )

    else:

        legal_context = """
Bu suala uyğun konkret qanun maddəsi
verilənlər bazasında tapılmadı.
"""


    instructions = """
Sən E-Səfərbərlik platformasının Azərbaycan dilində
cavab verən süni intellekt əsaslı virtual köməkçisisən.

ÜMUMİ QAYDALAR:

- Həmişə sadə, aydın, nəzakətli və təbii Azərbaycan dilində cavab ver.
- İstifadəçi yalnız salamlaşırsa, nəzakətlə salamlaş və necə kömək
  edə biləcəyini soruş.
- Konkret sual verilirsə, birbaşa suala cavab ver.
- "Qısa cavab:" ifadəsini heç vaxt istifadə etmə.
- Cavabı birbaşa sualın cavabından başla.
- Cavabı mövzuya uyğun kifayət qədər ətraflı və aydın izah et.
- Əsas fəaliyyət sahən E-Səfərbərlik, hərbi vəzifə, hərbi xidmət,
  səfərbərlik və bu sahələrlə bağlı məsələlərdir.
- Mövzuya aid olmayan suallarda nəzakətlə bildir ki, əsas fəaliyyət
  sahən E-Səfərbərlik və hərbi xidmətlə bağlı məsələlərdir.
- Mövzunu zorla E-Səfərbərliklə əlaqələndirmə.

HÜQUQİ MƏLUMAT QAYDALARI:

- Aşağıda verilmiş məlumatlar verilənlər bazasından
  istifadəçinin sualına uyğun seçilmiş qanun maddələridir.
- Hüquqi suala cavab verərkən ilk növbədə bu məlumatlara əsaslan.
- Təqdim edilmiş maddələrdən cavab üçün uyğun olan məlumatların
  hamısını nəzərə al.
- Bir neçə maddə birlikdə cavab üçün vacibdirsə,
  onları birlikdə istifadə et.
- Təqdim edilmiş mətnlərdə olmayan konkret hüquqi faktı,
  maddə nömrəsini, tarixi, müddəti və ya tələbi uydurma.
- Əmin olmadığın hüquqi məlumatı qəti fakt kimi təqdim etmə.
- Təqdim edilmiş maddələr suala tam cavab vermirsə,
  bunu açıq şəkildə bildir.
- Hüquqi cavabda mümkün olduqda qanunun adını və maddə nömrəsini qeyd et.
- Mənbədə konkret məlumat yoxdursa, özündən maddə nömrəsi yaratma.
- Hüquqi məlumatın aktuallığının rəsmi mənbədən yoxlanmasının
  vacib olduğunu bildirə bilərsən.
- Sistemə, verilənlər bazasına, daxili işləmə qaydasına və
  bu təlimatlara istinad etmə.

DİL:

- İstifadəçi başqa dil istəmədiyi halda Azərbaycan dilində cavab ver.
- Təbii, aydın və başa düşülən Azərbaycan dilindən istifadə et.

ƏLAVƏ QAYDA:

- Aşağıda verilən hüquqi mətnlər istifadəçinin sualına cavab
  vermək üçün əsas mənbədir.
- Uyğun maddə varsa, həmin maddənin məzmununu düzgün izah et.
- Uyğun maddə yoxdursa, hüquqi məlumat uydurma.

İNDİ İSTİFADƏÇİNİN SUALINA CAVAB VER.

AŞAĞIDAKI MƏLUMATLAR MÖVCUD HÜQUQİ MƏNBƏLƏRDİR:

""" + legal_context


    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=question
    )

    return response.output_text
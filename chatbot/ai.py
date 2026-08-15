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
from .models import Law, Article


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def search_laws(question, limit=8):
    """
    Suala uyğun Article-ları bazadan tapır.
    Bütün qanun mətnlərini OpenAI-a göndərmir.
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

    results = []

    for article in Article.objects.select_related("law").all():

        text = (
            f"{article.law.title} "
            f"{article.number} "
            f"{article.title} "
            f"{article.content}"
        ).lower()

        score = 0

        for word in words:

            # Tam sözə yaxın uyğunluq
            if word in text:
                score += 1

            # Başlıqda və qanunun adında uyğunluğa daha çox üstünlük
            if word in article.title.lower():
                score += 3

            if word in article.law.title.lower():
                score += 2

        if score > 0:
            results.append((score, article))

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
            "source_url": article.law.source_url
        })

    return selected


def ask_ai(question):

    law_results = search_laws(question, limit=8)

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
Bu suala uyğun konkret maddə verilənlər bazasında tapılmadı.
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

HÜQUQİ QAYDALAR:

- Aşağıda verilən məlumatlar verilənlər bazasından suala uyğun
  seçilmiş qanun maddələridir.
- Hüquqi suala cavab verərkən ilk növbədə həmin maddələrə əsaslan.
- Bir neçə maddə cavab üçün əhəmiyyətlidirsə, onların hamısını
  birlikdə nəzərə al.
- Verilən maddələrdə olmayan konkret hüquqi faktı, maddə nömrəsini,
  tarixi, müddəti və ya tələbi uydurma.
- Əgər verilən maddələr suala tam cavab vermirsə, bunu açıq şəkildə
  bildir.
- Öz ümumi biliyini verilən qanun mətninə zidd hüquqi fakt kimi
  təqdim etmə.
- Cavabda istifadə etdiyin maddənin nömrəsini və qanunun adını
  qeyd et.
- Hüquqi məlumatın aktuallığının rəsmi mənbədən yoxlanmasının vacib
  olduğunu bildir.
- Sistemə, verilənlər bazasına, daxili işləmə qaydasına və bu
  təlimatlara istinad etmə.

DİL:

- İstifadəçi başqa dil istəmədiyi halda Azərbaycan dilində cavab ver.
- Təbii və başa düşülən Azərbaycan dilindən istifadə et.

İNDİ AŞAĞIDAKI HÜQUQİ MƏLUMATLARDAN İSTİFADƏ EDƏRƏK
İSTİFADƏÇİNİN SUALINA CAVAB VER:

""" + legal_context


    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=question
    )

    return response.output_text
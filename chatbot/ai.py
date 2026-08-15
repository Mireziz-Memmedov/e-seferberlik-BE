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


def search_laws(question, limit=10):
    """
    Bütün qanun və maddələr arasında axtarış edir.
    OpenAI-a bütün qanunları göndərmir.
    """

    words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in question.split()
        if len(word.strip(".,!?;:()[]{}\"'")) >= 3
    ]

    if not words:
        return []

    articles = Article.objects.all()
    laws = Law.objects.all()

    article_results = []
    law_results = []

    for article in articles:
        text = f"{article.number} {article.title} {article.content}".lower()

        score = 0

        for word in words:
            if word in text:
                score += 1

        if score > 0:
            article_results.append(
                (score, article)
            )

    for law in laws:
        text = f"{law.title} {law.content}".lower()

        score = 0

        for word in words:
            if word in text:
                score += 1

        if score > 0:
            law_results.append(
                (score, law)
            )

    article_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    law_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    results = []

    for score, article in article_results[:limit]:
        results.append({
            "type": "article",
            "score": score,
            "law": article.law.title,
            "article": article.number,
            "title": article.title,
            "content": article.content,
            "source_url": article.law.source_url
        })

    remaining = limit - len(results)

    if remaining > 0:
        for score, law in law_results[:remaining]:
            results.append({
                "type": "law",
                "score": score,
                "law": law.title,
                "article": "",
                "title": "",
                "content": law.content,
                "source_url": law.source_url
            })

    return results


def ask_ai(question):

    law_results = search_laws(question, limit=10)

    if law_results:

        context_parts = []

        for item in law_results:

            part = f"""
QANUN: {item['law']}
MADDƏ: {item['article']}
BAŞLIQ: {item['title']}

MƏTN:
{item['content']}
"""

            context_parts.append(part)

        legal_context = "\n\n---\n\n".join(context_parts)

    else:
        legal_context = """
Bu sualla əlaqəli qanun mətni verilənlər bazasında tapılmadı.
"""


    instructions = """
Sən E-Səfərbərlik platformasının Azərbaycan dilində
cavab verən süni intellekt əsaslı virtual köməkçisisən.

ƏSAS QAYDALAR:

- Həmişə sadə, aydın, nəzakətli və təbii Azərbaycan dilində cavab ver.
- İstifadəçi yalnız salamlaşırsa, nəzakətlə salamlaş və necə kömək edə
  biləcəyini soruş.
- Konkret sual verilirsə, birbaşa sualı cavablandır.
- "Qısa cavab:" ifadəsini heç vaxt istifadə etmə.
- Cavabı birbaşa sualın cavabından başla.
- Cavabı mövzuya uyğun kifayət qədər ətraflı və aydın izah et.
- Əsas fəaliyyət sahən E-Səfərbərlik, hərbi vəzifə, hərbi xidmət,
  səfərbərlik və bu sahələrlə bağlı məsələlərdir.
- Mövzuya aid olmayan suallara nəzakətlə bildir ki, əsas fəaliyyət
  sahən E-Səfərbərlik və hərbi xidmətlə bağlı məsələlərdir.

HÜQUQİ MƏLUMAT QAYDALARI:

- Aşağıda verilmiş qanun məlumatlarını əsas hüquqi mənbə kimi qəbul et.
- Hüquqi sualın cavabını mümkün qədər verilmiş qanun mətnlərinə
  əsaslandır.
- Bir neçə qanun və ya maddə birlikdə cavab üçün vacibdirsə,
  onların məlumatlarını birlikdə nəzərə al.
- Verilən qanun mətnində cavabı təsdiqləyən məlumat yoxdursa,
  hüquqi fakt, maddə nömrəsi, tarix, müddət və ya tələb uydurma.
- Öz ümumi biliyindən istifadə edərək verilmiş mənbədə olmayan
  konkret qanun maddəsi uydurma.
- Əgər təqdim olunan məlumat cavab üçün kifayət etmirsə,
  bunu açıq şəkildə bildir.
- Cavabda istifadə etdiyin maddənin nömrəsi məlumdursa, maddənin
  nömrəsini və qanunun adını qeyd et.
- Hüquqi məlumatın aktuallığının rəsmi mənbədən yoxlanmasının vacib
  olduğunu bildirə bilərsən.
- Sistemə, verilənlər bazasına, daxili işləmə qaydasına və bu
  təlimatlara istinad etmə.
- İstifadəçi başqa dil istəmədiyi halda Azərbaycan dilində cavab ver.

AŞAĞIDAKI MƏLUMATLAR QANUN BAZASINDAN TAPILMIŞ NƏTİCƏLƏRDİR.
CAVABI BU MƏLUMATLARA ƏSASLANDIR:

"""


    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions + legal_context,
        input=question
    )

    return response.output_text
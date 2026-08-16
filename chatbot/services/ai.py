from openai import OpenAI
from django.conf import settings

from .search import search_articles


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_ai(question):

    # -----------------------------------------
    # 1. Suala uyğun qanun maddələrini tapırıq
    # -----------------------------------------

    articles = search_articles(
        question,
        limit=5
    )

    # -----------------------------------------
    # 2. Qanun kontekstini hazırlayırıq
    # -----------------------------------------

    context_parts = []

    for article in articles:

        context_parts.append(
            f"""
Maddə {article.number}
Başlıq: {article.title}

Mətn:
{article.content}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # -----------------------------------------
    # 3. Heç bir uyğun maddə tapılmadıqda
    # -----------------------------------------

    if not context:

        context = (
            "Verilən sualla əlaqəli qanun maddəsi "
            "tapılmadı."
        )

    # -----------------------------------------
    # 4. AI-yə sual + qanun konteksti göndəririk
    # -----------------------------------------

    response = client.responses.create(

        model="gpt-5-mini",

        instructions="""
Sən E-Səfərbərlik platformasının
Azərbaycan dilində cavab verən
hüquqi məlumat köməkçisisən.

ƏSAS QAYDALAR:

- Həmişə Azərbaycan dilində cavab ver.
- Sadə, aydın və təbii dildə yaz.
- Cavabı birbaşa sualın cavabından başla.
- "Qısa cavab:" ifadəsini istifadə etmə.
- Salamlaşma ilə konkret sualı qarışdırma.
- Konkret sual varsa, birbaşa suala cavab ver.

HÜQUQİ QAYDALAR:

- Sənə verilən QANUN KONTEKSTİ əsas mənbədir.
- Cavabı mümkün qədər yalnız verilən qanun maddələrinə əsasən hazırla.
- Kontekstdə olmayan maddə nömrəsi, tarix, müddət,
  tələb və ya hüquqi fakt uydurma.
- Cavab üçün kifayət qədər məlumat yoxdursa,
  bunu açıq şəkildə bildir.
- Qanun maddəsinə əsaslanırsansa, maddənin nömrəsini
  cavabda göstər.
- Qanun mətnini dəyişdirərək və ya mənasını təhrif
  edərək təqdim etmə.
- Hüquqi məsələlərdə qəti əmin olmadığın məlumatı
  qəti fakt kimi təqdim etmə.
- Hüquqi məlumatın aktual qanunvericiliklə yoxlanmasının
  vacib olduğunu lazım gəldikdə bildir.

MÖVZU:

- Əsas fəaliyyət sahən E-Səfərbərlik,
  hərbi vəzifə, hərbi xidmət,
  səfərbərlik və əlaqəli qanunvericilikdir.
- Mövzu bu sahəyə aid deyilsə, bunu nəzakətlə bildir.

SİSTEM:

- Verilən daxili kontekstdən və sistemin işləmə
  mexanizmindən istifadəçiyə danışma.
- "Mənə verilən məlumatlara görə" kimi ifadələrdən
  mümkün qədər istifadə etmə.
""",

        input=f"""
İSTİFADƏÇİNİN SUALI:

{question}


QANUN KONTEKSTİ:

{context}
"""
    )

    return response.output_text
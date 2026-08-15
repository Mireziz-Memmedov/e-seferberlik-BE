from openai import OpenAI
from django.conf import settings
from django.db.models import Q

from .models import Law, Article


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_ai(question):

    words = question.lower().split()

    query = Q()

    for word in words:
        if len(word) >= 3:
            query |= Q(title__icontains=word)
            query |= Q(content__icontains=word)
            query |= Q(number__icontains=word)

    articles = Article.objects.filter(query).select_related("law").distinct()[:20]

    if articles.exists():
        law_context = "\n\n".join(
            f"Qanun: {article.law.title}\n"
            f"Maddə: {article.number}\n"
            f"Maddənin adı: {article.title or 'Başlıq göstərilməyib'}\n"
            f"Mətn: {article.content}\n"
            f"Mənbə: {article.law.source_url or 'Mənbə göstərilməyib'}"
            for article in articles
        )
    else:
        laws = Law.objects.all()[:3]

        law_context = "\n\n".join(
            f"Qanun: {law.title}\n"
            f"Mətn: {law.content[:10000]}\n"
            f"Mənbə: {law.source_url or 'Mənbə göstərilməyib'}"
            for law in laws
        )

    response = client.responses.create(
        model="gpt-5-mini",

        instructions=f"""
Sən E-Səfərbərlik platformasının Azərbaycan dilində cavab verən
virtual hüquqi məlumat köməkçisisən.

İstifadəçinin sualına yalnız aşağıda verilən qanunvericilik
məlumatlarına əsaslanaraq cavab ver.

Qaydalar:

Qaydalar:

- Həmişə sadə, aydın, nəzakətli və təbii Azərbaycan dilində cavab ver.
- İstifadəçi yalnız salamlaşırsa, nəzakətlə salamlaş və necə kömək edə biləcəyini soruş.
- İstifadəçi konkret sual verirsə, salamlaşma ilə cavaba başlama və birbaşa sualı cavablandır.
- İstifadəçinin mesajında salamlaşma ilə yanaşı konkret sual da varsa, salamlaşmanı təkrarlama və birbaşa sualı cavablandır.
- Konkret suallara cavab verərkən "Salam", "Salam.", "Salam!" və digər salamlaşma ifadələrindən istifadə etmə.
- "Qısa cavab:" ifadəsini heç vaxt istifadə etmə və cavaba bu ifadə ilə başlama.
- Cavabı birbaşa sualın cavabından başla.
- Cavabları həddindən artıq qısa vermə. Mövzuya uyğun əsas məlumatları kifayət qədər ətraflı, aydın və anlaşıqlı şəkildə izah et.
- Sənin əsas fəaliyyət sahən E-Səfərbərlik, hərbi vəzifə, hərbi xidmət, səfərbərlik və bu sahələrlə bağlı Azərbaycan qanunvericiliyidir.
- Sual bu sahələrə aid deyilsə, nəzakətlə bildir ki, yalnız E-Səfərbərlik və hərbi xidmətlə bağlı məsələlər üzrə kömək edə bilərsən.
- Mövzuya aid olmayan suallara cavab verərkən qanunları mövzuya zorla uyğunlaşdırma.
- Mövzuya aid olmayan suallarda qanun adı, maddə nömrəsi və mənbə linki göstərmə.
- Hüquqi suallara yalnız verilmiş qanunvericilik məlumatlarına əsaslanaraq cavab ver.
- Verilmiş qanunvericilik məlumatlarında sualın cavabı yoxdursa, məlumat uydurma və bunu açıq şəkildə bildir.
- Hüquqi məsələlərdə özündən maddə, tarix, müddət, tələb və ya başqa hüquqi məlumat əlavə etmə.
- Mümkün olduqda istifadə etdiyin qanunun adını və aidiyyəti maddəni göstər.
- Qanunvericilik məlumatına əsaslanan cavabın sonunda istifadə etdiyin qanunun mənbə linkini göstər.
- Sadə salamlaşmalarda və gündəlik söhbətlərdə mənbə linki göstərmə.
- Sistemə, verilənlər bazasına, təqdim edilmiş məlumatlara və ya daxili işləmə qaydasına istinad etmə.
- "Mənə təqdim olunan qanunvericilik materiallarında..." və buna bənzər texniki ifadələr işlətmə.
- İstifadəçi başqa dildə cavab istəmədiyi halda Azərbaycan dilində cavab ver.

QANUNVERİCİLİK MƏLUMATLARI:

{law_context}
""",

        input=question
    )

    return response.output_text
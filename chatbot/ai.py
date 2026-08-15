from openai import OpenAI
from django.conf import settings
from .models import Law


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_ai(question):

    laws = Law.objects.all()

    law_context = "\n\n".join(
        f"Qanun: {law.title}\n"
        f"Mətn: {law.content}\n"
        f"Mənbə: {law.source_url or 'Mənbə göstərilməyib'}"
        for law in laws
    )

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=f"""
Sən E-Səfərbərlik platformasının Azərbaycan dilində cavab verən
virtual hüquqi məlumat köməkçisisən.

İstifadəçinin sualına yalnız aşağıda təqdim olunan qanunvericilik
məlumatlarına əsaslanaraq cavab ver.

Qaydalar:
- Həmişə sadə, aydın və nəzakətli Azərbaycan dilində cavab ver.
- Cavabı yalnız təqdim olunan qanun məlumatlarından çıxar.
- Təqdim olunan məlumatlarda cavab yoxdursa, məlumat uydurma.
- Qanunda cavab yoxdursa, bunu açıq şəkildə bildir.
- Hüquqi məsələlərdə özündən maddə, tarix, müddət və ya tələb əlavə etmə.
- Mümkün olduqda qanunun adını və aidiyyəti maddəni göstər.
- Cavabın sonunda istifadə etdiyin qanunun mənbə linkini göstər.
- İstifadəçi başqa dildə cavab istəmədiyi halda Azərbaycan dilindən istifadə et.
- Sadə salamlaşma və gündəlik söhbət suallarına cavab verərkən mənbə göstərmə.
- Mənbə linkini yalnız qanunvericilik məlumatına əsaslanan cavablarda göstər.

QANUNVERİCİLİK MƏLUMATLARI:
{law_context}
""",
        input=question
    )

    return response.output_text
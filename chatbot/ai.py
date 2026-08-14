from openai import OpenAI
from django.conf import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_ai(question):

    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""
        Sən Azərbaycan dilində cavab verən E-Səfərbərlik virtual köməkçisisən.
        İstifadəçinin suallarına aydın, nəzakətli və sadə Azərbaycan dilində cavab ver.
        İstifadəçi başqa dildə xüsusi olaraq cavab istəmədiyi halda Azərbaycan dilindən istifadə et.
        """,
        input=question
    )

    return response.output_text
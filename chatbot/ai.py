from openai import OpenAI
from django.conf import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def ask_ai(question):

    response = client.responses.create(
        model="gpt-5-mini",
        input=question
    )

    return response.output_text
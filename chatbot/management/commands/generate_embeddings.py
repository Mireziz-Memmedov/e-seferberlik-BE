from django.core.management.base import BaseCommand

from openai import OpenAI
from django.conf import settings

from chatbot.models import Article


class Command(BaseCommand):
    help = "Qanun maddələri üçün OpenAI embedding yaradır"

    def handle(self, *args, **options):

        client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        articles = Article.objects.all()

        total = articles.count()

        if total == 0:
            self.stdout.write(
                self.style.WARNING(
                    "Bazasında heç bir Article yoxdur."
                )
            )
            return

        self.stdout.write(
            f"{total} maddə üçün embedding yaradılır..."
        )

        updated_count = 0

        for article in articles:

            text = f"""
QANUN:
{article.law.title}

MADDƏ:
{article.number}

BAŞLIQ:
{article.title}

MƏTN:
{article.content}
""".strip()

            try:

                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )

                article.embedding = response.data[0].embedding

                article.save(
                    update_fields=["embedding"]
                )

                updated_count += 1

                self.stdout.write(
                    f"Maddə {article.number} — embedding yaradıldı."
                )

            except Exception as error:

                self.stdout.write(
                    self.style.ERROR(
                        f"Maddə {article.number} üçün xəta: {error}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tamamlandı. {updated_count}/{total} maddəyə embedding yazıldı."
            )
        )
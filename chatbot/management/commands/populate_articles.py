import re

from django.core.management.base import BaseCommand
from chatbot.models import Law, Article


class Command(BaseCommand):
    help = "Law mətnlərindən Article-ları avtomatik yaradır"

    def handle(self, *args, **kwargs):

        for law in Law.objects.all():

            if Article.objects.filter(law=law).exists():
                self.stdout.write(
                    f"{law.title} → artıq var, keçildi."
                )
                continue

            matches = re.findall(
                r'(?ms)^Maddə\s+(\d+)\.\s*(.*?)(?=^Maddə\s+\d+\.|\Z)',
                law.content
            )

            articles = []

            for number, content in matches:

                content = content.strip()
                lines = content.splitlines()

                title = ""

                if lines:
                    title = lines[0].strip()

                articles.append(
                    Article(
                        law=law,
                        number=number,
                        title=title,
                        content=content
                    )
                )

            Article.objects.bulk_create(articles)

            self.stdout.write(
                f"{law.title} → {len(articles)} maddə yaradıldı."
            )
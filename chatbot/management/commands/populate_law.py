import re

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError

from chatbot.models import Law, Article


LAW_TITLE = (
    "Hərbi vəzifə və hərbi xidmət haqqında "
    "— AZƏRBAYCAN RESPUBLİKASININ QANUNU"
)

SOURCE_URL = "https://frameworks.e-qanun.az/23/f_23021.html"


class Command(BaseCommand):

    help = "Hərbi vəzifə və hərbi xidmət haqqında qanunu import edir"

    def handle(self, *args, **options):

        self.stdout.write(
            "Rəsmi qanun mətni götürülür..."
        )

        # -----------------------------------------
        # 1. Rəsmi səhifədən məlumatı götürürük
        # -----------------------------------------

        try:
            response = requests.get(
                SOURCE_URL,
                timeout=30,
                headers={
                    "User-Agent": "E-Sefarberlik-Law-Bot/1.0"
                }
            )

            response.raise_for_status()

        except requests.RequestException as error:

            raise CommandError(
                f"Qanun mənbəyinə qoşulmaq mümkün olmadı: {error}"
            )

        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text(
            "\n",
            strip=True
        )

        # -----------------------------------------
        # 2. Qanunun əsas mətninin başlanğıcı
        # -----------------------------------------

        start_marker = "Maddə 1."

        start_index = text.find(
            start_marker
        )

        if start_index == -1:

            raise CommandError(
                "Qanunun 'Maddə 1.' hissəsi tapılmadı."
            )

        text = text[start_index:]

        # -----------------------------------------
        # 3. Dəyişiklik siyahılarından əvvəl
        #    əsas qanun mətnini saxlayırıq
        # -----------------------------------------

        end_markers = [
            "İSTİFADƏ OLUNMUŞ MƏNBƏ SƏNƏDLƏRİNİN SİYAHISI",
            "QANUNA EDİLMİŞ DƏYİŞİKLİK VƏ ƏLAVƏLƏRİN SİYAHISI",
        ]

        end_indexes = []

        for marker in end_markers:

            index = text.find(marker)

            if index != -1:
                end_indexes.append(index)

        if end_indexes:

            text = text[
                :min(end_indexes)
            ]

        # -----------------------------------------
        # 4. Artıq boş sətirləri təmizləyirik
        # -----------------------------------------

        text = re.sub(
            r"\n{2,}",
            "\n\n",
            text
        ).strip()

        # -----------------------------------------
        # 5. Maddələri tapırıq
        # -----------------------------------------

        article_pattern = re.compile(
            r"(?m)^Maddə\s+(\d+(?:-\d+)?)\.\s*(.*?)\s*$"
        )

        matches = list(
            article_pattern.finditer(text)
        )

        if not matches:

            raise CommandError(
                "Heç bir maddə tapılmadı."
            )

        # -----------------------------------------
        # 6. Law obyektini yaradırıq / tapırıq
        # -----------------------------------------

        law, created = Law.objects.get_or_create(
            title=LAW_TITLE,
            defaults={
                "content": text,
                "source_url": SOURCE_URL,
            }
        )

        if not created:

            law.content = text
            law.source_url = SOURCE_URL

            law.save(
                update_fields=[
                    "content",
                    "source_url",
                ]
            )

        # -----------------------------------------
        # 7. Köhnə Article-ləri tam təmizləyirik
        # -----------------------------------------

        Article.objects.filter(
            law=law
        ).delete()

        # -----------------------------------------
        # 8. Yeni Article-ləri yaradırıq
        # -----------------------------------------

        created_count = 0

        seen_numbers = set()

        for index, match in enumerate(matches):

            number = match.group(1).strip()

            title = match.group(2).strip()

            # -------------------------------------
            # Eyni maddə nömrəsi artıq tapılıbsa,
            # ikinci dəfə yaratmırıq
            # -------------------------------------

            if number in seen_numbers:
                continue

            seen_numbers.add(number)

            # -------------------------------------
            # Maddənin content hissəsinin başlanğıcı
            # -------------------------------------

            content_start = match.end()

            # -------------------------------------
            # Növbəti maddənin başlanğıcını tapırıq
            # -------------------------------------

            if index + 1 < len(matches):

                content_end = matches[
                    index + 1
                ].start()

            else:

                content_end = len(text)

            content = text[
                content_start:content_end
            ].strip()

            # -------------------------------------
            # Boş content varsa keçirik
            # -------------------------------------

            if not content:
                continue

            # -------------------------------------
            # Article yaradırıq
            # -------------------------------------

            Article.objects.create(
                law=law,
                number=number,
                title=title,
                content=content,
            )

            created_count += 1

        # -----------------------------------------
        # 9. Nəticə
        # -----------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                f"Import tamamlandı. "
                f"{created_count} maddə yaradıldı."
            )
        )
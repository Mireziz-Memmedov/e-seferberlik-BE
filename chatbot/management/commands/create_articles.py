import re

from django.core.management.base import BaseCommand

from chatbot.models import Law, Article


class Command(BaseCommand):
    help = "Law mətnlərindən Article obyektləri yaradır"

    def handle(self, *args, **options):

        laws = Law.objects.all()

        if not laws.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Bazasında heç bir Law yoxdur."
                )
            )
            return

        total_created = 0

        for law in laws:

            self.stdout.write(
                f"\nEmal olunur: {law.title}"
            )

            text = law.content.strip()

            if not text:
                self.stdout.write(
                    self.style.WARNING(
                        "Qanunun content hissəsi boşdur."
                    )
                )
                continue

            # ==================================================
            # 1. MADDƏ FORMATINI YOXLA
            # ==================================================

            article_pattern = re.compile(
                r"(?m)^\s*Maddə\s+"
                r"(\d+(?:-\d+)?)\.\s*(.*)$"
            )

            article_matches = list(
                article_pattern.finditer(text)
            )

            # ==================================================
            # 2. ƏSASNAMƏ ÜÇÜN SADƏ NÖMRƏ FORMATINI YOXLA
            #
            # 1. Mətn...
            # 2. Mətn...
            # 3. Mətn...
            #
            # ==================================================

            simple_pattern = re.compile(
                r"(?m)^\s*(\d+(?:\.\d+)?)\.\s+(.+)$"
            )

            simple_matches = list(
                simple_pattern.finditer(text)
            )

            # ==================================================
            # 3. HANSI FORMAT İSTİFADƏ OLUNACAQ?
            # ==================================================

            if article_matches:

                matches = article_matches
                format_type = "article"

            elif simple_matches:

                matches = simple_matches
                format_type = "simple"

            else:

                self.stdout.write(
                    self.style.WARNING(
                        "Maddə və ya nömrələnmiş bənd tapılmadı."
                    )
                )

                continue

            # ==================================================
            # 4. BU QANUNUN KÖHNƏ ARTICLE-LARINI SİL
            # ==================================================

            Article.objects.filter(
                law=law
            ).delete()

            created_count = 0

            seen_numbers = set()

            # ==================================================
            # 5. ARTICLE-LARI YARAT
            # ==================================================

            for index, match in enumerate(matches):

                number = match.group(1).strip()

                if number in seen_numbers:
                    continue

                seen_numbers.add(number)

                # ----------------------------------------------
                # Maddə formatı
                # ----------------------------------------------

                if format_type == "article":

                    title = match.group(2).strip()

                    content_start = match.end()

                    if index + 1 < len(matches):

                        content_end = matches[
                            index + 1
                        ].start()

                    else:

                        content_end = len(text)

                    content = text[
                        content_start:content_end
                    ].strip()

                # ----------------------------------------------
                # Sadə nömrəli format
                # ----------------------------------------------

                else:

                    title = ""

                    content_start = match.start()

                    if index + 1 < len(matches):

                        content_end = matches[
                            index + 1
                        ].start()

                    else:

                        content_end = len(text)

                    content = text[
                        content_start:content_end
                    ].strip()

                # ----------------------------------------------
                # Boş content
                # ----------------------------------------------

                if not content:
                    continue

                # ----------------------------------------------
                # Article yarat
                # ----------------------------------------------

                Article.objects.create(
                    law=law,
                    number=number,
                    title=title,
                    content=content,
                )

                created_count += 1

            total_created += created_count

            self.stdout.write(
                self.style.SUCCESS(
                    f"{created_count} Article yaradıldı."
                )
            )

        # ======================================================
        # NƏTİCƏ
        # ======================================================

        self.stdout.write(
            self.style.SUCCESS(
                f"\nÜmumi yaradılan Article sayı: "
                f"{total_created}"
            )
        )
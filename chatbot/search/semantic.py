# import re
# from typing import List, Dict, Any
# from django.conf import settings
# from django.db.models import Q, QuerySet
# from openai import OpenAI
# from pgvector.django import CosineDistance

# from chatbot.models import Article

# # OpenAI Klientinin inisializasiyası
# client = OpenAI(api_key=settings.OPENAI_API_KEY)
# EMBEDDING_MODEL = "text-embedding-3-small"


# def normalize_input(text: str) -> str:
#     """İstifadəçi sorğusunu təmizləyir və standart formaya gətirir."""
#     text = text.lower().strip()
#     return re.sub(r'[^\w\s\.]', '', text)


# def get_embedding(text: str) -> List[float]:
#     """OpenAI API vasitəsilə 1536-ölçülü vector embedding yaradır."""
#     clean_text = text.strip()
#     if not clean_text:
#         return []

#     response = client.embeddings.create(
#         model=EMBEDDING_MODEL,
#         input=clean_text[:12000],
#     )
#     return response.data[0].embedding


# def find_dataset_match(query_norm: str, dataset: List[Dict[Any, Any]]) -> Dict[str, Any]:
#     """
#     İstifadəçinin sorğusunu datasetdəki `normalized` və `phrases`
#     bölmələri ilə üst-üstə salaraq uyğun intent/keyword metadata-nı çıxarır.
#     """
#     # 1. Tam bərabərlik (Exact Match)
#     for item in dataset:
#         if item['normalized'] == query_norm:
#             return item

#     # 2. Fraza əsaslı uyğunluq (Phrase Matching)
#     for item in dataset:
#         for phrase in item.get('phrases', []):
#             if phrase in query_norm:
#                 return item

#     return {}


# def hybrid_search(user_query: str, dataset: List[Dict[str, Any]], limit: int = 5) -> QuerySet:
#     """
#     Dataset verilənlərindən istifadə edərək 3 pilləli axtarış icra edir:
#     1. Maddə Nömrəsi vasitəsilə dəqiq axtarış
#     2. Pgvector vasitəsilə Cosine Distance (Semantik Vektor Axtarışı)
#     3. Expanded Keywords əsasında Fuzzy Filter (Fallback)
#     """
#     query_norm = normalize_input(user_query)
#     matched_meta = find_dataset_match(query_norm, dataset)

#     # =========================================================
#     # 1-Cİ MƏRHƏLƏ: Dəqiq Maddə Nömrəsi Axtarışı (Article Matching)
#     # =========================================================
#     article_numbers = matched_meta.get('article_numbers', [])

#     # Əgər dataset-də tapılmadısa, mətnin içindən regex ilə maddə nömrəsi axtarırıq (məs: 46.1.3)
#     if not article_numbers:
#         article_numbers = re.findall(r'\b\d+(?:\.\d+)*\b', query_norm)

#     if article_numbers:
#         exact_qs = Article.objects.filter(article_number__in=article_numbers)
#         if exact_qs.exists():
#             return exact_qs[:limit]

#     # =========================================================
#     # 2-Cİ MƏRHƏLƏ: Semantik Axtarış (PGVector + OpenAI Embeddings)
#     # =========================================================
#     query_vector = get_embedding(user_query)

#     if query_vector:
#         # Distance Threshold: 0.40-dan böyük olanlar semantik olaraq uzaq sayılır.
#         semantic_qs = (
#             Article.objects.exclude(embedding__isnull=True)
#             .annotate(distance=CosineDistance("embedding", query_vector))
#             .filter(distance__lt=0.40)
#             .order_by("distance")[:limit]
#         )

#         if semantic_qs.exists():
#             return semantic_qs

#     # =========================================================
#     # 3-CÜ MƏRHƏLƏ: Açar Sözlər Əsasında Fallback (Fuzzy Keyword Search)
#     # =========================================================
#     # Dataset-dən genişləndirilmiş açar sözləri (expanded_keywords) götürürük
#     search_keywords = matched_meta.get('expanded_keywords') or matched_meta.get('keywords', [])

#     if not search_keywords:
#         # Dataset tutuşmazsa, sorğunun öz sözlərini götürürük
#         search_keywords = [w for w in query_norm.split() if len(w) > 2]

#     if not search_keywords:
#         return Article.objects.none()

#     keyword_query = Q()
#     for kw in search_keywords:
#         keyword_query |= Q(title__icontains=kw) | Q(content__icontains=kw)

#     return Article.objects.filter(keyword_query).distinct()[:limit]
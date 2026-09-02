# import re
# from typing import List

# from django.conf import settings
# from django.db.models import QuerySet
# from openai import OpenAI
# from pgvector.django import CosineDistance

# from chatbot.models import Article


# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )

# EMBEDDING_MODEL = "text-embedding-3-small"

# SEMANTIC_LIMIT = 20
# MAX_EMBEDDING_INPUT = 12000
# MAX_DISTANCE = 0.60


# def get_embedding(text: str) -> List[float]:
#     if not isinstance(text, str):
#         return []

#     text = text.strip()

#     if not text:
#         return []

#     response = client.embeddings.create(
#         model=EMBEDDING_MODEL,
#         input=text[:MAX_EMBEDDING_INPUT],
#     )

#     return response.data[0].embedding


# def hybrid_search(
#     user_query: str,
#     limit: int = SEMANTIC_LIMIT,
# ) -> list[dict]:

#     if not isinstance(user_query, str):
#         return []

#     user_query = user_query.strip()

#     if not user_query:
#         return []

#     query_vector = get_embedding(user_query)

#     if not query_vector:
#         return []

#     queryset = (
#         Article.objects
#         .exclude(embedding__isnull=True)
#         .annotate(
#             distance=CosineDistance(
#                 "embedding",
#                 query_vector,
#             )
#         )
#         .filter(
#             distance__lt=MAX_DISTANCE
#         )
#         .order_by("distance")[:limit]
#     )

#     return [
#         {
#             "article": article,
#             "distance": float(article.distance),
#         }
#         for article in queryset
#     ]
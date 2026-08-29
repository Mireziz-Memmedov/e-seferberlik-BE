
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase

from .services.search import (
    normalize_text,
    tokenize,
    get_keywords,
    detect_intents,
    detect_question_type,
    analyze_query,
    merge_candidates,
    rerank_candidates,
)


class SearchLogicTests(SimpleTestCase):

    # =====================================================
    # NORMALIZE
    # =====================================================

    def test_normalize_text(self):
        result = normalize_text(
            "Mənim Ailə Vəziyyətim"
        )

        self.assertEqual(
            result,
            "menim aile veziyyetim"
        )

    # =====================================================
    # TOKENIZE
    # =====================================================

    def test_tokenize(self):
        result = tokenize(
            "Ailə vəziyyətinə görə kimlər azaddır?"
        )

        self.assertIn("aile", result)
        self.assertIn("veziyyetine", result)
        self.assertIn("gore", result)

    # =====================================================
    # KEYWORDS
    # =====================================================

    def test_keywords(self):
        result = get_keywords(
            "Ailə vəziyyətinə görə kimlər toplanışdan azaddır?"
        )

        self.assertIn(
            "aile",
            result
        )

        self.assertIn(
            "toplanisdan",
            result
        )

        self.assertNotIn(
            "kimler",
            result
        )

        self.assertNotIn(
            "gore",
            result
        )

    # =====================================================
    # INTENTS
    # =====================================================

    def test_detect_intents(self):

        result = detect_intents(
            "Ailə vəziyyətinə görə toplanışdan kimlər azaddır?"
        )

        self.assertIn(
            "aile",
            result
        )

        self.assertIn(
            "toplanis",
            result
        )

        self.assertIn(
            "azadetme",
            result
        )

    # =====================================================
    # QUESTION TYPE
    # =====================================================

    def test_question_type(self):

        intents = {
            "toplanis",
            "ehtiyat",
            "aile",
        }

        result = detect_question_type(
            intents
        )

        self.assertEqual(
            result,
            "toplanis_ehtiyat_aile"
        )

    # =====================================================
    # QUERY ANALYSIS
    # =====================================================

    def test_analyze_query(self):

        result = analyze_query(
            "3 uşağı olan ehtiyatda olan şəxs "
            "toplanışdan azaddır?"
        )

        self.assertIn(
            "aile",
            result["intents"]
        )

        self.assertIn(
            "ehtiyat",
            result["intents"]
        )

        self.assertIn(
            "toplanis",
            result["intents"]
        )

        self.assertIn(
            "azadetme",
            result["intents"]
        )

        self.assertIn(
            "3",
            result["numbers"]
        )

    # =====================================================
    # MERGE CANDIDATES
    # =====================================================

    def test_merge_candidates(self):

        article = MagicMock()

        article.id = 1

        result = merge_candidates(

            [
                {
                    "article": article,
                    "semantic_score": 0.42,
                    "sources": {"semantic"},
                }
            ],

            [
                {
                    "article": article,
                    "semantic_score": 0.0,
                    "sources": {"keyword"},
                }
            ],
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["semantic_score"],
            0.42
        )

        self.assertEqual(
            result[0]["sources"],
            {
                "semantic",
                "keyword",
            }
        )

    # =====================================================
    # RERANK
    # =====================================================

    def test_rerank(self):

        article1 = MagicMock()

        article1.id = 1

        article1.title = (
            "Toplanışlardan azadetmə"
        )

        article1.content = (
            "Ailə vəziyyətinə görə bəzi şəxslər "
            "toplanışlardan azad edilirlər."
        )

        article2 = MagicMock()

        article2.id = 2

        article2.title = (
            "Hərbi xidmət"
        )

        article2.content = (
            "Hərbi xidmət haqqında "
            "ümumi müddəalar."
        )

        candidates = [

            {
                "article": article1,
                "semantic_score": 0.40,
                "sources": {
                    "semantic",
                    "keyword",
                },
            },

            {
                "article": article2,
                "semantic_score": 0.35,
                "sources": {
                    "semantic",
                },
            },

        ]

        analysis = analyze_query(
            "Ailə vəziyyətinə görə "
            "toplanışdan kimlər azaddır?"
        )

        ranked = rerank_candidates(
            candidates,
            analysis
        )

        self.assertEqual(
            ranked[0]["article"].id,
            1
        )

    # =====================================================
    # SEARCH WITHOUT DATABASE
    # =====================================================

    @patch(
        "chatbot.services.search.semantic_search"
    )
    @patch(
        "chatbot.services.search.keyword_search"
    )
    @patch(
        "chatbot.services.search.exact_article_search"
    )
    def test_search_articles_without_database(
        self,
        mock_exact,
        mock_keyword,
        mock_semantic,
    ):

        mock_exact.return_value = []

        mock_keyword.return_value = []

        mock_semantic.return_value = []

        from .services.search import (
            search_articles
        )

        result = search_articles(
            "Ailə vəziyyətinə görə "
            "kimlər toplanışdan azaddır?"
        )

        self.assertEqual(
            result,
            []
        )

        mock_exact.assert_called_once()

        mock_semantic.assert_called_once()

        mock_keyword.assert_called_once()



import unittest

from recommender.service import get_recommendations


class TestRecommendationService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Загружаем каталог и TF-IDF один раз
        cls.cold_start = get_recommendations({})
        cls.personalized = get_recommendations({
            "goal": "Как увеличить продажи и привлечь клиентов",
            "industry": "красота",
            "preferred_format": "article",
        })

    def test_cold_start_mode(self):
        self.assertEqual(
            self.cold_start["mode"],
            "cold_start"
        )

    def test_personalized_mode(self):
        self.assertEqual(
            self.personalized["mode"],
            "personalized"
        )

    def test_recommendations_count(self):
        self.assertEqual(self.cold_start["total"], 5)
        self.assertEqual(self.personalized["total"], 5)

    def test_required_fields(self):
        required = {
            "material_id",
            "material_type",
            "title",
            "slug",
            "payment_status",
            "score",
            "similarity",
            "reasons",
            "next_step",
        }

        for response in (
            self.cold_start,
            self.personalized,
        ):
            for material in response["recommendations"]:
                self.assertTrue(
                    required.issubset(material.keys())
                )

    def test_unique_materials(self):
        for response in (
            self.cold_start,
            self.personalized,
        ):
            keys = [
                (m["material_type"], m["material_id"])
                for m in response["recommendations"]
            ]

            self.assertEqual(len(keys), len(set(keys)))

    def test_cold_start_scores(self):
        for material in self.cold_start["recommendations"]:
            self.assertIsNone(material["score"])
            self.assertIsNone(material["similarity"])

    def test_personalized_scores(self):
        for material in self.personalized["recommendations"]:
            self.assertGreaterEqual(
                material["similarity"], 0
            )
            self.assertGreaterEqual(
                material["score"],
                material["similarity"]
            )

    def test_invalid_top_k(self):
        for invalid in (0, -1, 21, "5", True):
            with self.subTest(top_k=invalid):
                with self.assertRaises(ValueError):
                    get_recommendations({}, top_k=invalid)

    def test_partial_profile(self):
        response = get_recommendations({
            "goal": "Как открыть интернет-магазин"
        })

        self.assertEqual(response["mode"], "personalized")
        self.assertGreater(response["total"], 0)


if __name__ == "__main__":
    unittest.main()

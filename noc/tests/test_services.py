from django.test import TestCase
from unittest.mock import patch

from ..services import AbcApi


class ABCAPITestCase(TestCase):
    @patch("l3abc.services.AbcApi._fetch")
    def test_fetch_services(self, abc_api_mock):
        abc_api_mock.return_value = [
            [
                {
                    "id": 1059,
                    "parent": {
                        "id": 24471,
                        "slug": "acs",
                        "name": {"ru": "Аналитика Поиска", "en": "Search Analytics"},
                        "parent": 31752,
                    },
                    "slug": "mstand",
                },
                {
                    "id": 1060,
                    "parent": {
                        "id": 336,
                        "slug": "so",
                        "name": {"ru": "Спамооборона", "en": "Spamooborona"},
                        "parent": 871,
                    },
                    "slug": "proverkaform",
                },
            ],
        ]
        abc_api = AbcApi("https://fake-url.test", "not-a-token")
        services = list(abc_api.fetch_services())
        self.assertEqual(len(services), 2)
        self.assertEqual(services[0].slug, "mstand")
        self.assertEqual(services[1].id, 1060)
        self.assertEqual(services[1].parent, 336)

        abc_api_mock.return_value = [
            [
                {
                    "id": 1059,
                    "parent": None,
                    "slug": "mstand",
                },
            ],
        ]
        services = list(abc_api.fetch_services())
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].slug, "mstand")
        self.assertIsNone(services[0].parent)

        abc_api_mock.return_value = [
            [
                {
                    "id": 1059,
                    "parent": None,
                    "slug": "mstand",
                },
                {
                    "id": 1100,
                    "parent": None,
                    "slug": "some",
                },
            ],
            [
                {
                    "id": 998,
                    "parent": None,
                    "slug": "other",
                },
            ],
        ]
        services = list(abc_api.fetch_services())
        self.assertEqual(len(services), 3)
        self.assertEqual(services[2].slug, "other")
        self.assertIsNone(services[1].parent)

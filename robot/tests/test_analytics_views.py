import robot.smelter.backend.tests.conftest  # noqa
import robot.smelter.backend.tests.stub_yt as stub_yt
from robot.smelter.backend.tests.common import TestDB, prepare_test_client, TEST_USER, ANOTHER_TEST_USER, TEST_CHANNEL, ANOTHER_TEST_CHANNEL

from django.test import TestCase
from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestEmptyAnalytics(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    def test_stub_new_analytics(self):
        res = self.client.get(f"/analytics/channel_new/{TEST_USER}/{TEST_CHANNEL}?top_author_count=1&top_host_count=2&top_aspect_count=3")
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.json()["maintenance"])

        res = self.client.get(f"/analytics/channel_new/{ANOTHER_TEST_USER}/{ANOTHER_TEST_CHANNEL}?top_author_count=1&top_host_count=2&top_aspect_count=3")
        self.assertEqual(res.status_code, 403)

        res = self.client.get(f"/analytics/channel_new/{TEST_USER}/some_other_channel?top_author_count=1&top_host_count=2&top_aspect_count=3")
        self.assertEqual(res.status_code, 400)


@pytest.mark.django_db
class TestNonEmptyAnalytics(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=False))
    def test_new_analytics(self):
        res = self.client.get(f"/analytics/channel_new/{TEST_USER}/{TEST_CHANNEL}?top_author_count=1&top_host_count=2&top_aspect_count=3")
        self.assertEqual(res.json()["mentions"]["total"], 42)
        self.assertEqual(len(res.json()["mentions"]["points"]), 1)
        self.assertEqual(res.json()["mentions"]["points"][0]["ts"], 1649980800)
        self.assertEqual(res.json()["mentions"]["points"][0]["value"], 42)
        self.assertEqual(res.json()["positive_sentiments"]["total"], 21)
        self.assertEqual(res.json()["positive_sentiments"]["points"][0]["ts"], 1649980800)
        self.assertEqual(res.json()["positive_sentiments"]["points"][0]["value"], 21)
        self.assertEqual(res.json()["neutral_sentiments"]["total"], 21)
        self.assertEqual(res.json()["neutral_sentiments"]["points"][0]["ts"], 1649980800)
        self.assertEqual(res.json()["neutral_sentiments"]["points"][0]["value"], 21)
        self.assertEqual(res.json()["negative_sentiments"]["total"], 0)
        self.assertEqual(res.json()["first_url"], "https://channel1mod1.com/source1/timestamp1650000001")
        self.assertEqual(res.json()["last_url"], "https://channel1mod2.com/source2/timestamp1650000042")
        self.assertEqual(res.json()["first_post_timestamp"], 1650000001)
        self.assertEqual(res.json()["last_post_timestamp"], 1650000042)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=False))
    def test_new_analytics_by_hour(self):
        res = self.client.get(f"/analytics/channel_new/{TEST_USER}/{TEST_CHANNEL}?top_author_count=1&top_host_count=2&top_aspect_count=3&ts_granularity=3600")
        self.assertEqual(res.json()["mentions"]["total"], 42)
        self.assertEqual(len(res.json()["mentions"]["points"]), 1)
        self.assertEqual(res.json()["mentions"]["points"][0]["ts"], 1649998800)
        self.assertEqual(res.json()["mentions"]["points"][0]["value"], 42)
        self.assertEqual(res.json()["positive_sentiments"]["total"], 21)
        self.assertEqual(res.json()["positive_sentiments"]["points"][0]["ts"], 1649998800)
        self.assertEqual(res.json()["positive_sentiments"]["points"][0]["value"], 21)
        self.assertEqual(res.json()["neutral_sentiments"]["total"], 21)
        self.assertEqual(res.json()["neutral_sentiments"]["points"][0]["ts"], 1649998800)
        self.assertEqual(res.json()["neutral_sentiments"]["points"][0]["value"], 21)
        self.assertEqual(res.json()["negative_sentiments"]["total"], 0)
        self.assertEqual(res.json()["first_url"], "https://channel1mod1.com/source1/timestamp1650000001")
        self.assertEqual(res.json()["last_url"], "https://channel1mod2.com/source2/timestamp1650000042")
        self.assertEqual(res.json()["first_post_timestamp"], 1650000001)
        self.assertEqual(res.json()["last_post_timestamp"], 1650000042)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650000000 + 3600*24,
        timestamp_step=3600 * 2 + 1
    ))
    def test_new_analytics_with_zero_fillings(self):
        res = self.client.get(f"/analytics/channel_new/{TEST_USER}/{TEST_CHANNEL}?top_author_count=1&top_host_count=2&top_aspect_count=3&ts_granularity=3600")
        self.assertEqual(res.json()["mentions"]["total"], 12)
        self.assertEqual(len(res.json()["mentions"]["points"]), 23)
        self.assertEqual(res.json()["positive_sentiments"]["total"], 6)
        self.assertEqual(len(res.json()["positive_sentiments"]["points"]), 23)
        self.assertEqual(res.json()["neutral_sentiments"]["total"], 6)
        self.assertEqual(len(res.json()["neutral_sentiments"]["points"]), 23)
        self.assertEqual(res.json()["negative_sentiments"]["total"], 0)
        self.assertEqual(len(res.json()["negative_sentiments"]["points"]), 23)

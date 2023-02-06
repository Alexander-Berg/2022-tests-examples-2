import robot.smelter.backend.tests.conftest  # noqa
import robot.smelter.backend.tests.stub_yt as stub_yt
import robot.smelter.backend.tests.stub_starter as stub_starter
from robot.smelter.backend.tests.common import TestDB, prepare_test_client, prepare_yandex_test_client, prepare_anon_test_client, \
    TEST_USER, TEST_CHANNEL, NEW_TEST_CHANNEL, ANOTHER_TEST_USER, ANOTHER_TEST_CHANNEL, NEW_TEST_QUERY_PARAMS

from django.test import TestCase
from unittest.mock import patch
import hashlib
import pytest


@pytest.mark.django_db
class TestEmptyChannels(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)
        self.anon_client = prepare_anon_test_client()

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_channel(self):
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}")
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.json()["maintenance"])

        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=1000000")
        self.assertEqual(res.status_code, 200)

        res = self.anon_client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}")
        self.assertEqual(res.status_code, 403)  # non anonymous access

        res = self.client.get(f"/channels/channel/{ANOTHER_TEST_USER}/{ANOTHER_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 403)

        res = self.client.get(f"/channels/channel/{TEST_USER}/some_other_channel")
        self.assertEqual(res.status_code, 400)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.delete", new=stub_starter.empty_delete)
    def test_channel_creation_and_deletion(self):
        res = self.client.post(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}", {
            "title": "NewChannel",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 201)

        res = self.client.get(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 200)

        res = self.client.post(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}", {
            "title": "NewChannel",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 400)  # creating channel with the same name should not be allowed

        res = self.client.delete(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 204)

        res = self.client.get(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 400)  # channel should have been deleted in previous step

        res = self.client.post(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}", {
            "title": "NewChannel",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 201)  # ok after deletion

        res = self.client.post("/channels/channel/{ANOTHER_TEST_USER}/some_other_channel", {
            "title": "NewChannel",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 403)  # creating channel for another user should not be allowed

        res = self.client.delete(f"/channels/channel/{ANOTHER_TEST_USER}/{ANOTHER_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 403)  # deletion of other user's channel is not allowed

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.delete", new=stub_starter.empty_delete)
    def test_channel_creation_new_handler(self):
        title = "NewChannel"
        res = self.client.post("/channels/create_channel", {
            "title": title,
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 201)
        channel_name = res.json()["channel_name"]
        self.assertEqual(channel_name, hashlib.md5(title.encode('utf-8')).hexdigest()[:8])

        res = self.client.get(f"/channels/channel/{TEST_USER}/{channel_name}")
        self.assertEqual(res.status_code, 200)

        # channel with the same title is not allowed
        res = self.client.post("/channels/create_channel", {
            "title": title,
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 400)

        title = "NewTitle2"
        res = self.client.post("/channels/create_channel", {
            "title": "NewTitle2",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 201)
        channel_name = res.json()["channel_name"]
        self.assertEqual(channel_name, hashlib.md5(title.encode('utf-8')).hexdigest()[:8])

        res = self.client.get(f"/channels/channel/{TEST_USER}/{channel_name}")
        self.assertEqual(res.status_code, 200)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_post(self):
        res = self.client.get(f"/channels/post/{TEST_USER}/{TEST_CHANNEL}?post_timestamp=1245")
        self.assertEqual(res.status_code, 400)  # data is empty, so no post could be found

    def test_subscription(self):
        res = self.client.put(f"/channels/subscription/{TEST_USER}/{TEST_CHANNEL}", {
            "last_accessed_post_timestamp": 1234
        }, format="json")
        self.assertEqual(res.status_code, 201)
        res = self.client.get(f"/channels/subscription/{TEST_USER}/{TEST_CHANNEL}")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["last_accessed_post_timestamp"], 1234)

        res = self.client.delete(f"/channels/subscription/{TEST_USER}/{TEST_CHANNEL}")
        self.assertEqual(res.status_code, 204)

        res = self.client.get(f"/channels/subscription/{TEST_USER}/{TEST_CHANNEL}")
        self.assertEqual(res.status_code, 400)  # deleted

    def test_subscription_for_new_channel(self):
        res = self.client.get(f"/channels/subscription/{TEST_USER}/{NEW_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 400)  # no subscription yet

        res = self.client.post(f"/channels/channel/{TEST_USER}/{NEW_TEST_CHANNEL}", {
            "title": "NewChannel",
            "query_params": NEW_TEST_QUERY_PARAMS
        }, format="json")
        self.assertEqual(res.status_code, 201)

        res = self.client.get(f"/channels/subscription/{TEST_USER}/{NEW_TEST_CHANNEL}")
        self.assertEqual(res.status_code, 200)

    def test_subscriber(self):
        res = self.client.get(f"/channels/subscriber/{TEST_USER}")
        self.assertEqual(res.status_code, 200)

        res = self.client.get(f"/channels/subscriber/{ANOTHER_TEST_USER}")
        self.assertEqual(res.status_code, 403)

        res = self.anon_client.get(f"/channels/subscriber/{TEST_USER}")
        self.assertEqual(res.status_code, 403)

    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_preview(self):
        res = self.client.get("/channels/preview?query=testquery")
        self.assertEqual(res.status_code, 200)

        res = self.anon_client.get("/channels/preview?query=testquery")
        self.assertEqual(res.status_code, 403)


@pytest.mark.django_db
class TestNonEmptyChannels(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)
        self.yandex_client = prepare_yandex_test_client(self.test_db)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650050000,
        channel_id=1))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_long_channel_queries(self):
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=1000000")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 50000)  # last_timestamp - first_timestamp

        prev_post = None
        for post in res.json()["posts"]:
            if prev_post is None:
                prev_post = post
                continue
            self.assertEqual(post["post_timestamp"] + 1, prev_post["post_timestamp"])

            prev_post = post

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.non_empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_empty_feed_but_nonempty_saas(self):
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=35")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 0)  # actually no SerializedUrlRecord provided :(

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650000042,
        channel_id=1,
        is_present_in_channel_query=False))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.non_empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_non_present_in_channel_query(self):
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=42")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 42)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(empty=False))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.non_empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_fields(self):
        # Non-Yandex-client
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=42")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 42)
        for post in res.json()["posts"]:
            self.assertIsNone(post.get("last_access"))
            self.assertIsNone(post.get("times"))
            self.assertIsNone(post.get("incoming_links"))
            self.assertEqual(post["channel_info"]["total_likes"], 42)
            self.assertEqual(post["channel_info"]["total_views"], 7500)

        # Yandex-client should have access to the channel and debug fields
        res = self.yandex_client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=42")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 42)
        ts = 1650000042
        for post in res.json()["posts"]:
            self.assertEqual(post["last_access"], ts + stub_yt.LAST_ACCESS_TIME_DELAY)
            self.assertEqual(post["times"]["crawl_add_time"], ts + stub_yt.CRAWL_ADD_TIME_DELAY)
            self.assertEqual(post["times"]["multiboba_sentiment_time"], ts + stub_yt.MULTIBOBA_TIME_DELAY)
            self.assertEqual(post["channel_info"]["total_likes"], 42)
            self.assertEqual(post["channel_info"]["total_views"], 7500)
            self.assertTrue(post.get("incoming_links", {}).get("total_link_count", 0) > 0)
            ts -= 1

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(reset_select_rows=True))
    @patch("robot.smelter.backend.channels.utils.starter_client.search", new=stub_starter.non_empty_search)
    @patch("robot.smelter.backend.channels.utils.starter_client.setup_channel", new=stub_starter.empty_search)
    def test_sentiment_filter(self):
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=42&sentiment=pos&sentiment=neu")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 42)
        for post in res.json()["posts"]:
            self.assertTrue(post.get("sentiment") in ["neutral", "positive"])

        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?docs_per_page=42&sentiment=neg")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["post_count"], 0)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650000001,
        rows_per_select=1,
        reset_select_rows=True))
    def test_post(self):
        res = self.client.get(f"/channels/post/{TEST_USER}/{TEST_CHANNEL}?post_timestamp=1650000001")
        self.assertEqual(res.status_code, 200)


@pytest.mark.django_db
class TestSaasInfo(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)
        self.anon_client = prepare_anon_test_client()

    @patch("robot.smelter.backend.channels.utils.starter_client.get_saas_info", new=stub_starter.get_saas_info)
    def test_saas_base(self):
        res = self.anon_client.get("/channels/saas_base")
        self.assertEqual(res.status_code, 403)
        res = self.client.get("/channels/saas_base")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), stub_starter.SAAS_INFO_RESPONSE)

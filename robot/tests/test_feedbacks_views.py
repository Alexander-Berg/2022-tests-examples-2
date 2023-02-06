import robot.smelter.backend.tests.conftest  # noqa
import robot.smelter.backend.tests.stub_yt as stub_yt
from robot.smelter.backend.tests.common import TestDB, prepare_test_client, TEST_USER, TEST_CHANNEL
from robot.smelter.backend.channels.utils import pydantic_models

from django.test import TestCase
from django.conf import settings
from unittest.mock import patch

import pytest
import json


@pytest.mark.django_db
class TestChannelMarkup(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)

    def tearDown(self):
        stub_yt.StubYtClient.clear()

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650000061,
        rows_per_select=settings.MAX_ROWS_PER_SELECT,
        channel_id=1,
        return_inserted_rows=True))
    def test_successfull_markup(self):
        posts = [
            {
                "post_timestamp": 1650000041,
                "url": stub_yt.generate_post_url(1, 1650000041),
                "markup": {
                    "sentiment": "positive",
                    "is_main_topic": True,
                    "aspects": [
                        {
                            "name": "customer satisfaction",
                            "sentiment": "negative"

                        },
                        {
                            "name": "price",
                            "sentiment": "neutral"
                        }
                    ],
                    "tags": ["companya", "customerb"]
                }
            },
            {
                "post_timestamp": 1650000030,
                "url": stub_yt.generate_post_url(1, 1650000030),
                "markup": {
                    "sentiment": "negative",
                    "aspects": [
                        {
                            "name": "greatness",
                            "sentiment": "neutral"

                        },
                        {
                            "name": "size",
                            "sentiment": "negative"
                        }
                    ]
                }
            },
            {
                "post_timestamp": 1650000032,
                "url": stub_yt.generate_post_url(1, 1650000032),
                "markup": {
                    "is_main_topic": False,
                    "tags": ["companya"]
                },
            }
        ]
        res = self.client.post(f"/feedbacks/channel_markup/{TEST_USER}/{TEST_CHANNEL}", data={
            "posts": posts
        }, format="json")
        self.assertEqual(res.status_code, 200)

        inserted_posts = stub_yt.StubYtClient.ROWS_INSERTED[settings.FEEDS_MARKUP_TABLE_PATH]
        self.assertEqual(len(inserted_posts), len(posts))
        for inserted_post, original_post in zip(stub_yt.StubYtClient.ROWS_INSERTED[settings.FEEDS_MARKUP_TABLE_PATH], posts):
            self.assertEqual(inserted_post["Url"], original_post["url"])
            self.assertEqual(pydantic_models.PostMarkup.parse_obj(json.loads(inserted_post["MarkupJson"])), pydantic_models.PostMarkup.parse_obj(original_post["markup"]))

        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?tags=companya")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["posts"]), 2)
        self.assertEqual(res.data["posts"][0]["post_timestamp"], 1650000041)
        self.assertEqual(res.data["posts"][1]["post_timestamp"], 1650000032)
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?tags=companya&disallowed_tags=customerb")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["posts"]), 1)
        self.assertEqual(res.data["posts"][0]["post_timestamp"], 1650000032)

        stub_yt.StubYtClient.ROWS_FOR_SELECT[settings.FEEDS_MARKUP_TABLE_PATH] = [
            {
                "ChannelId": 1,
                "UrlType": 1,
                "Url": stub_yt.generate_post_url(1, 1650000010)[:-1],  # just one url actually, other dont' match
                "MarkupJson": json.dumps({
                    "aspects": [
                        {
                            "name": "greatness",
                            "sentiment": "negative"
                        }
                    ]
                })
            }
        ]
        res = self.client.get(f"/channels/channel/{TEST_USER}/{TEST_CHANNEL}?aspects=greatness")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["posts"]), 2)
        self.assertEqual(res.data["posts"][0]["post_timestamp"], 1650000030)
        self.assertEqual(res.data["posts"][1]["post_timestamp"], 1650000010)

    @patch("yt.wrapper.YtClient", new=stub_yt.make_stub_yt_client_creator(
        first_timestamp=1650000000,
        last_timestamp=1650000061,
        rows_per_select=settings.MAX_ROWS_PER_SELECT,
        channel_id=1))
    def tests_some_posts_not_found(self):
        posts_found = [
            {
                "post_timestamp": 1650000041,
                "url": stub_yt.generate_post_url(1, 1650000041),
                "markup": {
                    "sentiment": "positive",
                    "is_main_topic": True,
                    "aspects": [
                        {
                            "name": "customer satisfaction",
                            "sentiment": "negative"

                        },
                        {
                            "name": "price",
                            "sentiment": "neutral"

                        },
                    ]
                }
            }
        ]
        posts_not_found = [
            {
                "post_timestamp": 1650000090,
                "url": stub_yt.generate_post_url(1, 1650000090),
                "markup": {
                    "sentiment": "negative",
                    "is_main_topic": False,
                    "aspects": [
                        {
                            "name": "greatness",
                            "sentiment": "neutral"

                        },
                        {
                            "name": "size",
                            "sentiment": "negative"
                        },
                    ]
                }
            }
        ]

        stub_yt.StubYtClient.clear()

        res = self.client.post(f"/feedbacks/channel_markup/{TEST_USER}/{TEST_CHANNEL}", data={
            "posts": posts_found + posts_not_found
        }, format="json")
        self.assertEqual(res.status_code, 400)

        self.assertIsNone(stub_yt.StubYtClient.ROWS_INSERTED.get(settings.FEEDS_MARKUP_TABLE_PATH))
        self.assertEqual(len(res.data["posts_not_found"]), len(posts_not_found))

from robot.smelter.backend.users.models import User
from robot.smelter.backend.channels.models import Channel, Subscription
from rest_framework.test import APIClient

# these are created in TestDB
TEST_QUERY_PARAMS = {
    "deleted_authors": [],
    "min_followers": 0,
    "min_rel": 0,
    "only_main_topic": False,
    "query": "TestChannel",
    "should_request_ml_worker_markup": True,
    "sources": ["telegram", "vk", "habr", "pikabu", "zen", "twitter"],
    "tag": "company",
    "use_samovar_preparat": True
}
TEST_CHANNEL = "testchannel"
TEST_USER = "testuser"
ANOTHER_TEST_CHANNEL = "testchannel2"
ANOTHER_TEST_USER = "testuser2"
YANDEX_USER = "yandexuser"

# these are for creating in testing code
NEW_TEST_QUERY_PARAMS = {
    "deleted_authors": [],
    "min_followers": 42,
    "min_rel": 0.5,
    "only_main_topic": True,
    "query": "New+Test Channel",
    "should_request_ml_worker_markup": False,
    "sources": ["zen", "twitter"],
    "tag": "company"
}
NEW_TEST_CHANNEL = "new_test_channel"
NEW_USER = "newuser"


class TestDB:
    def __init__(self):
        self.user, _ = User.objects.get_or_create(username="testuser")
        self.another_user, _ = User.objects.get_or_create(username=ANOTHER_TEST_USER)
        self.yandex_user, _ = User.objects.get_or_create(username=YANDEX_USER, is_yandex=True)
        channel = Channel.objects.create(
            author=self.user,
            title="TestChannel",
            channel_name=TEST_CHANNEL,
            query_params_dumped=Channel.dump_query_params(TEST_QUERY_PARAMS)
        )
        Subscription.objects.create(
            user=self.user,
            channel=channel,
            last_accessed_post_timestamp=1
        )

        channel = Channel.objects.create(
            author=self.another_user,
            title="TestChannel",
            channel_name=ANOTHER_TEST_USER,
            query_params_dumped=Channel.dump_query_params(TEST_QUERY_PARAMS)
        )
        Subscription.objects.create(
            user=self.another_user,
            channel=channel,
            last_accessed_post_timestamp=1
        )


def prepare_test_client(test_db: TestDB):
    client = APIClient()
    client.force_authenticate(user=test_db.user)
    return client


def prepare_anon_test_client():
    return APIClient()


def prepare_yandex_test_client(test_db: TestDB):
    client = APIClient()
    client.force_authenticate(user=test_db.yandex_user)
    return client

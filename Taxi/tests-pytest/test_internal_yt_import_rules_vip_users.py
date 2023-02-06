import bson
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import yt_import


YT_IMPORT_RULE_NAME = 'vip_users'
YT_VIP_USERS_TABLE = '//home/taxi-dwh/public/top_users'

USER_PHONE_ID_KEY = 'user_phone_id'

PHONE_ID_TO_KEEP = '57b45967b51143bef1b24fc1'
PHONE_ID_TO_REMOVE = '57b45967b51143bef1b24fc2'
PHONE_ID_TO_ADD = '57b45967b51143bef1b24fc3'


class _DummyYtClient(object):
    def read_table(self, table, *args, **kwargs):
        assert table == YT_VIP_USERS_TABLE
        rows = [
            {USER_PHONE_ID_KEY: PHONE_ID_TO_KEEP},
            {USER_PHONE_ID_KEY: PHONE_ID_TO_ADD},
            {USER_PHONE_ID_KEY: PHONE_ID_TO_ADD},
        ]
        return iter(rows)

    def exists(self, path):
        return path == YT_VIP_USERS_TABLE

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, path, attribute):
        assert attribute == 'modification_time'
        return None


class _BulkWrapper(object):
    inserted = []

    def __init__(self, bulk):
        self.bulk = bulk
        self._pre_inserted = []

    def insert(self, doc):
        self._pre_inserted.append(doc)
        return self.bulk.insert(doc)

    def find(self, doc):
        return self.bulk.find(doc)

    @async.inline_callbacks
    def execute(self):
        self.inserted.extend(self._pre_inserted)
        async.return_value((yield self.bulk.execute()))


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(YT_VIP_USERS_TABLE=YT_VIP_USERS_TABLE)
@pytest.inline_callbacks
def test_do_stuff(patch):
    original_bulk_init = db.vip_users.initialize_unordered_bulk_op

    @patch('taxi.core.db.vip_users.initialize_unordered_bulk_op')
    def initialize_unordered_bulk_op():
        bulk = original_bulk_init()
        bulk_wrapper = _BulkWrapper(bulk)

        return bulk_wrapper

    dummy_hahn = _DummyYtClient()

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn'
        assert environment
        assert new
        return dummy_hahn

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    expected_inserted_docs = [
        [('_id', bson.ObjectId(PHONE_ID_TO_ADD))],
    ]
    inserted_docs = sorted(doc.items() for doc in _BulkWrapper.inserted)

    assert inserted_docs == expected_inserted_docs

    expected_vip_users = [
        [('_id', bson.ObjectId(PHONE_ID_TO_KEEP))],
        [('_id', bson.ObjectId(PHONE_ID_TO_ADD))],
    ]
    vip_users = yield db.vip_users.find().run()
    vip_users = sorted(user.items() for user in vip_users)

    assert vip_users == expected_vip_users

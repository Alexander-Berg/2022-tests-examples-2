import json

from bson import json_util
import pytest

from taxi.core import db
from taxi.internal import yt_import


YT_IMPORT_RULE_NAME = 'discount_users'
YT_DISCOUNT_USERS_TABLE = 'discounts/discount_users'


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOAD_DISCOUNT_USERS_ENABLED=True,
    LOAD_DISCOUNT_USERS_INTERVAL_MINUTES=24 * 60,
    LOAD_DISCOUNT_USERS_TO_OLD_PROCESSING_DB=False,
    LOAD_DISCOUNT_USERS_CHUNK_SIZE=10,
)
@pytest.inline_callbacks
def test_do_stuff(load, patch):
    yt_discount_users = json.loads(load('yt_discount_users.json'))
    yt_client = _DummyYtClient(rows=yt_discount_users)

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn-dwh'
        assert environment
        assert new
        return yt_client

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    expected = json_util.loads(load('expected.json'))
    discount_users = yield db.discount_users_misc.find().run()

    assert sorted(discount_users) == sorted(expected)


class _DummyYtClient(object):
    def __init__(self, rows):
        self._rows = rows

    def read_table(self, table, *args, **kwargs):
        assert table == YT_DISCOUNT_USERS_TABLE
        return iter(self._rows)

    def exists(self, path):
        return path == YT_DISCOUNT_USERS_TABLE

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, path, attribute):
        assert attribute == 'modification_time'
        return None

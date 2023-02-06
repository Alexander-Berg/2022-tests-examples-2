"""
Test for apply_updates mode

"""


from copy import deepcopy
import pytest

from taxi.core import db
from taxi.internal import yt_import


YT_IMPORT_RULE_NAME = 'antifraud_suspicious_users'
MONGO_COLLECTION_NAME = 'antifraud_suspicious_users'

YT_KEY_FIELD = 'updated_at'


class _DummyYtClient(object):
    def __init__(self, rows):
        self.__rows = rows
        self.row_count = len(rows)
        self.sorted_by = [YT_KEY_FIELD, ]

    class TablePath(object):
        def __init__(self, *args, **kwargs):
            self.lower_key = kwargs.get('lower_key')
            self.start_index = kwargs.get('start_index')

    def read_table(self, table, *args, **kwargs):
        rows = deepcopy(self.__rows)
        key_field = YT_KEY_FIELD
        lower_key = getattr(table, 'lower_key', None)
        start_index = getattr(table, 'start_index', None)
        if lower_key and start_index:
            raise ValueError('Incompatible parameters')
        if lower_key is not None:
            return (
                row for row in rows if
                row[key_field] >= lower_key
            )
        if start_index is not None:
            return (
                row for index, row in enumerate(rows) if
                index >= start_index
            )
        return iter(rows)

    def get(self, path):
        path, attr = path.split('/@')
        return getattr(self, attr, None)

    def exists(self, *args, **kwargs):
        return True


@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.parametrize(
    'inp,expected',
    [
        # update one and insert another
        (
            [
                {
                    'user_id': '0000002a1eaff0cfe07f5bf73c1494dc',
                    'common_params_flg': True,
                    'updated_at': '2019-05-06 20:13:58'
                },
                {
                    'user_id': '39b45783a2a6dd8685b24415babec184',
                    'common_params_flg': False,
                    'updated_at': '2019-05-06 20:13:58'
                },
            ],
            [
                {
                    '_id': '0000002a1eaff0cfe07f5bf73c1494dc',
                    'doc': {
                        'common_params_flg': True,
                    },
                    'updated_at': '2019-05-06 20:13:58',
                },
                {
                    '_id': '39b45783a2a6dd8685b24415babec184',
                    'doc': {
                        'common_params_flg': False,
                    },
                    'updated_at': '2019-05-06 20:13:58',
                },
            ],
        ),
        # insert user, than update it multiple times
        (
                [
                    {
                        'user_id': '39b45783a2a6dd8685b24415babec184',
                        'common_params_flg': True,
                        'updated_at': '2019-05-06 20:13:58'
                    },
                    {
                        'user_id': '39b45783a2a6dd8685b24415babec184',
                        'common_params_flg': False,
                        'updated_at': '2019-05-10 10:13:10'
                    },
                    {
                        'user_id': '39b45783a2a6dd8685b24415babec184',
                        'common_params_flg': True,
                        'updated_at': '2019-05-15 22:22:30'
                    },
                ],
                [
                    {
                        '_id': '0000002a1eaff0cfe07f5bf73c1494dc',
                        'doc': {
                            'common_params_flg': False,
                        },
                        'updated_at': '2000-01-01 00:01:01',
                    },
                    {
                        '_id': '39b45783a2a6dd8685b24415babec184',
                        'doc': {
                            'common_params_flg': True,
                        },
                        'updated_at': '2019-05-15 22:22:30',
                    },
                ],
        ),
        # do nothing
        (
                [
                    {
                        'user_id': '0000002a1eaff0cfe07f5bf73c1494dc',
                        'common_params_flg': True,
                        'updated_at': '2018-01-01 00:01:01'
                    },
                ],
                [
                    {
                        "_id": "0000002a1eaff0cfe07f5bf73c1494dc",
                        "doc": {
                            "common_params_flg": False
                        },
                        # i.e. should not be updated
                        # if db.yt_imports last_key is greater than
                        # updated_at from input data
                        "updated_at": "2000-01-01 00:01:01"
                    }
                ],
        ),
    ]
)
def test_do_stuff(inp, expected, patch):
    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(*args, **kwargs):
        return _DummyYtClient(inp)

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    actual = yield getattr(db, MONGO_COLLECTION_NAME).find().run()
    actual_sorted = sorted(actual, key=lambda e: e['_id'])

    expected_sorted = sorted(expected, key=lambda e: e['_id'])
    assert actual_sorted == expected_sorted

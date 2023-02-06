import bson
import pytest

from taxi.core import db
from taxi.internal.yt_import import cast
from taxi.internal.yt_import import consts
from taxi.internal.yt_import.modes import common
from taxi.internal.yt_import.schema import classes


YT_VIP_USERS_TABLE = '//home/taxi-dwh/public/top_users'

USER_PHONE_ID_KEY = 'user_phone_id'

PHONE_ID_TO_KEEP = '57b45967b51143bef1b24fc1'
PHONE_ID_TO_REMOVE = '57b45967b51143bef1b24fc2'
PHONE_ID_TO_ADD = '57b45967b51143bef1b24fc3'


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(YT_VIP_USERS_TABLE=YT_VIP_USERS_TABLE)
@pytest.mark.parametrize('yt_rows,expected', [
    (
        {
            YT_VIP_USERS_TABLE: [
                {USER_PHONE_ID_KEY: PHONE_ID_TO_KEEP},
                {USER_PHONE_ID_KEY: PHONE_ID_TO_ADD},
                {USER_PHONE_ID_KEY: PHONE_ID_TO_ADD},
            ],
        },
        [
            {'_id': bson.ObjectId(PHONE_ID_TO_KEEP)},
            {'_id': bson.ObjectId(PHONE_ID_TO_ADD)},
            {'_id': bson.ObjectId(PHONE_ID_TO_ADD)},
        ],
    ),
])
def test_get_new_docs(yt_rows, expected, monkeypatch):
    import_rule = _build_import_rule()
    dummy_hahn = _DummyYtClient(yt_rows)

    new_docs = common.get_new_docs(
        dummy_hahn,
        import_rule,
        import_rule.mapper_builder(),
    )

    assert list(new_docs) == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_insert_docs():
    collection = db.vip_users
    inserted = [
        {'_id': 'to_remove_1', 'field': 'foo'},
        {'_id': 'to_remove_2', 'field': 'bar'},
    ]

    yield common.insert_docs(inserted, collection, 1000)

    docs = yield collection.find().run()

    assert sorted(docs) == sorted(inserted)


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_remove_docs():
    collection = db.vip_users

    yield collection.insert([
        {'_id': 'to_remove_1', 'field': 'foo'},
        {'_id': 'to_remove_2', 'field': 'bar'},
        {'_id': 'to_keep', 'field': 'quux'},
    ])

    yield common.remove_docs(
        [
            {'_id': 'to_remove_1'},
            {'_id': 'to_remove_2'},
        ],
        collection,
        1000,
    )

    expected = [{'_id': 'to_keep', 'field': 'quux'}]
    docs = yield collection.find().run()

    assert sorted(docs) == sorted(expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('not_empty_columns,expected', [
    (
        None, [
            {
                '_id': 'to_update_1',
                'updated_field': ['new_foo'],
                'kept_field': 'bar',
            },
            {
                '_id': 'to_update_2',
                'updated_field': [],
            },
            {
                '_id': 'to_keep',
                'kept_field': ['no_update'],
            },
        ],
    ),
    (
        {'updated_field'}, [
            {
                '_id': 'to_update_1',
                'updated_field': ['new_foo'],
                'kept_field': 'bar',
            },
            {'_id': 'to_update_2'},
            {
                '_id': 'to_keep',
                'kept_field': ['no_update'],
            },
        ],
    ),
])
@pytest.inline_callbacks
def test_update_docs(not_empty_columns, expected):
    collection = db.vip_users

    yield collection.insert([
        {'_id': 'to_update_1', 'updated_field': ['foo'], 'kept_field': 'bar'},
        {'_id': 'to_update_2', 'updated_field': ['baz']},
        {'_id': 'to_keep', 'kept_field': ['no_update']},
    ])

    yield common.update_docs(
        [
            {'_id': 'to_update_1', 'updated_field': ['new_foo']},
            {'_id': 'to_update_2', 'updated_field': []},
        ],
        collection,
        1000,
        not_empty_columns,
    )

    docs = yield collection.find().run()

    assert sorted(docs) == sorted(expected)


class _DummyYtClient(object):
    def __init__(self, rows):
        self.rows = rows

    def read_table(self, table, *args, **kwargs):
        assert table == YT_VIP_USERS_TABLE
        return iter(self.rows.get(table, []))

    def exists(self, path):
        return path == YT_VIP_USERS_TABLE


def _build_import_rule():
    source = classes.Source(
        yt_client_name='hahn',
        table_path='//home/taxi-dwh/public/top_users',
    )
    mapper_builder = classes.MapperBuilder(
        column_mappers=[
            classes.ColumnMapper(
                input_column='user_phone_id',
                output_column='_id',
                cast=cast.get_cast_func('to_obj_id'),
            ),
        ],
    )
    import_rule = classes.YtImportRule(
        name='vip_users',
        source=source,
        destination='vip_users',
        mapper_builder=mapper_builder,
        mode=consts.IMPORT_MODE_BY_ID,
        chunk_size=classes.DEFAULT_CHUNK_SIZE,
    )

    return import_rule

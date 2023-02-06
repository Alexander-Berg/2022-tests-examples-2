import datetime

import bson
import pytest

_DOC1 = {
    '_id': '9b0ef3c5398b3e07b59f03110563479d',
    '_shard_id': 7,
    'order': {'status': 'finished'},
    'reorder': {'decisions': [], 'suggestions': []},
    'status': 'finished',
}
_DOC2 = {
    '_id': '8b0ef3c5398b3e07b59f03110563479d',
    '_shard_id': 7,
    'created': datetime.datetime(2020, 2, 4, 18, 57, 38, 722000),
    'order': {'status': 'finished', 'taxi_status': 'complete'},
    'status': 'finished',
}
_MONGO_IDS = {
    _DOC1['_id'],
    _DOC2['_id'],
    'alias_match1',
    'alias_match2',
    'reorder_id',
}

_DOC5_INDEXES = {
    '_id': 'indexes',
    '_shard_id': 0,
    'aliases': [
        {'id': 'alias_mismatch'},
        {'id': 'alias_match1'},
        {'id': 'alias_match2'},
    ],
    'reorder': {'id': 'reorder_id'},
}

_DOC6_YT1 = {
    '_id': '5b0ef3c5398b3e07b59f03110563479d',
    'updated': datetime.datetime(2018, 11, 25, 12, 30),
}

_DOC7_YT2 = {
    '_id': '4b0ef3c5398b3e07b59f03110563479d',
    'updated': datetime.datetime(2018, 12, 25, 12, 30),
}

_DOC8_YT3 = {
    '_id': '3b0ef3c5398b3e07b59f03110563479d',
    'updated': datetime.datetime(2019, 11, 25, 12, 30),
}
_DOC_YT_FALLBACK = {
    'id': 'ab0ef3c5398b3e07b59f03110563479d',
    'doc': (
        b'@\x00\x00\x00\x02_id\x00!\x00\x00\x00'
        b'ab0ef3c5398b3e07b59f03110563479d\x00\t'
        b'updated\x00@\x15\xd9Jg\x01\x00\x00\x00'
    ),
}
_DOC_YT_FALLBACK_EXPECTED = {
    '_id': 'ab0ef3c5398b3e07b59f03110563479d',
    'updated': datetime.datetime(2018, 11, 25, 12, 30),
}
_DOC_YT_VERIFIED_EXPECTED = {
    '_id': '2b0ef3c5398b3e07b59f03110563479d',
    'updated': datetime.datetime(2018, 11, 24, 12, 30),
}

_YT_MARK = pytest.mark.yt(
    dyn_table_data=[
        {
            'path': '//home/testsuite/order_proc',
            'values': [_DOC_YT_FALLBACK],
            'format': {'encoding': None},
        },
    ],
)
_FALLBACK_IDS = {_DOC_YT_FALLBACK['id']}

_YDB_MARK = pytest.mark.ydb(
    files=[
        'fill_orders.sql',
        'fill_order_id_index.sql',
        'fill_created_index.sql',
    ],
)


@pytest.mark.parametrize(
    'api_version, force_null_expected_ids',
    [
        pytest.param(
            1,
            _FALLBACK_IDS,
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': False},
            ),
        ),
        pytest.param(
            1,
            set(),
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': True},
            ),
        ),
        pytest.param(
            2,
            _MONGO_IDS.union(_FALLBACK_IDS),
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': False},
            ),
        ),
        pytest.param(
            2,
            _MONGO_IDS,
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': True},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'doc_id, indexes, expected_document',
    [
        ('123', None, None),
        ('9b0ef3c5398b3e07b59f03110563479d', None, _DOC1),
        ('9b0ef3c5398b3e07b59f03110563479d', [], _DOC1),
        ('9b0ef3c5398b3e07b59f03110563479d', ['alias', 'reorder'], _DOC1),
        ('8b0ef3c5398b3e07b59f03110563479d', None, _DOC2),
        ('alias_match1', ['alias'], _DOC5_INDEXES),
        ('alias_match2', ['alias'], _DOC5_INDEXES),
        ('alias_match1', ['alias', 'reorder'], _DOC5_INDEXES),
        ('alias_match1', ['reorder'], None),
        ('alias_match1', None, None),
        ('reorder_id', ['alias'], None),
        ('reorder_id', ['reorder'], _DOC5_INDEXES),
        ('reorder_id', ['alias', 'reorder'], _DOC5_INDEXES),
        ('queue_alias_id1', ['reorder'], None),
        ('queue_reorder_id', ['alias'], None),
        ('5b0ef3c5398b3e07b59f03110563479d', None, _DOC6_YT1),
        ('yt_reorder_id', ['reorder'], _DOC6_YT1),
        ('yt_reorder_id', ['reorder', 'alias'], _DOC6_YT1),
        ('yt_reorder_id', ['alias'], None),
        ('4b0ef3c5398b3e07b59f03110563479d', None, _DOC7_YT2),
        ('yt_performer_alias_id', ['alias'], _DOC7_YT2),
        ('yt_performer_alias_id', ['reorder', 'alias'], _DOC7_YT2),
        ('yt_performer_alias_id', ['reorder'], None),
        (
            'yt_performer_alias_id_verified',
            ['alias'],
            _DOC_YT_VERIFIED_EXPECTED,
        ),
        ('3b0ef3c5398b3e07b59f03110563479d', None, _DOC8_YT3),
        ('3b0ef3c5398b3e07b59f03110563479d', ['reorder'], _DOC8_YT3),
        ('ab0ef3c5398b3e07b59f03110563479d', None, _DOC_YT_FALLBACK_EXPECTED),
    ],
)
@_YDB_MARK
@_YT_MARK
async def test_order_proc_retrieve(
        mongodb,
        yt_apply,
        taxi_order_archive,
        doc_id,
        indexes,
        expected_document,
        api_version,
        force_null_expected_ids,
):
    json_doc = {'id': doc_id}
    if indexes is not None:
        json_doc['indexes'] = indexes
    response = await taxi_order_archive.post(
        f'v{api_version}/order_proc/retrieve', json=json_doc,
    )
    expected_status = 404 if expected_document is None else 200
    if doc_id in force_null_expected_ids:
        expected_status = 404
    assert response.status_code == expected_status
    if expected_status != 200:
        assert response.content == b''
    else:
        doc = bson.BSON(response.content).decode()
        assert doc == {'doc': expected_document}


@pytest.mark.parametrize(
    'doc_id, lookup_yt, expected_document',
    [
        ('5b0ef3c5398b3e07b59f03110563479d', True, _DOC6_YT1),
        ('5b0ef3c5398b3e07b59f03110563479d', False, None),
        ('4b0ef3c5398b3e07b59f03110563479d', True, _DOC7_YT2),
        ('4b0ef3c5398b3e07b59f03110563479d', False, None),
        ('3b0ef3c5398b3e07b59f03110563479d', True, _DOC8_YT3),
        ('3b0ef3c5398b3e07b59f03110563479d', False, None),
    ],
)
@_YDB_MARK
async def test_order_proc_retrieve_by_partitions(
        taxi_order_archive, doc_id, lookup_yt, expected_document,
):
    response = await taxi_order_archive.post(
        'v1/order_proc/retrieve', json={'id': doc_id, 'lookup_yt': lookup_yt},
    )
    if expected_document:
        assert response.status_code == 200

        doc = bson.BSON(response.content).decode()
        assert doc == {'doc': expected_document}
    else:
        assert response.status_code == 404
        assert response.content == b''


@pytest.mark.parametrize(
    'doc_ids, lookup_yt, expected_status, expected_docs',
    [
        (
            ['9b0ef3c5398b3e07b59f03110563479d'],
            True,
            200,
            {'9b0ef3c5398b3e07b59f03110563479d': _DOC1},
        ),
        (
            [
                '9b0ef3c5398b3e07b59f03110563479d',
                '8b0ef3c5398b3e07b59f03110563479d',
                '123',
            ],
            True,
            200,
            {
                '9b0ef3c5398b3e07b59f03110563479d': _DOC1,
                '8b0ef3c5398b3e07b59f03110563479d': _DOC2,
            },
        ),
        (
            ['9b0ef3c5398b3e07b59f03110563479d', '123'],
            True,
            200,
            {'9b0ef3c5398b3e07b59f03110563479d': _DOC1},
        ),
        (['123'], True, 200, {}),
        (
            [
                '9b0ef3c5398b3e07b59f03110563479d',
                '5b0ef3c5398b3e07b59f03110563479d',
                '4b0ef3c5398b3e07b59f03110563479d',
                '3b0ef3c5398b3e07b59f03110563479d',
                '123',
            ],
            True,
            200,
            {
                '9b0ef3c5398b3e07b59f03110563479d': _DOC1,
                '5b0ef3c5398b3e07b59f03110563479d': _DOC6_YT1,
                '4b0ef3c5398b3e07b59f03110563479d': _DOC7_YT2,
                '3b0ef3c5398b3e07b59f03110563479d': _DOC8_YT3,
            },
        ),
        (
            [
                '9b0ef3c5398b3e07b59f03110563479d',
                '5b0ef3c5398b3e07b59f03110563479d',
                '4b0ef3c5398b3e07b59f03110563479d',
                '3b0ef3c5398b3e07b59f03110563479d',
                '123',
            ],
            False,
            200,
            {'9b0ef3c5398b3e07b59f03110563479d': _DOC1},
        ),
        pytest.param(
            [
                'ab0ef3c5398b3e07b59f03110563479d',
                '9b0ef3c5398b3e07b59f03110563479d',
            ],
            True,
            200,
            {
                'ab0ef3c5398b3e07b59f03110563479d': _DOC_YT_FALLBACK_EXPECTED,
                '9b0ef3c5398b3e07b59f03110563479d': _DOC1,
            },
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': True},
            ),
        ),
        pytest.param(
            [
                'ab0ef3c5398b3e07b59f03110563479d',
                '9b0ef3c5398b3e07b59f03110563479d',
            ],
            True,
            200,
            {'9b0ef3c5398b3e07b59f03110563479d': _DOC1},
            marks=pytest.mark.config(
                ORDER_ARCHIVE_YDB={'fallback_on_yt': False},
            ),
        ),
    ],
)
@_YDB_MARK
@_YT_MARK
async def test_order_proc_retrieve_many(
        mongodb,
        yt_apply,
        taxi_order_archive,
        doc_ids,
        lookup_yt,
        expected_status,
        expected_docs,
):
    response = await taxi_order_archive.post(
        'v1/order_proc/bulk-retrieve',
        json={'ids': doc_ids, 'lookup_yt': lookup_yt},
    )
    assert response.status_code == expected_status
    if expected_status != 200:
        assert response.content == b''
    else:
        result = bson.BSON(response.content).decode()
        docs = {doc['doc']['_id']: doc['doc'] for doc in result['items']}
        assert docs == expected_docs


@_YT_MARK
@pytest.mark.servicetest
async def test_service(mongodb, yt_apply, taxi_order_archive):
    pass

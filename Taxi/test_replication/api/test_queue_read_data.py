# pylint: disable=protected-access
import base64
import datetime
import json

import bson
import pytest

from replication.api import queue_read_data


ALL_ITEMS = [
    {
        'data': (
            '{"decimal_value": {"$decimal": "123.222"}, '
            '"id": "id_1", "value": "test1"}'
        ),
        'id': 'id_1',
        'upload_ts': '2020-02-01T12:00:00+0000',
    },
    {
        'data': (
            '{"decimal_value": {"$decimal": "123.221"}, '
            '"id": "id_2", "value": "test2"}'
        ),
        'id': 'id_2',
        'upload_ts': '2020-02-01T20:00:00+0000',
    },
    {
        'data': '{"id": "id_3"}',
        'id': 'id_3',
        'upload_ts': '2020-02-01T21:00:00+0000',
    },
]

ALL_ITEMS_RAW = [
    {
        'id': 'id_1',
        'upload_ts': '2020-02-01T12:00:00+0000',
        'data': (
            '{"decimal_value": {"$a": {"raw_type": "decimal"}, '
            '"$v": "123.222"}, "id": "id_1", "value": "test1"}'
        ),
    },
    {
        'id': 'id_2',
        'upload_ts': '2020-02-01T20:00:00+0000',
        'data': (
            '{"decimal_value": {"$a": {"raw_type": "decimal"}, '
            '"$v": "123.221"}, "id": "id_2", "value": "test2"}'
        ),
    },
    {
        'id': 'id_3',
        'upload_ts': '2020-02-01T21:00:00+0000',
        'data': '{"id": "id_3"}',
    },
]


@pytest.mark.parametrize(
    'rule_name, query, status, expected',
    [
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_not_found'], 'limit': 2},
            404,
            {
                'message': 'Rules not found',
                'code': 'read-data-error',
                'details': {
                    'rule_name': 'test_sharded_pg',
                    'raw_error': (
                        'Not found replication rules for rule '
                        'test_sharded_pg, target names: '
                        'test_sharded_pg_not_found, '
                        'suitable target types: ext'
                    ),
                },
            },
        ),
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_ext_yammy'], 'limit': 2},
            200,
            {
                'confirm_id': 'dummy_id',
                'items': [],
                'count': 0,
                'output_format': 'json',
                'try_next_read_after': (
                    queue_read_data._DEFAULT_NEXT_TRY_AFTER_SECONDS
                ),
            },
        ),
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_ext_hahn'], 'limit': 2},
            200,
            {
                'confirm_id': 'dummy_id',
                'items': [
                    {
                        'data': (
                            '{"decimal_value": {"$decimal": "123.221"}, '
                            '"id": "id_2", "value": "test2"}'
                        ),
                        'id': 'id_2',
                        'upload_ts': '2020-02-01T20:00:00+0000',
                    },
                    {
                        'data': '{"id": "id_3"}',
                        'id': 'id_3',
                        'upload_ts': '2020-02-01T21:00:00+0000',
                    },
                ],
                'count': 2,
                'last_upload_ts': '2020-02-01T21:00:00+0000',
                'output_format': 'json',
            },
        ),
        (
            'test_polygons_raw_pg',
            {'targets': ['test_polygons_raw_pg_raw_ext']},
            200,
            {
                'confirm_id': 'dummy_id',
                'items': ALL_ITEMS_RAW,
                'count': len(ALL_ITEMS_RAW),
                'last_upload_ts': '2020-02-01T21:00:00+0000',
                'output_format': 'raw_json',
                'try_next_read_after': (
                    queue_read_data._DEFAULT_NEXT_TRY_AFTER_SECONDS
                ),
            },
        ),
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_ext_arni']},
            200,
            {
                'confirm_id': 'dummy_id',
                'items': ALL_ITEMS,
                'count': len(ALL_ITEMS),
                'last_upload_ts': '2020-02-01T21:00:00+0000',
                'output_format': 'json',
                'try_next_read_after': (
                    queue_read_data._DEFAULT_NEXT_TRY_AFTER_SECONDS
                ),
            },
        ),
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_ext_disabled'], 'limit': 2},
            410,
            {
                'code': 'inactive-target-error',
                'details': {
                    'raw_error': (
                        'State disabled: ReplicationStateExternal('
                        'queue_mongo-staging_test_sharded_pg-ext-'
                        'test_sharded_pg_ext_disabled: disabled)'
                    ),
                    'rule_name': 'test_sharded_pg',
                },
                'message': 'Found inactive states',
            },
        ),
        (
            'test_sharded_pg',
            {'targets': ['test_sharded_pg_ext_not_initialized'], 'limit': 2},
            410,
            {
                'code': 'inactive-target-error',
                'details': {
                    'raw_error': (
                        'State uninitialized: ReplicationStateExternal('
                        'queue_mongo-staging_test_sharded_pg-ext-'
                        'test_sharded_pg_ext_not_initialized: not initialized)'
                    ),
                    'rule_name': 'test_sharded_pg',
                },
                'message': 'Found inactive states',
            },
        ),
        (
            'test_sharded_mongo_sharded_queue',
            {'targets': ['test_sharded_mongo_sharded_queue_ext'], 'limit': 2},
            400,
            {
                'code': 'read-data-error',
                'details': {'rule_name': 'test_sharded_mongo_sharded_queue'},
                'message': (
                    'Sharded queue unsupported without queue_partition param'
                ),
            },
        ),
        (
            'test_sharded_mongo_sharded_queue',
            {
                'targets': ['test_sharded_mongo_sharded_queue_ext'],
                'queue_partition': '0_4',
                'limit': 2,
            },
            200,
            {
                'confirm_id': 'dummy_id',
                'items': [
                    {
                        'id': 'id_1',
                        'upload_ts': '2020-02-01T12:00:00+0000',
                        'data': 'EwAAAAJfaWQABQAAAGlkXzEAAA==',
                    },
                    {
                        'id': 'id_2',
                        'upload_ts': '2020-02-01T20:00:00+0000',
                        'data': 'EwAAAAJfaWQABQAAAGlkXzIAAA==',
                    },
                ],
                'count': 2,
                'last_upload_ts': '2020-02-01T20:00:00+0000',
                'output_format': 'bson_base64',
            },
        ),
        (
            'test_sharded_mongo_sharded_queue',
            {
                'targets': ['test_sharded_mongo_sharded_queue_ext'],
                'queue_partition': '1_4',
                'limit': 2,
            },
            200,
            {
                'confirm_id': 'dummy_id',
                'items': [
                    {
                        'id': 'id_4',
                        'upload_ts': '2020-02-01T20:00:00+0000',
                        'data': 'EwAAAAJfaWQABQAAAGlkXzQAAA==',
                    },
                ],
                'count': 1,
                'last_upload_ts': '2020-02-01T20:00:00+0000',
                'output_format': 'bson_base64',
                'try_next_read_after': (
                    queue_read_data._DEFAULT_NEXT_TRY_AFTER_SECONDS
                ),
            },
        ),
    ],
)
@pytest.mark.config(
    REPLICATION_WEB_CTL={
        'runtime': {
            'raw_queue_read': {
                'disable_all': False,
                'excluded_rules': ['test_sharded_pg'],
            },
            'read_data_use_pool_executor': True,
        },
    },
)
async def test_read_data(
        monkeypatch, replication_client, rule_name, query, status, expected,
):
    monkeypatch.setattr(
        queue_read_data, '_generate_confirm_id', lambda: 'dummy_id',
    )
    response = await replication_client.post(
        f'/v1/queue/read/{rule_name}', data=json.dumps(query),
    )
    assert response.status == status, await response.text()
    response_json = await response.json()
    assert response_json == expected
    if response_json.get('output_format') == 'bson_base64':
        for item in response_json['items']:
            bson.BSON(base64.b64decode(item['data'])).decode()


_CONFIRM_IDS_SEQUENCE = (
    'confirm_id_1',
    'confirm_id_2',
    'confirm_id_3',
    'confirm_id_4',
    'confirm_id_5',
    'confirm_id_6',
)


@pytest.mark.parametrize('limit', [2, 3, 4])
async def test_integration_read_data(
        monkeypatch, replication_client, replication_app, limit,
):
    confirm_ids = iter(_CONFIRM_IDS_SEQUENCE)
    monkeypatch.setattr(
        queue_read_data, '_generate_confirm_id', lambda: next(confirm_ids),
    )

    states_wrapper = replication_app.rule_keeper.states_wrapper
    state = states_wrapper.get_state(
        source_id='queue_mongo-staging_test_sharded_pg',
        target_id='ext-test_sharded_pg_ext_disabled',
    )
    await state.enable()

    all_items = {}

    async def _read_chunk():
        return await replication_client.post(
            '/v1/queue/read/test_sharded_pg',
            data=json.dumps(
                {'targets': ['test_sharded_pg_ext_disabled'], 'limit': limit},
            ),
        )

    async def _confirm_chunk(confirm_id):
        return await replication_client.post(
            '/v1/queue/confirm/test_sharded_pg',
            data=json.dumps(
                {
                    'targets': ['test_sharded_pg_ext_disabled'],
                    'confirm_id': confirm_id,
                },
            ),
        )

    assert state._confirm_id is None
    previous_items = None
    for query_num, expected_confirm_id in enumerate(_CONFIRM_IDS_SEQUENCE):
        response = await _read_chunk()
        assert response.status == 200, await response.text()
        assert response.headers['X-Replication-Output-Format'] == 'json'
        response_body = await response.json()
        confirm_id = response_body['confirm_id']
        assert confirm_id == expected_confirm_id
        assert state._confirm_id == confirm_id

        items = response_body['items']
        assert len(items) <= limit
        for item in items:
            all_items[item['id']] = item

        # Two readings, one confirm
        if query_num % 2 == 1:
            if previous_items is not None:
                assert previous_items == items, query_num

            assert state._last_stamp_draft is not None
            response = await _confirm_chunk(confirm_id)
            assert state._confirm_id == confirm_id
            assert state._last_stamp_draft is None

            assert response.status == 200, await response.text()
            response_json = await response.json()
            assert response_json['confirm_id'] == confirm_id

            # double confirm is 200
            await _assert_confirm_race(
                await _confirm_chunk(confirm_id), fail=False,
            )
            assert state._confirm_id == confirm_id
        else:
            await _assert_confirm_race(await _confirm_chunk('bad_id'))
            assert state._confirm_id == confirm_id

        previous_items = items

    with pytest.raises(StopIteration):
        next(confirm_ids)

    assert all_items == {item['id']: item for item in ALL_ITEMS}

    await _assert_confirm_race(await _confirm_chunk('bad_id'))

    assert state._confirm_id == _CONFIRM_IDS_SEQUENCE[-1]
    assert state.last_replication == datetime.datetime(2020, 2, 1, 21, 0)
    assert state._last_stamp_draft is None


async def _assert_confirm_race(response, fail=True):
    response_body = await response.json()
    if not fail:
        assert response.status == 200
        return
    raw_error = response_body['details']['raw_error']
    assert 'confirm id is not valid' in raw_error


_REPLICATION_WEB_CTL = {
    'runtime': {
        'read_data_left_bound_gap': {'__default__': 5, 'rule_name1': 10},
        'read_data_right_bound_gap': {'__default__': 5, 'rule_name2': 10},
    },
}
_START_STAMP = datetime.datetime(2020, 1, 2, 20, 11, 10)


@pytest.mark.parametrize(
    'bound, expected,',
    [
        pytest.param(
            _START_STAMP,
            _START_STAMP,
            marks=pytest.mark.config(REPLICATION_WEB_CTL=_REPLICATION_WEB_CTL),
        ),
        pytest.param(
            datetime.datetime(2020, 1, 2, 20, 11, 20),
            datetime.datetime(2020, 1, 2, 20, 11, 15),  # half of delta
            marks=pytest.mark.config(REPLICATION_WEB_CTL=_REPLICATION_WEB_CTL),
        ),
        pytest.param(
            datetime.datetime(2020, 1, 2, 20, 11, 15),
            datetime.datetime(2020, 1, 2, 20, 11, 12),  # round microseconds
            marks=pytest.mark.config(REPLICATION_WEB_CTL=_REPLICATION_WEB_CTL),
        ),
        pytest.param(
            datetime.datetime(2020, 1, 2, 20, 11, 35),
            datetime.datetime(2020, 1, 2, 20, 11, 25),
            marks=pytest.mark.config(REPLICATION_WEB_CTL=_REPLICATION_WEB_CTL),
        ),
        pytest.param(
            datetime.datetime(2020, 1, 2, 20, 11, 35),
            datetime.datetime(2020, 1, 2, 20, 11, 35),
            marks=pytest.mark.config(REPLICATION_WEB_CTL={}),
        ),
        pytest.param(
            datetime.datetime(2020, 1, 2, 20, 11, 35),
            datetime.datetime(2020, 1, 2, 20, 11, 25),
            marks=pytest.mark.config(
                REPLICATION_WEB_CTL={
                    'runtime': {
                        'read_data_left_bound_gap': {
                            '__default__': 10,
                            'rule_name_x': 20,
                        },
                        'read_data_right_bound_gap': {
                            '__default__': 10,
                            'rule_name_x': 20,
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.now(_START_STAMP.isoformat())
def test_get_bound_gap(replication_ctx, bound, expected):
    new_last_upload_ts = queue_read_data._with_left_bound_gap(
        replication_ctx.config,
        last_upload_ts=bound,
        rule_name='rule_name1',
        start_stamp=_START_STAMP,
    )
    assert new_last_upload_ts == expected

    new_end_stamp = queue_read_data._with_end_bound_gap(
        replication_ctx.config,
        end_stamp=bound,
        rule_name='rule_name2',
        start_stamp=_START_STAMP,
    )
    assert new_end_stamp == expected

    assert new_last_upload_ts <= new_end_stamp

import datetime
import decimal

import pytest

from replication_core.raw_types import yson_conversion


NOW = datetime.datetime(2018, 11, 26, 0)

_RAW_JSON_ID1 = (
    '{"created_at": {"$a": {"raw_type": "datetime"},'
    ' "$v": "2018-11-24T10:00:00"}, "id": "_id_1_", '
    '"polygon_data": {"$a": '
    '{"raw_type": "pg_polygon"}, '
    '"$v": [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], '
    '[4.0, 1.0]]}, "range_dttm": {"$a": '
    '{"raw_type": "pg_range"}, "$v": {"lower": {"$a": {"raw_type": '
    '"datetime"}, "$v": "2020-05-20T10:00:00"}, "lower_inc": false, '
    '"upper": null, "upper_inc": false}}, "total": {"$a": '
    '{"raw_type": "decimal"}, "$v": "0.000000"}}'
)

_RAW_JSON_ID2 = (
    '{"created_at": {"$a": {"raw_type": "datetime"},'
    ' "$v": "2018-11-24T11:00:00"}, "id": "_id_2_", '
    '"polygon_data": {"$a": '
    '{"raw_type": "pg_polygon"}, "$v": '
    '[[0.1, 20.0], [20.0, 30.0], [30.0, 0.1]]}, "range_dttm": {"$a": '
    '{"raw_type": "pg_range"}, "$v": {"lower": null, "lower_inc": false, '
    '"upper": null, "upper_inc": false}}, '
    '"total": {"$a": {"raw_type": "decimal"}, '
    '"$v": "1.000001"}}'
)

_PG_DATA = {
    '_id_1_': {
        '__raw_json': _RAW_JSON_ID1,
        '_id': '_id_1_',
        'created': datetime.datetime(2018, 11, 26, 0, 0),
        'data': {
            'created_at': datetime.datetime(2018, 11, 24, 10, 0),
            'id': '_id_1_',
            'polygon_data': [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 1.0]],
            'total': decimal.Decimal('0.000000'),
            'range_dttm': {
                'lower': datetime.datetime(2020, 5, 20, 10, 0),
                'lower_inc': False,
                'upper': None,
                'upper_inc': False,
            },
        },
        'updated': datetime.datetime(2018, 11, 26, 0, 0),
        'v': 3,
    },
    '_id_2_': {
        '__raw_json': _RAW_JSON_ID2,
        '_id': '_id_2_',
        'created': datetime.datetime(2018, 11, 26, 0, 0),
        'data': {
            'created_at': datetime.datetime(2018, 11, 24, 11, 0),
            'id': '_id_2_',
            'polygon_data': [[0.1, 20.0], [20.0, 30.0], [30.0, 0.1]],
            'total': decimal.Decimal('1.000001'),
            'range_dttm': {
                'lower': None,
                'lower_inc': False,
                'upper': None,
                'upper_inc': False,
            },
        },
        'updated': datetime.datetime(2018, 11, 26, 0, 0),
        'v': 2,
    },
}
_EXPECTED_YT = {
    'polygons': {
        '_id_1_': {
            'id': '_id_1_',
            'polygon_data': [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 1.0]],
        },
        '_id_2_': {
            'id': '_id_2_',
            'polygon_data': [[0.1, 20.0], [20.0, 30.0], [30.0, 0.1]],
        },
    },
    'polygons_raw': {
        '_id_1_': {
            'id': '_id_1_',
            'etl_updated': '2018-11-26T00:00:00',
            'custom_raw_doc': yson_conversion.json_to_yson_obj(_RAW_JSON_ID1),
        },
        '_id_2_': {
            'id': '_id_2_',
            'etl_updated': '2018-11-26T00:00:00',
            'custom_raw_doc': yson_conversion.json_to_yson_obj(_RAW_JSON_ID2),
        },
    },
}


@pytest.mark.pgsql('conditioned', files=['polygons.sql'])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'rule_name, expected_error, expected_queue, expected_yt',
    [pytest.param('pg_polygons', None, _PG_DATA, _EXPECTED_YT)],
)
async def test_pg_data_types(
        yt_clients_storage,
        run_replication,
        patch_queue_current_date,
        rule_name,
        expected_error,
        expected_queue,
        expected_yt,
):
    if expected_error is not None:
        with pytest.raises(expected_error):
            await run_replication(rule_name)
    else:
        with yt_clients_storage() as all_clients:
            targets_data = await run_replication(rule_name)
        queue_docs = targets_data.queue_data_by_id(drop_confirmations=True)

        assert (
            queue_docs == expected_queue
        ), f'pg replication to queue failed for {rule_name}'

        for cluster in ['hahn', 'arni']:
            assert all_clients[cluster].rows_by_ids == expected_yt

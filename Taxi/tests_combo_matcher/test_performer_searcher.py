import json

import pytest

import tests_combo_matcher.utils as utils

CANDIDATES = {
    'order_id0': {
        'candidates': [
            {
                'dbid': 'dbid0',
                'uuid': 'uuid0',
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 43,
                    'distance': 43,
                    'approximate': False,
                },
            },
            {
                'dbid': 'dbid0',
                'uuid': 'uuid1',
                'id': 'dbid0_uuid1',
                'route_info': {
                    'time': 43,
                    'distance': 43,
                    'approximate': False,
                },
            },
            {
                'dbid': 'dbid0',
                'uuid': 'uuid2',
                'id': 'dbid0_uuid2',
                'route_info': {
                    'time': 43,
                    'distance': 43,
                    'approximate': False,
                },
            },
        ],
    },
    'order_id1': {
        'candidates': [
            {
                'dbid': 'dbid0',
                'uuid': 'uuid1',
                'id': 'dbid0_uuid1',
                'route_info': {
                    'time': 430,
                    'distance': 430,
                    'approximate': False,
                },
            },
            {
                'dbid': 'dbid0',
                'uuid': 'uuid2',
                'id': 'dbid0_uuid2',
                'route_info': {
                    'time': 430,
                    'distance': 430,
                    'approximate': False,
                },
            },
            {
                'dbid': 'dbid0',
                'uuid': 'uuid3',
                'id': 'dbid0_uuid3',
                'route_info': {
                    'time': 430,
                    'distance': 430,
                    'approximate': False,
                },
            },
        ],
    },
}


async def test_performer_searcher(
        taxi_combo_matcher, mockserver, load_json, load, pgsql, testpoint,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        request_json = json.loads(request.get_data())
        order_id = request_json['order_id']
        request_json = {
            key: request_json[key]
            for key in request_json.keys() - {'order_id'}
        }

        assert request_json == {
            'zone_id': 'moscow',
            'allowed_classes': ['econom'],
            'point': [37.63, 55.74],
        }

        return mockserver.make_response(json=CANDIDATES[order_id], status=200)

    @mockserver.json_handler('/lookup/event')
    def _lookup_event(data):
        request = json.loads(data.get_data())
        assert request['status'] == 'found'
        assert request['candidate'] == {
            'dbid': 'dbid0',
            'id': 'dbid0_uuid2',
            'route_info': {'approximate': False, 'distance': 43, 'time': 43},
            'uuid': 'uuid2',
        }
        return {'success': True}

    @testpoint('log_performer_match_to_yt')
    def log_to_yt(data):
        return data

    sql_query = load('setup.sql').format(
        callback_url=mockserver.url('/lookup/event'),
    )
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(sql_query)

    await taxi_combo_matcher.run_task('performer-searcher')

    matchings = await utils.select_matchings(pgsql)

    assert matchings == [
        {'id': 0, 'orders': ['order_id0', 'order_id1'], 'performer': None},
    ]

    order_meta = await utils.select_order_meta(pgsql)

    assert sorted(order_meta, key=lambda x: x['order_id']) == [
        {
            'order_id': 'order_id0',
            'revision': 1,
            'status': 'dispatched',
            'matching_id': 0,
            'candidate': {
                'dbid': 'dbid0',
                'id': 'dbid0_uuid2',
                'route_info': {
                    'approximate': False,
                    'distance': 43,
                    'time': 43,
                },
                'uuid': 'uuid2',
            },
            'times_matched': 0,
            'times_dispatched': 1,
        },
        {
            'order_id': 'order_id1',
            'revision': 1,
            'status': 'performer_found',
            'matching_id': 0,
            'candidate': {
                'dbid': 'dbid0',
                'id': 'dbid0_uuid2',
                'route_info': {
                    'approximate': False,
                    'distance': 430,
                    'time': 430,
                },
                'uuid': 'uuid2',
            },
            'times_matched': 0,
            'times_dispatched': 0,
        },
    ]

    assert log_to_yt.times_called == 1
    match_log = log_to_yt.next_call()['data']
    match_log.pop('timestamp')
    assert match_log == {'matching_id': 0, 'dbid_uuid': 'dbid0_uuid2'}


async def test_candidates_requests_partially_failed(
        taxi_combo_matcher, mockserver, load_json, load, pgsql,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        request_json = json.loads(request.get_data())
        order_id = request_json['order_id']
        status = 500 if order_id == 'order_id0' else 200
        return mockserver.make_response(
            json=CANDIDATES[order_id], status=status,
        )

    sql_query = load('setup.sql').format(
        callback_url=mockserver.url('/lookup/event'),
    )
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(sql_query)

    await taxi_combo_matcher.run_task('performer-searcher')

    matchings = await utils.select_matchings(pgsql)

    assert matchings == [
        {'id': 0, 'orders': ['order_id0', 'order_id1'], 'performer': None},
    ]

    order_meta = await utils.select_order_meta(pgsql)

    assert sorted(order_meta, key=lambda x: x['order_id']) == [
        {
            'order_id': 'order_id0',
            'revision': 0,
            'status': 'matched',
            'matching_id': 0,
            'candidate': None,
            'times_matched': 0,
            'times_dispatched': 0,
        },
        {
            'order_id': 'order_id1',
            'revision': 0,
            'status': 'matched',
            'matching_id': 0,
            'candidate': None,
            'times_matched': 0,
            'times_dispatched': 0,
        },
    ]

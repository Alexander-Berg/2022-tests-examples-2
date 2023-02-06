import copy
import json

import pytest

from tests_order_search_status import eventus_tools
from tests_order_search_status import utils

ETALON_1 = {
    'order_1': [
        {'iteration': 0, 'driver_ids': ['dbid_uuid1']},
        {'iteration': 0, 'driver_ids': ['dbid_uuid2']},
        {'iteration': 1, 'driver_ids': ['dbid_uuid1']},
        {'iteration': 1, 'driver_ids': ['dbid_uuid2']},
        {'iteration': 1, 'driver_ids': ['dbid_uuid2']},
    ],
    'order_2': [{'iteration': 2, 'driver_ids': ['dbid_uuid1']}],
    'order_3': [{'iteration': 2, 'driver_ids': ['dbid_uuid2']}],
}

ETALON_7 = {
    'order_1': [
        {
            'iteration': 1,
            'driver_ids': ['dbid_uuid1', 'dbid_uuid2', 'dbid_uuid2'],
        },
    ],
    'order_2': [{'iteration': 2, 'driver_ids': ['dbid_uuid1']}],
    'order_3': [{'iteration': 2, 'driver_ids': ['dbid_uuid2']}],
}


@pytest.mark.parametrize(
    'bulk_size_threshold,etalon', [(1, ETALON_1), (7, ETALON_7)],
)
async def test_multioffer_rejects(
        taxi_order_search_status,
        testpoint,
        taxi_eventus_orchestrator_mock,
        bulk_size_threshold,
        etalon,
        redis_store,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_search_status,
        eventus_tools.create_rejects_pipeline(
            bulk_size_threshold=bulk_size_threshold,
        ),
    )

    events = [
        utils.generate_event('any', 'any', 'multioffer_seen_timeout'),
        utils.generate_event('any', 'any', 'multioffer_seen'),
        utils.generate_event('any', 'any', 'multioffer_accept'),
        utils.generate_event('any', 'any', 'multioffer_win'),
        utils.generate_event('any', 'any', 'multioffer_lose'),
        # previous iteration
        utils.generate_event(
            'order_1',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 0}},
        ),
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 0}},
        ),
        # actual iteration
        utils.generate_event(
            'order_1',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        utils.generate_event(
            'order_4', 'uuid2', 'multioffer_reject', {'auction': 'not_object'},
        ),
        # duplicate
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        # other cases
        utils.generate_event(
            'order_2',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 2}},
        ),
        utils.generate_event(
            'order_3',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 2}},
        ),
        utils.generate_event(
            'order_5',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 'not_int'}},
        ),
    ]

    copy_etalon = copy.deepcopy(etalon)

    @testpoint('multioffer_reject')
    def multioffer_reject_testpoint(data):
        nonlocal copy_etalon
        for order_id, event in data.items():
            event['driver_ids'].sort()
            order_etalons = copy_etalon[order_id]
            idx = order_etalons.index(event)
            del order_etalons[idx]
            if not order_etalons:
                del copy_etalon[order_id]

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    response = await taxi_order_search_status.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-search-status-rejects',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    await multioffer_reject_testpoint.wait_call()
    await commit.wait_call()
    assert not copy_etalon

    etalon = {
        'order_1:auction:1': ['dbid_uuid1', 'dbid_uuid2'],
        'order_2:auction:2': ['dbid_uuid1'],
        'order_3:auction:2': ['dbid_uuid2'],
    }
    if bulk_size_threshold == 1:
        etalon['order_1:auction:0'] = ['dbid_uuid1', 'dbid_uuid2']

    utils.check_redis_auction_values(redis_store, etalon)

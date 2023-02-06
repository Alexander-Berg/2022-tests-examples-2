# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=import-only-modules
import base64
import json

from driver_route_watcher_ng_plugins import *  # noqa: F403 F401
from logbroker_consumer.logbroker import logbroker_helper  # noqa: F401 C5521
import pytest

from tests_driver_route_watcher.utils import wrap_with_env


# pylint: disable=redefined-outer-name
@pytest.fixture
def driver_route_watcher_ng_adv(
        taxi_driver_route_watcher_ng,
        logbroker_helper,  # noqa: F811
        redis_store,
        taxi_driver_route_watcher_ng_aiohttp,
        testpoint,
):
    return wrap_with_env(
        taxi_driver_route_watcher_ng,
        redis_store,
        logbroker_helper,
        taxi_driver_route_watcher_ng_aiohttp,
        testpoint,
    )


@pytest.fixture(autouse=True)
def contractor_transport_request(mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '123456_4':
            return {'contractors_transport': [], 'cursor': '1234567_4'}
        data = {
            'contractors_transport': [
                {
                    'contractor_id': 'dbid_uuidpedestrian',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'park3_driver3',
                    'is_deleted': False,
                    'revision': '1234567_3',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
                {
                    'contractor_id': 'park4_driver4',
                    'is_deleted': False,
                    'revision': '1234567_4',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car4'},
                },
            ],
            'cursor': '1234567_4',
        }
        return mockserver.make_response(response=json.dumps(data))


@pytest.fixture
def make_redis_state_empty(load_json, redis_store):
    watch_fields = {
        x: base64.b64decode(y)
        for x, y in load_json('empty_service_id_watches_dump.json').items()
    }
    output_fields = {
        x: base64.b64decode(y)
        for x, y in load_json('empty_service_id_output_dump.json').items()
    }
    cmds = [
        ['flushall'],
        ['hmset', 'w/{dbid_uuidrestoreempty}', watch_fields],
        [
            'hset',
            'output:{dbid_uuidrestoreempty}',
            'output',
            output_fields['output'],
        ],
    ]
    for cmd in cmds:
        method = cmd[0]
        args = cmd[1:]
        getattr(redis_store, method)(*args)

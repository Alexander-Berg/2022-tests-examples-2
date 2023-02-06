import json

import pytest

from . import utils

DRIVER_HEADERS = {
    'X-Yandex-Login': 'vdovkin',
    'X-YaTaxi-Park-Id': 'park_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver_0',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.37 (1234)',
    'X-Request-Platform': 'android',
    'Accept-Language': 'ru',
}
ZONE_TO_COORDS = {
    'moscow': {'lon': 37.627920, 'lat': 55.744094, 'timestamp': 123},
    'spb': {'lon': -10, 'lat': -10, 'timestamp': 123},
}


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_activate.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_promocodes_enabled',
    consumers=['driver-promocodes/driver'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.parametrize(
    'promocode_id,classes,zone,zone_fallback,tags,request_tags,is_good,'
    'response_list',
    [
        # ok
        (
            'promocode_ok',
            ['econom', 'comfort'],
            'moscow',
            None,
            ['tag_no_group'],
            None,
            True,
            'response_list_after.json',
        ),
        # already has active commission promocode
        (
            'promocode_ok',
            ['econom', 'comfort'],
            'moscow',
            None,
            ['commission_promocode'],
            None,
            False,
            None,
        ),
        # already has active tag promocode
        (
            'promocode_tag_ok',
            ['econom', 'comfort'],
            'moscow',
            None,
            ['tag_no_group', 'tag_3_group_1'],
            None,
            False,
            None,
        ),
        # promocode tag ok
        (
            'promocode_tag_ok',
            ['econom', 'comfort'],
            'moscow',
            None,
            {'tag_group_1': {'ttl': '2020-06-01T10:50:00+0000'}},
            'request_tags.json',
            True,
            None,
        ),
        # expired
        (
            'promocode_expired',
            ['econom', 'comfort'],
            'moscow',
            None,
            [],
            None,
            False,
            None,
        ),
        # not exists
        (
            'unknown',
            ['econom', 'comfort'],
            'moscow',
            None,
            [],
            None,
            False,
            None,
        ),
        # wrong tariffs
        (
            'promocode_ok',
            ['comfort_plus'],
            'moscow',
            None,
            [],
            None,
            False,
            None,
        ),
        # wrong zone
        (
            'promocode_ok',
            ['econom', 'comfort'],
            'spb',
            None,
            [],
            None,
            False,
            None,
        ),
        # wrong driver
        (
            'promocode_wrong_driver',
            ['econom', 'comfort'],
            'moscow',
            None,
            [],
            None,
            False,
            None,
        ),
        # activated
        (
            'promocode_activated',
            ['econom', 'comfort'],
            'moscow',
            None,
            [],
            None,
            False,
            None,
        ),
        # zone fallback
        (
            'promocode_ok',
            ['econom', 'comfort'],
            None,
            'moscow',
            [],
            None,
            True,
            'response_list_after.json',
        ),
    ],
)
async def test_driver_promocodes_activation(
        taxi_driver_promocodes,
        stq,
        stq_runner,
        parks,
        load_json,
        mockserver,
        driver_tags_mocks,
        promocode_id,
        classes,
        zone,
        zone_fallback,
        tags,
        request_tags,
        is_good,
        response_list,
):
    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'uuid': 'driver_0',
                    'dbid': 'park_0',
                    'position': [33.0, 55.0],
                    'classes': classes,
                },
            ],
        }

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        if request_tags:
            assert json.loads(request.get_data()) == load_json(request_tags)
        return {}

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        if zone_fallback:
            return mockserver.make_response(
                json={
                    'position': ZONE_TO_COORDS[zone_fallback],
                    'type': 'raw',
                },
                status=200,
            )
        return mockserver.make_response(
            json={'message': 'Not found'}, status=404,
        )

    if isinstance(tags, list):
        driver_tags_mocks.set_tags_info('park_0', 'driver_0', tags)
    else:
        driver_tags_mocks.set_tags_info('park_0', 'driver_0', None, tags)

    body = {'id': promocode_id}
    if zone:
        body['position'] = ZONE_TO_COORDS[zone]
    response = await taxi_driver_promocodes.post(
        'driver/v1/promocodes/v1/activate-by-id',
        json=body,
        headers=DRIVER_HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    if response_list:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list', params={'id': promocode_id},
        )
        assert utils.remove_not_testable_promocodes(
            response.json(),
        ) == utils.remove_not_testable_promocodes(load_json(response_list))

    if request_tags:
        assert stq.driver_promocodes_upload_tags.times_called == 1
        await utils.call_tags_task(stq, stq_runner)

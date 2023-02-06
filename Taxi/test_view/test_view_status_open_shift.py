import pytest

from tests_driver_fix import common

MODE_INFO_RESPONSE = {
    'mode': {
        'name': 'driver_fix',
        'started_at': '2019-01-01T08:00:00+0300',
        'features': [
            {
                'name': 'driver_fix',
                'settings': {
                    'rule_id': 'subvention_rule_id',
                    'shift_close_time': '00:00:00+03:00',
                },
            },
            {'name': 'tags'},
        ],
    },
}

HEADERS = common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY.copy()
HEADERS.update({'Accept-Language': 'ru'})

REDIS_SHIFT_OPENED_KEY = 'dbid_uuid:shift_open'


def _set_shift_opened_value(redis_store, value):
    redis_store.set(REDIS_SHIFT_OPENED_KEY, value)


def _get_shift_opened_value(redis_store):
    bytestr = redis_store.get(REDIS_SHIFT_OPENED_KEY)
    return bytestr.decode() if bytestr is not None else None


@pytest.mark.parametrize(
    'init_mark_in_redis_value,'
    'expected_mark_in_redis_value,expect_called_shifts_open',
    [
        pytest.param(
            # init_mark_in_redis_value
            0,
            # expected_mark_in_redis_value
            '2018-12-31T21:00:00+0000|2019-01-01T05:00:00+0000',
            # expect_called_shifts_open
            1,
            id='open_shift_for_the_first_time',
        ),
        pytest.param(
            # init_mark_in_redis_value
            '2018-12-31T21:00:00+0000|2019-01-01T05:00:00+0000',
            # expected_markl_in_redis_value
            '2018-12-31T21:00:00+0000|2019-01-01T05:00:00+0000',
            # expect_called_shifts_open
            0,
            id='dont_open_shift_as_it_is_already_used',
        ),
        pytest.param(
            # init_mark_in_redis_value
            '2018-12-31T21:00:00+0000|2019-01-01T03:00:00+0000',
            # expected_mark_in_redis_value
            '2018-12-31T21:00:00+0000|2019-01-01T03:00:00+0000',
            # expect_called_shifts_open
            0,
            id='reopen_shift_after_unsubscription',
        ),
    ],
)
@pytest.mark.parametrize(
    'request_args',
    [
        pytest.param(
            {
                'path': 'v1/view/status',
                'params': {
                    'tz': 'Europe/Moscow',
                    'park_id': 'dbid',
                    'lon': 37.63361316,
                    'lat': 55.75419758,
                },
                'headers': HEADERS,
            },
            id='v1/view/status',
        ),
        pytest.param(
            {
                'path': 'v1/internal/status',
                'params': {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid',
                    'language': 'ru',
                },
                'headers': HEADERS,
            },
            id='v1/intenal/status',
        ),
    ],
)
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_open_shift(
        load_json,
        taxi_config,
        testpoint,
        taxi_driver_fix,
        redis_store,
        mockserver,
        mock_offer_requirements,
        unique_drivers,
        request_args,
        init_mark_in_redis_value,
        expected_mark_in_redis_value,
        expect_called_shifts_open,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    taxi_config.set_values(
        {
            'DRIVER_FIX_TRIGGER_SHIFT_OPENING': {
                'enabled': True,
                'shift_opened_mark_ttl_s': 86400,
            },
        },
    )

    # This testspoint must be registered to synchronize requests to redis
    @testpoint('wait_detached_operation')
    def _wait_detached_operation(data):
        pass

    @testpoint('wait_shift_open_task')
    def _wait_shift_open_task(data):
        pass

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {'subventions': []}

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return MODE_INFO_RESPONSE

    @mockserver.json_handler('/billing_subventions/v1/shifts/open')
    async def _shifts_open(request):
        assert request.json == {
            'driver': {
                'park_id': 'dbid',
                'driver_profile_id': 'uuid',
                'clid': 'nice_clid',
                'unique_driver_id': 'very_unique_id',
            },
            'as_of': '2019-01-01T09:00:00+00:00',
        }
        return {'doc_id': 123456}

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    if init_mark_in_redis_value is not None:
        _set_shift_opened_value(redis_store, init_mark_in_redis_value)

    response = await taxi_driver_fix.get(**request_args)

    assert response.status_code == 200

    if expect_called_shifts_open:
        await _wait_shift_open_task.wait_call()
        assert _shifts_open.times_called == 1

    assert _get_shift_opened_value(redis_store) == expected_mark_in_redis_value

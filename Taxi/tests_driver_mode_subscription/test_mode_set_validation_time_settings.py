from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

DRIVER_FIX_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00:00+03:00'}

_NOW = '2019-05-01T05:00:00+00:00'

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

HOURLY_RESTRICTION = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'hourly',
                'interval_count': 1,
                'max_change_count': 1,
            },
        ],
    },
}
HOURLY_RESTRICTION2 = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'hourly',
                'interval_count': 1,
                'max_change_count': 2,
            },
        ],
    },
}
TWO_HOURS_RESTRICTION = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'hourly',
                'interval_count': 2,
                'max_change_count': 1,
            },
        ],
    },
}
WEEK_HOURLY_RESTRICTION = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'hourly',
                'interval_count': 168,
                'max_change_count': 1,
            },
        ],
    },
}
DAYLY_RESTRICTION = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'dayly',
                'interval_count': 1,
                'max_change_count': 1,
            },
        ],
    },
}
THREE_DAYS_RESTRICTION = {
    'orders': {
        'restrictions': [
            {
                'interval_type': 'dayly',
                'interval_count': 3,
                'max_change_count': 1,
            },
        ],
    },
}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'set_by_session, docs, expect_success, restrictions, expect_retry_hours, '
    'time_check_history_calls',
    [
        pytest.param(
            False,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            True,
            HOURLY_RESTRICTION,
            1,
            1,  # 1 for current mode
            id='hourly_fail_1_hour_good_in_tvm',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            False,
            HOURLY_RESTRICTION,
            1,
            2,  # 1 for current mode, 1 for check
            id='hourly_fail_1_hour',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:01:00+03:00', 'orders'),
            ],
            False,
            HOURLY_RESTRICTION,
            1,
            2,  # 1 for current mode, 1 for check
            id='hourly_fail_1_hour_minus_minute',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:00:00+03:00', 'orders'),
            ],
            True,
            HOURLY_RESTRICTION,
            0,
            2,  # 1 for current mode, 1 for check
            id='hourly_success',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'driver_fix'),
            ],
            True,
            HOURLY_RESTRICTION,
            0,
            2,  # 1 for current mode, 1 for check
            id='hourly_success_fade',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            True,
            HOURLY_RESTRICTION2,
            0,
            2,  # 1 for current mode, 1 for check
            id='hourly2_success',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T02:02:00+03:00', 'orders'),
            ],
            False,
            TWO_HOURS_RESTRICTION,
            1,
            2,  # 1 for current mode, 1 for check
            id='hourly_2_hours_fail',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            False,
            TWO_HOURS_RESTRICTION,
            2,
            2,  # 1 for current mode, 1 for check
            id='hourly_2_hours_fail_2_fade',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:00:00+03:00', 'orders'),
            ],
            False,
            DAYLY_RESTRICTION,
            20,  # block subscription until end of the day
            2,  # 1 for current mode, 1 for check
            id='dayly_fail_20_fade',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-13T03:00:00+03:00', 'orders'),
            ],
            False,
            THREE_DAYS_RESTRICTION,
            44,  # 24 until next day and 20 until end of the day
            2,  # 1 for current mode, 1 for check
            id='dayly_3_days',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-13T23:59:00+03:00', 'orders'),
            ],
            True,
            DAYLY_RESTRICTION,
            0,
            2,  # 1 for current mode, 1 for check
            id='daily_',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T03:03:00+03:00', 'orders'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
                ('2019-11-14T03:01:00+03:00', 'driver_fix'),
            ],
            True,
            HOURLY_RESTRICTION2,
            0,
            1,  # 1 for current mode, 0 for check
            id='hourly2_set_same_mode',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T03:04:00+03:00', 'driver_fix'),
                ('2019-11-14T03:03:00+03:00', 'orders'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
                ('2019-11-14T03:01:00+03:00', 'orders'),
            ],
            True,
            HOURLY_RESTRICTION2,
            0,
            2,  # 1 for current mode, 1 for check
            id='hourly2_ignore_same_modes',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T03:06:00+03:00', 'driver_fix'),
                ('2019-11-14T03:05:00+03:00', 'custom_orders'),
                ('2019-11-14T03:04:00+03:00', 'driver_fix'),
                ('2019-11-14T03:03:00+03:00', 'custom_orders'),
                ('2019-11-14T03:02:00+03:00', 'driver_fix'),
                ('2019-11-14T03:01:00+03:00', 'custom_orders'),
            ],
            True,
            HOURLY_RESTRICTION,
            0,
            2,  # 1 for current mode, 1 for check
            id='hourly_ignore_other_modes',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T03:08:00+03:00', 'driver_fix'),
                ('2019-11-14T03:07:00+03:00', 'custom_orders'),
                ('2019-11-14T03:06:00+03:00', 'driver_fix'),
                ('2019-11-14T03:05:00+03:00', 'custom_orders'),
                ('2019-11-14T03:04:00+03:00', 'driver_fix'),
                ('2019-11-14T03:03:00+03:00', 'orders'),
                ('2019-11-14T03:02:00+03:00', 'driver_fix'),
                ('2019-11-14T03:01:00+03:00', 'custom_orders'),
            ],
            False,
            HOURLY_RESTRICTION,
            1,
            4,  # 1 for current mode, 3 for check
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_BR_READER_BULK_SIZE={'orders': 2},
                ),
            ],
            id='test_long_history_fail',
        ),
        pytest.param(
            True,
            [
                ('2019-11-14T03:08:00+03:00', 'driver_fix'),
                ('2019-11-14T03:07:00+03:00', 'custom_orders'),
                ('2019-11-14T03:06:00+03:00', 'driver_fix'),
                ('2019-11-14T03:05:00+03:00', 'custom_orders'),
                ('2019-11-14T02:04:00+03:00', 'driver_fix'),
                ('2019-11-14T02:03:00+03:00', 'custom_orders'),
                ('2019-11-14T02:02:00+03:00', 'driver_fix'),
                ('2019-11-14T02:01:00+03:00', 'custom_orders'),
            ],
            True,
            HOURLY_RESTRICTION,
            0,
            4,  # 1 for current mode, 3 for check
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_BR_READER_BULK_SIZE={'orders': 2},
                ),
            ],
            id='test_long_history_success',
        ),
    ],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_BR_READER_BULK_SIZE={'orders': 10},
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_time_validation_bad(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        docs,
        expect_success: bool,
        set_by_session: bool,
        restrictions,
        expect_retry_hours: int,
        time_check_history_calls: int,
):
    taxi_config.set_values(
        dict(DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS=restrictions),
    )

    history_chunk_size = taxi_config.get(
        'DRIVER_MODE_SUBSCRIPTION_BR_READER_BULK_SIZE',
    )['orders']

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    scenario.Scene.mock_driver_trackstory(mockserver, scenario.MOSCOW_POSITION)

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        chunk_num = int(request.json.get('cursor', '0'))

        docs_start = chunk_num * history_chunk_size
        docs_end = docs_start + history_chunk_size
        for occured, mode in docs[docs_start:docs_end]:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'dbid0',
                            'driver_profile_id': 'uuid0',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': 'some_id',
                            'shift_close_time': '00:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': f'{chunk_num + 1}'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )

    if expect_success:
        assert response.status_code == 200
    else:
        assert response.status_code == 423
        response_body = response.json()
        if set_by_session:
            assert response_body == {
                'code': 'TIME_VALIDATION_FAILED',
                'localized_message': (
                    'Вы слишком часто меняете режим, '
                    f'попробуйте через {expect_retry_hours} '
                    'часов'
                ),
                'localized_message_title': 'Слишком часто',
            }

        else:
            assert response_body['code'] == 'LOCKED'
            assert not response_body['message']
        assert 'details' not in response_body

    assert (
        _driver_mode_index_mode_history.times_called
        == time_check_history_calls
    )


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
@pytest.mark.parametrize(
    'fail_service',
    (
        pytest.param(False, id='success'),
        pytest.param(True, id='fail_dm_index_request'),
    ),
)
async def test_mode_set_time_validation_good(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        set_by_session: bool,
        fail_service: bool,
):
    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS=(
                HOURLY_RESTRICTION2
            ),
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        if fail_service:
            return {}
        documents = []

        docs = (
            ('2019-11-14T04:00:00+03:00', 'orders'),
            ('2019-11-14T03:00:00+03:00', 'driver_fix'),
        )
        for occured, mode in docs:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': 'some_id',
                            'shift_close_time': '00:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )

    if fail_service:
        if set_by_session:
            assert response.status_code == 503
            assert response.json() == {
                'code': 'SERVICE UNAVAILABLE',
                'message': '',
            }
        else:
            assert response.status_code == 503
    else:
        assert response.status_code == 200
        assert response.json() == common.build_set_mode_result(
            set_by_session,
            'orders',
            'orders_type',
            '2019-11-14T01:01:00+00:00',
        )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'expected_code, expect_retry_hours, '
    'trackstory_position, expect_position_error',
    [
        pytest.param(423, 19, scenario.MOSCOW_POSITION, False, id='moscow'),
        pytest.param(423, 0, None, True, id='trackstory no position'),
        pytest.param(
            423,
            165,
            None,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS=(
                        WEEK_HOURLY_RESTRICTION
                    ),
                ),
            ],
            id='trackstory no position hourly',
        ),
        pytest.param(
            423,
            17,  # 24:00 in Perm is 22:00 MSK, now 05:00 MSK
            scenario.PERM_POSITION,
            False,
            id='perm',
        ),
        pytest.param(
            200,
            0,  # 02:00 MSK is 23:00 in London, so new day started
            scenario.LONDON_POSITION,
            False,
            id='london',
        ),
    ],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_BR_READER_BULK_SIZE={'orders': 10},
    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS=DAYLY_RESTRICTION,
)
@pytest.mark.now('2019-11-14T05:00:00+03:00')
async def test_mode_set_time_validation_timezone(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        expected_code: int,
        expect_retry_hours: int,
        expect_position_error: bool,
        trackstory_position: Optional[common.Position],
):
    await taxi_driver_mode_subscription.invalidate_caches()

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        docs = [
            ('2019-11-14T04:00:00+03:00', 'driver_fix'),
            ('2019-11-14T02:00:00+03:00', 'orders'),
        ]
        documents = []

        chunk_num = int(request.json.get('cursor', '0'))

        history_chunk_size = 10
        docs_start = chunk_num * history_chunk_size
        docs_end = docs_start + history_chunk_size
        for occured, mode in docs[docs_start:docs_end]:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'dbid0',
                            'driver_profile_id': 'uuid0',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': 'some_id',
                            'shift_close_time': '00:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': f'{chunk_num + 1}'}

    scene.mock_driver_trackstory(mockserver, trackstory_position)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=True,
    )

    assert response.status_code == expected_code

    if expected_code == 423:
        response_body = response.json()
        if expect_position_error:
            assert response_body == {
                'code': 'POSITION_FETCH_FAILED',
                'localized_message': (
                    'Переместитесь на более открытую местность, чтобы мы '
                    'автоматически обновили данные.'
                ),
                'localized_message_title': 'Нет доступа к GPS',
            }
        else:
            assert response_body == {
                'code': 'TIME_VALIDATION_FAILED',
                'localized_message': (
                    'Вы слишком часто меняете режим, '
                    f'попробуйте через {expect_retry_hours} '
                    'часов'
                ),
                'localized_message_title': 'Слишком часто',
            }
        assert 'details' not in response_body

import datetime as dt

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules


REQUEST_PARAMS = {
    'park_id': 'park_id_0',
    'driver_profile_id': 'uuid',
    'tz': 'Europe/Moscow',
}

REQUEST_HEADERS = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
}


@pytest.mark.nofilldb()
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'mode_name, display_mode, starts_at, expected_code',
    [
        pytest.param(
            'some-default-mode',
            'some-default-mode',
            dt.datetime.fromisoformat('1970-01-01T00:00:00+00:00'),
            200,
            id='custom_mode_from_epoch',
        ),
        pytest.param(
            'driver_fix',
            'driver_fix-custom-type',
            dt.datetime.fromisoformat('1970-01-01T00:00:00-00:00'),
            200,
            id='driver_fix_from_epoch',
        ),
        pytest.param(
            'some-default-mode',
            'some-default-mode',
            dt.datetime.fromisoformat('1970-01-01T10:00:00+00:00'),
            200,
            id='custom_mode_and_time',
        ),
        pytest.param(
            'orders',
            'orders-type',
            dt.datetime.fromisoformat('1970-01-01T10:00:00-00:00'),
            200,
            id='orders_custom_time',
        ),
        pytest.param(
            'depeche_mode',
            'orders_type',
            dt.datetime.fromisoformat('1980-10-10T10:00:00+00:00'),
            200,
            id='depeche_mode_available',
        ),
        pytest.param(
            'depeche_mode',
            'orders_type',
            dt.datetime.fromisoformat('2030-10-10T00:00:00+00:00'),
            500,  # can't be used as default mode since at now() is not ready
            id='depech_mode_coming_soon',
        ),
    ],
)
async def test_get_empty_docs(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        taxi_config,
        mode_rules_data,
        mode_name: str,
        display_mode: str,
        starts_at: dt.datetime,
        expected_code: int,
):
    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_DEFAULT_MODE={'default_mode': mode_name},
        ),
    )

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched_mode_rules(
            rule_name=mode_name,
            display_mode=display_mode,
            starts_at=starts_at,
            # stops_at not affecting get
            stops_at=starts_at,
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        common.mode_history_response(request, 'orders', mocked_time)
        return {'docs': [], 'cursor': common.MODE_HISTORY_CURSOR}

    response = await taxi_driver_mode_subscription.get(
        'v1/mode/get', params=REQUEST_PARAMS, headers=REQUEST_HEADERS,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {
            'active_mode': mode_name,
            'active_mode_type': display_mode,
            'active_since': starts_at.isoformat(),
        }


@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_DEFAULT_MODE={
        'default_mode': 'some-default-mode',
    },
)
@pytest.mark.parametrize(
    'fail_service',
    (
        pytest.param(False, id='success'),
        pytest.param(True, id='fail_dm_index_request'),
    ),
)
async def test_get_invalid_or_different_history(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        taxi_config,
        mode_rules_data,
        fail_service: bool,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'driver_fix', mocked_time,
        )
        return {} if fail_service else response

    response = await taxi_driver_mode_subscription.get(
        'v1/mode/get',
        params=REQUEST_PARAMS,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    if fail_service:
        assert response.status_code == 500
        assert response.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }
    else:
        assert response.status_code == 200
        assert response.json() == {
            'active_mode': 'driver_fix',
            'active_mode_type': 'driver_fix_type',
            'active_since': '2019-05-01T05:00:00+00:00',
        }


@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'mode_name, mode_type, expected_code, expected_response',
    (
        pytest.param(
            'driver_fix',
            'driver_fix_type',
            200,
            {
                'active_mode': 'driver_fix',
                'active_mode_type': 'driver_fix_type',
                'active_since': '2019-05-01T05:00:00+00:00',
            },
            id='driver_fix',
        ),
        pytest.param(
            'unknown',
            None,
            500,
            {'code': '500', 'message': 'Internal Server Error'},
            id='unknown_mode',
        ),
    ),
)
async def test_get(
        mockserver,
        mocked_time,
        taxi_config,
        taxi_driver_mode_subscription,
        mode_name,
        mode_type,
        mode_rules_data,
        expected_code,
        expected_response,
):
    if mode_type:
        mode_rules_data.set_mode_rules(
            rules=mode_rules.patched_mode_rules(
                rule_name=mode_name, display_mode=mode_type,
            ),
        )

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(request, mode_name, mocked_time)

    response = await taxi_driver_mode_subscription.get(
        'v1/mode/get', params=REQUEST_PARAMS, headers=REQUEST_HEADERS,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response

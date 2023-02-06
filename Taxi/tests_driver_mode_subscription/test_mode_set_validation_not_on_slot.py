import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                'logistic_workshifts_auto',
                features={'logistic_workshifts': {}},
            ),
            mode_rules.Patch('custom_orders'),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, is_taximeter_request, expect_success',
    [
        pytest.param('custom_orders', True, True),
        pytest.param('custom_orders', False, True),
        pytest.param('logistic_workshifts_auto', True, False),
        pytest.param('logistic_workshifts_auto', False, True),
    ],
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_validation_not_on_slot(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        current_mode: str,
        is_taximeter_request: bool,
        expect_success: bool,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode(current_mode)})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=is_taximeter_request,
    )

    if expect_success:
        assert response.status_code == 200
    else:
        assert response.status_code == 423
        response_body = response.json()
        if is_taximeter_request:
            assert response_body == {
                'code': 'CHECK_NOT_ON_SLOT_FAILED',
                'localized_message': (
                    'Завершите смену, прежде чем изменять режим заработка.'
                ),
                'localized_message_title': 'Вы на слоте',
            }
        else:
            assert response_body['code'] == 'LOCKED'
        assert 'details' not in response_body

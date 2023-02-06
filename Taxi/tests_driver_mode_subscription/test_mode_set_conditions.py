from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

_DBID = 'parkid0'
_UUID = 'uuid0'


def get_bad_request_error_code(is_set_by_session_call: bool):
    if is_set_by_session_call:
        return 'BAD REQUEST'

    return 'WRONG_MODE_RULE'


@pytest.mark.parametrize(
    'set_by_session', [True, False], ids=['set_by_session_api', 'set_api'],
)
@pytest.mark.parametrize(
    'condition, expected_code, driver_tags_error',
    [
        pytest.param(
            {'all_of': ['tag1', 'tag2']},
            200,
            common.ServiceError.NoError,
            id='good all_of',
        ),
        pytest.param(
            {'all_of': ['tag3']},
            400,
            common.ServiceError.NoError,
            id='bad all_of',
        ),
        pytest.param(
            {'any_of': ['tag3']},
            400,
            common.ServiceError.NoError,
            id='bad any_of',
        ),
        pytest.param(
            {'none_of': ['tag1']},
            400,
            common.ServiceError.NoError,
            id='bad none_of',
        ),
        pytest.param(
            {'and': [{'none_of': ['tag1']}, {'all_of': ['tag2']}]},
            400,
            common.ServiceError.NoError,
            id='bad and',
        ),
        pytest.param(
            {'or': [{'any_of': ['tag1']}, {'all_of': ['tag3']}]},
            200,
            common.ServiceError.NoError,
            id='bad or',
        ),
        pytest.param(
            {'all_of': ['tag1', 'tag2']},
            503,
            common.ServiceError.TimeoutError,
            id='driver-tags timeout',
        ),
        pytest.param(
            {'all_of': ['tag1', 'tag2']},
            503,
            common.ServiceError.ServerError,
            id='driver-tags server error',
        ),
    ],
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_set_conditions(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        set_by_session: bool,
        condition: Dict[str, Any],
        expected_code: int,
        driver_tags_error: common.ServiceError,
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched_mode_rules(
            rule_name='orders', condition=condition,
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    driver_mock = common.make_driver_tags_mock(
        mockserver, ['tag1', 'tag2'], _DBID, _UUID, driver_tags_error,
    )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )

    assert response.status_code == expected_code

    if driver_tags_error == common.ServiceError.NoError:
        assert driver_mock.times_called == 1
    else:
        assert driver_mock.times_called == 3

    if expected_code != 200:
        response_body = response.json()
        if expected_code == 400:
            expected_code_str = get_bad_request_error_code(set_by_session)
        if expected_code == 503:
            expected_code_str = 'SERVICE UNAVAILABLE'
        assert response_body['code'] == expected_code_str
        if set_by_session:
            assert not response_body['message']
            assert 'details' not in response_body

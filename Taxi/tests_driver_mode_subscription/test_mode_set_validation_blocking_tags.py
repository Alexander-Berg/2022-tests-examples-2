from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch(rule_name='custom_orders')],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_BLOCKING_TAGS={
        '__default__': {
            'disable_button': 'offer_card.blocked.default.button',
            'message_title': 'offer_card.blocked.default.title',
            'message_body': 'offer_card.blocked.body',
        },
        'frozen': {
            'disable_button': 'offer_card.blocked.freeze.button',
            'message_title': 'offer_card.blocked.freeze.title',
            'message_body': 'offer_card.blocked.body',
        },
    },
    DRIVER_MODE_RULES_BLOCKING_TAGS={
        'custom_orders': {'tags': ['frozen', 'frauder']},
    },
)
@pytest.mark.parametrize(
    'tags_error, driver_tags, by_session, expected_code, '
    'code, message, message_title',
    [
        pytest.param(
            None, [], True, 200, None, None, None, id='session_success',
        ),
        pytest.param(None, [], False, 200, None, None, None, id='tvm_success'),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            [],
            False,
            200,
            None,
            None,
            None,
            id='tvm_success_ignore_tags',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            [],
            True,
            503,
            None,
            None,
            None,
            id='session_fail_tags',
        ),
        pytest.param(
            None,
            ['frauder', 'frozen'],
            False,
            200,
            None,
            None,
            None,
            id='tvm_ignore_blocking_tag',
        ),
        pytest.param(
            None,
            ['frauder'],
            True,
            423,
            'MODE_IS_BLOCKED',
            'Грустно, но переключать режим Вы не можете',
            'Вам это запрещено',
            id='session_blocked_by_tag',
        ),
        pytest.param(
            None,
            ['frozen'],
            True,
            423,
            'MODE_IS_BLOCKED',
            'Грустно, но переключать режим Вы не можете',
            'Вы замёрзли',
            id='session_blocked_by_tag_custom_title',
        ),
    ],
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_not_blocked_by_tag(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        tags_error: Optional[scenario.ServiceError],
        driver_tags: List[str],
        by_session: bool,
        expected_code: int,
        code: Optional[str],
        message: Optional[str],
        message_title: Optional[str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)
    scene.mock_driver_tags(
        mockserver,
        tags=driver_tags,
        service_error=tags_error or scenario.ServiceError.NoError,
    )

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='custom_orders',
        mode_settings=None,
        set_by_session=by_session,
    )

    assert response.status_code == expected_code
    response_body = response.json()
    if code:
        assert response_body['code'] == code
    if message:
        assert response_body['localized_message'] == message
    if message_title:
        assert response_body['localized_message_title'] == message_title

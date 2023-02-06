import pytest

import selfemployed.use_cases.resend_phone_confirmation as use_case

_USER_AGENT = (
    'app:pro brand:yandex version:10.12 platform:ios platform_version:15.0.1'
)

_HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'contractor_profile_id',
    'X-YaTaxi-Park-Id': 'park_id',
    'User-Agent': _USER_AGENT,
}


async def test_ok(se_client, patch):
    @patch(
        'selfemployed.use_cases.resend_phone_confirmation'
        '.Component.__call__',
    )
    async def react(park_id, contractor_profile_id, consumer_user_agent):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert consumer_user_agent == _USER_AGENT
        return

    response = await se_client.post(
        '/driver/v1/selfemployed/qse/resend-phone-confirmation',
        headers=_HEADERS,
    )

    assert react.calls
    assert response.status == 200


@pytest.mark.parametrize(
    'error,expected_status,expected_code',
    (
        (use_case.ProposalNotFound(), 404, 'PROPOSAL_NOT_FOUND'),
        (use_case.SmsLimitExceeded(), 409, 'SMS_LIMIT_EXCEEDED'),
    ),
)
async def test_error(se_client, patch, error, expected_status, expected_code):
    @patch(
        'selfemployed.use_cases.resend_phone_confirmation'
        '.Component.__call__',
    )
    async def react(park_id, contractor_profile_id, consumer_user_agent):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert consumer_user_agent == _USER_AGENT
        raise error

    response = await se_client.post(
        '/driver/v1/selfemployed/qse/resend-phone-confirmation',
        headers=_HEADERS,
    )

    assert react.calls

    response_data = await response.json()
    assert response.status == expected_status
    assert response_data['code'] == expected_code

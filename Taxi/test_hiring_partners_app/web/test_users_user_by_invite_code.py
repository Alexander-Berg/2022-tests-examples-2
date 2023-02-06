import pytest


@pytest.mark.parametrize(
    'invitation_code', ['code_does_not_exists', 'user1_code1', ''],
)
@pytest.mark.now('2022-07-14T10:10:00+03:00')
async def test_v1_users_user_id_by_code(
        taxi_hiring_partners_app_web, invitation_code, load_json,
):
    # arrange
    expected_response = load_json('responses.json')[invitation_code]

    # act
    resp = await taxi_hiring_partners_app_web.get(
        '/v1/users/user-by-invite-code',
        params={'invitation_code': invitation_code},
    )

    # assert
    assert resp.status == expected_response['status']
    assert await resp.json() == expected_response['body']

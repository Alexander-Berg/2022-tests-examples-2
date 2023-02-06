import pytest


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
@pytest.mark.parametrize(
    'wind_user_id, expected_response',
    [
        (
            'known_wind_user_id',
            dict(
                yandex_uid='known_yandex_uid',
                personal_phone_id='known_personal_phone_id',
            ),
        ),
        ('unknown wind_user_id', None),
    ],
)
async def test_subscriptions_expiration(
        taxi_talaria_misc, wind_user_id, expected_response,
):

    params = dict(wind_user_id=wind_user_id)
    response = await taxi_talaria_misc.get(
        '/talaria/v1/wind-user-to-yandex-user', params=params, json={},
    )
    if expected_response is not None:
        assert response.status_code == 200
        response_body = response.json()
        assert response_body == expected_response
    else:
        assert response.status_code == 404

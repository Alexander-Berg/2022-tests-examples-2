import pytest


@pytest.mark.parametrize('body,status', [[{}, 400], [{'logins': []}, 200]])
async def test_statuses(taxi_eats_restapp_tg_bot_web, body, status):
    response = await taxi_eats_restapp_tg_bot_web.post(
        '/v1/get-available-logins', json=body,
    )
    assert response.status == status


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['logins.sql'])
@pytest.mark.parametrize('testcase', ['already_lower', 'not_lower'])
async def test_should_return_actual_logins(
        taxi_eats_restapp_tg_bot_web, load_json, testcase,
):
    response = await taxi_eats_restapp_tg_bot_web.post(
        '/v1/get-available-logins', json=load_json('request.json')[testcase],
    )

    assert response.status == 200
    result = await response.json()
    assert result == load_json('response.json')[testcase]


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['logins.sql'])
@pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
async def test_should_return_actual_personal_logins(
        taxi_eats_restapp_tg_bot_web, load_json,
):
    response = await taxi_eats_restapp_tg_bot_web.post(
        '/v1/get-available-logins', json=load_json('request.json')['personal'],
    )

    assert response.status == 200
    result = await response.json()
    assert result == load_json('response.json')['personal']

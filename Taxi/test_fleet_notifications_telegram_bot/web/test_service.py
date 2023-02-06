import pytest


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.servicetest
async def test_ping(taxi_fleet_notifications_telegram_bot_web):
    response = await taxi_fleet_notifications_telegram_bot_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''

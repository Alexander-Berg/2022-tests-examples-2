DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'driver/rescue/v1/sos/info'

AUTH_PARAMS = {'park_id': DB}

HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'X-Driver-Session': SESSION}

BODY = {'order_id': 'order_id_1', 'position': {'lat': 56.89, 'lon': 68.9}}

TICKET_KEY = 'TICKET-1'


async def test_driver_sos_info(
        taxi_rescue,
        pgsql,
        api_tracker,
        driver_authorizer,
        driver_profiles,
        personal,
        taxi_config,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_rescue.post(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS, json=BODY,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {'code': '200', 'message': 'Disabled.'}

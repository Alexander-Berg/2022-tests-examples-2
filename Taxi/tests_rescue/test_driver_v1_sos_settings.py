INSERT_APPLICATION = (
    'INSERT INTO rescue.application '
    '(park_id, driver_profile_id, order_id, '
    ' longtitude, latitude, st_ticket)'
    ' VALUES (\'{}\', \'{}\', \'{}\', {}, {}, \'{}\')'
)

INSERT_MEDIA = (
    'INSERT INTO rescue.media '
    '(order_id, media_id, attach_id, content_type)'
    ' VALUES (\'{}\', \'{}\', \'{}\', \'{}\')'
)

DB = 'park1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'driver/rescue/v1/sos/settings'

AUTH_PARAMS = {'park_id': DB}

HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'X-Driver-Session': SESSION}

BODY = {'order_id': 'order_id_1', 'position': {'lat': 56.89, 'lon': 68.9}}

TICKET_KEY = 'TICKET-1'


async def test_driver_sos_settings_basic(
        taxi_rescue, pgsql, mock_fleet_parks_list, driver_authorizer,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_rescue.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['sos_number'] == '112'
    assert response_json['record_timer']['audio'] == 600
    assert response_json['record_timer']['video'] == 600
    assert response_json['cancelation_timer']['start'] == 10
    assert response_json['cancelation_timer']['send'] == 10
    assert not response_json['is_voice_notification_enabled']
    assert response_json['is_record_enabled']


async def test_driver_sos_settings_not_many_media(
        taxi_rescue, pgsql, mock_fleet_parks_list, driver_authorizer,
):
    cursor = pgsql['rescue'].cursor()
    cursor.execute(
        INSERT_APPLICATION.format(
            DB,
            UUID,
            BODY['order_id'],
            BODY['position']['lon'],
            BODY['position']['lat'],
            TICKET_KEY,
        ),
    )
    cursor.execute(
        INSERT_MEDIA.format(
            BODY['order_id'], '123', '123', 'some_content_type',
        ),
    )
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_rescue.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['is_record_enabled']


async def test_driver_sos_settings_many_media(
        taxi_rescue, pgsql, mock_fleet_parks_list, driver_authorizer,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    cursor = pgsql['rescue'].cursor()
    for order_id in ['1', '2']:
        cursor.execute(
            INSERT_APPLICATION.format(
                DB,
                UUID,
                order_id,
                BODY['position']['lon'],
                BODY['position']['lat'],
                TICKET_KEY,
            ),
        )
        for media_id in ['12', '123']:
            cursor.execute(
                INSERT_MEDIA.format(
                    order_id,
                    order_id + media_id,
                    order_id + media_id,
                    'some_content_type',
                ),
            )
    response = await taxi_rescue.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['is_record_enabled']


async def test_driver_sos_settings_many_old_media(
        taxi_rescue, pgsql, mock_fleet_parks_list, driver_authorizer,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    cursor = pgsql['rescue'].cursor()
    for order_id in ['1', '2']:
        cursor.execute(
            INSERT_APPLICATION.format(
                DB,
                UUID,
                order_id,
                BODY['position']['lon'],
                BODY['position']['lat'],
                TICKET_KEY,
            ),
        )
        for media_id in ['12', '123']:
            cursor.execute(
                INSERT_MEDIA.format(
                    order_id,
                    order_id + media_id,
                    order_id + media_id,
                    'some_content_type',
                ),
            )
        cursor.execute(
            'UPDATE rescue.application SET created = '
            '(NOW() - INTERVAL \'181 days\') WHERE '
            'order_id=\'{}\''.format(order_id),
        )
    response = await taxi_rescue.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['is_record_enabled']


async def test_driver_sos_settings_no_country(
        taxi_rescue, pgsql, mock_fleet_parks_list, driver_authorizer,
):
    db = 'unknown_park'
    driver_authorizer.set_session(db, SESSION, UUID)
    response = await taxi_rescue.get(
        HANDLER, params={'park_id': db}, headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['is_record_enabled']

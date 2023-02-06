import pytest


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

HANDLER = 'admin/rescue/v1/sos/order-media'

BODY = {'order_id': 'order_id_1', 'position': {'lat': 56.89, 'lon': 68.9}}

TICKET_KEY = 'TICKET-1'


@pytest.mark.parametrize('use_media_storage', [True, False])
async def test_admin_v1_sos_order_media(
        taxi_rescue, pgsql, taxi_config, media_storage, use_media_storage,
):
    taxi_config.set_values(
        {'RESCUE_SAVE_AUDIO_TO_MEDIA_STORAGE': use_media_storage},
    )
    cursor = pgsql['rescue'].cursor()
    cursor.execute(
        INSERT_APPLICATION.format(
            'db',
            'uuid',
            BODY['order_id'],
            BODY['position']['lon'],
            BODY['position']['lat'],
            TICKET_KEY,
        ),
    )
    for media_id in ['1', '2']:
        cursor.execute(
            INSERT_MEDIA.format(
                BODY['order_id'],
                media_id + BODY['order_id'],
                media_id + BODY['order_id'],
                'some_content_type',
            ),
        )
        if use_media_storage:
            media_storage.store_object(media_id + BODY['order_id'])

    response = await taxi_rescue.get(
        HANDLER, params={'order_id': BODY['order_id']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['ticket'] == TICKET_KEY
    assert response_json['position'] == BODY['position']
    assert len(response_json['media']) == 2


async def test_admin_v1_sos_order_media_no_application(taxi_rescue):
    response = await taxi_rescue.get(
        HANDLER, params={'order_id': 'some_not_existing_id'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['code'] == '200'
    assert response_json['message'] == 'Have not pushed SOS'

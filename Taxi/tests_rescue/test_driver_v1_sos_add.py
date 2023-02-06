from typing import Dict
from typing import List
import uuid

import pytest

DB = 'park1'
UUID = 'uuid1'
SESSION = 'session1'
TICKET_KEY = 'TICKET-1'
ORDER_ID = 'order_id_1'

SELECT_APPLICATION = 'SELECT * FROM rescue.application WHERE order_id = \'{}\''

EMPTY_DRIVER_PROFILES_RESPONSE1 = {
    'profiles': [
        {
            'park_driver_profile_id': DB + '_' + UUID,
            'data': {'phone_pd_ids': [{}]},
        },
    ],
}
EMPTY_DRIVER_PROFILES_RESPONSE2 = {
    'profiles': [
        {
            'park_driver_profile_id': DB + '_' + UUID,
            'data': {'phone_pd_ids': []},
        },
    ],
}
EMPTY_DRIVER_PROFILES_RESPONSE3 = {
    'profiles': [{'park_driver_profile_id': DB + '_' + UUID, 'data': {}}],
}
EMPTY_DRIVER_PROFILES_RESPONSE4 = {
    'profiles': [{'park_driver_profile_id': DB + '_' + UUID}],
}
EMPTY_DRIVER_PROFILES_RESPONSE5 = {
    'profiles': [],
}  # type: Dict[str, List[str]]
WRONG_DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {'park_driver_profile_id': DB + '_' + UUID},
        {'park_driver_profile_id': DB + '_' + UUID},
    ],
}
WRONG_DRIVER_PROFILES_RESPONSE1 = {
    'profiles': [
        {
            'park_driver_profile_id': DB + '_' + UUID,
            'data': {'phone_pd_ids': [{}, {}]},
        },
    ],
}


async def add_audio(taxi_rescue, order_id, media_id, content):

    params = dict(park_id=DB, order_id=order_id)
    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-Driver-Session': SESSION,
        'Content-Type': 'audio/aac',
        'X-Idempotency-Token': media_id,
    }

    response = await taxi_rescue.post(
        'driver/rescue/v1/sos/add/audio',
        params=params,
        headers=headers,
        data=content,
    )

    return response


def check_media(pgsql, mds_s3, media_storage, order_id, media_id, content):
    assert media_storage.get_object(media_id)

    cursor = pgsql['rescue'].cursor()
    cursor.execute(
        'SELECT media_id, order_id FROM rescue.media '
        f'WHERE media_id = \'{media_id}\'',
    )

    result = list(row for row in cursor)
    assert len(result) == 1
    assert result[0] == (media_id, order_id)


def check_media_count(pgsql, order_id, count):
    cursor = pgsql['rescue'].cursor()
    cursor.execute(
        f'SELECT * FROM rescue.media WHERE order_id = \'{order_id}\'',
    )
    assert len([row for row in cursor]) == count


def check_ticket(pgsql):
    cursor = pgsql['rescue'].cursor()
    cursor.execute(SELECT_APPLICATION.format(ORDER_ID))
    result = list(row for row in cursor)[0]
    assert result[0] == DB
    assert result[1] == UUID
    assert result[2] == ORDER_ID
    assert result[7] == TICKET_KEY


async def test_driver_sos_add_audio(
        taxi_rescue,
        pgsql,
        mock_fleet_parks_list,
        driver_authorizer,
        mds_s3,
        api_tracker,
        load_binary,
        taxi_config,
        media_storage,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    api_tracker.set_response(response=dict(id=uuid.uuid4().hex))
    api_tracker.set_response(
        handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
    )
    api_tracker.set_response(
        handler='v2/issues/{issue}/comments', response=dict(id=123500),
    )

    order_id = ORDER_ID
    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')

    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 200
    assert response.json() == dict(code='200', message='File uploaded.')
    check_media(pgsql, mds_s3, media_storage, order_id, media_id, audio)
    check_ticket(pgsql)

    # Check idempotency. Send again
    api_tracker.set_error(
        handler='v2/issues', status=409, headers={'X-Ticket-Key': TICKET_KEY},
    )
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 200
    assert response.json() == dict(code='200', message='Already exists.')
    check_media(pgsql, mds_s3, media_storage, order_id, media_id, audio)

    # Send new media
    media_id = uuid.uuid4().hex
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 200
    assert response.json() == dict(code='200', message='File uploaded.')
    check_media(pgsql, mds_s3, media_storage, order_id, media_id, audio)

    # Check if we have uploaded 2 attachment to the order
    check_media_count(pgsql, order_id, 2)


async def test_driver_sos_add_audio_error(
        taxi_rescue,
        pgsql,
        mock_fleet_parks_list,
        driver_authorizer,
        api_tracker,
        mds_s3,
        load_binary,
        taxi_config,
        media_storage,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    api_tracker.set_response(response=dict(id=uuid.uuid4().hex))

    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')

    # Check order without application ticket
    api_tracker.set_error(handler='v2/issues', status=500)
    order_id = ORDER_ID
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 500
    assert response.json() == dict(
        code='500', message='Couldn\'t create ticket',
    )
    # Check if nothing've been uploaded
    check_media_count(pgsql, order_id, 0)

    order_id = ORDER_ID

    # Emulate mds exception
    api_tracker.set_response(
        handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
    )
    media_storage.set_error(500)
    where = 'media-storage'
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 500
    assert response.json() == dict(
        code='500', message=('Couldn\'t store media to ' + where),
    )
    check_media_count(pgsql, order_id, 0)

    mds_s3.set_error(None)
    media_storage.set_error(None)

    # Emulate tracker errors
    api_tracker.set_error(handler='v2/issues/{issue}/comments', status=500)
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 500
    assert response.json() == dict(
        code='500', message='Error while add comments.',
    )
    check_media_count(pgsql, order_id, 0)


@pytest.mark.pgsql('rescue', files=['rescue_limit_exceeded.sql'])
async def test_driver_sos_add_audio_limit_exceeded(
        taxi_rescue,
        pgsql,
        mock_fleet_parks_list,
        driver_authorizer,
        mds_s3,
        api_tracker,
        load_binary,
        taxi_config,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    api_tracker.set_response(response=dict(id=uuid.uuid4().hex))
    api_tracker.set_response(
        handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
    )
    api_tracker.set_response(
        handler='v2/issues/{issue}/comments', response=dict(id=123500),
    )

    order_id = ORDER_ID
    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')

    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    assert response.status_code == 400
    assert response.json() == dict(code='400', message='Audio limit exceeded.')


async def test_driver_create_ticket_tracker_500(
        taxi_rescue,
        pgsql,
        api_tracker,
        mock_fleet_parks_list,
        driver_authorizer,
        driver_profiles,
        load_binary,
        personal,
        taxi_config,
):
    api_tracker.set_error()
    driver_authorizer.set_session(DB, SESSION, UUID)
    order_id = ORDER_ID
    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')
    response = await add_audio(taxi_rescue, order_id, media_id, audio)
    response_json = response.json()
    assert response.status_code == 500
    assert response_json == {
        'code': '500',
        'message': 'Couldn\'t create ticket',
    }


@pytest.mark.parametrize(
    'driver_profiles_response',
    [
        'default',
        WRONG_DRIVER_PROFILES_RESPONSE,
        WRONG_DRIVER_PROFILES_RESPONSE1,
        EMPTY_DRIVER_PROFILES_RESPONSE1,
        EMPTY_DRIVER_PROFILES_RESPONSE2,
        EMPTY_DRIVER_PROFILES_RESPONSE3,
        EMPTY_DRIVER_PROFILES_RESPONSE4,
        EMPTY_DRIVER_PROFILES_RESPONSE5,
        None,
    ],
)
@pytest.mark.parametrize('personal_response', ['default', None])
async def test_driver_create_ticket_driver_phone_test(
        taxi_rescue,
        pgsql,
        api_tracker,
        mock_fleet_parks_list,
        driver_authorizer,
        driver_profiles,
        load_binary,
        personal,
        driver_profiles_response,
        personal_response,
        taxi_config,
):
    if driver_profiles_response is None:
        driver_profiles.set_error()
    elif driver_profiles_response != 'default':
        driver_profiles.set_response(driver_profiles_response)
    if personal_response is None:
        personal.set_error()
    driver_authorizer.set_session(DB, SESSION, UUID)
    api_tracker.set_response(response=dict(id=uuid.uuid4().hex))
    api_tracker.set_response(
        handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
    )
    api_tracker.set_response(
        handler='v2/issues/{issue}/comments', response=dict(id=123500),
    )

    order_id = ORDER_ID
    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')

    response = await add_audio(taxi_rescue, order_id, media_id, audio)

    assert response.status_code == 200


@pytest.mark.parametrize(
    'order_core_response',
    [
        {
            'fields': {},
            'order_id': '123',
            'replica': 'master',
            'version': 'v1',
        },
        {
            'fields': {'order': {'city': 'Москва'}},
            'order_id': '123',
            'replica': 'master',
            'version': 'v1',
        },
        None,
    ],
)
async def test_driver_create_ticket_order_id_test(
        taxi_rescue,
        pgsql,
        api_tracker,
        driver_authorizer,
        mock_fleet_parks_list,
        driver_profiles,
        load_binary,
        order_core,
        personal,
        order_core_response,
        taxi_config,
):
    if order_core_response is None:
        order_core.set_error()
    else:
        order_core.set_response(order_core_response)
    driver_authorizer.set_session(DB, SESSION, UUID)
    api_tracker.set_response(response=dict(id=uuid.uuid4().hex))
    api_tracker.set_response(
        handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
    )
    api_tracker.set_response(
        handler='v2/issues/{issue}/comments', response=dict(id=123500),
    )

    order_id = ORDER_ID
    media_id = uuid.uuid4().hex
    audio = load_binary('test_audio.mp3')

    response = await add_audio(taxi_rescue, order_id, media_id, audio)

    assert response.status_code == 200

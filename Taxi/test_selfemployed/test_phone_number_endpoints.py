# pylint: disable=redefined-outer-name,unused-variable
import pytest

from testsuite.utils import http

from selfemployed.db import dbmain
from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_confirm_phone(se_client, se_web_context, mockserver):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'Taximeter 9.30'
        return {
            'deny_resend_until': 1618326242,
            'status': 'ok',
            'code_length': 6,
            'global_sms_id': '2070000508845559',
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
            'track_id': 'sms_track_id',
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _commit(request: http.Request):
        assert request.form == {
            'track_id': 'sms_track_id',
            'code': '000000',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'Taximeter 9.30'
        return {
            'status': 'ok',
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
        }

    phone = '+70123456789'
    driver_id = '8d'
    park_id = '8p'

    data = {'step': dbmain.Step.SMS, 'phone_number': phone}

    # let's prepare and create a new profile first...
    await dbmain.insert_new(se_web_context.pg, park_id, driver_id)

    response = await se_client.post(
        '/self-employment/fns-se/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'sms_sent_again',
        'text': 'СМС отправлено повторно',
    }

    # data['code'] = '111111'
    # response = await se_client.post(
    #     '/self-employment/fns-se/confirm-phone',
    #     headers=conftest.DEFAULT_HEADERS,
    #     params={'park': park_id, 'driver': driver_id},
    #     json=data)
    # assert response.status == 409
    # content = await response.json()
    # assert content == {'code': 'bad',
    #                    'text': 'Введен неверный код подтверждения'}

    data['code'] = '000000'
    response = await se_client.post(
        '/self-employment/fns-se/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': dbmain.Step.PHONE_NUMBER,
        'step_index': 2,
        'step_count': 7,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, phone,
             park_id, driver_id,
             created_at, modified_at)
        VALUES
            (\'aaa15\', \'8d\', \'8p\', \'+70123456789\',
             \'8p_new\', \'8d_new\',
             now()::timestamp, now()::timestamp)
        """,
    ],
)
async def test_phone_number(se_client):
    driver_id = '8d'
    park_id = '8p'
    phone = '+70123456789'

    response = await se_client.get(
        '/self-employment/fns-se/phone-number',
        headers=conftest.DEFAULT_HEADERS,
        params={'driver': driver_id, 'park': park_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'phone_number': phone, 'sms_retry_timeout': 5000}


async def test_post_bind_401(se_client):
    data = {'step': dbmain.Step.PHONE_NUMBER, 'phone_number': '+70123456789'}

    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_bind_body_400(se_client):
    params = {'park': '1p', 'driver': '1d'}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json={},
    )
    assert response.status == 400


async def test_post_bind_step_400(se_client):
    data = {'step': dbmain.Step.INTRO}
    params = {'park': '1p', 'driver': '1d'}

    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


async def test_post_bind_change_phone_200(
        se_client, se_web_context, mockserver,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'Taximeter 9.30'
        return {
            'deny_resend_until': 1618326242,
            'status': 'ok',
            'code_length': 6,
            'global_sms_id': '2070000508845559',
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
            'track_id': 'sms_track_id',
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _commit(request: http.Request):
        assert request.form == {
            'track_id': 'sms_track_id',
            'code': '000000',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'Taximeter 9.30'
        return {
            'status': 'ok',
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
        }

    park_id = '9p'
    driver_id = '9d'
    phone = '+70123456789'
    data = {'step': dbmain.Step.PHONE_NUMBER, 'phone_number': phone}
    params = {'park': park_id, 'driver': driver_id}

    # let's prepare and create a new profile first...
    await dbmain.insert_new(se_web_context.pg, park_id, driver_id)

    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': dbmain.Step.SMS,
        'step_index': 2,
        'step_count': 7,
    }

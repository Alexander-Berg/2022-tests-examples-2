# pylint: disable=unused-variable
import pytest

from testsuite.utils import http

from selfemployed.fns import client as fns
from . import conftest


async def test_no_park_driver_401(se_client):
    # Requests w\\o 'park' and 'driver' parameters are considered
    #   unauthorised
    phone_number = '+70123456789'
    step = 'phone_number'
    data = {'step': step, 'phone_number': phone_number}

    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_body_no_step_400(se_client):
    # Requests must contain 'step' body parameter
    park_id = '5'
    driver_id = '5'
    phone_number = '+70123456789'
    data = {'phone_number': phone_number}
    params = {'park': park_id, 'driver': driver_id}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


async def test_body_no_phone_400(se_client):
    # Requests must contain 'phone_number' body parameter
    park_id = '5'
    driver_id = '5'
    step = 'phone_number'
    data = {'step': step}
    params = {'park': park_id, 'driver': driver_id}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


async def test_wrong_step_400(se_client):
    # Requests 'step' parameter must be 'phone_number'
    park_id = '5'
    driver_id = '5'
    phone_number = '+70123456789'
    step = 'intro'
    data = {'step': step, 'phone_number': phone_number}
    params = {'park': park_id, 'driver': driver_id}

    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status,
             phone, sms_track_id, created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd0', 'confirmed',
             '+70123456789', '123456', NOW(), NOW()),
            ('smz2', 'inn2', 'p1', 'd1', 'confirmed',
             '', '', NOW(), NOW()),
            ('smz3', 'inn3', 'p1', 'd2', 'confirmed',
             '+70987654321', '', NOW(), NOW())
        """,
    ],
)
async def test_change_number_200(se_client, patch, mockserver):
    # Requests with proper parameters and body must
    #   return code '200', next step description and proper headers
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
            'track_id': track_id_,
        }

    @patch('selfemployed.db.dbmain.update_sms_track_id')
    async def _update(
            pool,
            park_id: str,
            driver_id: str,
            phone_number: str,
            track_id: str,
    ):
        assert park_id == park_id_
        assert driver_id == driver_id_
        assert phone_number == phone_number_
        assert track_id == track_id_

    park_id_ = 'p1'
    driver_id_: str
    phone_number_ = '+70123456789'
    step_ = 'phone_number'
    data = {'step': step_, 'phone_number': phone_number_}
    track_id_ = 'some_track_id'

    for i in range(3):
        driver_id_ = 'd' + str(i)

        params = {'park': park_id_, 'driver': driver_id_}

        response = await se_client.post(
            '/self-employment/fns-se/bind',
            headers=conftest.DEFAULT_HEADERS,
            params=params,
            json=data,
        )

        assert response.status == 200
        content = await response.json()
        assert content == {
            'next_step': 'sms',
            'step_index': 2,
            'step_count': 7,
        }
        assert 'X-Polling-Delay' in response.headers


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status,
             phone, sms_track_id, created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'confirmed',
             '+70123456789', '123456', NOW(), NOW())
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_change_number_limit_409(se_client, patch, mockserver):
    # Requests with proper parameters and body must
    #   return code '200', next step description and proper headers
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
            'status': 'error',
            'errors': ['sms_limit.exceeded'],
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
            'track_id': 'track_id_',
        }

    park_id_ = 'p1'
    driver_id_ = 'd1'
    phone_number_ = '+70123456789'
    step_ = 'phone_number'
    data = {'step': step_, 'phone_number': phone_number_}
    params = {'park': park_id_, 'driver': driver_id_}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'sms_limit_exceeded',
        'text': 'Достигнут предел отправки СМС',
    }


@pytest.mark.pgsql('selfemployed_main', files=['test_fns_request.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_fns_request_200(se_client, patch):
    # Requests with proper parameters and body must
    #   return code '200', next step description and proper headers
    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id: str, driver_id: str, phone: str):
        assert park_id == park_id_
        assert driver_id == driver_id_
        assert phone == phone_number_
        return request_id_

    park_id_ = 'p1'
    driver_id_ = 'd1'
    phone_number_ = '+70123456789'
    step_ = 'phone_number'
    data = {'step': step_, 'phone_number': phone_number_}
    params = {'park': park_id_, 'driver': driver_id_}
    request_id_ = 'request_id'
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'agreement',
        'step_index': 3,
        'step_count': 7,
    }


@pytest.mark.pgsql('selfemployed_main', files=['test_fns_request.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_fns_request_no_req_id_409(se_client, patch):
    # Requests with proper parameters and body must
    #   return code '200', next step description and proper headers
    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id: str, driver_id: str, phone: str):
        assert park_id == park_id_
        assert driver_id == driver_id_
        assert phone == phone_number_
        return None

    park_id_ = 'p1'
    driver_id_ = 'd1'
    phone_number_ = '+70123456789'
    step_ = 'phone_number'
    data = {'step': step_, 'phone_number': phone_number_}
    params = {'park': park_id_, 'driver': driver_id_}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'no_selfemployed_found',
        'text': 'Вы не являетесь самозанятым',
    }


@pytest.mark.pgsql('selfemployed_main', files=['test_fns_request.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_fns_request_smz_error_409(se_client, patch):
    # Requests with proper parameters and body must
    #   return code '200', next step description and proper headers
    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id: str, driver_id: str, phone: str):
        assert park_id == park_id_
        assert driver_id == driver_id_
        assert phone == phone_number_
        raise fns.SmzPlatformError(
            'error', fns.SmzErrorCode.TAXPAYER_UNREGISTERED_CODE,
        )

    park_id_ = 'p1'
    driver_id_ = 'd1'
    phone_number_ = '+70123456789'
    step_ = 'phone_number'
    data = {'step': step_, 'phone_number': phone_number_}
    params = {'park': park_id_, 'driver': driver_id_}
    response = await se_client.post(
        '/self-employment/fns-se/bind',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'no_selfemployed_found',
        'text': 'Вы не являетесь самозанятым',
    }

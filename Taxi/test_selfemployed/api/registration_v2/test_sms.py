import pytest

from testsuite.utils import http

from selfemployed.services import nalogru
from test_selfemployed import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_confirm_phone(
        se_client, se_web_context, mockserver, patch, mock_personal,
):
    phone = '+70123456789'
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

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

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        return 'request_id'

    data = {'step': 'sms', 'phone_number': phone}

    response = await se_client.post(
        '/self-employment/fns-se/v2/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json=data,
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'SMS_SENT_AGAIN',
        'text': 'СМС отправлено повторно',
    }

    data['code'] = '000000'
    response = await se_client.post(
        '/self-employment/fns-se/v2/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'agreement',
        'step_index': 3,
        'step_count': 7,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id,
             is_phone_verified, track_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID',
                FALSE, 'sms_track_id');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_confirm_phone_fns_unavailable(
        se_client, se_web_context, mockserver, patch, mock_personal,
):
    phone = '+70123456789'
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

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

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        raise nalogru.FnsUnavailable()

    data = {'step': 'sms', 'phone_number': phone, 'code': '000000'}
    response = await se_client.post(
        '/self-employment/fns-se/v2/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json=data,
    )
    assert response.status == 504
    content = await response.json()
    assert content == {
        'code': 'NALOGRU_UNAVALABLE',
        'text': 'Мой Налог временно недоступен',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_confirm_phone_expired(
        se_client, se_web_context, mockserver, patch, mock_personal,
):
    phone = '+70123456789'
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

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
        return {'status': 'error', 'errors': ['track.not_found']}

    data = {'step': 'sms', 'phone_number': phone}

    response = await se_client.post(
        '/self-employment/fns-se/v2/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json=data,
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'SMS_SENT_AGAIN',
        'text': 'СМС отправлено повторно',
    }

    data['code'] = '000000'
    response = await se_client.post(
        '/self-employment/fns-se/v2/confirm-phone',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json=data,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {'code': 'SMS_TRACK_EXPIRED', 'text': 'Код истек'}

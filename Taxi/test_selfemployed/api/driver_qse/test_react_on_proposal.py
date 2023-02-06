import datetime

import pytest

from testsuite.utils import http

_USER_AGENT = (
    'app:pro brand:yandex version:10.12 platform:ios platform_version:15.0.1'
)

_HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'contractor_profile_id',
    'X-YaTaxi-Park-Id': 'park_id',
    'User-Agent': _USER_AGENT,
}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id'),
               ('OTHER_PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED', NULL);
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00')
        """,
    ],
)
async def test_ok_accepted(se_client, se_web_context, mockserver, stq):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'track_id': 'sms_track_id',
            'code': 'sms_code',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == _USER_AGENT
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

    response = await se_client.post(
        '/driver/v1/selfemployed/qse/react-on-proposal',
        headers=_HEADERS,
        json={'sms_code': 'sms_code', 'is_accepted': True},
    )
    assert response.status == 200

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_profile_id',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=True,
        sms_track_id=None,
        is_accepted=True,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
    )
    stq_next_call = stq.selfemployed_fns_finish_qse_binding.next_call()
    del stq_next_call['id']
    assert stq_next_call == {
        'queue': 'selfemployed_fns_finish_qse_binding',
        'args': [],
        'kwargs': {
            'park_id': 'park_id',
            'contractor_id': 'contractor_profile_id',
            'phone_pd_id': 'PHONE_PD_ID',
        },
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id'),
               ('OTHER_PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED', NULL);
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00')
        """,
    ],
)
async def test_ok_not_accepted(se_client, se_web_context, stq):
    response = await se_client.post(
        '/driver/v1/selfemployed/qse/react-on-proposal',
        headers=_HEADERS,
        json={'sms_code': 'sms_code', 'is_accepted': False},
    )
    assert response.status == 200

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_profile_id',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=False,
        sms_track_id='sms_track_id',
        is_accepted=False,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
    )
    assert not stq.selfemployed_fns_finish_qse_binding.has_calls


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id'),
               ('OTHER_PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED', NULL);
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00')
        """,
    ],
)
async def test_code_required(se_client, se_web_context, stq):
    response = await se_client.post(
        '/driver/v1/selfemployed/qse/react-on-proposal',
        headers=_HEADERS,
        json={'is_accepted': True},
    )
    assert response.status == 400
    response_data = await response.json()
    assert response_data['code'] == 'SMS_CODE_REQUIRED'

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_profile_id',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=False,
        sms_track_id='sms_track_id',
        is_accepted=None,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=1,
    )
    assert not stq.selfemployed_fns_finish_qse_binding.has_calls


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id'),
               ('OTHER_PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED', NULL);
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00')
        """,
    ],
)
@pytest.mark.parametrize(
    'passport_error,expected_code,expected_status',
    (
        ('track.not_found', 400, 'SMS_TRACK_EXPIRED'),
        ('code.invalid', 409, 'BAD_SMS_CODE'),
    ),
)
async def test_passport_error(
        se_client,
        se_web_context,
        mockserver,
        passport_error,
        expected_status,
        expected_code,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _commit(request: http.Request):
        assert request.form == {
            'track_id': 'sms_track_id',
            'code': 'sms_code',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == _USER_AGENT
        return {'status': 'error', 'errors': [passport_error]}

    response = await se_client.post(
        '/driver/v1/selfemployed/qse/react-on-proposal',
        headers=_HEADERS,
        json={'sms_code': 'sms_code', 'is_accepted': True},
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data['code'] == expected_status

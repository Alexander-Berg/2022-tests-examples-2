import datetime

import pytest

from testsuite.utils import http

from selfemployed.generated.web import web_context
from selfemployed.use_cases import resend_phone_confirmation

_USER_AGENT = (
    'app:pro brand:yandex version:10.12 platform:ios platform_version:15.0.1'
)


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id');
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00');
        """,
    ],
)
async def test_just_resend_ok(
        se_web_context: web_context.Context, mock_personal, mockserver,
):
    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'route': 'taxi',
            'display_language': 'ru',
            'number': '+70123456789',
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

    await se_web_context.use_cases.resend_phone_confirmation(
        park_id='park_id',
        contractor_profile_id='contractor_profile_id',
        consumer_user_agent=_USER_AGENT,
    )

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
        sms_track_id=None,
        is_accepted=None,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
    )


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id');
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID',
                FALSE, 'sms_track_id', NULL, '2021-08-01+00:00');
        """,
    ],
)
async def test_just_resend_error(
        se_web_context: web_context.Context, mock_personal, mockserver,
):
    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'route': 'taxi',
            'display_language': 'ru',
            'number': '+70123456789',
        }
        assert request.headers['Ya-Client-User-Agent'] == _USER_AGENT
        return {'status': 'error', 'errors': ['sms_limit.exceeded']}

    form_before_resend = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )

    with pytest.raises(resend_phone_confirmation.SmsLimitExceeded):
        await se_web_context.use_cases.resend_phone_confirmation(
            park_id='park_id',
            contractor_profile_id='contractor_profile_id',
            consumer_user_agent=_USER_AGENT,
        )

    form_after_resend = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )

    assert form_before_resend == form_after_resend


async def test_not_found(
        se_web_context: web_context.Context, mock_personal, mockserver,
):
    with pytest.raises(resend_phone_confirmation.ProposalNotFound):
        await se_web_context.use_cases.resend_phone_confirmation(
            park_id='park_id',
            contractor_profile_id='contractor_profile_id',
            consumer_user_agent=_USER_AGENT,
        )

import datetime

import pytest

from testsuite.utils import http

from selfemployed.generated.web import web_context
from selfemployed.services import nalogru
from selfemployed.use_cases import park_bind_quasi_se

# TODO: split and test separate components
#   now it's more of an integration test, will fix that later


@pytest.fixture(name='mock_driver_app_profile')
def _mock_driver_app_profile(mock_driver_profiles):
    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve_profile_app(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': [
                'data.taximeter_version',
                'data.taximeter_version_type',
                'data.taximeter_platform',
                'data.taximeter_platform_version',
                'data.taximeter_brand',
                'data.taximeter_build_type',
            ],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {
                        'taximeter_platform': 'android',
                        'taximeter_version': '10.04 (8646)',
                        'taximeter_platform_version': '15.14.13',
                        'taximeter_brand': 'yandex',
                        'taximeter_build_type': '',
                    },
                },
            ],
        }


@pytest.mark.config(
    SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_phone_verification_sms': '99.9'},
        },
    },
)
@pytest.mark.now('2021-08-01T00:00:00Z')
async def test_full_happy_path_with_sms(
        se_web_context: web_context.Context,
        patch,
        mock_personal,
        mock_driver_profiles,
        mock_driver_app_profile,
        mock_client_notify,
        mockserver,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        return 'bind_request_id'

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'OTHER_PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'YaBro'
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': True},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=False,
        sms_track_id='sms_track_id',
        is_accepted=None,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=3,
    )

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        status='IN_PROGRESS',
        bind_request_id='bind_request_id',
        bind_requested_at=datetime.datetime(
            2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )


@pytest.mark.config(
    SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_phone_verification_sms': '1.0'},
        },
    },
)
@pytest.mark.now('2021-08-01T00:00:00Z')
async def test_full_happy_path(
        se_web_context: web_context.Context,
        patch,
        mock_personal,
        mock_driver_profiles,
        mock_driver_app_profile,
        mock_client_notify,
        mockserver,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        return 'bind_request_id'

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'OTHER_PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'YaBro'
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': True},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
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

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        status='IN_PROGRESS',
        bind_request_id='bind_request_id',
        bind_requested_at=datetime.datetime(
            2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.parks_additional_terms (park_id, contractor_profile_id,
        yandex_uid, yandex_provider, is_accepted, created_at, updated_at)
        VALUES ('parkid', 'contractorprofileid', '123', 'yandex', true,
        '2021-08-01T00:00:00', '2021-08-01T00:00:00');
        """,  # noqa: W291
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_phone_verification_sms': '1.0'},
        },
    },
)
@pytest.mark.now('2021-08-01T00:00:00Z')
async def test_park_additional_terms_accepted(
        se_web_context: web_context.Context,
        patch,
        mock_personal,
        mock_driver_profiles,
        mock_driver_app_profile,
        mock_client_notify,
        mockserver,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        return 'bind_request_id'

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'OTHER_PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'YaBro'
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': True},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
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

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        status='IN_PROGRESS',
        bind_request_id='bind_request_id',
        bind_requested_at=datetime.datetime(
            2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )


@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=True)
async def test_park_additional_terms_not_accepted(
        se_web_context: web_context.Context, patch, mock_personal,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        return 'bind_request_id'

    with pytest.raises(park_bind_quasi_se.AdditionalTermsNotAccepted):
        await se_web_context.use_cases.park_bind_quasi_se(
            park_id='parkid',
            contractor_profile_id='contractorprofileid',
            phone_raw='+7 012 345-67-89',
            consumer_user_agent='YaBro',
            yandex_uid='123',
            ticket_provider='yandex',
        )


@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False)
async def test_taxpayer_unregistered(
        se_web_context: web_context.Context, patch, mock_personal,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        raise nalogru.TaxpayerUnregistered()

    with pytest.raises(park_bind_quasi_se.TaxpayerUnregistered):
        await se_web_context.use_cases.park_bind_quasi_se(
            park_id='parkid',
            contractor_profile_id='contractorprofileid',
            phone_raw='+7 012 345-67-89',
            consumer_user_agent='YaBro',
            yandex_uid='123',
            ticket_provider='yandex',
        )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    assert not form_record

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        status='NEW',
        bind_request_id=None,
        bind_requested_at=None,
        increment=1,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )


@pytest.mark.config(
    SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_phone_verification_sms': '1.0'},
        },
    },
)
@pytest.mark.now('2021-08-01T00:00:00Z')
async def test_taxpayer_already_bound(
        se_web_context: web_context.Context,
        patch,
        mock_personal,
        mock_driver_profiles,
        mock_driver_app_profile,
        mock_client_notify,
        mockserver,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        assert request.json == {'value': '012345678901', 'validate': True}
        return {'value': '012345678901', 'id': 'INN_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        raise nalogru.TaxpayerAlreadyBound('012345678901')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'OTHER_PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'YaBro'
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': True},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id='INN_PD_ID',
        is_phone_verified=False,
        sms_track_id=None,
        is_accepted=None,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
    )

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id='INN_PD_ID',
        status='COMPLETED',
        bind_request_id=None,
        bind_requested_at=None,
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )


@pytest.mark.config(
    SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_phone_verification_sms': '00.0'},
        },
    },
)
@pytest.mark.now('2021-08-01T00:00:00Z')
async def test_set_phone_verified_by_correcting(
        se_web_context: web_context.Context,
        patch,
        mock_personal,
        mock_driver_profiles,
        mock_driver_app_profile,
        mock_client_notify,
        mockserver,
):
    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '+7 012 345-67-89', 'validate': True}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind_fns(phone):
        assert phone == '+70123456789'
        return 'bind_request_id'

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id):
        assert request_id == 'bind_request_id'
        return nalogru.nalogru_binding.BindingStatus.IN_PROGRESS, None

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'OTHER_PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'YaBro'
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': True},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
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

    binding_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        status='IN_PROGRESS',
        bind_request_id='bind_request_id',
        bind_requested_at=datetime.datetime(
            2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile_fixed_phone(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorprofileid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorprofileid',
                    'data': {'phone_pd_ids': [{'pd_id': 'PHONE_PD_ID'}]},
                },
            ],
        }

    @mock_client_notify('/v2/push')
    async def _send_message_fixed_phone(request: http.Request):
        assert request.json == {
            'intent': 'QuasiSelfemployedProposal',
            'service': 'taximeter',
            'client_id': 'parkid-contractorprofileid',
            'data': {'code': 1380, 'is_sms_code_check_needed': False},
        }
        return {'notification_id': 'notification_id'}

    await se_web_context.use_cases.park_bind_quasi_se(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_raw='+7 012 345-67-89',
        consumer_user_agent='YaBro',
        yandex_uid='123',
        ticket_provider='yandex',
    )

    form_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='parkid',
        contractor_profile_id='contractorprofileid',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=True,
        sms_track_id=None,
        is_accepted=None,
        requested_at=datetime.datetime(
            2021, 8, 1, tzinfo=datetime.timezone.utc,
        ),
        increment=4,
    )

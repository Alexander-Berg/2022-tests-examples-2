import datetime

import aiohttp
import pytest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, business_unit, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', 'market', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements, created_park_id, created_contractor_id)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}',
             'new_park_id', 'new_contractor_id');
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_FNS_PROFESSION_TO_BUSINESS_UNIT_MAPPING={
        'market-courier': 'market',
    },
    SE_FNS_PROFILES_FNS_PERMISSIONS_FOR_PROFESSION={
        'market-courier': ['TEST1', 'TEST2'],
    },
)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        pgsql,
        prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
        return {
            'profiles': [
                {
                    'park_id': 'new_park_id',
                    'driver_id': 'new_contractor_id',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/status')
    async def _bind_status(request):
        return {'result': 'COMPLETED', 'inn_pd_id': 'INN_PD_ID'}

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind_phone(request):
        return aiohttp.web.json_response(
            {
                'code': 'TAXPAYER_ALREADY_BOUND',
                'details': {'inn_pd_id': 'INN_PD_ID'},
            },
            status=409,
        )

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/taxpayer/status')
    async def _taxpayer_status(request):
        return dict(
            first_name='Имий',
            last_name='Фамильев',
            registration_time=datetime.datetime(
                2021, 1, 1, tzinfo=datetime.timezone.utc,
            ).isoformat(),
            region_oktmo_code='46000000',
            phone_pd_id='PHONE_PD_ID',
            oksm_code='643',
            middle_name='Отчествович',
            activities=['test1', 'test2'],
        )

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/'
        'salesforce-selfemployed-account/v1',
    )
    async def _taxpayer_status_salesforce(request):
        assert request.json == {
            'park_id': 'new_park_id',
            'contractor_profile_id': 'new_contractor_id',
            'agreements': {'general': True, 'gas_stations': False},
            'last_name': 'Фамильев',
            'first_name': 'Имий',
            'middle_name': 'Отчествович',
            'phone_pd_id': 'PHONE_PD_ID',
            'inn_pd_id': 'INN_PD_ID',
            'selfemployed_id': 'external_id',
        }
        return dict(sf_account_id='sf_account_id')

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('permission', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'await-park-created',
        'step_count': 9,
        'step_index': 7,
    }

    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(
        """
        SELECT inn_pd_id, first_name, second_name, registration_time,
               region_oktmo_code, phone_pd_id, oksm_code, middle_name,
               unregistration_time, unregistration_reason, activities,
               email, account_number, update_time,
               registration_certificate_num, increment
        FROM se.taxpayer_status_cache
        """,
    )
    status_cache = cursor.fetchone()

    assert status_cache == (
        'INN_PD_ID',
        'Имий',
        'Фамильев',
        datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        '46000000',
        'PHONE_PD_ID',
        '643',
        'Отчествович',
        None,
        None,
        ['test1', 'test2'],
        None,
        None,
        None,
        None,
        1,
    )


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, business_unit, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', 'market', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements, created_park_id, created_contractor_id)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}',
             'new_park_id', 'new_contractor_id');
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_FNS_PROFESSION_TO_BUSINESS_UNIT_MAPPING={
        'market-courier': 'market',
    },
    SE_FNS_PROFILES_FNS_PERMISSIONS_FOR_PROFESSION={
        'market-courier': ['TEST1', 'TEST2'],
    },
)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_unbound(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/status')
    async def _bind_status(request):
        return {'result': 'FAILED', 'inn_pd_id': None}

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind_phone(request):
        return {'request_id': 'request_id'}

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('permission', 'passport_uid'),
    )

    assert response.status == 409
    content = response.json()
    assert content == {
        'code': 'BINDING_ERROR',
        'message': 'Для продолжения необходима привязка к ФНС',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, business_unit, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', 'market', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements, created_park_id, created_contractor_id)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}',
             'new_park_id', 'new_contractor_id');
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_FNS_PROFESSION_TO_BUSINESS_UNIT_MAPPING={
        'market-courier': 'market',
    },
    SE_FNS_PROFILES_FNS_PERMISSIONS_FOR_PROFESSION={
        'market-courier': ['TEST1', 'TEST2'],
    },
)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_fns_unavailable(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/status')
    async def _bind_status(request):
        return aiohttp.web.json_response(
            {'code': 'FNS_UNAVAILABLE'}, status=503,
        )

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('permission', 'passport_uid'),
    )

    assert response.status == 409
    content = response.json()
    assert content == {
        'code': 'NALOGRU_UNAVAILABLE',
        'message': 'Мой Налог временно недоступен',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id,
             created_park_id, created_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'salesforce_account_id', NULL,
             'park_id', 'contractor_id',
             'new_park_id', 'new_contractor_id');
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_FNS_PROFESSION_TO_BUSINESS_UNIT_MAPPING={
        'market-courier': 'market',
    },
    SE_FNS_PROFILES_FNS_PERMISSIONS_FOR_PROFESSION={
        'market-courier': ['TEST1', 'TEST2'],
    },
)
async def test_incorrect_transition(
        taxi_selfemployed_fns_profiles, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('permission', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {'next_step': 'intro', 'step_count': 9, 'step_index': 1}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, business_unit, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', 'market', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements, created_park_id, created_contractor_id)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}',
             'new_park_id', 'new_contractor_id');
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_FNS_PROFESSION_TO_BUSINESS_UNIT_MAPPING={
        'market-courier': 'market',
    },
    SE_FNS_PROFILES_FNS_PERMISSIONS_FOR_PROFESSION={
        'market-courier': ['TEST1', 'TEST2'],
    },
)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_no_oksm(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        pgsql,
        prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
        return {
            'profiles': [
                {
                    'park_id': 'new_park_id',
                    'driver_id': 'new_contractor_id',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/status')
    async def _bind_status(request):
        return {'result': 'COMPLETED', 'inn_pd_id': 'INN_PD_ID'}

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind_phone(request):
        return aiohttp.web.json_response(
            {
                'code': 'TAXPAYER_ALREADY_BOUND',
                'details': {'inn_pd_id': 'INN_PD_ID'},
            },
            status=409,
        )

    @mockserver.json_handler('/selfemployed-fns-proxy/v1/taxpayer/status')
    async def _taxpayer_status(request):
        return dict(
            first_name='Имий',
            last_name='Фамильев',
            registration_time=datetime.datetime(
                2021, 1, 1, tzinfo=datetime.timezone.utc,
            ).isoformat(),
            region_oktmo_code='46000000',
            phone_pd_id='PHONE_PD_ID',
            oksm_code=None,
            middle_name='Отчествович',
        )

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('permission', 'passport_uid'),
    )

    assert response.status == 409
    content = response.json()
    assert content == {
        'code': 'FNS_TEMPORARY_REGISTRATION',
        'message': 'У вас временная регистрация',
    }

    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(
        """
        SELECT inn_pd_id, first_name, second_name, registration_time,
               region_oktmo_code, phone_pd_id, oksm_code, middle_name,
               unregistration_time, unregistration_reason, activities,
               email, account_number, update_time,
               registration_certificate_num, increment
        FROM se.taxpayer_status_cache
        """,
    )
    status_cache = cursor.fetchone()

    assert status_cache == (
        'INN_PD_ID',
        'Имий',
        'Фамильев',
        datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        '46000000',
        'PHONE_PD_ID',
        None,
        'Отчествович',
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        1,
    )

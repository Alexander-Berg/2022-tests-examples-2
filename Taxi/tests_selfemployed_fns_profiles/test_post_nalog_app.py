import aiohttp
import pytest


GET_PHONE_BINDING = """
SELECT status, inn_pd_id, bind_request_id from se.nalogru_phone_bindings
"""


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
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
async def test_post_nalog_app(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        pgsql,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind(request):
        assert request.json == {
            'phone_pd_id': 'PHONE_PD_ID',
            'permissions': ['TEST1', 'TEST2'],
        }
        return {'request_id': 'request_id'}

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('nalog-app', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'agreement',
        'step_count': 9,
        'step_index': 5,
    }

    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(GET_PHONE_BINDING)
    row = cursor.fetchone()

    assert row == ('IN_PROGRESS', None, 'request_id')


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES
            ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'salesforce_account_id', NULL,
             'park_id', 'contractor_id');
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
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind(request):
        assert request.json == {
            'phone_pd_id': 'PHONE_PD_ID',
            'permissions': ['TEST1', 'TEST2'],
        }
        return {'request_id': 'request_id'}

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('nalog-app', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {'next_step': 'intro', 'step_count': 9, 'step_index': 1}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
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
async def test_post_nalog_app_selfreg_unregisteged(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind(request):
        assert request.json == {
            'phone_pd_id': 'PHONE_PD_ID',
            'permissions': ['TEST1', 'TEST2'],
        }
        return aiohttp.web.json_response(
            {
                'code': 'TAXPAYER_UNREGISTERED',
                'message': 'Налогоплательщик не зарегистрирован',
            },
            status=409,
        )

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('nalog-app', 'passport_uid'),
    )

    assert response.status == 409
    content = response.json()
    assert content == {
        'code': 'TAXPAYER_UNREGISTERED',
        'message': 'Вы не зарегистрировались как самозанятый',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
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
async def test_post_nalog_app_unavailable(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind(request):
        assert request.json == {
            'phone_pd_id': 'PHONE_PD_ID',
            'permissions': ['TEST1', 'TEST2'],
        }
        return aiohttp.web.json_response(
            {'code': 'FNS_UNAVAILABLE'}, status=503,
        )

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('nalog-app', 'passport_uid'),
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
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
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
async def test_post_nalog_app_already_bound(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        pgsql,
        prepare_post_rq,
):
    @mockserver.json_handler('/selfemployed-fns-proxy/v1/bind/phone')
    async def _bind(request):
        assert request.json == {
            'phone_pd_id': 'PHONE_PD_ID',
            'permissions': ['TEST1', 'TEST2'],
        }
        return aiohttp.web.json_response(
            {
                'code': 'TAXPAYER_ALREADY_BOUND',
                'details': {'inn_pd_id': 'INN_PD_ID'},
            },
            status=409,
        )

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('nalog-app', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'agreement',
        'step_count': 9,
        'step_index': 5,
    }

    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(GET_PHONE_BINDING)
    row = cursor.fetchone()

    assert row == ('COMPLETED', 'INN_PD_ID', None)

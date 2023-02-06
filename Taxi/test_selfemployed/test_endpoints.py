# pylint: disable=redefined-outer-name,unused-variable
import pytest

from selfemployed.db import dbmain
from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_get_steps(se_client):
    park_id = 'gs1p'
    driver_id = 'gs1d'

    response = await se_client.get(
        '/self-employment/fns-se/steps',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'steps': [
            {
                'key': 'intro',
                'text': 'Получите статус самозанятого',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '1 из 6',
            },
            {
                'key': 'nalog_app',
                'text': 'Стать самозанятым',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'intro',
                'title': '1 из 6',
            },
            {
                'key': 'phone_number',
                'text': 'Проверка номера',
                'done': False,
                'visible_for_user': False,
                'previous_step': 'nalog_app',
                'title': '1 из 6',
            },
            {
                'key': 'sms',
                'text': 'Код из СМС',
                'done': False,
                'visible_for_user': False,
                'previous_step': 'phone_number',
                'title': '1 из 6',
            },
            {
                'key': 'agreement',
                'text': 'Соглашение',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'nalog_app',
                'title': '2 из 6',
            },
            {
                'key': 'address',
                'text': 'Укажите адрес прописки',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'agreement',
                'title': '3 из 6',
            },
            {
                'key': 'permission',
                'text': 'Свяжите профили',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'address',
                'title': '4 из 6',
            },
            {
                'key': 'requisites',
                'text': 'Укажите реквизиты',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'permission',
                'title': '5 из 6',
            },
        ],
        'fns_package_name': 'com.gnivts.selfemployed',
        'fns_appstore_id': '1437518854',
        'current_step': 'intro',
    }


async def test_complete_steps(se_client):
    park_id = '1'
    driver_id = '1'
    data = {'step': 'overview'}

    response = await se_client.post(
        '/self-employment/fns-se/steps',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'nalog_app',
        'step_index': 1,
        'step_count': 7,
    }


async def test_post_intro_401(se_client):
    data = {'step': dbmain.Step.INTRO}

    response = await se_client.post(
        '/self-employment/fns-se/intro',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_intro_400(se_client):
    response = await se_client.post(
        '/self-employment/fns-se/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': '1', 'driver': '1'},
        json={},
    )
    assert response.status == 400


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_intro_409(se_client, se_web_context):
    park_id = '1'
    driver_id = '1'
    data = {'step': dbmain.Step.INTRO}

    response = await se_client.post(
        '/self-employment/fns-se/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )

    # assert response
    assert response.status == 409
    content = await response.json()
    assert content == {'code': 'update_app', 'text': 'Обновите приложение'}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_selfreg_intro_409(se_client, se_web_context):
    selfreg_id = '123'
    data = {'step': dbmain.Step.INTRO}

    response = await se_client.post(
        '/self-employment/fns-se/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'selfreg_id': selfreg_id},
        json=data,
    )

    # assert response
    assert response.status == 409
    content = await response.json()
    assert content == {'code': 'update_app', 'text': 'Обновите приложение'}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@conftest.agreement_configs3
async def test_get_agreement(se_client):
    park_id = '1'
    driver_id = '1'

    response = await se_client.get(
        '/self-employment/fns-se/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == conftest.AGREEMENT_DEFAULT_RESPONSE


@pytest.mark.parametrize(
    'request_body, selfreg_profile, driver_profile, expected_response',
    [
        # selfreg, courier
        (
            {'selfreg_id': '123'},
            {'license_pd_id': None},
            None,
            conftest.AGREEMENT_DEFAULT_RESPONSE,
        ),
        # selfreg, driver
        (
            {'selfreg_id': '123'},
            {'license_pd_id': 'license_id_driver'},
            None,
            conftest.AGREEMENT_WITH_DRIVER_LICENSE_RESPONSE,
        ),
        # from park, courier
        (
            {'park': 'park_id_1', 'driver': 'driver_id_1'},
            None,
            {'license': {'pd_id': 'license_id_courier'}},
            conftest.AGREEMENT_DEFAULT_RESPONSE,
        ),
        # from park, driver
        (
            {'park': 'park_id_1', 'driver': 'driver_id_1'},
            None,
            {'license': {'pd_id': 'license_id_driver'}},
            conftest.AGREEMENT_WITH_DRIVER_LICENSE_RESPONSE,
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@conftest.agreement_configs3
async def test_get_v2_agreement(
        se_client,
        mockserver,
        request_body,
        selfreg_profile,
        driver_profile,
        expected_response,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request):
        assert request.json['id_in_set'] == ['park_id_1_driver_id_1']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park_id_1_driver_id_1',
                    'data': driver_profile,
                },
            ],
        }

    @mockserver.json_handler('/selfreg-api/get_profile')
    def _selfreg_get_profile(request):
        assert request.method == 'POST'
        return selfreg_profile

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _license_retrieve(request):
        value = None
        if request.json['id'] == 'license_id_driver':
            value = '12345678'
        elif request.json['id'] == 'license_id_courier':
            value = 'COURIER38288'
        return {'id': request.json['id'], 'value': value}

    response = await se_client.get(
        '/self-employment/fns-se/v2/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


async def test_post_agreement_401(se_client):
    data = {'step': dbmain.Step.AGREEMENT, 'accepted': True}

    response = await se_client.post(
        '/self-employment/fns-se/agreement',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_agreement_body_400(se_client):
    params = {'park': '1', 'driver': '1'}
    response = await se_client.post(
        '/self-employment/fns-se/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json={},
    )
    assert response.status == 400


async def test_post_agreement_step_400(se_client):
    data = {'step': dbmain.Step.INTRO}
    params = {'park': '1', 'driver': '1'}

    response = await se_client.post(
        '/self-employment/fns-se/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


async def test_post_agreement_200(se_client, se_web_context):
    park_id = '2'
    driver_id = '2'
    data = {'step': dbmain.Step.AGREEMENT, 'accepted': True}
    params = {'park': park_id, 'driver': driver_id}

    # let's prepare and create a new profile first...
    postgres = se_web_context.pg
    await dbmain.insert_new(postgres, park_id, driver_id)

    # ... and now accepting agreement
    response = await se_client.post(
        '/self-employment/fns-se/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'address',
        'step_index': 4,
        'step_count': 7,
    }

    # assert db
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    assert row['agreement_accepted']
    assert not row['gas_stations_accepted']
    assert row['status'] == dbmain.Status.NEW
    assert row['step'] == dbmain.Step.AGREEMENT


async def test_post_v2_agreement_401(se_client):
    data = {
        'step': dbmain.Step.AGREEMENT,
        'agreements': [{'id': 'id1', 'state': 'accepted'}],
    }

    response = await se_client.post(
        '/self-employment/fns-se/v2/agreement',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_v2_agreement_body_400(se_client):
    params = {'park': '1', 'driver': '1'}
    response = await se_client.post(
        '/self-employment/fns-se/v2/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json={},
    )
    assert response.status == 400


@pytest.mark.config(GAS_STATIONS_OFFER_URL=conftest.GAS_STATIONS_OFFER_URL)
@pytest.mark.parametrize(
    'accepted_agreements,expected_response_code,expected_gas_stations_status',
    [
        # not all required agreements accepted
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
            ],
            409,
            False,
        ),
        # all required accepted, no gas stations
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'some_not_existing_agreement',
            ],
            200,
            False,
        ),
        # all accepted, including gas stations
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'agreement_taxi_transfer_to_third_party_checkbox',
                'agreement_taxi_gas_stations_checkbox',
            ],
            200,
            True,
        ),
        # one out of two gas stations offers accepted
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'agreement_taxi_gas_stations_checkbox',
            ],
            200,
            False,
        ),
    ],
)
@conftest.agreement_configs3
async def test_post_v2_agreement_some_agreements_accepted(
        se_client,
        se_web_context,
        mockserver,
        accepted_agreements,
        expected_response_code,
        expected_gas_stations_status,
):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    license_id = 'license_pd_id_1'
    license_value = '12345678'

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request):
        assert request.json['id_in_set'] == [f'{park_id}_{driver_id}']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': f'{park_id}_{driver_id}',
                    'data': {'license': {'pd_id': license_id}},
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _license_retrieve(request):
        assert request.json['id'] == license_id
        return {'id': license_id, 'value': license_value}

    postgres = se_web_context.pg
    await dbmain.insert_new(postgres, park_id, driver_id)

    request = {
        'step': dbmain.Step.AGREEMENT,
        'agreements': [
            {'id': x, 'state': 'accepted'} for x in accepted_agreements
        ],
    }

    params = {'park': park_id, 'driver': driver_id}
    response = await se_client.post(
        '/self-employment/fns-se/v2/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=request,
    )

    assert response.status == expected_response_code
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    if response.status == 200:
        assert row['agreement_accepted']
        assert row['gas_stations_accepted'] == expected_gas_stations_status
        assert row['step'] == dbmain.Step.AGREEMENT
    else:
        assert not row['agreement_accepted']
        assert not row['gas_stations_accepted']
        assert row['step'] == dbmain.Step.INTRO


async def test_post_nalog_app_401(se_client):
    data = {'step': dbmain.Step.NALOG_APP, 'phone_number': '+71234567890'}

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_nalog_app_body_400(se_client):
    params = {'park': '1', 'driver': '1'}
    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json={},
    )
    assert response.status == 400


async def test_post_nalog_app_step_400(se_client):
    data = {'step': dbmain.Step.NALOG_APP}
    params = {'park': '1', 'driver': '1'}

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


async def test_post_nalog_app_with_id_200(se_client, se_web_context, patch):
    park_id = '3'
    driver_id = '3'
    phone = '+70003234444'
    data = {'step': dbmain.Step.NALOG_APP, 'phone_number': phone}
    params = {'park': park_id, 'driver': driver_id}

    # let's prepare and create a new profile first...
    postgres = se_web_context.pg
    await dbmain.insert_new(postgres, park_id, driver_id)

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_mock(*args, **kwargs):
        return '454'

    @patch('taxi.clients.parks.ParksClient.get_driver_phone')
    async def _get_phones(park_id_: str, driver_id_: str):
        assert park_id_ == park_id
        assert driver_id_ == driver_id
        return ['+70003234444']

    # ... and now trying to bind to FNS
    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': dbmain.Step.AGREEMENT,
        'step_index': 3,
        'step_count': 7,
    }

    # assert db
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    assert row['status'] == dbmain.Status.REQUESTED
    assert row['step'] == dbmain.Step.NALOG_APP


async def test_post_nalog_app_no_id_200(se_client, se_web_context, patch):
    park_id = '4'
    driver_id = '4'
    phone = '+70003234444'
    data = {'step': dbmain.Step.NALOG_APP, 'phone_number': phone}
    params = {'park': park_id, 'driver': driver_id}

    # let's prepare and create a new profile first...
    postgres = se_web_context.pg
    await dbmain.insert_new(postgres, park_id, driver_id)

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_mock(*args, **kwargs):
        return None

    @patch('taxi.clients.parks.ParksClient.get_driver_phone')
    async def _get_phones(park_id_: str, driver_id_: str):
        assert park_id_ == park_id
        assert driver_id_ == driver_id
        return ['+70003234444']

    # ... and now trying to bind to FNS
    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': dbmain.Step.PHONE_NUMBER,
        'step_index': 2,
        'step_count': 7,
    }

    # assert db
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    assert row['status'] == dbmain.Status.NEW
    assert row['step'] == dbmain.Step.NALOG_APP


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        'INSERT INTO profiles (id, from_park_id, from_driver_id, status, '
        'step, created_at, modified_at) '
        'VALUES(\'8eb93a7e1b734cfebce7d69b85973972\', \'2\', \'2\', \'new\', '
        '\'intro\', now()::timestamp, now()::timestamp) ',
    ],
)
async def test_reg_address_flow(se_client, se_web_context, patch):
    park_id = '2'
    driver_id = '2'
    postal_code = '123456'

    @patch('taxi.clients.geocoder.GeocoderClient.get_postal_code')
    async def get_postal_code(*args, **kwargs):
        return postal_code

    response = await se_client.get(
        '/self-employment/fns-se/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'address': '', 'apartment_number': ''}

    # make an entry

    address = 'Россия, Москва, Южнобутовская улица, 62'
    flat = '70'
    data = {
        'step': dbmain.Step.ADDRESS,
        'address': address,
        'apartment_number': flat,
    }

    response = await se_client.post(
        '/self-employment/fns-se/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': dbmain.Step.PERMISSION,
        'step_index': 5,
        'step_count': 7,
    }

    # check entry

    response = await se_client.get(
        '/self-employment/fns-se/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'address': address, 'apartment_number': flat}

    entry = await dbmain.get_from_driver(se_web_context.pg, park_id, driver_id)
    assert entry['post_code'] == postal_code


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        'INSERT INTO profiles (id, from_driver_id, from_park_id, '
        'phone, park_id, driver_id, created_at, modified_at) '
        'VALUES(\'aaa15\', \'1d\', \'1p\', \'+70123456789\', '
        '\'1p_new\', \'1d_new\', now()::timestamp, now()::timestamp)',
    ],
)
async def test_finish(se_client):
    park_id = '1p'
    driver_id = '1d'

    response = await se_client.get(
        '/self-employment/fns-se/finish',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'is_phone_changed': True,
        'selfemployed': {
            'name': 'Работать на себя',
            'park_id': '1p_new',
            'phone_number': '+70123456789',
        },
        'promocode_enabled': True,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """INSERT INTO profiles (id, from_driver_id, from_park_id,
        phone, park_id, driver_id, created_at, modified_at)
        VALUES('aaa15', 'driver_selfreg_token', 'selfreg', '+70123456789',
        'park_new', 'driver_new', now(), now())""",
    ],
)
@pytest.mark.parametrize(
    'get_profile_response, expect_code, expect_response',
    [
        pytest.param(
            {},
            500,
            None,
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'owncar'},
            200,
            {
                'new_driver': {
                    'park_id': 'park_new',
                    'driver_id': 'driver_new',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'referral_promocode': 'test'},
            200,
            {
                'new_driver': {
                    'park_id': 'park_new',
                    'driver_id': 'driver_new',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'referral_promocode': 'test'},
            200,
            {
                'new_driver': {
                    'park_id': 'park_new',
                    'driver_id': 'driver_new',
                },
                'promocode_enabled': False,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=True),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'park': {'name': 'park_for_rent'}},
            200,
            {
                'new_driver': {
                    'park_id': 'park_new',
                    'driver_id': 'driver_new',
                },
                'park_to_visit': {
                    'name': 'park_for_rent',
                    'description': '',
                    'phone': '',
                    'documents': [],
                    'address': '',
                    'working_hours': '',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
    ],
)
async def test_finish_from_selfreg(
        se_client,
        mockserver,
        get_profile_response,
        expect_code,
        expect_response,
):
    @mockserver.json_handler('/driver-referrals/service/save-invited-driver')
    async def save_invited_driver(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/selfreg-api/get_profile')
    def _selfreg_get_profile(request):
        assert request.method == 'POST'
        return get_profile_response

    selfreg_id = 'driver_selfreg_token'
    response = await se_client.get(
        '/self-employment/fns-se/finish',
        headers=conftest.DEFAULT_HEADERS,
        params={'selfreg_id': selfreg_id},
    )
    assert response.status == expect_code
    if expect_response is not None:
        content = await response.json()
        assert content == expect_response

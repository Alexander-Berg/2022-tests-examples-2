import pytest

from testsuite.utils import http

from test_selfemployed import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@conftest.intro_info_configs3
async def test_get_intro(se_client, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks')
    async def _get_parks(request: http.Request):
        assert request.query['park_id'] == 'park_id'
        return {
            'id': 'park_id',
            'city_id': 'Москва',
            'country_id': 'rus',
            'demo_mode': True,
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'locale': 'ru',
            'login': 'login',
            'name': 'name',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.get(
        '/self-employment/fns-se/v2/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content['items'] == [
        {
            'horizontal_divider_type': 'bottom_icon',
            'right_icon': 'undefined',
            'subtitle': 'Быть партнером хорошо',
            'type': 'header',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
            },
            'right_icon': 'undefined',
            'title': 'Нет комиссии таксопарка',
            'subtitle': 'Подзаголовок',
            'type': 'icon_detail',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
            },
            'right_icon': 'undefined',
            'title': 'Деньги на карту сразу',
            'subtitle': 'Подзаголовок',
            'type': 'icon_detail',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
                'tint_color': '',
            },
            'right_icon': 'undefined',
            'title': 'Приоритет на месяц',
            'subtitle': 'Подзаголовок',
            'type': 'icon_detail',
        },
    ]


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'version,items',
    [
        ('Taximeter 1.00', [{'type': 'default', 'title': 'Подзаголовок'}]),
        ('Taximeter 8.79', [{'type': 'icon_detail', 'title': 'Подзаголовок'}]),
        ('Taximeter 8.80', [{'type': 'type_detail', 'title': 'Подзаголовок'}]),
        ('Taximeter 8.84', [{'type': 'future', 'title': 'Подзаголовок'}]),
    ],
)
@conftest.intro_info_configs3
async def test_get_intro_w_useragent(
        se_client, version, items, mock_fleet_parks,
):
    @mock_fleet_parks('/v1/parks')
    async def _get_parks(request: http.Request):
        assert request.query['park_id'] == 'park_id'
        return {
            'id': 'park_id',
            'city_id': 'Москва',
            'country_id': 'rus',
            'demo_mode': True,
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'locale': 'ru',
            'login': 'login',
            'name': 'name',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    park_id = 'park_id'
    contractor_id = 'contractor_id'
    response = await se_client.get(
        '/self-employment/fns-se/v2/intro',
        params={'park': park_id, 'driver': contractor_id},
        headers={'User-Agent': version},
    )
    assert response.status == 200
    content = await response.json()
    assert content['items'] == items


async def test_post_intro(se_client, mock_personal):
    park_id = 'p1'
    contractor_id = 'c1'

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID'}

    response = await se_client.post(
        '/self-employment/fns-se/v2/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'intro', 'phone_number': '+70001234567'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'nalog_app',
        'step_count': 7,
        'step_index': 1,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'PHONE_PD_ID');
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
async def test_post_intro_park_changed(se_client, mock_personal):
    park_id = 'other_park_id'
    contractor_id = 'other_contractor_id'

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID'}

    response = await se_client.post(
        '/self-employment/fns-se/v2/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'intro', 'phone_number': '+70001234567'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }

# pylint: disable=redefined-outer-name

import pytest

from testsuite.utils import http

from . import conftest


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
    driver_id = 'contractor_id'

    response = await se_client.get(
        '/self-employment/fns-se/intro',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
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
    driver_id = 'contractor_id'

    response = await se_client.get(
        '/self-employment/fns-se/intro',
        headers={'User-Agent': version},
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content['items'] == items

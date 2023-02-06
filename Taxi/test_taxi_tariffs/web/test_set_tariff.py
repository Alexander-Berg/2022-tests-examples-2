import http
import json

import pytest

from taxi import config


def _all_languages(value):
    return {locale: value for locale in config.Config.LOCALES_SUPPORTED}


TRANSLATIONS = {
    'geoareas': {
        'moscow': _all_languages('Moscow'),
        'inside_suburb': _all_languages('Suburb'),
        'city': _all_languages('City'),
        'dme': _all_languages('DME'),
    },
    'tariff': {
        'interval.24h': _all_languages('all day'),
        'currency.rub': _all_languages('ruble'),
        'service_name.covid_test': _all_languages('Covid Test'),
    },
}


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize(
    'zone, data, expected_status, expected_content',
    (
        (
            'moscow',
            'request_vip_category.json',
            http.HTTPStatus.OK,
            'response_vip_category.json',
        ),
        (
            'moscow',
            'request_with_extra.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Unexpected fields: unexpected_field',
            },
        ),
        (
            'moscow',
            'request_with_invalid_requirement.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'unknown_requirement',
                'message': 'unknown_requirement: "invalid_requirement"',
            },
        ),
        (
            'moscow',
            'request_with_usa_currency.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'unknown_currency',
                'message': 'missing_currencies: {\'USD\'}',
            },
        ),
        (
            'moscow',
            'request_with_invalid_currency.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'unknown_currency',
                'message': 'missing_currencies: {\'AAA\'}',
            },
        ),
        (
            'moscow',
            'request_with_overlaped_category_by_time.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'overlapping_categories',
                'message': 'categories with name "business" is overlaped',
            },
        ),
        (
            'moscow',
            'request_with_overlaped_categories.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'overlapping_categories',
                'message': 'categories with name "econom" is overlaped',
            },
        ),
        (
            'moscow',
            'request_vip_category_too_different.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'invalid_price_interval',
                'message': (
                    'home_zone moscow; '
                    'category vip; '
                    'type application; '
                    'day type 2; '
                    'from 00:00; '
                    'to 23:59; '
                    'field minimal'
                ),
            },
        ),
        (
            'moscow',
            'request_vip_same_category.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ok',
                'message': (
                    'tariff was not modified, as it is equal to current'
                ),
            },
        ),
        (
            'moscow',
            'request_vip_category_with_summable_requirements.json',
            http.HTTPStatus.OK,
            'response_vip_category_with_summable_requirements.json',
        ),
        (
            'moscow',
            {
                'activation_zone': 'moscow_activation',
                'country': 'invalid_country',
                'geo_node_name': 'test_geo_node',
                'categories': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_COUNTRY',
                'message': (
                    'geoarea "moscow" has country "rus", '
                    'but request body has "invalid_country"'
                ),
            },
        ),
        (
            'moscow',
            'request_pool_category.json',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'error',
                'message': 'Invalid tariffs: missing pool or drivers_pool',
            },
        ),
        (
            'moscow',
            {
                'activation_zone': 'moscow_activation',
                'country': 'invalid_country',
                'geo_node_name': 'test_geo_node',
                'categories': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_COUNTRY',
                'message': (
                    'geoarea "moscow" has country "rus", '
                    'but request body has "invalid_country"'
                ),
            },
        ),
    ),
)
@pytest.mark.parametrize(
    'url', ('/v1/tariff/draft/apply', '/v1/tariff/draft/check'),
)
@pytest.mark.now('2020-01-01T18:00:00+00:00')
async def test_set_tariff(
        web_app_client,
        zone,
        data,
        expected_status,
        expected_content,
        mockserver,
        open_file,
        url,
):
    if isinstance(data, str):
        data = json.loads(open_file(data).read().encode())

    if isinstance(expected_content, str):
        expected_content = json.loads(
            open_file(expected_content).read().encode(),
        )

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/admin/tariff_zones/set_parent/check/',
    )
    async def _agglomeration_check_set_parent_handler(request):
        geo_node = request.json['parent']['geo_node_name']

        return {
            'change_doc_id': geo_node,
            'data': request.json,
            'lock_ids': [{'custom': True, 'id': geo_node}],
        }

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/admin/tariff_zones/set_parent/',
    )
    async def _agglomeration_set_parent_handler(request):
        return request.json

    @mockserver.json_handler('territories/v1/countries/list')
    async def _territories_country_list_handler(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'region_id': 1,
                    'phone_code': '7',
                    'code2': 'RU',
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '7',
                    'currency': 'RUB',
                },
                {
                    '_id': 'usa',
                    'region_id': 1,
                    'phone_code': '7',
                    'code2': 'RU',
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '7',
                    'currency': 'USD',
                },
            ],
        }

    for category in data['categories']:
        category.setdefault('meters', [])
        category.setdefault('zonal_prices', [])
        category.setdefault('included_one_of', [])
        category.setdefault('special_taximeters', [])
        category.setdefault('summable_requirements', [])
    data['home_zone'] = zone
    response = await web_app_client.post(url, json=data, params={'zone': zone})
    assert response.status == expected_status, await response.json()
    content = await response.json()
    if response.status == http.HTTPStatus.OK:
        if 'check' in url:
            return
        for category in content['categories']:
            category.pop('id', None)
    assert content == expected_content

import json

import pytest


@pytest.mark.parametrize(
    'path, response_filename',
    [
        # без поисковых параметров
        (
            '/admin/v1/partner/in-category/new/',
            'v1_partner_in-category_new.json',
        ),
        (
            '/admin/v1/partner/in-category/denied/',
            'v1_partner_in-category_denied.json',
        ),
        (
            '/admin/v1/partner/in-category/resolved/',
            'v1_partner_in-category_resolved.json',
        ),
        # с поисковыми параметрами
        (
            '/admin/v1/partner/in-category/new/?park_name=inTaxis',
            'v1_partner_in-category_new_park_name_inTaxis.json',
        ),
        (
            '/admin/v1/partner/in-category/new/?company_fullname=Хараев',
            'v1_partner_in-category_new_company_fullname.json',
        ),
        (
            '/admin/v1/partner/in-category/resolved/?company_inn=773000663134',
            'v1_partner_in-category_resolved_company_inn_773000663134.json',
        ),
        # UID в базе может быть записан как число
        (
            '/admin/v1/partner/in-category/resolved/?uid=5',
            'v1_partner_in-category_resolved_uid_5.json',
        ),
        # UID в базе может быть записан как строка
        (
            '/admin/v1/partner/in-category/new/?uid=1000000008',
            'v1_partner_in-category_new_company_fullname.json',
        ),
        # поиск по городу ищет в двух полях
        (
            '/admin/v1/partner/in-category/denied/?park_city=Зеленоград',
            'v1_partner_in-category_denied_park_city.json',
        ),
        # спецсимволы в запросах
        (
            '/admin/v1/partner/in-category/denied/'
            '?park_city=Зеленоград+%28МО%29',
            'v1_partner_in-category_denied_park_city_with_symbols.json',
        ),
        (
            '/admin/v1/partner/in-category/denied/'
            '?park_city=Зеленоград%20%28МО%29',
            'v1_partner_in-category_denied_park_city_with_symbols.json',
        ),
        # проверка работы limit (без skip)
        (
            '/admin/v1/partner/in-category/new/?limit=2',
            'v1_partner_in-category_new_limit_2.json',
        ),
        # проверка работы limit (со skip)
        (
            '/admin/v1/partner/in-category/new/?limit=1&skip=1',
            'v1_partner_in-category_new_limit_1_skip_1.json',
        ),
        # проверка работы limit (со skip и поисковым параметром)
        (
            '/admin/v1/partner/in-category/new/'
            '?limit=1&skip=1&park_city=Москва',
            'v1_partner_in-category_new_limit_1_skip_1_park_city.json',
        ),
    ],
)
async def test_partner_categories(
        web_app_client, load, path, response_filename,
):
    response = await web_app_client.get(path)
    assert response.status == 200
    content = await response.json()
    expected_response = json.loads(load(response_filename))
    assert content == expected_response

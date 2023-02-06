# pylint: disable=redefined-outer-name
import copy

import pytest

from partner_offers import geosearch_parsing as geo

BUSINESS_OID = 123456

STUB_ORGANIZATION = geo.OrganizationData(
    name='Магнит',
    logo_uri='https://avatars.mds.yandex.net/get-altay/1881734/2/M',
    chain_id=58,
)

STUB_LOCATIONS = [
    geo.LocationData(
        name='Магнит',
        business_oid=BUSINESS_OID,
        longitude=50.43,
        latitude=30.6,
        work_times=[(2342344, 2345344), (2842344, 2845344)],
        timezone_offset=10800,
        country='Россия',
        city='Кукуево',
        formatted_address='Россия, с.Кукуево, ул.Ильича, д.Лампочка',
        logo_uri='https://avatars.mds.yandex.net/get-altay/11734/2/M',
        chain=geo.ChainData(chain_id=58, name='Магнит'),
    ),
    geo.LocationData(
        name='Магнит2',
        business_oid=BUSINESS_OID + 5,
        longitude=54.43,
        latitude=33.6,
        work_times=[(2342344, 2345342), (2842344, 2845342)],
        timezone_offset=10800,
        country='Россия',
        city='Мухоморы',
        formatted_address='Россия, Грибная Респ., Радиоволновой р-н, '
        'г.Мухоморы, Ленинский пр., д.1917',
        logo_uri='https://avatars.mds.yandex.net/get-altay/11734/2/M',
        chain=geo.ChainData(chain_id=58, name='Магнит'),
    ),
]

TRANSLATIONS = {'Food': {'ru': 'Еда', 'en': 'Food'}}

PARTNER_DEALS_PARTNER_CATEGORIES_STUB = [
    {
        'category': 'food',
        'name': 'Food',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
    },
    {
        'category': 'service',
        'name': 'invalid_key',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
    },
]

EXPECTED_RESPONSE_BODY = {
    'id': '1',
    'name': 'Магнит',
    'logo': 'https://avatars.mds.yandex.net/get-altay/1881734/2/M',
    'deals_related': {'category': 'food', 'comment': 'some comment'},
    'locations': [
        {
            'name': 'Россия, Кукуево',
            'locations': [
                {
                    'address': 'Россия, с.Кукуево, ул.Ильича, д.Лампочка',
                    'name': 'Магнит',
                    'id': str(BUSINESS_OID),
                    'map_link': f'https://yandex.ru/maps/?mode=search&ol=biz&oid={BUSINESS_OID}',  # noqa: E501
                },
            ],
        },
        {
            'name': 'Россия, Мухоморы',
            'locations': [
                {
                    'address': (
                        'Россия, Грибная Респ., Радиоволновой р-н, '
                        'г.Мухоморы, Ленинский пр., д.1917'
                    ),
                    'name': 'Магнит2',
                    'id': str(BUSINESS_OID + 5),
                    'map_link': f'https://yandex.ru/maps/?mode=search&ol=biz&oid={BUSINESS_OID + 5}',  # noqa: E501
                },
            ],
        },
    ],
    'changelog': {'updated_by': 'Piter', 'created_by': 'Piter'},
}

BIG_ZOMBIE_SHOP_STUB_RESPONSE = {
    'name': 'Big zombie shop',
    'logo': 'https://example.com/image.jpg',
    'deals_related': {'category': 'food', 'comment': 'Some comment text'},
    'locations': [],
    'changelog': {
        'updated_by': 'valery',
        'updated_at': '2019-05-26T19:10:25+03:00',
        'created_by': 'valery',
        'created_at': '2019-05-26T19:10:25+03:00',
    },
}


@pytest.fixture
def search_org_mock_success(patch):
    @patch('partner_offers.geosearch_parsing.search_organization')
    async def _search_organization(
            business_oid: int, lang: str, *args, **kwargs,
    ):
        return STUB_ORGANIZATION, STUB_LOCATIONS[0]

    return _search_organization


@pytest.fixture
def search_org_mock_not_found(patch):
    @patch('partner_offers.geosearch_parsing.search_organization')
    async def _search_organization(*args, **kwargs):
        return None

    return _search_organization


@pytest.fixture
def get_locations_mock_success(patch):
    @patch('partner_offers.geosearch_parsing.get_locations_of_organization')
    async def _get_locations_of_organization(
            chain_id, lang: str, context, *args, **kwargs,
    ):
        assert chain_id == STUB_ORGANIZATION.chain_id
        return STUB_LOCATIONS

    return _get_locations_of_organization


@pytest.fixture
def get_locations_mock_throw(patch):
    @patch('partner_offers.geosearch_parsing.get_locations_of_organization')
    async def _get_locations_of_organization(
            chain_id, lang: str, context, *args, **kwargs,
    ):
        assert False, 'Must not be called'

    return _get_locations_of_organization


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_create_partner_201(
        search_org_mock_success,
        get_locations_mock_success,
        web_app_client,
        pgsql,
):
    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 201, await response.text()
    result_json = await response.json()
    del result_json['changelog']['created_at']
    del result_json['changelog']['updated_at']
    res = copy.deepcopy(EXPECTED_RESPONSE_BODY)
    del res['deals_related']['category']
    assert result_json == res

    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(
        'SELECT id, geo_chain_id, category, comment, '
        'name, logo, created_by, updated_by FROM partner;',
    )
    rows = [x for x in cursor]
    assert len(rows) == 1, rows
    row = rows[0]
    assert row[0] == 1
    assert row[1] == STUB_ORGANIZATION.chain_id
    assert row[2] == 'here_will_be_marketplace_category'
    assert row[3] == 'some comment'
    assert row[4] == 'Магнит'
    assert row[5] == STUB_ORGANIZATION.logo_uri
    assert row[6] == 'Piter'
    assert row[7] == 'Piter'

    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(
        'SELECT business_oid, partner_id, longitude, latitude, name,'
        ' country, city, address, work_time_intervals FROM location '
        'ORDER BY business_oid;',
    )
    rows = list(cursor)
    assert len(rows) == 2, rows
    for loc, row in zip(STUB_LOCATIONS, rows):
        assert row[0] == loc.business_oid
        assert row[1] == 1
        assert row[2] == loc.longitude
        assert row[3] == loc.latitude
        assert row[4] == loc.name
        assert row[5] == loc.country
        assert row[6] == loc.city
        assert row[7] == loc.formatted_address
        assert [(x['from'], x['to']) for x in row[8]] == loc.work_times


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_create_partner_with_cat_400(
        search_org_mock_success,
        get_locations_mock_success,
        web_app_client,
        pgsql,
):
    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'category': 'food', 'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 400
    assert (await response.json()) == {
        'text': 'New partners should not have categories',
        'code': 'category_in_request',
    }


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.pgsql(
    'partner_offers',
    files=['../test_search_organizations/pg_static_data.sql'],
)
async def test_create_partner_200_old_business_oid(web_app_client, mockserver):
    """Check that we do not modify if business_oid not exists."""

    # pylint: disable=unused-variable

    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(_):
        assert False, 'Must not be called'

    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    del response_json['id']
    expected = {
        **BIG_ZOMBIE_SHOP_STUB_RESPONSE,
        'locations': [
            {
                'name': 'Russia, Moscow',
                'locations': [
                    {
                        'address': 'Москва, Лубянка, 5',
                        'name': 'Big zombie shop',
                        'id': str(BUSINESS_OID),
                        'map_link': f'https://yandex.ru/maps/?mode=search&ol=biz&oid={BUSINESS_OID}',  # noqa: E501
                    },
                ],
            },
        ],
    }
    assert response_json == expected


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.pgsql('partner_offers', files=['pg_chain_id_exists.sql'])
async def test_create_partner_200_old_chain_id(
        search_org_mock_success, get_locations_mock_success, web_app_client,
):
    """Check that we do not modify if chain_id exists"""
    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    del response_json['id']
    expected = BIG_ZOMBIE_SHOP_STUB_RESPONSE
    assert response_json == expected


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_create_partner_200_insert_in_the_middle(
        search_org_mock_success, monkeypatch, web_app_client, pgsql,
):
    """Checks that nothing changes in DB
    if the row appears after first check
    but before getting answer from geosearch"""

    async def _get_locations_of_organization(
            business_oid: int, lang: str, *args, **kwargs,
    ):
        with pgsql['partner_offers'].cursor() as cursor:
            cursor.execute(
                """INSERT INTO partner
            (category, geo_chain_id, name, logo, comment, created_by,
             created_at, updated_by, updated_at)
            VALUES (
                    'food',
                    58,
                    'Big zombie shop',
                    'https://example.com/image.jpg',
                    'Some comment text',
                    'valery',
                    '2019-05-26 19:10:25+3',
                    'valery',
                    '2019-05-26 19:10:25+3'
                   );""",
            )
        return STUB_LOCATIONS

    monkeypatch.setattr(
        'partner_offers.geosearch_parsing.get_locations_of_organization',
        _get_locations_of_organization,
    )
    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    del response_json['id']
    expected = BIG_ZOMBIE_SHOP_STUB_RESPONSE
    assert response_json == expected


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=PARTNER_DEALS_PARTNER_CATEGORIES_STUB,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_org_not_found(
        search_org_mock_not_found, get_locations_mock_throw, web_app_client,
):
    response = await web_app_client.post(
        '/internal/v1/partners/',
        json={
            'business_oid': str(BUSINESS_OID),
            'deals_related': {'comment': 'some comment'},
        },
        headers={'Accept-Language': 'ru-RU,ru', 'X-Yandex-Login': 'Piter'},
    )
    assert response.status == 400, await response.text()
    assert await response.json() == {
        'code': 'not_found_organization',
        'text': 'Not found org with id 123456. Try search_organizations first',
    }

# pylint: disable=redefined-outer-name
import pytest

from partner_offers import geosearch_parsing


@pytest.fixture
def search_org_mock_success(patch):
    @patch('partner_offers.geosearch_parsing.search_organization')
    async def _search_organization(
            business_oid: int, lang: str, *args, **kwargs,
    ):
        return (
            geosearch_parsing.OrganizationData(
                name='Магнит',
                logo_uri='https://avatars.mds.yandex.net/get-altay/1881734/2a0000016a35aba90cfe1b24c59b99f31939/M',  # noqa: E501,
                chain_id=None,
            ),
            geosearch_parsing.LocationData(
                name='Магнит',
                business_oid=business_oid,
                longitude=50.0,
                latitude=30.0,
                work_times=[],
                timezone_offset=3600,
                country='Россия',
                city='Кукуево',
                formatted_address='Россия, с. Кукуево, ул. Ильича, д. Лампочка',  # noqa: E501
                logo_uri='https://avatars.mds.yandex.net/get-altay/1881734/2a0000016a35aba90cfe1b24c59b99f31939/M',  # noqa: E501
                chain=None,
            ),
        )

    return _search_organization


@pytest.fixture
def search_org_mock_not_found(patch):
    @patch('partner_offers.geosearch_parsing.search_organization')
    async def _search_organization(*args, **kwargs):
        return None

    return _search_organization


async def test_search_organizations(web_app_client, search_org_mock_success):
    business_oid = 1255966696
    uri = f'/internal/v1/organizations/list?business_oid={business_oid}'
    response = await web_app_client.post(uri)
    assert response.status == 200, await response.text()
    content = await response.json()
    expected = {
        'organizations': [
            {
                'business_oid': str(business_oid),
                'logo': 'https://avatars.mds.yandex.net/get-altay/1881734/2a0000016a35aba90cfe1b24c59b99f31939/M',  # noqa: E501
                'name': 'Магнит',
            },
        ],
    }
    assert content == expected


@pytest.mark.pgsql('partner_offers', files=['pg_static_data.sql'])
async def test_already_has(web_app_client, mockserver):
    # pylint: disable=unused-variable

    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(_):
        assert False, 'Must not be called'

    business_oid = 123456
    uri = f'/internal/v1/organizations/list?business_oid={business_oid}'
    response = await web_app_client.post(uri)
    assert response.status == 409, await response.text()
    response_json = await response.json()
    del response_json['id']
    expected = {
        'name': 'Big zombie shop',
        'logo': 'https://example.com/image.jpg',
        'deals_related': {'category': 'food', 'comment': 'Some comment text'},
        'locations': [
            {
                'name': 'Russia, Moscow',
                'locations': [
                    {
                        'address': 'Москва, Лубянка, 5',
                        'name': 'Big zombie shop',
                        'id': str(business_oid),
                        'map_link': f'https://yandex.ru/maps/?mode=search&ol=biz&oid={business_oid}',  # noqa: E501
                    },
                ],
            },
        ],
        'changelog': {
            'updated_by': 'valery',
            'updated_at': '2019-05-26T19:10:25+03:00',
            'created_by': 'valery',
            'created_at': '2019-05-26T19:10:25+03:00',
        },
    }
    assert response_json == expected


async def test_search_organizations_not_found(
        web_app_client, search_org_mock_not_found,
):
    business_oid = 123456
    uri = f'/internal/v1/organizations/list?business_oid={business_oid}'
    response = await web_app_client.post(uri)
    assert response.status == 404, await response.text()

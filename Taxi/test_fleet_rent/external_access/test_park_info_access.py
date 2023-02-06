from testsuite.utils import http

from fleet_rent.entities import park
from fleet_rent.generated.web import web_context as context_module


async def test_base(web_context: context_module.Context, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _list(request: http.Request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'name': 'name',
                    'is_active': True,
                    'city_id': 'city_id',
                    'tz_offset': 3,
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id',
                    'provider_config': {'type': 'none', 'clid': 'clid'},
                    'demo_mode': False,
                    'fleet_type': 'yandex',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    park_data = await web_context.external_access.park.get_park_info(
        park_id='park_id',
    )

    assert park_data == park.Park(
        id='park_id',
        name='name',
        clid='clid',
        tz_offset=3,
        city_id='city_id',
        country_id='country_id',
        locale='ru',
        fleet_type='yandex',
    )


async def test_base_batch(
        web_context: context_module.Context, mock_fleet_parks,
):
    @mock_fleet_parks('/v1/parks/list')
    async def _list(request: http.Request):
        ids = set(request.json['query']['park']['ids'])
        assert ids == {'park_id2', 'park_id'}
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'name': 'name',
                    'is_active': True,
                    'city_id': 'city_id',
                    'tz_offset': 3,
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id',
                    'provider_config': {'type': 'none', 'clid': 'clid'},
                    'demo_mode': False,
                    'fleet_type': 'yandex',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
                {
                    'id': 'park_id2',
                    'login': 'login2',
                    'name': 'name2',
                    'is_active': False,
                    'city_id': 'city_id2',
                    'tz_offset': 4,
                    'locale': 'en',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id2',
                    'provider_config': {'type': 'none', 'clid': 'clid2'},
                    'demo_mode': False,
                    'fleet_type': 'yandex',
                    'driver_partner_source': 'selfemployed_fns',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    park_data = await web_context.external_access.park.get_park_info_batch(
        {'park_id', 'park_id2'},
    )

    assert park_data == {
        'park_id': park.Park(
            id='park_id',
            name='name',
            clid='clid',
            tz_offset=3,
            city_id='city_id',
            country_id='country_id',
            locale='ru',
            fleet_type='yandex',
            driver_partner_source=None,
        ),
        'park_id2': park.Park(
            id='park_id2',
            name='name2',
            clid='clid2',
            owner=None,
            tz_offset=4,
            city_id='city_id2',
            country_id='country_id2',
            fleet_type='yandex',
            locale='en',
            driver_partner_source='selfemployed_fns',
        ),
    }


async def test_billing_client_data(
        web_context: context_module.Context,
        mock_parks_replica,
        mock_billing_replication,
):
    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _get_billing_client_id(request: http.Request):
        return {'billing_client_id': 'billing_client_id'}

    @mock_billing_replication('/person/')
    async def _get_inn(request: http.Request):
        return [
            {
                'ID': 'billing_client_id',
                'INN': 'inn',
                'LEGALADDRESS': 'legal_address',
                'LONGNAME': 'long_name',
            },
        ]

    park_data = await web_context.external_access.park.get_park_billing_data(
        'my_clid',
    )

    assert park_data == park.ParkBillingClientData(
        clid='my_clid',
        inn='inn',
        billing_client_id='billing_client_id',
        legal_name='long_name',
        legal_address='legal_address',
    )

    park_data = await web_context.external_access.park.get_park_billing_data(
        None,
    )
    assert park_data == park.ParkBillingClientData(
        clid=None,
        inn=None,
        billing_client_id=None,
        legal_name=None,
        legal_address=None,
    )


async def test_contacts(web_context: context_module.Context, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/contacts')
    async def _contacts(request: http.Request):
        return {
            'drivers': {
                'address': 'address',
                'address_coordinates': {'lon': '1.2', 'lat': '2.1'},
                'email': 'email',
                'phone': 'phone',
            },
        }

    park_data = await web_context.external_access.park.get_park_contacts(
        'park_id',
    )

    assert park_data == park.ParkContacts(
        id='park_id',
        phone='phone',
        address='address',
        coordinates=park.ParkCoordinates(lon='1.2', lat='2.1'),
    )


async def test_fallback_access(
        web_context: context_module.Context,
        mock_territories,
        park_stub_factory,
):
    @mock_territories('/v1/countries/retrieve')
    async def _countries_retrieve(request: http.Request):
        assert request.json == {'_id': 'bel', 'projection': ['currency']}
        return {'_id': 'bel', 'currency': 'BYN'}

    park_ob = park_stub_factory('some_park_id', country_id='bel')
    park_info_access = web_context.external_access.park
    result = await park_info_access.get_fallback_park_currency(park_ob)
    assert result == 'BYN'

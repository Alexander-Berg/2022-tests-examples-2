import pytest

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

CONSUMER = 'fleet-legal-entities'
PARK_ID = 'park_id1'
PARK_ID_NOT_SUPPORTED = 'park_id3'
CAR_ID = 'a988ff6aef116826d223065de782926d'

ENDPOINT = '/v1/carrier/by-order'


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
@pytest.mark.config(PARKS_USE_PARK_DEFAULT_WORK_HOURS=True)
@pytest.mark.config(PARK_DEFAULT_WORK_HOURS='default hours')
@pytest.mark.parametrize(
    ('park_id', 'order_zone', 'tariff_class', 'status_code', 'response_json'),
    [
        (
            PARK_ID,
            'moscow',
            'uberblack',
            200,
            {
                'address': 'г Красноярск, ул Красной Армии, д 10',
                'name': 'БИЗНЕС ГАРД ОА ООО',
                'registration_number': '1173468000539',
                'additional_fields': [
                    {'alias': 'work_hours', 'value': '9:00 - 18:00'},
                ],
            },
        ),
        (PARK_ID, 'moscow', 'uberx', 204, {}),
        (
            PARK_ID_NOT_SUPPORTED,
            'berlin',
            'uberblack',
            200,
            {
                'address': 'park_address',
                'name': 'park_name',
                'registration_number': 'park_ogrn',
                'additional_fields': [
                    {'alias': 'work_hours', 'value': 'default hours'},
                ],
            },
        ),
    ],
)
async def test_get_order_carrier_ok(
        taxi_fleet_legal_entities,
        mockserver,
        park_id,
        order_zone,
        tariff_class,
        status_code,
        response_json,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _mock_vehicles(request):
        assert request.query['consumer'] == CONSUMER
        assert request.json == {
            'id_in_set': ['{}_{}'.format(park_id, CAR_ID)],
            'projection': ['data.carrier_permit_owner_id'],
        }
        return {
            'vehicles': [
                {
                    'park_id_car_id': '{}_{}'.format(park_id, CAR_ID),
                    'data': {
                        'carrier_permit_owner_id': '5c223136de2a722c67dc3090',
                    },
                },
            ],
        }

    response = await taxi_fleet_legal_entities.get(
        ENDPOINT,
        params={
            'park_id': park_id,
            'order_zone': order_zone,
            'order_tariff': tariff_class,
            'car_id': CAR_ID,
            'park_clid': 'CLID',
        },
    )

    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == response_json


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_get_carrier_not_found(taxi_fleet_legal_entities, mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _mock_vehicles(request):
        assert request.query['consumer'] == CONSUMER
        assert request.json == {
            'id_in_set': ['{}_{}'.format(PARK_ID_NOT_SUPPORTED, CAR_ID)],
            'projection': ['data.carrier_permit_owner_id'],
        }
        return {
            'vehicles': [
                {
                    'park_id_car_id': '{}_{}'.format(
                        PARK_ID_NOT_SUPPORTED, CAR_ID,
                    ),
                },
            ],
        }

    response = await taxi_fleet_legal_entities.get(
        ENDPOINT,
        params={
            'park_id': PARK_ID_NOT_SUPPORTED,
            'order_zone': 'moscow',
            'order_tariff': 'uberblack',
            'car_id': CAR_ID,
            'park_clid': 'CLID_NOT_FOUND',
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }

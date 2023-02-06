import pytest

OFFER_ID = 'nonfixed_price_no_upgrade'
MDB_OFFER_ID = 'mdb_offer_id'
PRICES = [
    {'cls': 'econom', 'driver_price': 335, 'price': 335, 'sp': 1},
    {'cls': 'business', 'driver_price': 335, 'price': 335, 'sp': 1},
    {'cls': 'comfortplus', 'driver_price': 335, 'price': 335, 'sp': 1},
]


def construct_offer_fields_response(fields, offer_id):
    response = {'_id': offer_id}
    if 'distance' in fields:
        response['distance'] = 5334.986203042357
    if 'route' in fields:
        response['route'] = [[37.61672446877377, 55.75774301935856]]
    if 'prices' in fields:
        response['prices'] = PRICES
    return response


FETCH_FROM_MDB_MARK = pytest.mark.config(
    ORDER_OFFERS_FETCH_OFFER_FROM_MDB=True,
)


@pytest.mark.parametrize(
    'fields',
    [
        (['_id']),
        (['distance', 'route', 'prices']),
        (['_id', 'unknown_field']),
        (['unknown_field']),
    ],
    ids=[
        'simple',
        'known_fields',
        'known_and_unknown_fields',
        'unknown_fields',
    ],
)
@pytest.mark.parametrize(
    'offer_id, status, fetch_result_tag',
    [
        pytest.param(OFFER_ID, 200, 'ok'),
        pytest.param(OFFER_ID, 404, 'not_found', marks=[FETCH_FROM_MDB_MARK]),
        pytest.param(MDB_OFFER_ID, 404, 'not_found'),
        pytest.param(MDB_OFFER_ID, 200, 'ok', marks=[FETCH_FROM_MDB_MARK]),
    ],
)
async def test_offer_fields_request_fields(
        taxi_order_offers,
        testpoint,
        fields,
        status,
        fetch_result_tag,
        offer_id,
):
    @testpoint('fetch-fields-result')
    def _testpoint_fetch_result(data):
        assert data == fetch_result_tag

    request_params = {'offer_id': offer_id, 'fields': fields}
    response = await taxi_order_offers.post(
        '/v1/offer-fields', json=request_params,
    )
    assert response.status_code == status
    if status == 200:
        assert response.json()['fields'] == construct_offer_fields_response(
            fields, offer_id,
        )

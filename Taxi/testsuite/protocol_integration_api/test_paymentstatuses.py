import pytest


@pytest.fixture
def paymentstatuses_services(mockserver, load):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '4006998555'},
            'status': {'value': 'VALID'},
            'oauth': {
                'scope': (
                    'yataxi:read yataxi:write yataxi:pay '
                    'yataxi:yauber_request'
                ),
            },
            'phones': [{'attributes': {'102': '+71111111111'}, 'id': '1111'}],
        }


USER_ID = 'a664ff1f661140d2821f711c2f5c644e'


@pytest.mark.parametrize(
    'id, orderid, format_currency, response_file, zone_name',
    [
        (
            USER_ID,
            'c85ea0c44fbe4d2a80400cddc61819e5',
            False,
            'response_orderid_1.json',
            'moscow',
        ),
    ],
)
def test_paymentstatuses_by_order_id(
        taxi_integration,
        load_json,
        paymentstatuses_services,
        id,
        orderid,
        format_currency,
        response_file,
        zone_name,
        db,
):
    json_temp = {'id': id, 'orderid': orderid}
    if format_currency is not None:
        json_temp.update({'format_currency': format_currency})
    db.orders.update_one({'_id': orderid}, {'$set': {'nz': zone_name}})

    response = taxi_integration.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_file)

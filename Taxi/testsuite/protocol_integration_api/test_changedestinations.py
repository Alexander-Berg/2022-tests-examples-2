import json

import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH


@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'corp-integration-api'}],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_simple(
        taxi_integration, db, mockserver, notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-22T17:20:20+0000')
    request = {
        'id': '78a6e6d26b4849db87bd76a36dde917e',
        'orderid': '8c83b49edb274ce0992f337061042222',
        'created_time': created_time.isoformat(),
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'type': 'address',
                'uri': 'ymapsbm1://geo?ll=37.642%2C55.738',
            },
        ],
    }

    @mockserver.json_handler('/corp_integration_api/corp_paymentmethods')
    def mock_corp_paymentmethods(request):
        data = json.loads(request.get_data())
        assert data['client_id'] == '327eba75e92c4603933981bbf3216889'
        assert data['identity']['phone_id'] == '5714f45e98956f0600000003'
        assert data['route'][0]['geopoint'] == [37.59, 55.73]
        assert data['route'][1]['geopoint'] == [
            37.59090617361221,
            55.73921060048498,
        ]
        return mockserver.make_response(
            json.dumps(
                {
                    'methods': [
                        {
                            'client_id': '327eba75e92c4603933981bbf3216889',
                            'zone_available': True,
                        },
                    ],
                },
            ),
        )

    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None

    response = taxi_integration.post(
        'v1/changedestinations', request, headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200

    # validate response according to protocol
    request['destinations'][0]['uris'] = [request['destinations'][0]['uri']]
    request['destinations'][0].pop('uri')
    assert response.json() == {
        'change_id': response.json()['change_id'],
        'status': 'success',
        'name': 'destinations',
        'value': request['destinations'],
    }


@pytest.mark.parametrize('disable_price_changing', [True, False])
@pytest.mark.config(FIXED_PRICE_MAX_CHANGE_DESTINATION_DISTANCE=100)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_fixed_price(
        taxi_integration,
        db,
        disable_price_changing,
        notify_on_change_version_switch,
):

    order_id = '8c83b49edb274ce0992f337061042222'
    geo_template = {
        'country': 'Russian Federation',
        'description': 'Moscow, Russian Federation',
        'exact': False,
        'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
        'locality': 'Moscow',
        'object_type': 'другое',
        'short_text': 'Kropotkinsky Lane',
        'thoroughfare': 'Kropotkinsky Lane',
        'type': 'address',
        'use_geopoint': True,
    }
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    dict(geopoint=point, **geo_template)
                    for point in [[37.588630, 55.734367]]
                ],
            },
        },
    )

    for change in [[[37.588630, 55.734367]]]:
        request = {
            'id': '78a6e6d26b4849db87bd76a36dde917e',
            'orderid': order_id,
            'created_time': '2017-08-01T10:00:00+0000',
            'destinations': [
                dict(geopoint=point, **geo_template) for point in change
            ],
            'disable_price_changing': disable_price_changing,
        }
        response = taxi_integration.post('/v1/changedestinations', request)
        assert response.status_code == 200, response.content

    fixed_price = db.order_proc.find_one(order_id)['order']['fixed_price']
    if disable_price_changing:
        assert fixed_price.get('price') == 100
        assert fixed_price.get('driver_price') == 100
    else:
        assert fixed_price.get('price') is None
        assert fixed_price.get('driver_price') is None


@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_full_auction(
        taxi_integration, db, notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061042222'
    geo_template = {
        'country': 'Russian Federation',
        'description': 'Moscow, Russian Federation',
        'exact': False,
        'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
        'locality': 'Moscow',
        'object_type': 'другое',
        'short_text': 'Kropotkinsky Lane',
        'thoroughfare': 'Kropotkinsky Lane',
        'type': 'address',
        'use_geopoint': True,
    }
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    dict(geopoint=point, **geo_template)
                    for point in [[37.588630, 55.734367]]
                ],
                'driver_bid_info': {
                    'max_price': 10,
                    'min_price': 1,
                    'price_options': [2, 3, 4],
                },
            },
        },
    )

    for change in [[[37.588630, 55.734367]]]:
        request = {
            'id': '78a6e6d26b4849db87bd76a36dde917e',
            'orderid': order_id,
            'created_time': '2017-08-01T10:00:00+0000',
            'destinations': [
                dict(geopoint=point, **geo_template) for point in change
            ],
        }
        response = taxi_integration.post('/v1/changedestinations', request)
        assert response.status_code == 404, response.content

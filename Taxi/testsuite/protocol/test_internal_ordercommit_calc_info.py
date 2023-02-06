import pytest

COMMIT_URLS = ('3.0/ordercommit', 'internal/ordercommit')


def _common_calc(calc_dict):
    ORDER_PROC_CALC_COMMON_FIELDS = {
        'dist',
        'time',
        'recalculated',
        'alternative_type',
    }
    return {
        k: v
        for k, v in calc_dict.items()
        if k in ORDER_PROC_CALC_COMMON_FIELDS
    }


@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('url', COMMIT_URLS)
@pytest.mark.parametrize(
    'offer_id,alternative_type',
    [
        (None, None),  # if no offer - guess not alternative one
        ('offer_id', None),
        ('alt_offer_id', 'explicit_antisurge'),
        ('alt_offer_id_2', 'combo_order'),
    ],
)
def test_ordercommit_get_calc_info(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        url,
        offer_id,
        alternative_type,
):
    """simply get info from the right order"""

    USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
    ORDER_ID = '8c83b49edb274ce0992f337061047399'

    db.order_proc.update_one(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': offer_id}},
        upsert=False,
    )

    request = {'id': USER_ID, 'orderid': ORDER_ID}
    response = taxi_protocol.post(url, request)

    assert response.status_code == 200

    order_proc = db.order_proc.find_one({'_id': request['orderid']})
    assert order_proc is not None
    order = order_proc['order']

    expected_calc = {
        'distance': 5334.986203042357,
        'recalculated': False,
        'allowed_tariffs': {'__park__': {'econom': 335.0}},
        'time': 819.1817197048313,
    }

    if alternative_type is not None:
        expected_calc['alternative_type'] = alternative_type

    assert order['calc'] == expected_calc

    assert order['discount'] == {
        'cashbacks': [],
        'by_classes': [
            {
                'price': 408,
                'class': 'econom',
                'value': 0.35,
                'original_value': 0.35,
                'reason': 'for_all',
                'method': 'subvention-fix',
                'limited_rides': False,
            },
        ],
        'limited_rides': False,
        'with_restriction_by_usages': False,
        'reason': 'for_all',
        'method': 'subvention-fix',
        'price': 0,
        'value': 0,
        'driver_less_coeff': 0.3,
    }

    assert 'fixed_price' in order
    assert order['request']['sp'] == 1
    assert order['request']['offer'] == offer_id
    assert order['fixed_price']['driver_price'] == 400


def _route_maps(mockserver, load_binary):
    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route.protobuf'),
            content_type='application/x-protobuf',
        )


def _mock_surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.7,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('url,exp_status', zip(COMMIT_URLS, (406, 200)))
def test_ordercommit_send_obsolete_price(
        taxi_protocol,
        mockserver,
        load_binary,
        db,
        now,
        url,
        exp_status,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    """check that UpdateCalcInfo is called through invalidating calc_info
    with the obsolete offer.
    As use fixed_price experiment, so no commit, status is draft,
    get Warning: 'commit has been failed: PRICE_CHANGED'"""

    _route_maps(mockserver, load_binary)
    _mock_surge(mockserver)

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047399',
    }
    response = taxi_protocol.post(url, request)
    assert response.status_code == exp_status

    order = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )

    assert order is not None

    assert order['status'] == 'draft'
    assert order['commit_state'] == 'init'

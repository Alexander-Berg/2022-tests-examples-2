import json


def get_surge_calculator_response(request, surge_value, surcharge=None):
    data = json.loads(request.get_data())
    result = {
        'zone_id': 'MSK-Entusiast Ryazan',
        'is_cached': False,
        'experiment_id': 'exp_id',
        'experiment_name': 'exp_name',
        'calculation_id': 'some_calculation_id',
        'experiment_layer': 'default',
        'experiments': [],
        'experiment_errors': [],
        'classes': [
            {
                'name': name,
                'surge': {'value': surge_value},
                'value_raw': surge_value,
                'calculation_meta': {
                    'reason': 'pins_free',
                    'smooth': {
                        'point_a': {'value': surge_value, 'is_default': False},
                        'point_b': {'value': surge_value, 'is_default': False},
                    },
                    'counts': {
                        'free': 6,
                        'free_chain': 0,
                        'total': 6,
                        'pins': 0,
                        'radius': 3000,
                    },
                },
            }
            for name in data['classes']
        ],
    }
    if surcharge:
        for t in result['classes']:
            t['surge']['surcharge'] = {
                'alpha': surcharge.alpha,
                'beta': surcharge.beta,
                'value': surcharge.surcharge,
            }
    return result


def mock_driver_eta(load_json, name):
    def driver_eta_func(request):
        retval_json = load_json(name)
        data = json.loads(request.get_data())
        to_remove = set()
        for c in retval_json['classes']:
            if c not in data['classes']:
                to_remove.add(c)
        for c in to_remove:
            retval_json['classes'].pop(c)
        assert len(retval_json['classes']) == len(data['classes'])
        return retval_json

    return driver_eta_func


def prices_array_to_map(prices_array):
    prices_map = {}
    for item in prices_array:
        assert 'cls' in item
        prices_map[item['cls']] = item
    return prices_map


def get_saved_offer(
        db=None, mock_order_offers=None, order_offers_save_enabled=False,
):
    if order_offers_save_enabled:
        assert mock_order_offers
        return mock_order_offers.last_saved_offer
    else:
        assert db
        return db.order_offers.find_one()


def get_offer(
        offer_id,
        db=None,
        mock_order_offers=None,
        order_offers_save_enabled=False,
):
    if order_offers_save_enabled:
        assert mock_order_offers
        return mock_order_offers.get_offer(offer_id)
    else:
        assert db
        return db.order_offers.find_one(offer_id)


def get_user_offer(
        offer_id,
        user_id,
        db=None,
        mock_order_offers=None,
        order_offers_save_enabled=False,
):
    if order_offers_save_enabled:
        assert mock_order_offers
        return mock_order_offers.get_user_offer(offer_id, user_id)
    else:
        assert db
        return db.order_offers.find_one({'_id': offer_id, 'user_id': user_id})


def set_default_tariff_info_and_prices(pricing_data_preparer):
    pricing_data_preparer.set_tariff_info(
        price_per_minute=9,
        price_per_kilometer=9,
        included_minutes=5,
        included_kilometers=2,
        category='econom',
    )
    pricing_data_preparer.set_meta('min_price', 99, category='econom')
    pricing_data_preparer.set_cost(
        user_cost=99, driver_cost=99, category='econom',
    )

    pricing_data_preparer.set_tariff_info(
        price_per_minute=12,
        price_per_kilometer=12,
        included_minutes=5,
        included_kilometers=2,
        category='business',
    )
    pricing_data_preparer.set_meta('min_price', 199, category='business')
    pricing_data_preparer.set_cost(
        user_cost=199, driver_cost=199, category='business',
    )

    pricing_data_preparer.set_tariff_info(
        price_per_minute=13,
        price_per_kilometer=13,
        included_minutes=5,
        included_kilometers=0,
        category='comfortplus',
    )
    pricing_data_preparer.set_meta('min_price', 199, category='comfortplus')
    pricing_data_preparer.set_cost(
        user_cost=199, driver_cost=199, category='comfortplus',
    )

    pricing_data_preparer.set_tariff_info(
        price_per_minute=18,
        price_per_kilometer=18,
        included_minutes=5,
        included_kilometers=0,
        category='vip',
    )
    pricing_data_preparer.set_meta('min_price', 299, category='vip')
    pricing_data_preparer.set_cost(
        user_cost=299, driver_cost=299, category='vip',
    )

    pricing_data_preparer.set_tariff_info(
        price_per_minute=12,
        price_per_kilometer=12,
        included_minutes=5,
        included_kilometers=0,
        category='minivan',
    )
    pricing_data_preparer.set_meta('min_price', 199, category='minivan')
    pricing_data_preparer.set_cost(
        user_cost=199, driver_cost=199, category='minivan',
    )

    pricing_data_preparer.set_tariff_info(
        price_per_minute=0,
        price_per_kilometer=0,
        included_minutes=5,
        included_kilometers=2,
        category='child_tariff',
    )
    pricing_data_preparer.set_meta('min_price', 432, category='child_tariff')
    pricing_data_preparer.set_cost(
        user_cost=432, driver_cost=432, category='child_tariff',
    )

import copy

from dateutil import parser
import pytest

from tests_eats_retail_market_integration import common
from tests_eats_retail_market_integration import models
from tests_eats_retail_market_integration.eats_catalog_internals import storage

# pylint: disable=too-many-lines

CATALOG_SLUG_HANDLER = '/eats-catalog/eats-catalog/v1/slug/'
HANDLER = '/v1/market/cart/actualize'

BRAND_ID = 777
PLACE_ID = '1'
PLACE_SLUG = 'slug'
ZONE_ID = 1
BUSINESS_ID = 999
SHOP_ID = 9
ASSEMBLY_COST = 1

DEFAULT_DELIVERY_MIN_TIME = 0
DEFAULT_DELIVERY_MAX_TIME = 50
DEFAULT_DELIVERY_TIME = DEFAULT_DELIVERY_MIN_TIME
DEFAULT_DELIVERY_COST = 1500


async def test_200_delivery_time(
        mockserver,
        mock_nomenclature,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    min_delivery_time = 100
    max_delivery_time = 200

    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response(
            min_delivery_time=min_delivery_time,
            max_delivery_time=max_delivery_time,
        )

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {'total_item_price': 0, 'total_item_discount': 0}

    # Item 1

    item_1 = common.NmnProduct(public_id='item_1')
    place.add_product(item_1)

    requested_items.append({'feed_offer_id': item_1.public_id, 'count': 1})
    expected_items[item_1.public_id] = {'item': item_1, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_1.public_id]['count']
        * expected_items[item_1.public_id]['item'].price
    )
    expected_response['delivery_time'] = min_delivery_time
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_catalog_default_delivery_thresholds(),
    )

    await _test_handler(requested_items, expected_items, expected_response, 1)


async def test_200_item_count(
        mockserver,
        mock_nomenclature,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response()

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {
        'total_item_price': 0,
        'total_item_discount': 0,
        'thresholds': _map_delivery_thresholds_for_response(
            _generate_catalog_default_delivery_thresholds(),
        ),
    }

    # Item 1 (requested less than available)

    item_1 = common.NmnProduct(public_id='item_1', in_stock=10)
    place.add_product(item_1)

    requested_items.append(
        {'feed_offer_id': item_1.public_id, 'count': item_1.in_stock / 2},
    )
    expected_items[item_1.public_id] = {
        'item': item_1,
        'count': item_1.in_stock / 2,
    }
    expected_response['total_item_price'] += (
        expected_items[item_1.public_id]['count']
        * expected_items[item_1.public_id]['item'].price
    )

    await _test_handler(requested_items, expected_items, expected_response, 1)

    # Item 2 (requested more than available)

    item_2 = common.NmnProduct(public_id='item_2', in_stock=20)
    place.add_product(item_2)

    requested_items.append(
        {'feed_offer_id': item_2.public_id, 'count': item_2.in_stock * 2},
    )
    expected_items[item_2.public_id] = {
        'item': item_2,
        'count': item_2.in_stock,
    }
    expected_response['total_item_price'] += (
        expected_items[item_2.public_id]['count']
        * expected_items[item_2.public_id]['item'].price
    )

    await _test_handler(requested_items, expected_items, expected_response, 2)

    # Item 3 (unavailable item)

    item_3 = common.NmnProduct(public_id='item_3', is_available=False)
    place.add_product(item_3)

    requested_items.append({'feed_offer_id': item_3.public_id, 'count': 100})
    expected_items[item_3.public_id] = {'item': item_3, 'count': 0}

    await _test_handler(requested_items, expected_items, expected_response, 3)

    # Item 4 (unknown item)

    # Disable product request verification,
    # since we are sending an unknown item,
    # hence we have to verify request manually
    mock_nomenclature.set_mock_req_validation_state(enable=False)

    item_4 = common.NmnProduct(public_id='item_4', is_available=False, price=0)

    requested_items.append({'feed_offer_id': 'item_4', 'count': 100})
    expected_items[item_4.public_id] = {
        'item': item_4,
        'count': 0,
        'found': False,
    }

    await _test_handler(requested_items, expected_items, expected_response, 4)

    last_mock_requests = mock_nomenclature.mock_last_requests()
    assert set(last_mock_requests['v1_products_info'].json['product_ids']) == {
        i['feed_offer_id'] for i in requested_items
    }
    assert set(
        last_mock_requests['v1_place_products_info'].json['product_ids'],
    ) == {i['feed_offer_id'] for i in requested_items}


async def test_200_item_weight(
        mockserver,
        mock_nomenclature,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    weight_limit_kg = 2

    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response(
            order_constraints=_generate_catalog_constraints(
                maximum_order_weight=weight_limit_kg,
            ),
        )

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {
        'total_item_price': 0,
        'total_item_discount': 0,
        'thresholds': _map_delivery_thresholds_for_response(
            _generate_catalog_default_delivery_thresholds(),
        ),
        'max_order_weight_threshold': weight_limit_kg,
    }

    # Item 1 (kgrm)

    item_1 = common.NmnProduct(
        public_id='item_1', measure=(weight_limit_kg / 2, 'KGRM'),
    )
    place.add_product(item_1)

    requested_items.append({'feed_offer_id': item_1.public_id, 'count': 1})
    expected_items[item_1.public_id] = {'item': item_1, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_1.public_id]['count']
        * expected_items[item_1.public_id]['item'].price
    )

    await _test_handler(requested_items, expected_items, expected_response, 1)

    # Item 2 (mlt)

    item_2 = common.NmnProduct(
        public_id='item_2', measure=(weight_limit_kg * 1000 / 4, 'MLT'),
    )
    place.add_product(item_2)

    requested_items.append({'feed_offer_id': item_2.public_id, 'count': 1})
    expected_items[item_2.public_id] = {'item': item_2, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_2.public_id]['count']
        * expected_items[item_2.public_id]['item'].price
    )

    await _test_handler(requested_items, expected_items, expected_response, 2)

    # Item 3 (lt, multiple items)

    item_3 = common.NmnProduct(
        public_id='item_3', measure=(weight_limit_kg * 1000 / 8, 'GRM'),
    )
    place.add_product(item_3)

    requested_items.append({'feed_offer_id': item_3.public_id, 'count': 2})
    expected_items[item_3.public_id] = {'item': item_3, 'count': 2}
    expected_response['total_item_price'] += (
        expected_items[item_3.public_id]['count']
        * expected_items[item_3.public_id]['item'].price
    )

    await _test_handler(requested_items, expected_items, expected_response, 3)

    # Item 4 (catch weight, multiple items and above limit)

    item_4 = common.NmnProduct(
        public_id='item_4',
        measure=(weight_limit_kg * 1000 / 8, 'MLT'),
        is_catch_weight=True,
        quantum=0.5,
    )
    place.add_product(item_4)

    requested_items.append({'feed_offer_id': item_4.public_id, 'count': 2})
    expected_items[item_4.public_id] = {'item': item_4, 'count': 2}
    expected_response['total_item_price'] += (
        expected_items[item_4.public_id]['count']
        * expected_items[item_4.public_id]['item'].price
    )
    expected_response['errors'] = ['WeightExceeded']

    await _test_handler(
        requested_items,
        expected_items,
        expected_response,
        expected_times_called=4,
    )


async def test_200_item_price(
        mockserver,
        mock_nomenclature,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    threshold_1_min_price = 10
    threshold_2_min_price = 60
    threshold_3_min_price = 80
    threshold_3_max_price = 100
    constraint_price_min_limit = int(threshold_1_min_price / 3)
    constraint_price_max_limit = threshold_3_max_price * 2
    delivery_cost_1 = 100
    delivery_cost_2 = 10

    def _generate_delivery_thresholds():
        return _generate_catalog_delivery_thresholds(
            [
                {
                    'min': threshold_1_min_price,
                    'max': threshold_2_min_price,
                    'delivery_cost': delivery_cost_1,
                },
                {
                    'min': threshold_2_min_price,
                    'max': threshold_3_min_price,
                    'delivery_cost': delivery_cost_2,
                },
                {
                    'min': threshold_3_min_price,
                    'max': threshold_3_max_price,
                    'delivery_cost': 0,
                },
            ],
        )

    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response(
            order_constraints=_generate_catalog_constraints(
                minimum_order_price=constraint_price_min_limit,
                maximum_order_price=constraint_price_max_limit,
            ),
            delivery_thresholds=_generate_delivery_thresholds(),
        )

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {
        'total_item_price': 0,
        'total_item_discount': 0,
        'min_order_price': constraint_price_min_limit,
        'max_order_price_threshold': constraint_price_max_limit,
    }

    times_called = 0

    # Item 1 (normal price and below min limit)

    item_1 = common.NmnProduct(
        public_id='item_1', price=threshold_1_min_price / 2,
    )
    place.add_product(item_1)

    requested_items.append({'feed_offer_id': item_1.public_id, 'count': 1})
    expected_items[item_1.public_id] = {'item': item_1, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_1.public_id]['count']
        * expected_items[item_1.public_id]['item'].price
    )
    expected_response['shipping_cost'] = delivery_cost_1
    expected_response['free_delivery_threshold'] = threshold_3_min_price
    expected_response['errors'] = ['PriceInsufficient']
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # swap treshold and contsraint limits
    # to test that both are correctly handled
    constraint_price_min_limit, threshold_1_min_price = (
        threshold_1_min_price,
        constraint_price_min_limit,
    )
    expected_response['min_order_price'] = constraint_price_min_limit
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # swap back
    constraint_price_min_limit, threshold_1_min_price = (
        threshold_1_min_price,
        constraint_price_min_limit,
    )
    expected_response['min_order_price'] = constraint_price_min_limit

    # Item 2 (promo price above min limit, threshold 1)

    item_2 = common.NmnProduct(
        public_id='item_2',
        price=(
            threshold_2_min_price - expected_response['total_item_price'] - 1
        ),
        old_price=constraint_price_max_limit * 2,
    )
    place.add_product(item_2)

    requested_items.append({'feed_offer_id': item_2.public_id, 'count': 1})
    expected_items[item_2.public_id] = {'item': item_2, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_2.public_id]['count']
        * expected_items[item_2.public_id]['item'].price
    )
    expected_response['total_item_discount'] += (
        expected_items[item_2.public_id]['count']
        * (
            expected_items[item_2.public_id]['item'].old_price
            - expected_items[item_2.public_id]['item'].price
        )
    )
    expected_response['shipping_cost'] = delivery_cost_1
    expected_response['free_delivery_threshold'] = threshold_3_min_price
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )
    expected_response.pop('errors', None)

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # Item 3 (multiple items, threshold 2)

    item_3 = common.NmnProduct(
        public_id='item_3',
        price=(
            threshold_3_min_price - expected_response['total_item_price'] - 1
        )
        / 2.0,
    )
    place.add_product(item_3)

    requested_items.append({'feed_offer_id': item_3.public_id, 'count': 2})
    expected_items[item_3.public_id] = {'item': item_3, 'count': 2}
    expected_response['total_item_price'] += (
        expected_items[item_3.public_id]['count']
        * expected_items[item_3.public_id]['item'].price
    )
    expected_response['shipping_cost'] = delivery_cost_2
    expected_response['free_delivery_threshold'] = threshold_3_min_price
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # Item 4 (threshold 3)

    item_4 = common.NmnProduct(
        public_id='item_4',
        price=(
            threshold_3_max_price - expected_response['total_item_price'] - 1
        ),
    )
    place.add_product(item_4)

    requested_items.append({'feed_offer_id': item_4.public_id, 'count': 1})
    expected_items[item_4.public_id] = {'item': item_4, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_4.public_id]['count']
        * expected_items[item_4.public_id]['item'].price
    )
    expected_response['shipping_cost'] = 0
    expected_response.pop('free_delivery_threshold', None)
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # Item 5 (catch weight, multiple items and above max limit)

    item_5 = common.NmnProduct(
        public_id='item_5',
        price=(threshold_3_max_price - expected_response['total_item_price'])
        / 4
        + 1,
        measure=(500, 'MLT'),
        is_catch_weight=True,
        quantum=0.5,
    )
    place.add_product(item_5)

    requested_items.append({'feed_offer_id': item_5.public_id, 'count': 2})
    expected_items[item_5.public_id] = {'item': item_5, 'count': 2}
    expected_response['total_item_price'] += (
        expected_items[item_5.public_id]['count']
        * expected_items[item_5.public_id]['item'].price
    )
    expected_response['shipping_cost'] = 0
    expected_response['errors'] = ['PriceExceeded']
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # swap treshold and contsraint limits
    # to test that both are correctly handled
    constraint_price_max_limit, threshold_3_max_price = (
        threshold_3_max_price,
        constraint_price_max_limit,
    )
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )
    expected_response['max_order_price_threshold'] = constraint_price_max_limit

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )

    # Test that NULL max threshold is handled as well
    constraint_price_max_limit = 999999
    threshold_3_max_price = None
    expected_response['shipping_cost'] = 0
    expected_response.pop('errors', None)
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_delivery_thresholds(),
    )
    expected_response['max_order_price_threshold'] = constraint_price_max_limit

    times_called += 1
    await _test_handler(
        requested_items, expected_items, expected_response, times_called,
    )


async def test_200_catalog_unavailable_place(
        taxi_eats_retail_market_integration,
        mockserver,
        mock_nomenclature,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    place_available_from = '2019-01-01T12:00:00+00:00'

    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response(
            is_available=False, available_from=place_available_from,
        )

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {
        'total_item_price': 0,
        'total_item_discount': 0,
        'is_available': False,
        'available_from': place_available_from,
        'thresholds': _map_delivery_thresholds_for_response(
            _generate_catalog_default_delivery_thresholds(),
        ),
    }

    await _test_handler(requested_items, expected_items, expected_response, 1)


async def test_404_catalog_unknown_place(
        taxi_eats_retail_market_integration,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    @mockserver.handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)

        return mockserver.make_response(
            status=404, json=[{'code': 'notFound', 'title': 'Not found'}],
        )

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    request = _build_handler_request(SHOP_ID, [])
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )
    assert response.status == 404
    assert _mock_catalog_slug.times_called == 1


async def test_404_unknown_shop_id(
        taxi_eats_retail_market_integration, save_brands_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])

    request = _build_handler_request(SHOP_ID, [])
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )
    assert response.status == 404


async def test_404_nmn_unknown_place_id(
        taxi_eats_retail_market_integration,
        mockserver,
        mock_nomenclature,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response()

    @mockserver.handler('eats-nomenclature/v1/place/products/info')
    def _mock_place_products_override(request):
        assert request.query['place_id'] == PLACE_ID
        return mockserver.make_response('Not found', status=404)

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    item_with_same_stocks = common.NmnProduct(
        public_id='item_with_same_stocks', in_stock=10,
    )
    place.add_product(item_with_same_stocks)

    request = _build_handler_request(
        SHOP_ID,
        [{'feed_offer_id': item_with_same_stocks.public_id, 'count': 123}],
    )
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )
    assert response.status == 404
    assert _mock_catalog_slug.times_called == 1
    assert _mock_place_products_override.times_called == 1


@pytest.mark.experiments3(filename='cart_service_fee_exp.json')
async def test_additional_fees(
        mockserver,
        mock_nomenclature,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
        save_brand_places_to_storage,
        eats_catalog_storage,
):
    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response()

    eats_places_set_init_places(eats_catalog_storage)

    async def _test_handler(
            requested_items,
            expected_items,
            expected_response,
            expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )
        assert response.status == 200
        _verify_handler_response_json(
            response.json(), expected_items, expected_response,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_brand_places_to_storage(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_items = dict()
    expected_response = {'total_item_price': 0, 'total_item_discount': 0}

    # Item 1

    item_1 = common.NmnProduct(public_id='item_1')
    place.add_product(item_1)

    requested_items.append({'feed_offer_id': item_1.public_id, 'count': 1})
    expected_items[item_1.public_id] = {'item': item_1, 'count': 1}
    expected_response['total_item_price'] += (
        expected_items[item_1.public_id]['count']
        * expected_items[item_1.public_id]['item'].price
    )
    expected_response['thresholds'] = _map_delivery_thresholds_for_response(
        _generate_catalog_default_delivery_thresholds(),
    )
    expected_response['additional_fees'] = [
        {
            'value': 39,
            'title': 'Работа сервиса',
            'description': (
                'Мы развиваем Еду для вас — внедряем новые '
                'функции и улучшаем сервис. Спасибо, что вы с нами!'
            ),
            'confirm_text': 'Хорошо',
        },
    ]

    await _test_handler(requested_items, expected_items, expected_response, 1)


@pytest.mark.parametrize('enable_assembly_cost', [True, False])
async def test_assembly_cost(
        eats_catalog_storage,
        mockserver,
        mock_nomenclature,
        save_brand_places_to_storage,
        save_brands_to_db,
        save_market_brand_places_to_db,
        save_places_info_to_db,
        taxi_eats_retail_market_integration,
        update_taxi_config,
        # parametrize params
        enable_assembly_cost,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_DELIVERY_COST',
        {'should_include_assembly_cost': enable_assembly_cost},
    )

    @mockserver.json_handler(CATALOG_SLUG_HANDLER, prefix=True)
    def _mock_catalog_slug(request):
        assert request.path.endswith(PLACE_SLUG)
        return _generate_catalog_response()

    eats_places_set_init_places(eats_catalog_storage)

    async def _test_handler(
            requested_items, expected_response, expected_times_called,
    ):
        request = _build_handler_request(SHOP_ID, requested_items)
        response = await taxi_eats_retail_market_integration.post(
            HANDLER, json=request,
        )

        nmn_times_called = mock_nomenclature.mock_times_called()
        assert nmn_times_called['v1_products_info'] == expected_times_called
        assert (
            nmn_times_called['v1_place_products_info'] == expected_times_called
        )
        assert _mock_catalog_slug.times_called == expected_times_called

        assert response.status == 200
        response_data = response.json()
        assert (
            response_data['prices']['shipping_cost']
            == expected_response['shipping_cost']
        )
        assert response_data['prices']['total'] == expected_response['total']

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_brand_places_to_storage(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    places_info = _generate_places_info()
    save_places_info_to_db(places_info)

    place = common.NmnPlace(
        place_id=PLACE_ID, slug=PLACE_SLUG, brand_id=BRAND_ID,
    )
    mock_nomenclature.set_place(place)

    requested_items = []
    expected_response = {'total_item_price': 0, 'total_item_discount': 0}

    # Item 1

    item_1 = common.NmnProduct(public_id='item_1')
    place.add_product(item_1)
    requested_items.append({'feed_offer_id': item_1.public_id, 'count': 1})

    expected_response['shipping_cost'] = DEFAULT_DELIVERY_COST
    if enable_assembly_cost:
        expected_response['shipping_cost'] += ASSEMBLY_COST
    expected_response['total'] = (
        item_1.price + expected_response['shipping_cost']
    )

    await _test_handler(requested_items, expected_response, 1)


def _generate_catalog_delivery_thresholds(thresholds):
    return [
        {
            'name': f'на заказ до {i["min"]} $',
            'orderPrice': {
                'min': int(i['min']),
                'decimalMin': str(i['min']),
                'max': (
                    int(i['max'])
                    if 'max' in i and i['max'] is not None
                    else None
                ),
                'decimalMax': (
                    str(i['max'])
                    if 'max' in i and i['max'] is not None
                    else None
                ),
            },
            'deliveryCost': int(i['delivery_cost']),
            'decimalDeliveryCost': str(i['delivery_cost']),
        }
        for i in thresholds
    ]


def _generate_catalog_default_delivery_thresholds():
    return _generate_catalog_delivery_thresholds(
        [
            {'min': 0, 'max': 99, 'delivery_cost': DEFAULT_DELIVERY_COST},
            {'min': 100, 'max': 9999, 'delivery_cost': 401},
            {'min': 10000, 'max': 99, 'delivery_cost': 2},
        ],
    )


def _generate_catalog_constraints(
        minimum_order_price=None,
        maximum_order_price=None,
        maximum_order_weight=None,
):
    return {
        'minimum_order_price': (
            {'text': f'{minimum_order_price} $', 'value': minimum_order_price}
            if minimum_order_price
            else None
        ),
        'maximum_order_price': (
            {'text': f'{minimum_order_price} $', 'value': maximum_order_price}
            if maximum_order_price
            else None
        ),
        'maximum_order_weight': (
            {
                'text': f'{minimum_order_price} кг',
                'value': maximum_order_weight,
            }
            if maximum_order_weight
            else None
        ),
    }


def _generate_catalog_response(
        is_available=True,
        available_from=None,
        delivery_thresholds=None,
        order_constraints=None,
        min_delivery_time=DEFAULT_DELIVERY_MIN_TIME,
        max_delivery_time=DEFAULT_DELIVERY_MAX_TIME,
):
    response_template = {
        'payload': {
            'foundPlace': {
                'place': {
                    'id': 1,
                    'name': 'Тестовое заведение 1293',
                    'slug': 'coffee_boy_novodmitrovskaya_2k6',
                    'market': False,
                    'tags': [{'id': 1, 'name': 'Завтраки'}],
                    'priceCategory': {
                        'id': 1,
                        'name': '<category-$><category-$><category-$>',
                        'value': 1.0,
                    },
                    'rating': None,
                    'ratingCount': None,
                    'minimalOrderPrice': 0,
                    'minimalDeliveryCost': 0,
                    'isNew': True,
                    'picture': {
                        'uri': (
                            '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg'
                        ),
                        'ratio': 1.33,
                    },
                    'image': {
                        'dark': {
                            'uri': '/images/dark-{w}x{h}.jpg',
                            'ratio': 1.33,
                        },
                        'light': {
                            'uri': '/images/ligth-{w}x{h}.jpg',
                            'ratio': 1.33,
                        },
                    },
                    'deliveryConditions': 'Доставка 2–1500 $',
                    'deliveryThresholds': [],
                    'isPromoAvailable': False,
                    'isStore': False,
                    'brand': {'slug': 'coffee_boy_euocq'},
                    'currency': {'sign': '$', 'code': 'USD'},
                    'previewDeliveryFee': '',
                    'features': {
                        'ecoPackaging': {'show': False},
                        'delivery': {'isYandexTaxi': False},
                        'map': None,
                        'yandexPlus': None,
                        'badge': None,
                        'favorite': None,
                    },
                    'footerDescription': (
                        'Исполнитель (продавец): '
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
                        ' ИНН 7714457772, рег.номер 1207700043759.'
                        '<br>'
                        'Режим работы: с 10:00 до 14:00'
                    ),
                    'business': 'restaurant',
                    'availablePaymentMethods': [1, 2, 3, 4],
                    'type': {'id': 1, 'name': 'Ресторан'},
                    'address': {
                        'location': {
                            'longitude': 37.5916,
                            'latitude': 55.8129,
                        },
                        'city': 'Москва',
                        'short': 'Новодмитровская улица, 2к6',
                    },
                    'sharedLink': (
                        'https://eda.yandex/restaurant/'
                        'coffee_boy_novodmitrovskaya_2k6'
                        '?utm_source=rst_shared_link&utm_medium=referral&'
                        'utm_campaign=superapp_taxi_web'
                    ),
                    'messages': {
                        'constraints': {'title': 'Лимиты', 'footer': ''},
                        'thresholds': {
                            'title': 'Условия доставки',
                            'footer': '',
                        },
                    },
                    'constraints': {},
                    'promos': [],
                    'promoTypes': [],
                    'personalizationStrategy': None,
                    'ratingDescription': None,
                    'regionSlug': 'moscow',
                    'accent_color': [
                        {'theme': 'dark', 'value': '#bada55'},
                        {'theme': 'light', 'value': '#bada55'},
                    ],
                },
                'locationParams': {
                    'deliveryTime': {'min': 100, 'max': 500},
                    'available': True,
                    'availableNow': True,
                    'availableByTime': True,
                    'availableByLocation': True,
                    'distance': 1.1010703634086447,
                    'availableShippingTypes': [{'type': 'delivery'}],
                    'availableFrom': None,
                    'availableSlug': None,
                    'availableTo': '2021-01-01T14:00:00+03:00',
                    'eatDay': 0,
                    'prepareTime': {'minutes': 0.0, 'readyAt': None},
                    'shippingInfoAction': {
                        'deliveryFee': {'name': '201 $'},
                        'message': 'Повышенный спрос',
                    },
                },
                'surge': {
                    'deliveryFee': 201,
                    'description': 'Повышенный спрос',
                    'message': (
                        'Заказов сейчас очень много — чтобы еда приехала '
                        'в срок, стоимость доставки временно увеличена'
                    ),
                    'title': 'Повышенный спрос',
                },
            },
            'availableTimePicker': [[], []],
        },
    }

    response = copy.deepcopy(response_template)
    found_place = response['payload']['foundPlace']
    found_place['place']['deliveryThresholds'] = (
        delivery_thresholds
        if delivery_thresholds is not None
        else _generate_catalog_default_delivery_thresholds()
    )
    found_place['place']['constraints'] = order_constraints or {}
    found_place['locationParams']['available'] = is_available
    found_place['locationParams']['availableFrom'] = available_from
    found_place['locationParams']['deliveryTime']['min'] = min_delivery_time
    found_place['locationParams']['deliveryTime']['max'] = max_delivery_time

    return response


def _build_handler_request(shop_id, requested_items):
    return {
        'shop_id': shop_id,
        'user_address': {'latitude': 10, 'longitude': 20},
        'items': [
            {'feed_offer_id': i['feed_offer_id'], 'count': i['count']}
            for i in requested_items
        ],
    }


def _map_delivery_thresholds_for_response(delivery_thresholds):
    thresholds_for_response = []
    for threshold in delivery_thresholds:
        response_threshold = {
            'delivery_price': threshold['deliveryCost'],
            'min_cart_included': threshold['orderPrice']['min'],
        }
        if (
                'max' in threshold['orderPrice']
                and threshold['orderPrice']['max'] is not None
        ):
            response_threshold['max_cart_excluded'] = threshold['orderPrice'][
                'max'
            ]
        thresholds_for_response.append(response_threshold)
    return thresholds_for_response


def _verify_handler_response_json(
        response_json, expected_items, expected_response,
):
    def _sorted_response(response):
        response['items'].sort(key=lambda product: product['feed_offer_id'])
        if 'errors' in response:
            response['errors'].sort()
        return response

    shipping_cost = (
        expected_response['shipping_cost']
        if 'shipping_cost' in expected_response
        else DEFAULT_DELIVERY_COST
    )
    delivery_time = (
        expected_response['delivery_time']
        if 'delivery_time' in expected_response
        else DEFAULT_DELIVERY_TIME
    )
    additional_fees = (
        expected_response['additional_fees']
        if 'additional_fees' in expected_response
        else []
    )

    full_expected_response = {
        'currency': 'RUR',
        'delivery_time_minutes': delivery_time,
        'items': [
            {
                'count': item['count'],
                'feed_offer_id': public_id,
                'found': item.get('found', True),
                'price': item['item'].old_price or item['item'].price,
                **(
                    {'discount_price': item['item'].price}
                    if item['item'].old_price
                    else {}
                ),
            }
            for public_id, item in expected_items.items()
        ],
        'prices': {
            'items_total': expected_response['total_item_price'],
            'items_total_before_discount': (
                expected_response['total_item_price']
                + expected_response['total_item_discount']
            ),
            'items_total_discount': expected_response['total_item_discount'],
            'shipping_cost': shipping_cost,
            'total': (
                shipping_cost
                + expected_response['total_item_price']
                + sum([float(fee['value']) for fee in additional_fees])
            ),
            'additional_fees': additional_fees,
        },
        'shop_is_available': expected_response.get('is_available', True),
    }
    if 'thresholds' in expected_response:
        full_expected_response['prices']['thresholds'] = expected_response[
            'thresholds'
        ]
    if 'min_order_price' in expected_response:
        full_expected_response['prices'][
            'min_order_price'
        ] = expected_response['min_order_price']
    if 'max_order_price_threshold' in expected_response:
        full_expected_response[
            'max_order_price_threshold'
        ] = expected_response['max_order_price_threshold']
    if 'max_order_weight_threshold' in expected_response:
        full_expected_response[
            'max_order_weight_threshold'
        ] = expected_response['max_order_weight_threshold']
    if 'errors' in expected_response:
        full_expected_response['errors'] = expected_response['errors']
    if 'free_delivery_threshold' in expected_response:
        full_expected_response['prices']['left_for_free_delivery'] = max(
            0,
            expected_response['free_delivery_threshold']
            - expected_response['total_item_price'],
        )
    if 'available_from' in expected_response:
        full_expected_response['shop_is_available_from'] = expected_response[
            'available_from'
        ]
    assert _sorted_response(response_json) == _sorted_response(
        full_expected_response,
    )


def _generate_db_init_data():
    brand1 = models.Brand(brand_id=BRAND_ID, slug=str(BRAND_ID))
    brand1.add_places([models.Place(place_id=PLACE_ID, slug=PLACE_SLUG)])

    market_brand_place = models.MarketBrandPlace(
        brand_id=BRAND_ID,
        place_id=PLACE_ID,
        business_id=BUSINESS_ID,
        partner_id=SHOP_ID,
        feed_id=SHOP_ID,
    )

    return {'brands': [brand1], 'market_brand_places': [market_brand_place]}


def _generate_places_info():
    places_info = [
        models.PlaceInfo(
            partner_id=SHOP_ID,
            place_id=PLACE_ID,
            place_name=PLACE_SLUG,
            assembly_cost=ASSEMBLY_COST,
        ),
    ]

    return places_info


def eats_places_set_init_places(eats_catalog_storage):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-24T06:00:00+00:00'),
            end=parser.parse('2021-12-24T18:00:00+00:00'),
        ),
    ]

    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=ZONE_ID,
            place_id=int(PLACE_ID),
            working_intervals=open_schedule,
        ),
    )

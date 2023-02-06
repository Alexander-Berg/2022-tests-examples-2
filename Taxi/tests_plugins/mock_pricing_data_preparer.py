from collections import defaultdict
import copy
import json

import pytest


def _make_composite_price(cost):
    return {
        'boarding': float(cost),
        'destination_waiting': 0.0,
        'distance': 0.0,
        'requirements': 0.0,
        'time': 0.0,
        'transit_waiting': 0.0,
        'waiting': 0.0,
    }


PDP_CATEGORY_DATA = {
    'additional_prices': {},
    'base_price': _make_composite_price(100),
    'category_prices_id': 'c/0a6297a87cd247eb8d14a346995c6d50',
    'tariff_id': '01234567890abcdefghij0987654321z',
    'category_id': '0a6297a87cd247eb8d14a346995c6d50',
    'meta': {},
    'modifications': {'for_fixed': [], 'for_taximeter': []},
    'price': {'total': 100},
}

DEFAULT_TARIFF_INFO = {
    'time': {'included_minutes': 0, 'price_per_minute': 0},
    'distance': {'included_kilometers': 0, 'price_per_kilometer': 0},
    'point_a_free_waiting_time': 1,
    'max_free_waiting_time': 2,
}

PDP_DEFAULT_RESPONSE = {
    'corp_decoupling': False,
    'fixed_price': True,
    'geoarea_ids': ['g/c7f1d00b69e3434a8899c616b329febb'],
    'taximeter_metadata': {
        'max_distance_from_point_b': 500,
        'show_price_in_taximeter': False,
    },
    'driver': {},
    'user': {},
    'currency': {'fraction_digits': 0, 'name': 'RUB', 'symbol': '₽'},
    'tariff_info': DEFAULT_TARIFF_INFO,
}

PDP_DEFAULT_SURGE = {'value': 1.0, 'value_raw': 1, 'value_smooth': 1}

PDP_DEFAULT_TARIFF = {
    'boarding_price': 149.0,
    'minimum_price': 0.0,
    'requirement_multipliers': {},
    'requirement_prices': {
        'animaltransport': 150.0,
        'childchair_other': 100.0,
        'kronstadt_trip': 0.0,
        'luggage': 100.0,
        'no_smoking': 0.0,
        'ring_road_trip': 0.0,
        'ski': 150.0,
        'universal': 200.0,
        'waiting_in_transit': 5.0,
    },
    'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 8.0},
}


def _make_backend_variables(
        decoupling=False,
        fixed_price=True,
        discount=None,
        surge=None,
        coupon=None,
        user_tags=[],
        forced_fixprice=None,
):
    result = {
        'category_data': {
            'decoupling': decoupling,
            'fixed_price': fixed_price,
        },
        'experiments': [],
        'requirements': {},
        'surge_params': copy.deepcopy(PDP_DEFAULT_SURGE),
        'tariff': copy.deepcopy(PDP_DEFAULT_TARIFF),
        'temporary': {'route_parts': []},
        'user_data': {'has_yaplus': False, 'has_cashback_plus': False},
        'user_tags': user_tags,
    }
    if discount:
        result['discount'] = discount
    if surge:
        result['surge_params'] = surge
    if coupon:
        result['coupon'] = coupon
    if forced_fixprice:
        result['forced_fixprice'] = forced_fixprice
    return result


def _make_category_data(
        total_price,
        trip_info,
        backend_variables=None,
        meta=None,
        strikeout_price=None,
        category_prices_id=None,
        category_id=None,
        tariff_id=None,
        paid_supply=None,
        is_calc_paid_supply=False,
        antisurge=None,
):
    category_data = copy.deepcopy(PDP_CATEGORY_DATA)
    if trip_info:
        category_data['trip_information'] = trip_info
    category_data['price']['total'] = total_price
    if meta:
        category_data['meta'] = meta
    if backend_variables:
        category_data['data'] = backend_variables
    category_data['price']['total'] = total_price
    if strikeout_price is not None:
        category_data['price']['strikeout'] = strikeout_price
    if category_prices_id:
        category_data['category_prices_id'] = category_prices_id
    if category_id:
        category_data['category_id'] = category_id
    if tariff_id:
        category_data['tariff_id'] = tariff_id
    if antisurge:
        antisurge_price = {'total': antisurge['total']}
        if 'strikeout' in antisurge:
            antisurge_price['strikeout'] = antisurge['strikeout']
        category_data['additional_prices']['antisurge'] = {
            'meta': antisurge.get('meta', {}),
            'modifications': {'for_fixed': [], 'for_taximeter': []},
            'price': antisurge_price,
        }
    if is_calc_paid_supply and paid_supply:
        paid_supply_total = (
            paid_supply.get('total') or paid_supply['price'] + total_price
        )
        paid_supply_price = {'total': paid_supply_total}
        if 'strikeout' in paid_supply:
            paid_supply_price['strikeout'] = paid_supply['strikeout']

        category_data['additional_prices']['paid_supply'] = {
            'meta': paid_supply['meta'] if 'meta' in paid_supply else {},
            'modifications': {'for_fixed': [], 'for_taximeter': []},
            'price': paid_supply_price,
        }
    return category_data


def _make_surge(
        sp,
        alpha=None,
        beta=None,
        surcharge=None,
        explicit_antisurge=None,
        value_b=None,
):
    surge = {
        'value': float(sp),
        'value_raw': float(sp),
        'value_smooth': float(sp),
    }
    if beta is not None:
        surge['surcharge_beta'] = float(beta)
    if alpha is not None:
        surge['surcharge_alpha'] = float(alpha)
    if surcharge is not None:
        surge['surcharge'] = float(surcharge)
    if explicit_antisurge is not None:
        surge['explicit_antisurge'] = {'value': explicit_antisurge}
    if value_b is not None:
        surge['value_b'] = value_b
    return surge


def _make_discount():
    return {
        'id': 'e7ffe6c7-ef99-4fc9-8575-efe73615a700',
        'is_cashback': False,
        'calc_data_hyperbolas': {
            'threshold': 100.0,
            'hyperbola_lower': {'p': 99.0, 'a': 0.0, 'c': 1.0},
            'hyperbola_upper': {'p': 0.0, 'a': 10000.0, 'c': 0.0},
        },
        'restrictions': {
            'min_discount_coeff': 0.0,
            'max_discount_coeff': 0.99,
            'driver_less_coeff': 1.0,
            'newbie_max_coeff': 1.0,
            'newbie_num_coeff': 0.0,
            'completed_on_special_conditions_count': 0.0,
            'payment_type': 'googlepay',
        },
        'limited_rides': False,
        'discount_offer_id': '5eb2d6636b5636011e5b1ce4',
        'description': 'google_pay_discount_100_rus_2',
        'reason': 'newbie_googlepay',
        'method': 'subvention-fix',
    }


def _make_trip_information(distance, time, toll_roads):
    if distance is None and time is None:
        return None
    if toll_roads is not None:
        return {
            'distance': distance,
            'jams': True,
            'time': time,
            'has_toll_roads': toll_roads,
        }
    return {'distance': distance, 'jams': True, 'time': time}


DEFAULT_CATEGORY_NAME = '__default__'


class PricingDataPreparerContext:
    def __init__(self, is_fallback_response=False):
        self.calls = 0
        self.last_request = None
        self.categories = []
        self.error_code = None
        self.locale = 'en'
        self.with_strikeout = False
        self.corp_decoupling = False
        self.is_fallback_response = is_fallback_response
        self.category_settings = defaultdict(
            lambda: {},
            {
                DEFAULT_CATEGORY_NAME: {
                    'time': 100,
                    'distance': 100,
                    'fixed_price': True,
                    'decoupling': False,
                    'user_price': 100,
                    'driver_price': 100,
                    'active': True,
                },
            },
        )
        self.settings_stack = []
        self.marked_settings_v2_prepare = {}
        self.marked_settings_v2_calc_paid_supply = {}

    def set_error(self, code=500):
        self.error_code = code

    def set_locale(self, locale):
        self.locale = locale

    def set_meta(self, key, value, category=DEFAULT_CATEGORY_NAME):
        if value is None:
            return
        settings = self.category_settings[category]
        if 'meta' not in settings:
            settings['meta'] = {}
        settings['meta'][key] = value

    def delete_meta(self, key, category=DEFAULT_CATEGORY_NAME):
        settings = self.category_settings[category]
        if 'meta' not in settings:
            settings['meta'] = {}
        if key in settings['meta']:
            del settings['meta'][key]

    def set_active(self, category, active):
        settings = self.category_settings[category]
        settings['active'] = active

    def set_discount_meta(self, price, value, category=DEFAULT_CATEGORY_NAME):
        self.set_meta('discount_price', price, category)
        self.set_meta('discount_value', value, category)

    def set_discount(self, discount=None, category=DEFAULT_CATEGORY_NAME):
        settings = self.category_settings[category]
        if not discount:
            settings['discount'] = _make_discount()
        else:
            settings['discount'] = discount

    def set_discount_offer_id(self, discount_offer_id):
        settings = self.category_settings[DEFAULT_CATEGORY_NAME]
        settings['discount_offer_id'] = discount_offer_id

    def set_strikeout(self, price, category=DEFAULT_CATEGORY_NAME):
        self.category_settings[category]['stikeout'] = price

    def set_paid_supply(
            self, price, driver_price=None, category=DEFAULT_CATEGORY_NAME,
    ):
        self.category_settings[category]['paid_supply'] = price
        self.category_settings[category]['paid_supply_driver'] = (
            driver_price or price
        )

    def set_antisurge(
            self, price, driver_price=None, category=DEFAULT_CATEGORY_NAME,
    ):
        self.category_settings[category]['antisurge'] = price
        self.category_settings[category]['antisurge_driver'] = (
            driver_price or price
        )

    def set_coupon(
            self,
            value,
            percent=None,
            price_before_coupon=None,
            limit=1000,
            category=DEFAULT_CATEGORY_NAME,
            valid_classes=None,
            valid=True,
            description='some coupon description',
            details=None,
            currency_rules=None,
            format_currency=False,
    ):
        if price_before_coupon is not None:
            self.set_meta(
                'price_before_coupon', price_before_coupon, category=category,
            )
        self.category_settings[category]['coupon'] = {
            'valid': valid,
            'value': value,
            'format_currency': format_currency,
            'currency_code': 'rub',
            'descr': description,
            'percent': percent,
            'limit': limit,
            'details': details,
            'currency_rules': currency_rules,
        }
        if valid_classes is not None:
            self.category_settings[category]['coupon'][
                'valid_classes'
            ] = valid_classes

    def set_user_surge(
            self,
            sp,
            alpha=None,
            beta=None,
            surcharge=None,
            explicit_antisurge=None,
            value_b=None,
            category=DEFAULT_CATEGORY_NAME,
    ):
        self.category_settings[category]['user_surge'] = _make_surge(
            sp, alpha, beta, surcharge, explicit_antisurge, value_b,
        )
        self.set_meta('synthetic_surge', max(1.0, sp), category)
        if surcharge is not None:
            self.set_meta('setcar.show_surcharge', beta * surcharge, category)

    def set_driver_surge(
            self,
            sp,
            alpha=None,
            beta=None,
            surcharge=None,
            explicit_antisurge=None,
            value_b=None,
            category=DEFAULT_CATEGORY_NAME,
    ):
        self.category_settings[category]['driver_surge'] = _make_surge(
            sp, alpha, beta, surcharge, explicit_antisurge, value_b,
        )

    def set_fixed_price(
            self, enable, reason=None, category=DEFAULT_CATEGORY_NAME,
    ):
        assert isinstance(enable, bool)
        self.category_settings[category]['fixed_price'] = enable
        self.category_settings[category]['fixed_price_discard_reason'] = reason

    def set_tariff_info(
            self,
            included_minutes=0,
            included_kilometers=0,
            price_per_minute=0,
            price_per_kilometer=0,
            category=DEFAULT_CATEGORY_NAME,
    ):
        tariff_info = copy.deepcopy(DEFAULT_TARIFF_INFO)
        tariff_info.update(
            {
                'time': {
                    'included_minutes': included_minutes,
                    'price_per_minute': price_per_minute,
                },
                'distance': {
                    'included_kilometers': included_kilometers,
                    'price_per_kilometer': price_per_kilometer,
                },
            },
        )
        self.category_settings[category]['tariff_info'] = tariff_info

    def set_corp_decoupling(self, enable):
        assert isinstance(enable, bool)
        self.corp_decoupling = enable

    def set_decoupling(self, enable, category=DEFAULT_CATEGORY_NAME):
        assert isinstance(enable, bool)
        self.category_settings[category]['decoupling'] = enable
        if enable:
            self.corp_decoupling = True

    def set_cost(self, user_cost, driver_cost, category=DEFAULT_CATEGORY_NAME):
        settings = self.category_settings[category]
        settings['driver_price'] = float(driver_cost)
        settings['user_price'] = float(user_cost)

    def push(self, id=None, is_calc_paid_supply=False):
        if id is None:
            self.settings_stack.append(copy.deepcopy(self.category_settings))
        else:
            if is_calc_paid_supply:
                self.marked_settings_v2_calc_paid_supply[id] = copy.deepcopy(
                    self.category_settings,
                )
            else:
                self.marked_settings_v2_prepare[id] = copy.deepcopy(
                    self.category_settings,
                )

    def pop(self):
        if self.settings_stack:
            self.category_settings = self.settings_stack[0]
            self.settings_stack.pop(0)

    def set_trip_information(
            self,
            time,
            distance,
            toll_roads=None,
            category=DEFAULT_CATEGORY_NAME,
    ):
        self.category_settings[category]['distance'] = float(distance)
        self.category_settings[category]['time'] = float(time)
        self.category_settings[category]['toll_roads'] = toll_roads

    def set_user_tags(self, tags, category=DEFAULT_CATEGORY_NAME):
        self.category_settings[category]['user_tags'] = tags

    def set_no_trip_information(self, category=DEFAULT_CATEGORY_NAME):
        self.category_settings[category]['distance'] = None
        self.category_settings[category]['time'] = None

    def set_categories(self, categories, category=DEFAULT_CATEGORY_NAME):
        self.categories = categories

    def set_user_category_prices_id(
            self,
            category_prices_id,
            category_id=None,
            tariff_id=None,
            category=DEFAULT_CATEGORY_NAME,
    ):
        settings = self.category_settings[category]
        settings['user_category_prices_id'] = category_prices_id
        if category_id:
            settings['user_category_id'] = category_id
        if tariff_id:
            settings['user_tariff_id'] = tariff_id

    def set_driver_category_prices_id(
            self,
            category_prices_id,
            category_id=None,
            tariff_id=None,
            category=DEFAULT_CATEGORY_NAME,
    ):
        settings = self.category_settings[category]
        settings['driver_category_prices_id'] = category_prices_id
        if category_id:
            settings['driver_category_id'] = category_id
        if tariff_id:
            settings['driver_tariff_id'] = tariff_id

    def _get_category_settings(
            self, category, is_calc_paid_supply, point_id=None,
    ):
        csettings = self.category_settings

        if is_calc_paid_supply:
            if self.marked_settings_v2_calc_paid_supply != {}:
                csettings = self.marked_settings_v2_calc_paid_supply[point_id]
        else:
            if self.marked_settings_v2_prepare != {}:
                csettings = self.marked_settings_v2_prepare[point_id]

        category_settings = defaultdict(
            lambda: None, csettings[DEFAULT_CATEGORY_NAME],
        )

        category_settings.update(csettings[category])

        return category_settings

    def get_pricing_data(
            self,
            category=DEFAULT_CATEGORY_NAME,
            is_calc_paid_supply=False,
            point_id=None,
            forced_fixprice=None,
    ):
        cat_settings = self._get_category_settings(
            category, is_calc_paid_supply, point_id=point_id,
        )
        if not cat_settings['active']:
            return None

        response = copy.deepcopy(PDP_DEFAULT_RESPONSE)
        response['corp_decoupling'] = self.corp_decoupling
        response['fixed_price'] = cat_settings['fixed_price']
        if cat_settings['fixed_price_discard_reason']:
            response['fixed_price_discard_reason'] = cat_settings[
                'fixed_price_discard_reason'
            ]

        if self.is_fallback_response:
            response['is_fallback'] = True

        user_bv = _make_backend_variables(
            decoupling=cat_settings['decoupling'],
            fixed_price=cat_settings['fixed_price'],
            surge=cat_settings['user_surge'],
            coupon=cat_settings['coupon'],
            discount=cat_settings['discount'],
            user_tags=cat_settings['user_tags'] or [],
            forced_fixprice=forced_fixprice,
        )

        trip_info = _make_trip_information(
            cat_settings['distance'],
            cat_settings['time'],
            cat_settings['toll_roads'],
        )
        response['user'] = _make_category_data(
            total_price=cat_settings['user_price'],
            backend_variables=user_bv,
            trip_info=trip_info,
            meta=cat_settings['meta'],
            strikeout_price=cat_settings['stikeout'],
            category_prices_id=cat_settings['user_category_prices_id'],
            category_id=cat_settings['user_category_id'],
            tariff_id=cat_settings['user_tariff_id'],
            paid_supply=cat_settings['paid_supply'],
            is_calc_paid_supply=is_calc_paid_supply,
            antisurge=cat_settings['antisurge'],
        )

        driver_bv = None
        if cat_settings['decoupling']:
            driver_bv = _make_backend_variables(
                decoupling=False,
                fixed_price=cat_settings['fixed_price'],
                surge=cat_settings['driver_surge'],
                discount=cat_settings['discount'],
            )

        response['driver'] = _make_category_data(
            total_price=cat_settings['driver_price'],
            backend_variables=driver_bv,
            trip_info=trip_info,
            meta=cat_settings['meta'],
            category_prices_id=cat_settings['driver_category_prices_id'],
            category_id=cat_settings['driver_category_id'],
            tariff_id=cat_settings['driver_tariff_id'],
            paid_supply=cat_settings['paid_supply_driver'],
            is_calc_paid_supply=is_calc_paid_supply,
            antisurge=cat_settings['antisurge_driver'],
        )

        if cat_settings['tariff_info']:
            response['tariff_info'] = cat_settings['tariff_info']

        return response


def _pdp_mock_impl(request, pdp_context, mockserver, is_calc_paid_supply):
    if 'Accept-Language' in request.headers:
        assert request.headers['Accept-Language'] == pdp_context.locale

    req_data = json.loads(request.get_data())

    assert 'zone' in req_data and req_data['zone']
    pdp_context.last_request = req_data
    pdp_context.calls += 1
    if pdp_context.error_code:
        return mockserver.make_response(
            'Something bad happened', pdp_context.error_code,
        )

    response = {}
    categories = (
        pdp_context.categories
        if pdp_context.categories
        else req_data['categories']
    )
    forced_fixprice = req_data.get('extra', {}).get('forced_fixprice')
    transport = req_data.get('transport_by_categories')

    point_id = None
    if is_calc_paid_supply:
        if 'econom' in req_data['categories']:
            point_id = req_data['categories']['econom']['prepared']['user'][
                'price'
            ]['total']
            print('point_id', point_id)
            print(pdp_context.marked_settings_v2_calc_paid_supply)
    elif 'waypoints' in req_data:
        if len(req_data['waypoints']) > 1:
            point_id = (
                '%.8f' % req_data['waypoints'][0][0]
                + '%.8f' % req_data['waypoints'][1][0]
            )
            if point_id not in pdp_context.marked_settings_v2_prepare:
                point_id = '%.8f' % req_data['waypoints'][0][0]
        else:
            point_id = '%.8f' % req_data['waypoints'][0][0]

    for category in categories:
        if not is_calc_paid_supply and len(req_data['waypoints']) < 2:
            pdp_context.set_fixed_price(False, 'NO_POINT_B')

        cat = pdp_context.get_pricing_data(
            category,
            is_calc_paid_supply,
            point_id=point_id,
            forced_fixprice=forced_fixprice,
        )

        if cat is not None:
            response[category] = cat
            if transport is not None and category in transport:
                response[category]['transport'] = transport[category]

    pdp_context.pop()
    return {'categories': response}


@pytest.fixture()
def pricing_data_preparer(mockserver):
    pdp_context = PricingDataPreparerContext()

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        return _pdp_mock_impl(
            request, pdp_context, mockserver, is_calc_paid_supply=False,
        )

    @mockserver.json_handler('/pricing_data_preparer/v2/calc_paid_supply')
    def _mock_v2_calc_paid_supply(request):
        return _pdp_mock_impl(
            request, pdp_context, mockserver, is_calc_paid_supply=True,
        )

    return pdp_context


@pytest.fixture()
def pricing_data_preparer_fallback(mockserver):
    pdp_context = PricingDataPreparerContext(is_fallback_response=True)
    pdp_context.set_fixed_price(False)

    @mockserver.json_handler('/pricing_fallback/v1/get_pricing_data')
    def _mock_v2_prepare(request):
        if 'Accept-Language' in request.headers:
            assert request.headers['Accept-Language'] == pdp_context.locale

        req_data = json.loads(request.get_data())
        assert 'zone' in req_data and req_data['zone']
        pdp_context.last_request = req_data
        pdp_context.calls += 1
        if pdp_context.error_code:
            return mockserver.make_response(
                'Something bad happened', pdp_context.error_code,
            )
        response = {}
        categories = (
            pdp_context.categories
            if pdp_context.categories
            else req_data['categories']
        )
        for category in categories:
            response[category] = pdp_context.get_pricing_data(category)
        return {'categories': response}

    return pdp_context


class RecalcOrderContext:
    class Price:
        def __init__(self):
            self.total = 0.0
            self.meta = {}
            self.paid_cancel_in_waiting = None

        def make_response(self):
            res = {'total': self.total}
            meta = copy.deepcopy(self.meta)
            if self.paid_cancel_in_waiting:
                meta.update(
                    {
                        'paid_cancel_in_waiting_price': (
                            self.paid_cancel_in_waiting
                        ),
                    },
                )
            res.update({'meta': meta})
            return res

    def __init__(self):
        self.calls = 0
        self.last_request = None
        self.error_code = None
        self.driver = self.Price()
        self.user = self.Price()

    def set_error_code(self, error_code):
        self.error_code = error_code

    def set_recalc_result(self, total, paid_cancel_in_waiting=None, meta=None):
        self.set_driver_recalc_result(total, paid_cancel_in_waiting, meta)
        self.set_user_recalc_result(total, paid_cancel_in_waiting, meta)

    def set_driver_recalc_result(
            self, total, paid_cancel_in_waiting=None, meta=None,
    ):
        self.driver.total = total
        self.driver.paid_cancel_in_waiting = paid_cancel_in_waiting
        if meta is not None:
            self.driver.meta = meta

    def set_user_recalc_result(
            self, total, paid_cancel_in_waiting=None, meta=None,
    ):
        self.user.total = total
        self.user.paid_cancel_in_waiting = paid_cancel_in_waiting
        if meta is not None:
            self.user.meta = meta

    def make_response(self):
        return {
            'price': {
                'driver': self.driver.make_response(),
                'user': self.user.make_response(),
            },
        }


@pytest.fixture()
def recalc_order(mockserver):
    recalc_order_context = RecalcOrderContext()

    @mockserver.json_handler('/pricing_data_preparer/v2/recalc_order')
    def _mock_v2_recalc_order(request):
        assert request.args['order_id']
        recalc_order_context.last_request = request.args
        recalc_order_context.calls += 1
        if recalc_order_context.error_code:
            return mockserver.make_response(
                'Something bad happened', recalc_order_context.error_code,
            )
        return recalc_order_context.make_response()

    return recalc_order_context

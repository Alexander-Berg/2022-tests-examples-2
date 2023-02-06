DEFAULT_USER_AGENT = 'yandex-taxi/1.0.0.0 Android/10 (Nokia 3310)'


class Request:
    def __init__(self):
        self.request = {
            'modifications_scope': 'taxi',
            'waypoints': [[37.683, 55.774], [37.656, 55.764]],
            'categories': ['econom'],
            'order_type': 'APPLICATION',
            'classes_requirements': {},
            'user_info': {
                'application': {
                    'name': 'Citimobile',
                    'version': '6.6.6',
                    'platform_version': '3.3.3',
                    'user_agent': DEFAULT_USER_AGENT,
                },
                'user_id': 'some_user_id',
                'payment_info': {'type': 'SOME_PAYMENT_TYPE'},
            },
            'tolls': 'DENY',
            'zone': 'moscow',
        }

    def get_waypoints(self):
        return self.request['waypoints']

    def add_coupon(self, coupon='SOME_COUPON'):
        self.request['user_info']['payment_info'].update({'coupon': coupon})
        return self

    def add_decoupling_method(self):
        self.request['user_info']['payment_info'].update(
            {'method_id': 'corp-decoupling', 'type': 'corp'},
        )
        return self

    def set_categories(self, categories):
        self.request['categories'] = categories
        return self

    def remove_user_info(self):
        self.request.pop('user_info')
        return self

    def set_waypoints(self, way):
        self.request['waypoints'] = way
        return self

    def set_or_update_extra(self, key, value):
        extra = self.request.get('extra', {})
        extra[key] = value
        self.request.update({'extra': extra})

    def set_moscow_route(self):
        self.set_waypoints([[37.683, 55.774], [37.656, 55.764]])
        return self

    def set_one_point_route(self):
        self.set_waypoints([[37.683, 55.774]])
        return self

    def set_forced_fixprice(self, value):
        self.set_or_update_extra('forced_fixprice', value)
        return self

    def set_expected_prices(self, value):
        self.set_or_update_extra('expected_prices', value)
        return self

    def set_shuttle_params(self, is_street_hail_booking):
        self.set_or_update_extra(
            'shuttle_params',
            {'is_street_hail_booking': is_street_hail_booking},
        )
        return self

    def set_requirements(self, requirements):
        self.request['classes_requirements'] = requirements
        return self

    def set_application(self, name=None, version=None):
        assert 'user_info' in self.request
        if name:
            self.request['user_info']['application']['name'] = name
        if version:
            self.request['user_info']['application']['version'] = version
        return self

    def set_user_id(self, user_id):
        assert 'user_info' in self.request
        self.request['user_info']['user_id'] = user_id
        return self

    def set_cashback_enabled(self, enabled):
        assert 'user_info' in self.request
        assert 'payment_info' in self.request['user_info']
        payment_info = self.request['user_info']['payment_info']
        if enabled is not None:
            payment_info.update({'cashback_enabled': enabled})
        elif 'cashback_enabled' in payment_info:
            payment_info.pop('cashback_enabled')
        return self

    def set_zone(self, zone):
        self.request['zone'] = zone

    def enable_cashback(self):
        return self.set_cashback_enabled(True)

    def disable_cashback(self):
        return self.set_cashback_enabled(False)

    def clear_cashback(self):
        return self.set_cashback_enabled(None)

    def set_tolls(self, tolls):
        assert tolls in ('DENY', 'ALLOW')
        self.request['tolls'] = tolls
        return self

    def set_additional_prices(
            self,
            antisurge=False,
            strikeout=False,
            plus_promo=False,
            combo_order=False,
            combo_inner=False,
            combo_outer=False,
            combo=False,
            alt_offer_discount=False,
            full_auction=False,
    ):
        self.request.update(
            {
                'calc_additional_prices': {
                    'antisurge': antisurge,
                    'strikeout': strikeout,
                    'plus_promo': plus_promo,
                    'combo_order': combo_order,
                    'combo_inner': combo_inner,
                    'combo_outer': combo_outer,
                    'combo': combo,
                    'alt_offer_discount': alt_offer_discount,
                    'full_auction': full_auction,
                },
            },
        )
        return self

    def set_personal_wallet(self, wallet_id, balance):
        assert 'user_info' in self.request
        assert 'payment_info' in self.request['user_info']
        payment_info = self.request['user_info']['payment_info']
        if wallet_id and balance >= 0.0:
            payment_info.update(
                {
                    'complements': {
                        'personal_wallet': {
                            'method_id': wallet_id,
                            'balance': balance,
                        },
                    },
                },
            )
        else:
            payment_info.pop('complements')
        return self

    def set_order_type(self, order_type):
        self.request['order_type'] = order_type
        return self

    def set_due(self, due):
        self.request['due'] = due
        return self

    def set_is_delayed(self, is_delayed):
        self.request['is_delayed'] = is_delayed
        return self

    def _update_providers(self, provider, update):
        providers = self.request.get('extra', {}).get('providers', {})
        if update is None:
            if provider in providers:
                providers.pop(provider)
        else:
            providers[provider] = update
        if providers:
            if 'extra' not in self.request:
                self.request.update({'extra': {}})
            self.request['extra']['providers'] = providers
        elif 'extra' in self.request:
            if 'providers' in self.request['extra']:
                self.request['extra'].pop('providers')
        return self

    def set_discounts_enabled(self, enabled):
        return self._update_providers(
            'discounts',
            {'is_enabled': enabled} if enabled is not None else None,
        )

    def set_surge_enabled(self, enabled):
        return self._update_providers(
            'surge', {'is_enabled': enabled} if enabled is not None else None,
        )

    def set_use_fallback_router(self, is_fallback):
        return self._update_providers(
            'router',
            {'is_fallback': is_fallback} if is_fallback is not None else None,
        )

    def set_coupons_order_id(self, order_id):
        return self._update_providers(
            'coupons',
            {'order_id': order_id} if order_id is not None else None,
        )

    def set_details_enabled(self, consumer):
        self.request.update({'additional_payloads': {'details': consumer}})
        return self

    def set_need_strikeout_price_flag(
            self, need_strikeout_price_modifications,
    ):
        self.request.update(
            {
                'additional_payloads': {
                    'need_strikeout_price_modifications': (
                        need_strikeout_price_modifications
                    ),
                },
            },
        )
        return self

    def set_modifications_scope(self, scope):
        self.request.update({'modifications_scope': scope})
        return self

    def get(self):
        return self.request


class SaveOrderDetailsRequest:
    def __init__(self):
        self._request = {
            'diagnostic': {
                'other_data': {'a': 6, 'action': '*', 'b': 7},
                'some_data': 42,
            },
            'ride': {
                'driver': {
                    'calc_method': 'taximeter',
                    'rounded_price': 450,
                    'trip_details': {
                        'total_distance': 1000,
                        'total_time': 600,
                        'user_options': {},
                        'waiting_in_destination_time': 0,
                        'waiting_in_transit_time': 0,
                        'waiting_time': 0,
                    },
                },
                'route': [
                    {'distance': 0, 'lat': 60.0, 'lon': 40.0, 'time': 0},
                    {
                        'distance': 1000,
                        'lat': 60.02,
                        'lon': 40.02,
                        'time': 600,
                    },
                ],
                'user': {
                    'calc_method': 'taximeter',
                    'rounded_price': 675,
                    'trip_details': {
                        'total_distance': 1000,
                        'total_time': 600,
                        'user_options': {},
                        'waiting_in_destination_time': 0,
                        'waiting_in_transit_time': 0,
                        'waiting_time': 0,
                    },
                },
            },
        }

    def set_total_distance(self, distance):
        self._request['ride']['user']['trip_details'][
            'total_distance'
        ] = distance
        self._request['ride']['route'][-1]['distance'] = distance

    def set_total_time(self, time):
        self._request['ride']['user']['trip_details']['total_time'] = time
        self._request['ride']['route'][-1]['time'] = time

    def set_waitings(
            self, waiting=0, waiting_in_transit=0, waiting_in_destination=0,
    ):
        self._request['ride']['user']['trip_details'][
            'waiting_in_destination_time'
        ] = waiting_in_destination
        self._request['ride']['user']['trip_details'][
            'waiting_in_transit_time'
        ] = waiting_in_transit
        self._request['ride']['user']['trip_details']['waiting_time'] = waiting

    def set_invalid_route(self):
        self._request['ride']['route'] = [
            {'distance': 0, 'lat': 60.0, 'lon': 40.0, 'time': 0},
            {'distance': 1100, 'lat': 61.0, 'lon': 41.0, 'time': 800},
            {'distance': 1000, 'lat': 60.02, 'lon': 40.02, 'time': 600},
        ]

    def set_empty_route(self):
        self._request['ride']['route'] = []

    def set_invalid_trip_details(self):
        self.set_total_distance(1000)
        self._request['ride']['route'][-1]['distance'] = 4224

    def get(self):
        return self._request

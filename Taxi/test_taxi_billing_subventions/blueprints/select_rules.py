def api_request(attrs):
    defaults = {
        'is_personal': False,
        'status': 'enabled',
        'time_range': {
            'start': '2000-01-01T00:00:00.000+00:00',
            'end': '3000-01-01T00:00:00.000+00:00',
        },
        'profile_tags': ['subv_disable_all'],
    }
    defaults.update(attrs)
    return defaults


def api_discount_payback_rule(attrs):
    defaults = {
        'bonus_amount': '0',
        'currency': 'RUB',
        'cursor': '3000-01-01T00:00:00.000000+00:00/5d7b36f8c081365f03b18fe2',
        'end': '3000-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'discount_payback',
        'start': '2500-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/5d7b36f8c081365f03b18fe2',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'type': 'discount_payback',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_ridecount_rule(attrs):
    defaults = {
        'currency': 'RUB',
        'cursor': '3000-01-01T00:00:00.000000+00:00/5db9d98879b9e540b6028753',
        'days_span': 1,
        'end': '3000-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'guarantee',
        'start': '2500-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/5db9d98879b9e540b6028753',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'trips_bounds': [{'bonus_amount': '0', 'lower_bound': 1}],
        'type': 'guarantee',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_mfg_geo_rule(attrs):
    defaults = {
        'bonus_amount': '100',
        'currency': 'RUB',
        'cursor': '2510-01-01T00:00:00.000000+00:00/000000000000000000000000',
        'end': '2510-01-01T00:00:00.000000+00:00',
        'geoareas': ['some_geoarea'],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'guarantee',
        'start': '2500-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/000000000000000000000000',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'type': 'guarantee',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_on_top_geo_rule(attrs):
    defaults = {
        'bonus_amount': '100',
        'currency': 'RUB',
        'cursor': '2520-01-01T00:00:00.000000+00:00/111111111111111111111111',
        'end': '2520-01-01T00:00:00.000000+00:00',
        'geoareas': ['some_geoarea'],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'add',
        'start': '2510-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/111111111111111111111111',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'type': 'add',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_mfg_rule(attrs):
    defaults = {
        'bonus_amount': '100',
        'currency': 'RUB',
        'cursor': '2530-01-01T00:00:00.000000+00:00/222222222222222222222222',
        'end': '2530-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'guarantee',
        'start': '2520-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/222222222222222222222222',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'type': 'guarantee',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_on_top_rule(attrs):
    defaults = {
        'bonus_amount': '100',
        'currency': 'RUB',
        'cursor': '2540-01-01T00:00:00.000000+00:00/333333333333333333333333',
        'end': '2540-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'add',
        'start': '2530-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/333333333333333333333333',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'type': 'add',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': False,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_nmfg_rule(attrs):
    defaults = {
        'currency': 'RUB',
        'cursor': '2550-01-01T00:00:00.000000+00:00/444444444444444444444444',
        'days_span': 1,
        'driver_points': 41,
        'end': '2550-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'has_commission': True,
        'hours': [],
        'is_net': False,
        'is_personal': False,
        'is_test': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'min_activity_points': 41,
        'order_payment_type': None,
        'payment_type': 'guarantee',
        'start': '2540-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'steps': [{'bonus': 1800, 'orders_count': 20}],
        'subvention_rule_id': 'group_id/8532540f-19d9-4c70-8d65-fdfb9776824c',
        'tags': [],
        'tariff_classes': ['econom', 'uberx'],
        'tariff_zones': ['moscow'],
        'taximeter_daily_guarantee_tag': 'steps',
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'trips_bounds': [
            {'bonus_amount': '1800', 'lower_bound': 20, 'upper_bound': 20},
        ],
        'type': 'daily_guarantee',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults


def api_do_x_get_y_rule(attrs):
    defaults = {
        'currency': 'RUB',
        'cursor': '2560-01-01T00:00:00.000000+00:00/555555555555555555555555',
        'days_span': 1,
        'end': '2560-01-01T00:00:00.000000+00:00',
        'geoareas': [],
        'group_id': 'e0bbfa361a90d174fd81acb23ab6cf622bcf0ef5',
        'has_commission': False,
        'hours': [],
        'is_personal': False,
        'log': [
            {
                'login': 'saab',
                'ticket': 'TAXIRATE-228',
                'updated': '2500-01-01T00:00:00.000000+00:00',
            },
        ],
        'order_payment_type': None,
        'payment_type': 'add',
        'start': '2550-01-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/555555555555555555555555',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-228',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'trips_bounds': [{'bonus_amount': '55', 'lower_bound': 15}],
        'type': 'add',
        'updated': '2500-01-01T00:00:00.000000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }
    defaults.update(attrs)
    return defaults

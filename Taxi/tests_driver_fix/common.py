import re

import pytest


# Generated via `tvmknife unittest service -s 123 -d 123321`
# mock_service is testsuite, that calls our service
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIexC5wwc:Q9I_85'
    'oQtOPXLu9Ds2xuQNWKPxksLjXJ4AqHbvuCulWBk5N'
    'O2CXoV4FoNn-5uN4gjYLAgq19i3AV5_hfSdGYfTph'
    'Ibm6wzagYf8nMoSTWW_7aBoY2VPHmmhJF9zDcN2Au'
    'MnuEXa5CTym5hyAM3g8lq-BfvL16ZAg7iTGOxipklY'
)

DEFAULT_DRIVER_FIX_HEADER = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}

DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY = {
    'X-YaTaxi-Driver-Profile-Id': 'uuid',
    'X-YaTaxi-Park-Id': 'dbid',
    'X-Request-Application-Version': '8.90 (228)',
    'X-Request-Platform': 'android',
    'X-Request-Application': 'taximeter',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
}

# pylint: disable=invalid-name
tvm_ticket = pytest.mark.tvm2_ticket({111: 'ticket'})


PROFILES_DEFAULT_VALUE = {
    'classes': ['econom', 'business'],
    'dbid': '7ad36bc7560449998acbe2c57a75c293',
    'position': [37.63361316, 55.75419758],
    'uuid': 'c5673ab7870c45b3adc42fec699a252c',
}

DCB_DEFAULT_VALUE = {
    'dbid': 'dbid',
    'driver_classes': ['econom', 'business'],
    'payment_type_restrictions': 'none',
    'uuid': 'uuid',
}

PAYMENT_TYPES_DEFAULT_VALUES = [
    {
        'park_id': 'dbid',
        'driver_profile_id': 'uuid',
        'payment_types': [
            {'payment_type': 'none', 'active': True, 'available': True},
            {'payment_type': 'cash', 'active': False, 'available': True},
            {'payment_type': 'online', 'active': False, 'available': True},
        ],
    },
]

NEARESTZONE_DEFAULT_VALUE = 'moscow'

TAGS_DEFAULT_VALUE = ['tag1', 'tag2', 'tag3']

DEFAULT_DRIVER_FIX_RULE = {
    'tariff_zones': ['moscow'],
    'status': 'enabled',
    'start': '2019-01-01T01:05:00.000000+03:00',
    'end': '2019-01-10T23:59:00.000000+03:00',
    'type': 'driver_fix',
    'is_personal': False,
    'taxirate': 'TAXIRATE-01',
    'subvention_rule_id': 'subvention_rule_id',
    'cursor': 'cursor',
    'tags': ['driver-fix_tags'],
    'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
    'currency': 'RUB',
    'updated': '2019-01-01T00:00:00.000000+00:00',
    'visible_to_driver': True,
    'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    'hours': [],
    'log': [],
    'geoareas': ['msk-driver-fix-poly'],
    'tariff_classes': ['econom'],
    'profile_payment_type_restrictions': 'online',
    'profile_tariff_classes': ['business', 'econom'],
    'rates': [
        {'week_day': 'mon', 'start': '00:00', 'rate_per_minute': '5.0'},
        {'week_day': 'mon', 'start': '05:00', 'rate_per_minute': '5.5'},
        {'week_day': 'mon', 'start': '13:00', 'rate_per_minute': '6.0'},
        {'week_day': 'tue', 'start': '01:02', 'rate_per_minute': '4.8'},
        {'week_day': 'wed', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'thu', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'fri', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sat', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sun', 'start': '12:00', 'rate_per_minute': '4.5'},
    ],
    'commission_rate_if_fraud': '90.90',
}

DEFAULT_GEOBOOKING_RULE = {
    'driver_points': 50,
    'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    'updated': '2020-01-01T00:00:00.000000+00:00',
    'is_relaxed_order_time_matching': False,
    'is_personal': False,
    'min_online_minutes': 300,
    'subvention_rule_id': '_id/subvention_rule_id',
    'tariff_classes': ['business', 'econom'],
    'taxirate': 'TAXIRATE-100',
    'tags': ['geobooking_moscow_2020'],
    'type': 'geo_booking',
    'payment_type': 'add',
    'is_relaxed_income_matching': True,
    'tariff_zones': ['moscow'],
    'budget': {
        'id': 'bded3963-0609-4345-9e9a-d9a3e39c6661',
        'weekly': '10000',
        'rolling': True,
        'threshold': 120,
        'daily': '3000',
    },
    'workshift': {'start': '07:00', 'end': '18:00'},
    'geoareas': ['moscow_center'],
    'rate_on_order_per_minute': '10',
    'has_commission': False,
    'time_zone': {'offset': '+03:00', 'id': 'Europe/Moscow'},
    'hours': [],
    'rate_free_per_minute': '10',
    'end': '2020-01-01T21:00:00.000000+00:00',
    'status': 'enabled',
    'profile_payment_type_restrictions': 'none',
    'visible_to_driver': True,
    'cursor': 'cursor',
    'currency': 'RUB',
    'start': '2019-12-31T21:00:00.000000+00:00',
    'order_payment_type': None,
    'min_activity_points': 40,
    'log': [],
}


def default_init_mock_offer_requirements(mor):
    mor.init(
        PROFILES_DEFAULT_VALUE,
        DCB_DEFAULT_VALUE,
        PAYMENT_TYPES_DEFAULT_VALUES,
        NEARESTZONE_DEFAULT_VALUE,
        DEFAULT_DRIVER_FIX_RULE,
        None,
        None,
    )


def generate_online_time_tags_config(
        zone, zone_tags_config, common_tags_config,
):
    def _add_online_time_tags(tags_config, online_tags):
        online_time_tags = tags_config.setdefault('online_time_tags', [])
        for seconds, tags in online_tags.items():
            online_time_tags.append(
                {
                    'time_in_seconds': seconds,
                    'add_tags': tags['add_tags'],
                    'remove_tags': tags['remove_tags'],
                },
            )

    online_tags_config = dict()
    if zone_tags_config is not None:
        tags_by_zone = online_tags_config.setdefault(
            'additional_tags_by_zone', {},
        )
        zone_tags = tags_by_zone.setdefault(zone, {})
        _add_online_time_tags(zone_tags, zone_tags_config)
    if common_tags_config is not None:
        common_tags = online_tags_config.setdefault('common_tags', {})
        _add_online_time_tags(common_tags, common_tags_config)
    return online_tags_config


def set_native_restrictions_cfg(taxi_config, enabled, override=None):
    native_restrictions_cfg = taxi_config.get(
        'DRIVER_FIX_NATIVE_RESTRICTIONS_V2',
    )
    if override:
        native_restrictions_cfg.update(override)
    taxi_config.set(
        DRIVER_FIX_NATIVE_RESTRICTIONS_V2=native_restrictions_cfg,
        DRIVER_FIX_NATIVE_RESTRICTIONS_ENABLED=enabled,
    )


def get_enriched_params(supported_features, panel_body_hash=None) -> dict:
    params = {'tz': 'Europe/Moscow', 'park_id': 'dbid'}
    if supported_features:
        params['supported_features'] = ','.join(supported_features)
    if panel_body_hash is not None:
        params['panel_body_hash'] = panel_body_hash
    return params


DEFAULT_OFFER_CONFIG_V2 = {
    'offer_card': {
        'title': 'offer_card.title',
        'description': 'offer_card.description',
    },
    'offer_screen': [
        {
            'type': 'caption',
            'title': 'offer_screen.title',
            'description': 'offer_screen.description',
        },
        {
            'type': 'driver_fix_tariffication',
            'title': 'offer_screen.tariffication',
            'caption': 'offer_screen.tariffication_select_date',
        },
        {
            'type': 'driver_fix_requirements',
            'title': 'offer_screen.requirements',
            'items': [{'type': 'default_constraints'}],
        },
        {
            'type': 'detail_button',
            'text': 'offer_screen.full_description_button_text',
            'payload_url': 'https://driver.yandex',
            'payload_title': 'offer_screen.title',
        },
    ],
    'memo_screen': [
        {'type': 'header', 'caption': 'memo_screen.header'},
        {'type': 'multy_paragraph_text', 'text': 'memo_screen.text'},
        {'type': 'image', 'image_url': 'memo_image.png'},
    ],
}


def extract_check_value(ctor, regex):
    """Extracts check value from constructor by regular expression"""
    for item in ctor['items']:
        if item['type'] == 'tip_detail':
            if re.match(regex, item['title']):
                icon = item['left_tip']['icon']['icon_type']
                is_checked = icon == 'check'
                return (is_checked, item['title'])
    return None


def extract_ctor_object_with_index(ctor, regex):
    """
    Extracts first constructor object that contains
    text mathed by regular expression
    """
    for i, item in enumerate(ctor['items']):
        for _key, value in item.items():
            if isinstance(value, str) and re.match(regex, value):
                return item, i
    return None, None


def build_constraint_on_tags_config(
        constraint_name,
        violate_if,
        apply_if=None,
        should_freeze_timer=None,
        show_in_offer_screen=None,
        show_in_status_panel=None,
        use_ttl=None,
        apply_always_when_role=None,
):
    dct = {'violate_if': violate_if}
    if apply_if is not None:
        dct['apply_if'] = apply_if
    if should_freeze_timer is not None:
        dct['should_freeze_timer'] = should_freeze_timer
    if show_in_offer_screen is not None:
        dct['show_in_offer_screen'] = show_in_offer_screen
    if show_in_status_panel is not None:
        dct['show_in_status_panel'] = show_in_status_panel
    if use_ttl is not None:
        dct['use_ttl'] = use_ttl
    if apply_always_when_role is not None:
        dct['apply_always_when_role'] = apply_always_when_role
    return {constraint_name: dct}

import copy
import datetime

_NOW = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


def from_start(minutes: float):
    return (_NOW + datetime.timedelta(minutes=minutes)).isoformat()


def set_v2prepare_resp_discounts(v1_calc_creator, load_json):
    prepare_resp = load_json('v2_prepare.json')

    prepare_resp['cargocorp']['user']['additional_payloads'] = {
        'modifications_for_strikeout_price': {
            'for_fixed': [1, 2, 3],
            'for_taximeter': [4, 5, 6],
        },
    }

    v1_calc_creator.mock_prepare.categories = prepare_resp


def set_v2prepare_resp_combo(v2_calc_creator, load_json):
    prepare_resp = load_json('v2_prepare.json')

    prepare_resp['cargocorp']['user']['additional_prices']['combo_order'] = {
        'modifications': {'for_fixed': [1, 2, 3], 'for_taximeter': [4, 5, 6]},
        'price': {'total': 170.0},
        'meta': {},
    }

    prepare_resp['cargocorp']['user']['data']['combo_coeff'] = 0.5

    v2_calc_creator.mock_prepare.categories = prepare_resp


def set_v2recalc_resp_discounts(v1_calc_creator, coupon_value, discount_value):
    user_recalc_response = v1_calc_creator.mock_recalc.response['price'][
        'user'
    ]
    recalc_details = user_recalc_response['additional_payloads']['details']
    recalc_details['services'].append(
        {
            'name': 'coupon_value',
            'text': {
                'keyset': 'taximeter_driver_messages',
                'tanker_key': 'coupon_value',
            },
            'price': coupon_value,
        },
    )
    recalc_details['services'].append(
        {
            'name': 'discount_delta_raw',
            'text': {
                'keyset': 'taximeter_driver_messages',
                'tanker_key': 'discount_delta_raw',
            },
            'price': -discount_value,
        },
    )

    user_recalc_response['strikeout'] = 453
    user_recalc_response['meta']['coupon_value'] = coupon_value


def enable_coupon_and_discounts(v1_calc_creator, load_json):
    v1_calc_creator.payload['discounts_enabled'] = True
    v1_calc_creator.payload['calc_strikeout_price'] = True
    v1_calc_creator.payload['payment_info']['coupon'] = 'coupon212'
    set_v2prepare_resp_discounts(v1_calc_creator, load_json)
    set_v2recalc_resp_discounts(
        v1_calc_creator, coupon_value=153, discount_value=17,
    )


def get_default_calc_request():
    return {
        'price_for': 'client',
        'homezone': 'moscow',
        'payment_info': {'type': 'corp', 'method_id': 'corp-xxx'},
        'clients': [
            {'user_id': 'user_id', 'corp_client_id': 'corp_client_id'},
        ],
        'tariff_class': 'cargocorp',
        'taxi_requirements': {'door_to_door': True, 'cargo_type': 'van'},
        'waypoints': [
            {
                'claim_id': 'claim1',
                'id': 'waypoint1',
                'type': 'pickup',
                'position': [37.6489887, 55.5737046],
                'first_time_arrived_at': from_start(minutes=0),
                'resolution_info': {
                    'resolved_at': from_start(minutes=11),
                    'resolution': 'delivered',
                },
            },
            {
                'claim_id': 'claim1',
                'id': 'waypoint2',
                'type': 'dropoff',
                'position': [37.5447415, 55.9061769],
                'first_time_arrived_at': from_start(minutes=11.5),
                'resolution_info': {
                    'resolved_at': from_start(minutes=22),
                    'resolution': 'delivered',
                },
            },
            {
                'claim_id': 'claim1',
                'id': 'waypoint3',
                'type': 'return',
                'position': [37.6489887, 55.5737046],
                'first_time_arrived_at': from_start(minutes=22),
                'resolution_info': {
                    'resolved_at': from_start(minutes=23),
                    'resolution': 'delivered',
                },
            },
        ],
        'resolution_info': {
            'resolution': 'completed',
            'resolved_at': from_start(minutes=21),
        },
        'transport': 'auto',
        'is_usage_confirmed': False,
        'entity_id': 'claim1',
        'origin_uri': '/some/origin/uri',
        'calc_kind': 'final',
    }


def set_limit_paid_waiting(experiments3, value):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_pricing_paid_waiting_control',
        consumers=['cargo-pricing/v1/taxi/calc'],
        clauses=[],
        default_value=value,
    )


def fake_middle_point_count(user_options):
    return sum(
        [
            value
            for option_name, value in user_options.items()
            if option_name.startswith('fake_middle_point_')
        ],
    )


def discrete_overweight_count(user_options):
    return sum(
        [
            value
            for option_name, value in user_options.items()
            if option_name.startswith('discrete_overweight')
        ],
    )


async def calc_with_previous_calc_id(v1_calc_creator, prev_calc_id):
    second_payload = get_default_calc_request()
    second_payload['previous_calc_id'] = prev_calc_id

    v1_calc_creator.payload = second_payload
    second_response = await v1_calc_creator.execute()
    return second_response


def add_category_to_request(v2_calc_creator):
    v2_calc_creator.payload['calc_requests'].append(
        copy.deepcopy(v2_calc_creator.payload['calc_requests'][0]),
    )
    second_calc_req = v2_calc_creator.payload['calc_requests'][1]
    second_calc_req['tariff_class'] = 'courier'

    v2_calc_creator.mock_prepare.categories['courier'] = copy.deepcopy(
        v2_calc_creator.mock_prepare.categories['cargocorp'],
    )
    return second_calc_req


def get_recalc_request_user_options(v1_calc_creator):
    user_options = v1_calc_creator.mock_recalc.request['user']['trip_details'][
        'user_options'
    ]
    driver_options = v1_calc_creator.mock_recalc.request['driver'][
        'trip_details'
    ]['user_options']
    assert user_options == driver_options
    return driver_options


async def set_events_saving_by_calc_kind(
        experiments3, taxi_cargo_pricing, value,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_pricing_enable_events_saving_for_calc_kind',
        consumers=['cargo-pricing/processing_events_saving'],
        clauses=[],
        default_value=value,
    )
    await taxi_cargo_pricing.invalidate_caches()

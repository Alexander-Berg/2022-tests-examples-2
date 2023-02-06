import copy

from tests_superapp_misc.test_availability import consts


def build_payload(
        position=None,
        eats_available=True,
        grocery_available=True,
        empty_services=False,
        send_services=True,
        shortcuts=None,
        state=None,
        fields=None,
):
    payload = {'position': position or consts.DEFAULT_POSITION}
    if send_services:
        payload['services'] = (
            []
            if empty_services
            else [
                {'type': 'eats', 'is_available': eats_available},
                {'type': 'grocery', 'is_available': grocery_available},
            ]
        )

    if shortcuts is not None:
        payload.update({'shortcuts': shortcuts})
    if state is not None:
        payload.update({'state': state})
    if fields is not None:
        payload['fields'] = fields
    return payload


def build_exp_value(is_frauder=None, used_services=None, **kwargs):
    if used_services is None:
        used_services = {'eats': True, 'grocery': True}
    exp_service_value = {
        'priority': list(used_services),
        'services': {
            name: {'enabled': is_used, **kwargs}
            for name, is_used in used_services.items()
        },
    }

    result = {'main': exp_service_value, 'on_order': exp_service_value}
    if is_frauder is not None:
        result['is_frauder'] = is_frauder
    return result


def build_mode(mode, available, **kwargs):
    return {
        'mode': mode,
        'parameters': {'available': available, 'product_tag': mode, **kwargs},
    }


def build_product(product_name):
    return {
        'service': product_name,
        'tag': product_name,
        'title': product_name.title(),
    }


def taxi_ok_response(available=True, zone_name='moscow', geobase_city_id=None):
    response = copy.deepcopy(consts.EMPTY_RESPONSE)
    response['modes'].append(build_mode('taxi', available))
    response['products'].append(build_product('taxi'))
    if zone_name:
        response['zone_name'] = zone_name
    if geobase_city_id:
        response['geobase_city_id'] = geobase_city_id
    return response


def ok_response(eats_available=True, grocery_available=True):
    response = taxi_ok_response()
    response['modes'].append(build_mode('eats', eats_available))
    response['modes'].append(build_mode('grocery', grocery_available))
    response['products'].append(build_product('eats'))
    response['products'].append(build_product('grocery'))
    return response


def masstransit_ok_response(is_available=False):
    response = ok_response()
    response['modes'].append(build_mode('masstransit', is_available))
    response['products'].append(build_product('masstransit'))
    return response


def drive_ok_response(
        is_available=False, is_registered=False, show_disabled=False,
):
    response = ok_response()
    drive_params = {
        'product_tag': 'drive',
        'available': is_available,
        'is_registered': is_registered,
    }
    if show_disabled:
        drive_params['show_disabled'] = True

    response['modes'].append({'mode': 'drive', 'parameters': drive_params})
    response['products'].append(build_product('drive'))

    return response


def market_ok_response(
        is_available=False,
        is_registered=False,
        show_disabled=False,
        deathflag=False,
):
    response = ok_response()
    market_params = {'product_tag': 'market', 'available': is_available}
    if show_disabled:
        market_params['show_disabled'] = True
    if deathflag:
        market_params['deathflag'] = True

    response['modes'].append({'mode': 'market', 'parameters': market_params})
    response['products'].append(build_product('market'))

    return response


def get_drive_offer_answer(
        is_available=False, is_registered=False, reason_code=None,
):
    response = {'app_link': 'app-link', 'offers': [], 'cars': [], 'views': []}
    if is_available:
        response['is_service_available'] = True
    if is_registered:
        response['is_registred'] = True
    if reason_code:
        response['reason_code'] = reason_code
    return response


def build_state(field_point_b=None):
    state = {
        'known_orders_info': [
            {
                'orderid': '123',
                'service': 'taxi',
                'waypoints': [
                    {'type': 'A', 'position': consts.DEFAULT_POSITION},
                    {'type': 'B', 'position': consts.ADDITIONAL_POSITION},
                ],
            },
        ],
    }

    if field_point_b is not None:
        state['fields'] = [{'type': 'b', 'position': field_point_b, 'log': ''}]

    return state


def add_exp_multipoint(experiments3, enabled):
    experiments3.add_experiment(
        clauses=[
            {
                'title': 'main clause',
                'value': {'enabled': enabled},
                'predicate': {'type': 'true'},
            },
        ],
        name='superapp_multipoint_availability',
        consumers=['superapp-misc/availability'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )


def is_equal_position(request, pos):
    return [float(request['longitude']), float(request['latitude'])] == pos

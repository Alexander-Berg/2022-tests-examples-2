DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


def find_action(json, action_type):
    for action in json['current_point']['actions']:
        if action['type'] == action_type:
            return action
    return None


async def call_and_check_robocall(
        taxi_cargo_orders, my_waybill_info, default_order_id,
):
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert find_action(response.json(), 'robocall') is not None

    response = await taxi_cargo_orders.post(
        '/internal/cargo-orders/v1/robocall/actions',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'auth_params': {
                'driver_profile_id': 'driver_id1',
                'park_id': 'park_id1',
                'version': '9.40',
                'platform': 'android',
                'version_type': '',
                'brand': 'yandex',
            },
        },
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json() is not None

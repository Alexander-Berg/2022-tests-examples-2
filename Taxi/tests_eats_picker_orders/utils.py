import datetime

import pytest


COMMUNICATION_POLICIES = ['by_phone', 'in_app']
NOT_FOUND_ITEM_POLICIES = ['propose_replacement', 'skip_item']


def to_string(whatever):
    if whatever is None:
        return None
    if isinstance(whatever, datetime.datetime):
        return whatever.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return str(whatever)


def da_headers(picker_id=None):
    headers = {
        'Accept-Language': 'en',
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'XYPro',
        'X-Request-Application-Version': '9.99 (9999)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'ios',
    }
    if picker_id:
        headers['X-YaEda-CourierId'] = picker_id
    return headers


def parse_datetime(date_string):
    """Необходимо для парсинга дробной части секунд,
    не дополненной нулями справа"""
    return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f%z')


def check_updated_item_measure(
        db_item, measure_value, quantity, price, quantum=0.75,
):
    assert db_item['measure_value'] == measure_value, [
        f'{db_item["measure_value"]} != {measure_value}',
        dict(db_item),
    ]
    assert db_item['quantity'] == quantity
    if db_item['measure_quantum'] is not None:
        assert db_item['measure_quantum'] == int(quantum * measure_value), [
            quantum,
            measure_value,
            dict(db_item),
        ]
        assert db_item['price'] == price, [price, dict(db_item)]
        assert float(db_item['quantum_price']) == round(price * quantum, 2), [
            price,
            quantum,
            dict(db_item),
        ]
        assert db_item['absolute_quantity'] == int(quantity * measure_value), [
            quantity,
            measure_value,
            dict(db_item),
        ]
        # т. к. у quantum_quantity одинарная точность,
        # непосредственное сравнение тут не подходит
        assert (
            abs(1 - db_item['quantum_quantity'] * quantum / quantity) < 1e-5
        ), [db_item['quantum_quantity'], quantum, quantity]
    else:
        assert db_item['measure_quantum'] is None
        assert db_item['quantum_price'] is None
        assert db_item['price'] == price, [price, dict(db_item)]
        assert db_item['absolute_quantity'] is None
        assert db_item['quantum_quantity'] is None


def check_picked_item_position(actual_position, expected_position):
    assert actual_position['count'] == expected_position['count']
    assert actual_position['weight'] == expected_position['weight']
    if 'barcode' in expected_position:
        assert actual_position['barcode'] == expected_position['barcode']
    if 'mark' in expected_position:
        assert actual_position['mark'] == expected_position['mark']


def check_picked_item(actual_item, actual_positions, expected_item):
    assert actual_item['cart_version'] == expected_item['cart_version']
    assert actual_item['order_item_id'] == expected_item['order_item_id']
    assert actual_item['picker_id'] == expected_item['picker_id']
    if 'weight' in expected_item:
        assert actual_item['weight'] == expected_item['weight']
    if 'count' in expected_item:
        assert actual_item['count'] == expected_item['count']
    expected_positions = expected_item['positions']
    assert len(actual_positions) == len(expected_positions)
    for actual_position, expected_position in zip(
            actual_positions, expected_positions,
    ):
        check_picked_item_position(actual_position, expected_position)


def polling_delay_config():
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_picker_orders_polling_delay',
        consumers=['eats-picker-orders/polling-delay'],
        clauses=[],
        default_value={
            'get_order_status': 5,
            'get_order': 60,
            'get_picker_orders': 30,
            'get_picker_orders_history': 120,
            'get_x_polling_config': (
                'picking=45s,auto_handle=3s,manual_handle=20s'
            ),
        },
    )


def compare_db_with_expected_data(db_data, expected_data):
    for key, value in expected_data.items():
        if isinstance(db_data[key], datetime.datetime) and not isinstance(
                value, datetime.datetime,
        ):
            assert (
                db_data[key].isoformat() == value
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'
        else:
            assert (
                db_data[key] == value
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'


def make_headers(picker_id, measure_version=None):
    headers = da_headers(picker_id)
    if picker_id is not None:
        headers['X-YaEda-CourierId'] = picker_id
    if measure_version is not None:
        headers['X-Measure-Version'] = measure_version
    return headers


def cargo_info_synchronizer_config(
        period_seconds=10, auto_complete_delay=10, claim_info_batch_size=10,
):
    return pytest.mark.experiments3(
        name='eats_picker_orders_cargo_info_synchronizer',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-picker-orders/cargo-info-synchronizer'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={
            'period_seconds': period_seconds,
            'auto_complete_delay': auto_complete_delay,
            'claim_info_batch_size': claim_info_batch_size,
        },
    )


def update_order_talks_config(batch_size=500, batch_delay=0):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_update_order_talks',
        consumers=['eats-picker-orders/update-order-talks'],
        default_value={'batch_size': batch_size, 'batch_delay': batch_delay},
    )


def upload_not_picked_items_config(enabled=True):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_upload_not_picked_items',
        consumers=['eats-picker-orders/upload-not-picked-items'],
        default_value={'enabled': enabled},
    )


def use_postprocessing_config(enabled=False):
    return pytest.mark.experiments3(
        is_config=False,
        name='eats_picker_orders_use_postprocessing',
        consumers=['eats-picker-orders/use-postprocessing'],
        default_value={'enabled': enabled},
    )


# pylint: disable=invalid-name
def update_prices_and_availability_experiment(
        update_prices=False, update_availability=False,
):
    return pytest.mark.experiments3(
        is_config=False,
        name='eats_picker_orders_update_prices_and_availability',
        consumers=['eats-picker-orders/update-prices-and-availability'],
        default_value={
            'update_prices': update_prices,
            'update_availability': update_availability,
        },
    )


def zero_limit_on_picking_start_experiment(enabled=False):
    return pytest.mark.experiments3(
        is_config=False,
        name='eats_picker_orders_zero_limit_on_picking_start',
        consumers=['eats-picker-orders/zero-limit-on-picking-start'],
        default_value={'enabled': enabled},
    )


def autostart_picking_config(
        enabled: bool = True,
        delay: int = 10,
        stq_retries: int = 3,
        stq_timeout: int = 10,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_autostart_picking',
        consumers=['eats-picker-orders/autostart-picking'],
        default_value={
            'enabled': enabled,
            'delay': delay,
            'stq_retries': stq_retries,
            'stq_timeout': stq_timeout,
        },
    )


def send_order_events_config(enabled: bool = True):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_send_order_events',
        consumers=['eats-picker-orders/send-order-events'],
        default_value={'enabled': enabled},
    )


def update_phone_forwarding_config(
        stq_retries: int = 3, stq_timeout: int = 10,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_update_phone_forwarding',
        consumers=['eats-picker-orders/update-phone-forwarding'],
        default_value={'stq_retries': stq_retries, 'stq_timeout': stq_timeout},
    )


def metro_soft_check_config(
        enabled: bool = True, items_search_tasks_count: int = 5,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_metro_soft_check',
        consumers=['eats-picker-orders/metro-soft-check'],
        default_value={
            'enabled': enabled,
            'items_search_tasks_count': items_search_tasks_count,
        },
    )


def allowed_phone_forwardings(requester_type, callee_type):
    return {
        'name': 'eats_picker_orders_allowed_phone_forwardings',
        'consumers': ['eats-picker-orders/allowed-phone-forwardings'],
        'clauses': [
            {
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': requester_type,
                                    'arg_name': 'requester_type',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'value': callee_type,
                                    'arg_name': 'callee_type',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
                'value': {
                    'empty_requester_phone_id_allowed': True,
                    'phone_forwarding_allowed': True,
                },
            },
        ],
        'default_value': {
            'phone_forwarding_allowed': False,
            'empty_requester_phone_id_allowed': False,
        },
    }


def globus_soft_check_config(
        enabled: bool = False,
        soft_check_enabled: bool = False,
        retries: int = 3,
        lock_fake_eats_id: str = 'globus-fake-eats-id',
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_globus_soft_check',
        consumers=['eats-picker-orders/globus-soft-check'],
        default_value={
            'enabled': enabled,
            'soft_check_enabled': soft_check_enabled,
            'retries': retries,
            'timeout': 200,
            'guid_length': 6,
            'lock_fake_eats_id': lock_fake_eats_id,
            'calculation_subjects': {
                'do_not_require_marks': 1,
                'require_marks': 33,
            },
        },
    )


def picked_item_positions_config(require_positions=False):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_picked_item_positions',
        consumers=['eats-picker-orders/picked-item-positions'],
        default_value={'require_positions': require_positions},
    )


def marking_types_config():
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_orders_marking_types',
        consumers=['eats-picker-orders/marking-types'],
        clauses=[
            {
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': ['marked_milk'],
                                    'arg_name': 'marking_type',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                        ],
                    },
                },
                'value': {'require_marks': True},
            },
        ],
        default_value={'require_marks': False},
    )


def soft_check_quantity_fix_experiment(enabled=False):
    return pytest.mark.experiments3(
        is_config=False,
        name='eats_picker_orders_soft_check_quantity_fix',
        consumers=['eats-picker-orders/soft-check-quantity-fix'],
        default_value={'enabled': enabled},
    )

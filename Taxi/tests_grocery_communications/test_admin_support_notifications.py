import functools

from tests_grocery_communications import configs


def _compare_notification_parameters(lhs, rhs):
    if lhs['key'] < rhs['key']:
        return -1
    if lhs['key'] > rhs['key']:
        return 1
    if lhs['translation'] < rhs['translation']:
        return -1
    if lhs['translation'] > rhs['translation']:
        return 1
    return 0


def _compare_responses(response, reference):
    lhs = response['support_notifications'][0]
    rhs = reference['support_notifications'][0]
    assert lhs['support_description'] == rhs['support_description']
    lhs_parameters_sorted = sorted(
        lhs['notification_parameters'],
        key=functools.cmp_to_key(_compare_notification_parameters),
    )
    rhs_parameters_sorted = sorted(
        rhs['notification_parameters'],
        key=functools.cmp_to_key(_compare_notification_parameters),
    )
    assert lhs_parameters_sorted == rhs_parameters_sorted
    assert lhs['tanker_key'] == rhs['tanker_key']


@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
async def test_basic(taxi_grocery_communications, grocery_orders):
    request = {'order_id': '123'}
    grocery_orders.add_order(order_id='123', locale='ru')
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/notifications',
        headers={'Accept-Language': 'en'},
        json=request,
    )
    assert response.status_code == 200
    resp = response.json()
    reference = {
        'support_notifications': [
            {
                'support_description': 'Hello message',
                'notification_parameters': [
                    {'key': 'client_name', 'translation': 'Client name'},
                    {
                        'key': 'discount',
                        'translation': 'Discount size in percent',
                    },
                    {'key': 'promocode', 'translation': 'Promocode'},
                ],
                'tanker_key': 'support_test_notification',
            },
            {
                'support_description': 'Test support description',
                'notification_parameters': [
                    {'key': 'arg1', 'translation': 'Parameter 1'},
                    {'key': 'arg2', 'translation': 'Parameter 2'},
                ],
                'tanker_key': 'test_tanker_key',
            },
        ],
    }
    _compare_responses(resp, reference)


async def test_order_not_found(taxi_grocery_communications, grocery_orders):
    request = {'order_id': '123'}
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/notifications',
        headers={'Accept-Language': 'en'},
        json=request,
    )
    assert response.status_code == 404


async def test_no_available_notifications(
        taxi_grocery_communications, grocery_orders,
):
    request = {'order_id': '123'}
    grocery_orders.add_order(order_id='123', locale='ru')
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/notifications',
        headers={'Accept-Language': 'en'},
        json=request,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {'support_notifications': []}

import datetime

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_feedback_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='fleet_parks_service', autouse=True)
def _fleet_parks_service(mockserver):
    class FleetParksContext:
        def __init__(self):
            self.response_template = {
                'orders': {'shard_number': 0, 'table_name': 'MOCK_TABLE_NAME'},
                'payments': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
                'transactions': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
                'payments_agg': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
                'changes': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
                'feedbacks': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
                'passengers': {
                    'shard_number': 0,
                    'table_name': 'MOCK_TABLE_NAME',
                },
            }

        def set_feedbacks_data(self, shard_number, table_name):
            self.response_template['feedbacks']['shard_number'] = shard_number
            self.response_template['feedbacks']['table_name'] = table_name

    context = FleetParksContext()
    context.set_feedbacks_data(0, 'feedbacks_0')

    @mockserver.json_handler('/fleet-parks/v1/shard/info')
    def _shard_info_handler(request):
        return context.response_template

    return context


@pytest.fixture(name='driver_orders', autouse=True)
def _driver_orders(mockserver):
    class DriverOrdersContext:
        def __init__(self):
            booked_at = datetime.datetime.now() - datetime.timedelta(days=5)
            ended_at = booked_at + datetime.timedelta(hours=1)
            self.response_template = {
                'orders': [
                    {
                        'id': 'order_id_1',
                        'order': {
                            'short_id': 1,
                            'driver_profile_id': 'DriverId',
                            'status': 'complete',
                            'booked_at': booked_at.strftime(
                                '%Y-%m-%dT%H:%M:%S.%f+00:00',
                            ),
                            'created_at': booked_at.strftime(
                                '%Y-%m-%dT%H:%M:%S.%f+00:00',
                            ),
                            'provider': 'partner',
                            'payment_method': 'cash',
                            'ended_at': ended_at.strftime(
                                '%Y-%m-%dT%H:%M:%S.%f+00:00',
                            ),
                        },
                    },
                ],
            }

        def set_order_params(self, order_id, params):
            order = next(
                (
                    order
                    for order in self.response_template['orders']
                    if order['id'] == order_id
                ),
                None,
            )
            if order:
                order['order'].update(params)

    context = DriverOrdersContext()

    @mockserver.json_handler('driver-orders/v1/parks/orders/bulk_retrieve')
    def _order_info_handler(request):
        return context.response_template

    return context


@pytest.fixture(name='order_core', autouse=True)
def _order_core(mockserver, load_json):
    @mockserver.json_handler('order-core/v1/tc/order-fields')
    def _order_info_handler(request):
        return load_json('order_core.json')

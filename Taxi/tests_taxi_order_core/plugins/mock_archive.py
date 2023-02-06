import copy
import datetime
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.fixture(name='archive')
def _archive(order_archive_mock):
    def merge(source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                merge(value, node)
            else:
                destination[key] = value
        return destination

    class ArchiveContext:
        STATIC_ORDER_PROC = {
            '_id': 'default_order_id',
            'updated': datetime.datetime(2019, 1, 29, 0, 0, 0, 0),
            'order': {
                '_id': 'default_order_id',
                'status': 'pending',
                'nz': 'moscow',
                'user_id': 'default_user_id',
                'experiments': [],
                'excluded_parks': [],
                'request': {
                    'due': datetime.datetime(2019, 3, 18, 0, 0, 0, 0),
                    'requirements': {
                        'childchair_moscow': 7,
                        'animaltransport': True,
                        'creditcard': True,
                        'passengers_count': 1,
                        'capacity': [1],
                        'cargo_loaders': [1, 1],
                    },
                    'class': ['econom'],
                    'source': {'geopoint': [11.111111, 22.222222]},
                    'destinations': [{'geopoint': [33.333333, 44.444444]}],
                    'payment': {'type': 'cash', 'payment_method_id': None},
                },
            },
        }

        def __init__(self):
            self.order_procs = {}
            self.expected_api_key = 'archive-key'

        def set_order_proc_patches(self, order_procs):
            self.order_procs = {}
            for proc in order_procs:
                proc_object = merge(
                    proc, copy.deepcopy(ArchiveContext.STATIC_ORDER_PROC),
                )
                order_archive_mock.set_order_proc(proc_object)

        def set_api_key(self, key):
            self.expected_api_key = key

    context = ArchiveContext()
    context.set_order_proc_patches([{}])

    return context


@pytest.fixture(name='archive_api')
def _archive_api(mongodb, mockserver, now):
    yt_order_proc_data = {}

    class Mock:
        def __init__(self):
            self.order_proc_restore = _order_proc_restore
            self.orders_restore = _orders_restore

        @staticmethod
        def set_order_proc(order_proc_list):
            if isinstance(order_proc_list, dict):
                order_proc_list = [order_proc_list]
            for order_proc in order_proc_list:
                try:
                    yt_order_proc_data[order_proc['_id']] = order_proc
                except KeyError:
                    raise RuntimeError(
                        f'Invalid order_proc without _id: {order_proc}',
                    )

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def _order_proc_restore(request):
        logger.debug('Handled %s', str(request))
        order_id = request.json['id']
        update = request.json.get('update', False)

        if mongodb.order_proc.find_one({'_id': order_id}):
            if update:
                mongodb.order_proc.update(
                    {'_id': order_id}, {'$set', {'updated': now}},
                )
                return [{'id': order_id, 'status': 'updated'}]
            return [{'id': order_id, 'status': 'mongo'}]

        if order_id in yt_order_proc_data:
            proc = {'updated': now}
            proc.update(yt_order_proc_data[order_id])
            mongodb.order_proc.insert(proc)
            return [{'id': order_id, 'status': 'restored'}]
        return [{'id': order_id, 'status': 'not_found'}]

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    async def _orders_restore(request):
        order_id = request.json['id']
        if order_id in yt_order_proc_data:
            return [{'id': order_id, 'status': 'restored'}]
        return [{'id': order_id, 'status': 'not_found'}]

    return Mock()

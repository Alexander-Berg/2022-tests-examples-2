import copy
import datetime

import pytest


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
            '_id': 'example_order_id',
            'order': {
                '_id': 'example_order_id',
                'created': datetime.datetime(2019, 3, 17, 0, 0, 0, 0),
                'status': 'pending',
                'nz': 'moscow',
                'user_id': 'sample_user_id',
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
                    'class': ['vip', 'econom'],
                    'source': {'geopoint': [11.111111, 22.222222]},
                    'destinations': [{'geopoint': [33.333333, 44.444444]}],
                },
                'virtual_tariffs': [
                    {
                        'class': 'econom',
                        'special_requirements': [{'id': 'food_delivery'}],
                    },
                ],
            },
        }

        def __init__(self):
            self.order_procs = {}
            self.expected_api_key = 'archive-key'

        def set_order_procs(self, order_procs):
            self.order_procs = {}
            for proc in order_procs:
                proc_object = merge(
                    proc, copy.deepcopy(ArchiveContext.STATIC_ORDER_PROC),
                )
                order_archive_mock.set_order_proc(proc_object)

        def set_api_key(self, key):
            self.expected_api_key = key

    context = ArchiveContext()
    context.set_order_procs([{}])

    return context

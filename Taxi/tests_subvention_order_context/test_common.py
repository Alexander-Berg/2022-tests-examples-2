import copy
import datetime
import functools


DEFAULT_CONTEXT_DATA = {
    'order_id': 'order_id',
    'dbid_uuid': 'dbid_uuid',
    'updated': datetime.datetime(2020, 1, 1, 12, 0),
    'value': {
        'driver_point': [37.5, 55.7],
        'activity_points': 91,
        'subvention_geoareas': ['geoarea1'],
        'branding': {'has_sticker': False, 'has_lightbox': False},
        'tags': ['tag1', 'tag2'],
        'virtual_tags': ['virtual_tag1'],
        'tariff_class': 'econom',
        'tariff_zone': 'moscow',
        'geonodes': 'br_root/br_russia/br_moscow/moscow',
        'time_zone': 'Europe/Moscow',
        'unique_driver_id': 'unique_driver_id',
        'ref_time': datetime.datetime(2020, 1, 1, 12, 0),
    },
}

DEFAULT_KWARGS = {
    'order_id': 'order_id',
    'dbid': 'dbid',
    'uuid': 'uuid',
    'driver_points': 91,
    'driver_point': [37.5, 55.7],
    'nz': 'moscow',
    'tariff_class': 'econom',
    'driving_at': '2020-01-01T11:59:00+0000',
    'tags': ['tag1', 'tag2', 'tag3'],
    'branding': {'has_lightbox': False, 'has_sticker': False},
}


def fetcher_test(field_name):
    def decorator(test_func):
        @functools.wraps(test_func)
        async def decorated(mongodb, *args, **kwargs):
            context_data = copy.deepcopy(DEFAULT_CONTEXT_DATA)
            del context_data['value'][field_name]
            mongodb.subvention_order_context.insert_one(context_data)
            await test_func(*args, **kwargs, mongodb=mongodb)

        return decorated

    return decorator

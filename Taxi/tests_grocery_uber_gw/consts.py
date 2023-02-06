from tests_grocery_uber_gw import models

DEFAULT_STORES = {
    '00000000-0000-0000-0000-000000000001': models.Store(
        store_id='00000000-0000-0000-0000-000000000001',
    ),
    '00000000-0000-0000-0000-000000000002': models.Store(
        store_id='00000000-0000-0000-0000-000000000002',
    ),
    '00000000-0000-0000-0000-000000000003': models.Store(
        store_id='00000000-0000-0000-0000-000000000003',
    ),
    '00000000-0000-0000-0000-000000000004': models.Store(
        store_id='00000000-0000-0000-0000-000000000004',
    ),
    '00000000-0000-0000-0000-000000000005': models.Store(
        store_id='00000000-0000-0000-0000-000000000005',
    ),
}

DEFAULT_ORDERS = {
    '00000000-0000-0000-0000-000000000001': models.Order(
        order_id='00000000-0000-0000-0000-000000000001',
    ),
    '00000000-0000-0000-0000-000000000002': models.Order(
        order_id='00000000-0000-0000-0000-000000000002',
    ),
}

DEFAULT_MENUS = {
    '00000000-0000-0000-0000-000000000001': models.Menu(
        store_id='00000000-0000-0000-0000-000000000001',
    ),
}

STATUS_MAPPING = {
    'started': ['delivering'],
    'arriving': [],  # TODO
    'delivered': ['closed'],
    'skip_processing': [  # list of unprocessed statuses (no mapping for uber)
        'draft',
        'checked_out',
        'reserving',
        'reserved',
        'assembling',
        'assembled',
    ],
}

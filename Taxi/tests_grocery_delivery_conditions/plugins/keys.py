DEFAULT_LEGACY_DEPOT_ID = '123'
DEFAULT_WMS_DEPOT_ID = 'wms_depot_id'
DEFAULT_DEPOT_LOCATION = {'lon': 37.61, 'lat': 55.75}

DEFAULT_DELIVERY_CONDITIONS = {
    'timetable': [{'to': '00:00', 'from': '00:00', 'day_type': 'everyday'}],
    'payload': {
        'surge': False,
        'max_eta_minutes': '25',
        'min_eta_minutes': '15',
        'delivery_conditions': [
            {'order_cost': '10', 'delivery_cost': '0'},
            {'order_cost': '0', 'delivery_cost': '7'},
        ],
    },
}

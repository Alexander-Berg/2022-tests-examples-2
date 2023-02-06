from __future__ import absolute_import

import atlas.service_utils.map as map_utils

data_single_filters = {
    'tl': [55.9034512224878, 37.24529117345811],
    'br': [55.59479009164081, 37.85915225744248],
    'city': 'Москва',
    'filter_operation': 'or',
    'driver_statuses': ['free'],
    'tx_statuses': ['free'],
    'car_classes': ['pool']
}

data_multiple_filters = {
    'tl': [55.9034512224878, 37.24529117345811],
    'br': [55.59479009164081, 37.85915225744248],
    'city': 'Москва',
    'filter_operation': 'or',
    'driver_statuses': ['free', 'verybusy'],
    'tx_statuses': ['free', 'order_free'],
    'car_classes': ['pool', 'business', 'drivers_pool', 'child_tariff', 'vip']
}

data_without_filters = {
    'tl': [55.9034512224878, 37.24529117345811],
    'br': [55.59479009164081, 37.85915225744248],
    'city': 'Москва',
    'filter_operation': 'or'
}


class TestGetAtlasDriversFilter:
    def test_get_filter(self):
        assert map_utils.get_atlas_drivers_filter(data_single_filters) == \
        {
            'search_area': {'top_left': {'lat': 55.9034512224878, 'lon': 37.24529117345811},
                            'bottom_right': {'lat': 55.59479009164081, 'lon': 37.85915225744248}},
            'filter': {
                '$and': [
                    {'car_classes.actual': {
                        '$any': ['pool']}
                    },
                    {'statuses.driver': 'free'},
                    {'statuses.taximeter': 'free'}]
            }
        }
        assert map_utils.get_atlas_drivers_filter(data_multiple_filters) == \
        {
            'search_area': {'top_left': {'lat': 55.9034512224878, 'lon': 37.24529117345811},
                            'bottom_right': {'lat': 55.59479009164081, 'lon': 37.85915225744248}},
            'filter': {
                '$and': [
                    {'car_classes.actual': {
                        '$any': ['pool', 'business', 'drivers_pool', 'child_tariff', 'vip']}
                    },
                    {'$or': [{'statuses.driver': 'free'}, {'statuses.driver': 'verybusy'}]},
                    {'$or': [{'statuses.taximeter': 'free'}, {'statuses.taximeter': 'order_free'}]}
                ]
            }
        }

        assert map_utils.get_atlas_drivers_filter(data_without_filters) == \
        {
            'search_area': {'top_left': {'lat': 55.9034512224878, 'lon': 37.24529117345811},
                            'bottom_right': {'lat': 55.59479009164081, 'lon': 37.85915225744248}}
        }
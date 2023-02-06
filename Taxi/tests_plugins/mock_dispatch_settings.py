import pytest


@pytest.fixture(autouse=True)
def taxi_dispatch_settings(mockserver):
    @mockserver.json_handler('/dispatch_settings/v2/categories/fetch')
    def _mock_category_fetch(_):
        return {
            'categories': [
                {'zone_name': '__default__', 'tariff_names': ['__default__']},
            ],
            'groups': [],
        }

    @mockserver.json_handler('/dispatch_settings/v1/settings/fetch')
    def mock_dispatch_settings(request):
        return {
            'settings': [
                {
                    'zone_name': '__default__',
                    'tariff_name': '__default__',
                    'parameters': [
                        {
                            'values': {
                                'AIRPORT_QUEUE_DISPATCH_BONUS_MAX': 0,
                                'AIRPORT_QUEUE_DISPATCH_BONUS_MIN': 0,
                                'AIRPORT_QUEUE_DISPATCH_BONUS_STEP': 0,
                                'ANTISURGE_BONUS_COEF': 3,
                                'ANTISURGE_BONUS_GAP': 0,
                                'APPLY_ETA_ETR_IN_CAR_RANGING': True,
                                'DISPATCH_DRIVER_TAGS_BLOCK': ['COMFORTblock'],
                                'DISPATCH_DRIVER_TAGS_BONUSES': {
                                    '__default__': 0,
                                    'qa': 4,
                                },
                                'DISPATCH_GRADE_BONUS_SECONDS': {
                                    '2': 123,
                                    '__default__': 0,
                                },
                                'DISPATCH_HOME_BONUS_SECONDS': 0,
                                'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {
                                    '__default__': 0,
                                },
                                'DISPATCH_REPOSITION_BONUS': {
                                    '__default__': 0,
                                },
                                'DYNAMIC_DISTANCE_A': 0.5,
                                'DYNAMIC_DISTANCE_B': 100,
                                'DYNAMIC_TIME_A': 0.5,
                                'DYNAMIC_TIME_B': 27,
                                'E_ETA': 0,
                                'E_ETR': 0,
                                'K_ETR': 0,
                                'MAX_ROBOT_DISTANCE': 8000,
                                'MAX_ROBOT_TIME': 720,
                                'MAX_ROBOT_TIME_SCORE_ENABLED': False,
                                'MIN_URGENCY': 180,
                                'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
                                'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
                                'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
                                'SURGE_BONUS_COEF': 1,
                                'WAVE_THICKNESS_MINUTES': 2,
                                'WAVE_THICKNESS_SECONDS': 120,
                                'ORDER_CHAIN_MAX_LINE_DISTANCE': 3000,
                                'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 4000,
                                'ORDER_CHAIN_MAX_ROUTE_TIME': 300,
                                'ORDER_CHAIN_MIN_TAXIMETER_VERSION': '8.06',
                                'PAX_EXCHANGE_TIME': 1,
                                'QUERY_LIMIT_FREE_PREFERRED': 10,
                                'QUERY_LIMIT_LIMIT': 20,
                                'QUERY_LIMIT_MAX_LINE_DIST': 10000,
                            },
                        },
                    ],
                },
                {
                    'zone_name': 'test_zone_1',
                    'tariff_name': 'test_tariff_2',
                    'parameters': [
                        {
                            'values': {
                                'AIRPORT_QUEUE_DISPATCH_BONUS_MAX': 100,
                                'AIRPORT_QUEUE_DISPATCH_BONUS_MIN': 20,
                                'AIRPORT_QUEUE_DISPATCH_BONUS_STEP': 10,
                                'ANTISURGE_BONUS_COEF': 13,
                                'ANTISURGE_BONUS_GAP': 10,
                                'APPLY_ETA_ETR_IN_CAR_RANGING': True,
                                'DISPATCH_DRIVER_TAGS_BLOCK': ['COMFORTblock'],
                                'DISPATCH_DRIVER_TAGS_BONUSES': {
                                    '__default__': 0,
                                    'qa': 4,
                                },
                                'DISPATCH_GRADE_BONUS_SECONDS': {
                                    '2': 123,
                                    '__default__': 0,
                                },
                                'DISPATCH_HOME_BONUS_SECONDS': 0,
                                'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {
                                    '__default__': 0,
                                },
                                'DISPATCH_REPOSITION_BONUS': {
                                    '__default__': 0,
                                },
                                'DYNAMIC_DISTANCE_A': 1.5,
                                'DYNAMIC_DISTANCE_B': 200,
                                'DYNAMIC_TIME_A': 1.5,
                                'DYNAMIC_TIME_B': 127,
                                'E_ETA': 1,
                                'E_ETR': 2,
                                'K_ETR': 3,
                                'MAX_ROBOT_DISTANCE': 9000,
                                'MAX_ROBOT_TIME': 200,
                                'MAX_ROBOT_TIME_SCORE_ENABLED': False,
                                'MIN_URGENCY': 280,
                                'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 1,
                                'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 2,
                                'NEW_DRIVER_BONUS_VALUE_SECONDS': 3,
                                'SURGE_BONUS_COEF': 4,
                                'WAVE_THICKNESS_MINUTES': 5,
                                'WAVE_THICKNESS_SECONDS': 620,
                                'ORDER_CHAIN_MAX_LINE_DISTANCE': 7000,
                                'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 8000,
                                'ORDER_CHAIN_MAX_ROUTE_TIME': 900,
                                'ORDER_CHAIN_MIN_TAXIMETER_VERSION': '18.06',
                                'PAX_EXCHANGE_TIME': 2,
                                'QUERY_LIMIT_FREE_PREFERRED': 40,
                                'QUERY_LIMIT_LIMIT': 50,
                                'QUERY_LIMIT_MAX_LINE_DIST': 20000,
                            },
                        },
                    ],
                },
            ],
        }

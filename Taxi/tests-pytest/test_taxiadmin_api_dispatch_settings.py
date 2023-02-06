from __future__ import unicode_literals

import json
import pytest

from django import test as django_test

from taxi.core import async


SEARCH_SETTINGS_CLASSES_DEFAULT = {
    'DYNAMIC_TIME_B': 1,
    'MAX_ROBOT_DISTANCE': 5000,
    'DYNAMIC_TIME_A': 0.66,
    'WAVE_THICKNESS_MINUTES': 2,
    'DYNAMIC_DISTANCE_A': 0.66,
    'DYNAMIC_DISTANCE_B': 1,
    'MIN_URGENCY': 240,
    'MAX_ROBOT_TIME': 480,
    'K_ETR': 0.0,
    'E_ETA': 0.0,
    'E_ETR': 0.0,
    'APPLY_ETA_ETR_IN_CAR_RANGING': False,
    'WAVE_THICKNESS_SECONDS': 120,
    'SURGE_BONUS_COEF': 0,
    'ANTISURGE_BONUS_COEF': 0,
    'ANTISURGE_BONUS_GAP': 0,
    'DISPATCH_GRADE_BONUS_SECONDS': {
        '__default__': 0
    },
    'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {
        '__default__': 0
    },
    'DISPATCH_HOME_BONUS_SECONDS': 0,
    'DISPATCH_REPOSITION_BONUS': {
        '__default__': 0
    },
    'DISPATCH_DRIVER_TAGS_BONUSES': {
        '__default__': 0
    },
    'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
    'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
    'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
    'AIRPORT_QUEUE_DISPATCH_BONUS_MIN': 0,
    'AIRPORT_QUEUE_DISPATCH_BONUS_STEP': 0,
    'AIRPORT_QUEUE_DISPATCH_BONUS_MAX': 0,
    'MAX_ROBOT_TIME_SCORE_ENABLED': False,
    'MAX_ROBOT_TIME_SCORE': 10000,
}


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_configured_dispatch_zones():
    url = '/api/dispatch_zones/list/'
    response = yield django_test.Client().get(url)
    assert 200 == response.status_code
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_dispatch_zones_get_settings(zone):
    url = '/api/dispatch_zones/get_settings/?zone=' + zone
    response = yield django_test.Client().get(url)
    assert 200 == response.status_code
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_dispatch_zones_set_settings(data):
    url = '/api/dispatch_zones/set_settings/'
    response = yield django_test.Client().post(url, json.dumps({'dispatch_config_updates': data}),
                                               content_type='application/json')
    assert 200 == response.status_code
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_dispatch_zones_delete_settings(zone):
    url = '/api/dispatch_zones/delete_settings/'
    response = yield django_test.Client().post(url, json.dumps({'zone': zone}), content_type='application/json')
    assert 200 == response.status_code
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_empty_dispatch_zones():
    expected_response = {'zones': []}
    response = yield _request_configured_dispatch_zones()
    assert expected_response == response


@pytest.mark.config(
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
        'almaty': {
            '__default__': {
                'MIN_URGENCY': 500,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_one_dispatch_zone():
    expected_response = {'zones': ['almaty']}
    response = yield _request_configured_dispatch_zones()
    assert expected_response == response


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT
        },
        'dedovsk': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
        'zelenograd': {
            '__default__': {
                'MIN_URGENCY': 500,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        },
        'baku': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 9000,
            },
        },
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        },
        'astana': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3500,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        },
    },
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_multiple_dispatch_zone():
    expected_response = {'zones': ['astana', 'baku', 'dedovsk', 'zelenograd']}
    response = yield _request_configured_dispatch_zones()
    assert expected_response == response


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        }
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        }
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_invalid_get_dispatch_zone_setting():
    url = '/api/dispatch_zones/get_settings/'
    response = yield django_test.Client().get(url)
    assert response.status_code == 406

    url = '/api/dispatch_zones/get_settings/?zone=moscow'
    response = yield django_test.Client().get(url)
    assert response.status_code == 404


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
        },
        'moscow': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
            'econom': {
                'DYNAMIC_TIME_B': 1,
                'MAX_ROBOT_DISTANCE': 9000,
                'DYNAMIC_TIME_A': 0.66,
                'WAVE_THICKNESS_MINUTES': 2,
                'DYNAMIC_DISTANCE_A': 0.66,
                'DYNAMIC_DISTANCE_B': 1,
                'MIN_URGENCY': 120,
                'MAX_ROBOT_TIME': 240,
                'K_ETR': 0.0,
                'E_ETA': 0.0,
                'E_ETR': 0.0,
                'APPLY_ETA_ETR_IN_CAR_RANGING': False,
                'WAVE_THICKNESS_SECONDS': 240,
                'SURGE_BONUS_COEF': 0,
                'ANTISURGE_BONUS_COEF': 0,
                'ANTISURGE_BONUS_GAP': 0,
                'DISPATCH_GRADE_BONUS_SECONDS': {
                    '__default__': 0
                },
                'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {
                    '__default__': 0
                },
                'DISPATCH_HOME_BONUS_SECONDS': 0,
                'DISPATCH_REPOSITION_BONUS': {
                    '__default__': 0
                },
                'DISPATCH_DRIVER_TAGS_BONUSES': {
                    '__default__': 0
                },
                'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
                'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
                'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
                'AIRPORT_QUEUE_DISPATCH_BONUS_MIN': 0,
                'AIRPORT_QUEUE_DISPATCH_BONUS_STEP': 0,
                'AIRPORT_QUEUE_DISPATCH_BONUS_MAX': 0,
                'MAX_ROBOT_TIME_SCORE_ENABLED': False,
                'MAX_ROBOT_TIME_SCORE': 9000,
            },
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
        'moscow': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
            'econom': {
                'MIN_URGENCY': 500,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        },
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        },
        'moscow': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
            'econom': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 9000,
            },
        },
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        },
        'moscow': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            },
            'econom': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3500,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        },
    },
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_dispatch_zone_settings(load):
    expected_response = json.loads(load('dispatch_config.json'))
    response = yield _request_dispatch_zones_get_settings('moscow')
    assert expected_response['moscow'] == response['moscow']


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_invalid_set_dispatch_zone_setting():
    settings_to_set = {
        'moscow': {
            '__default__': {
                'SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES': {
                    'MIN_URGENCY': -600,
                    'LIMIT': -200,
                    'FREE_PREFERRED': -50,
                }
            }
        }
    }

    url = '/api/dispatch_zones/set_settings/'
    response = yield django_test.Client().post(url, json.dumps({'dispatch_config_updates': settings_to_set}),
                                               content_type='application/json')
    assert response.status_code == 404
    async.return_value(json.loads(response.content))


@pytest.mark.config(
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_dispatch_zone_setting():
    response = yield _request_configured_dispatch_zones()
    assert {'zones': []} == response

    settings_to_set = {
        'moscow': {
            '__default__': {
                'SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES': {
                    'MIN_URGENCY': 600,
                    'LIMIT': 200,
                    'FREE_PREFERRED': 50,
                }
            },
            'econom': {
                'SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES': {
                    'MIN_URGENCY': 500,
                    'LIMIT': 220,
                    'FREE_PREFERRED': 40,
                }
            },
            'comfort': {
                'SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES': {
                    'MIN_URGENCY': 540,
                    'LIMIT': 330,
                    'FREE_PREFERRED': 44,
                }
            },
        }
    }

    response = yield _request_dispatch_zones_set_settings(settings_to_set)
    assert {} == response

    response = yield _request_configured_dispatch_zones()
    assert {'zones': ['moscow']} == response

    response = yield _request_dispatch_zones_get_settings('moscow')
    assert settings_to_set == response

    del settings_to_set['moscow']['comfort']

    response = yield _request_dispatch_zones_set_settings(settings_to_set)
    assert {} == response

    response = yield _request_dispatch_zones_get_settings('moscow')
    assert settings_to_set == response


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        }
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        }
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_dispatch_zone_settings(load):
    response = yield _request_configured_dispatch_zones()
    assert {'zones': []} == response

    settings_to_set = json.loads(load('dispatch_config.json'))
    response = yield _request_dispatch_zones_set_settings(settings_to_set)
    assert {} == response

    response = yield _request_configured_dispatch_zones()
    assert {'zones': ['almaty', 'moscow']} == response

    for zone in ['moscow', 'almaty']:
        response = yield _request_dispatch_zones_get_settings(zone)
        assert settings_to_set[zone] == response[zone]


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        }
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        }
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_invalid_delete_dispatch_zone_setting():
    url = '/api/dispatch_zones/delete_settings/'
    response = yield django_test.Client().post(url, json.dumps({}), content_type='application/json')
    assert 406 == response.status_code

    url = '/api/dispatch_zones/delete_settings/'
    response = yield django_test.Client().post(url, json.dumps({'zone': 'moscow'}), content_type='application/json')
    assert 404 == response.status_code


@pytest.mark.config(
    SEARCH_SETTINGS_CLASSES={
        '__default__': {
            '__default__':
                SEARCH_SETTINGS_CLASSES_DEFAULT,
        },
    },
    SEARCH_SETTINGS_AIRPORT_OVERRIDE_CLASSES={
        '__default__': {
            '__default__': {
                'MIN_URGENCY': 600,
                'LIMIT': 200,
                'FREE_PREFERRED': 50,
            },
        }
    },
    SEARCH_SETTINGS_QUERY_LIMIT_CLASSES={
        '__default__': {
            '__default__': {
                'LIMIT': 20,
                'FREE_PREFERRED': 5,
                'MAX_LINE_DIST': 10000,
            },
        }
    },
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 300,
                'MIN_TAXIMETER_VERSION': '8.06',
                'PAX_EXCHANGE_TIME': 120
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_dispatch_zone_settings(load):
    response = yield _request_configured_dispatch_zones()
    assert {'zones': []} == response

    settings_to_set = json.loads(load('dispatch_config.json'))
    response = yield _request_dispatch_zones_set_settings(settings_to_set)
    assert {} == response

    response = yield _request_configured_dispatch_zones()
    assert {'zones': ['almaty', 'moscow']} == response

    response = yield _request_dispatch_zones_delete_settings('moscow')
    assert {} == response

    response = yield _request_configured_dispatch_zones()
    assert {'zones': ['almaty']} == response

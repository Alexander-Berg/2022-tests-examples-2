import datetime


# FLEET_DRIVERS_SCORING_ENABLED config variants
SCORING_ENABLED_CONFIG1 = {
    'FLEET_DRIVERS_SCORING_ENABLED': {
        'cities': [],
        'countries': ['rus'],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
}
SCORING_ENABLED_CONFIG2 = {
    'FLEET_DRIVERS_SCORING_ENABLED': {
        'cities': ['city1'],
        'countries': ['rus'],
        'dbs': ['park2', 'park3'],
        'dbs_disable': ['park3'],
        'enable': True,
    },
}
SCORING_ENABLED_CONFIG3 = {
    'FLEET_DRIVERS_SCORING_ENABLED': {
        'cities': ['city1'],
        'countries': ['kaz'],
        'dbs': ['park2', 'park3'],
        'dbs_disable': ['park3'],
        'enable': False,
    },
}

# FLEET_DRIVERS_SCORING_RATE_LIMITS config variants (for free access)
RATE_LIMIT_CONFIG1 = {
    'FLEET_DRIVERS_SCORING_RATE_LIMITS': {
        '__default__': {'day': 1},
        'clid1': {'day': 10},
        'clid3': {'day': 9, 'week': 40},
    },
}
RATE_LIMIT_CONFIG2 = {
    'FLEET_DRIVERS_SCORING_RATE_LIMITS': {
        '__default__': {'week': 100},
        'clid1': {'week': 10},
        'clid3': {'week': 16, 'day': 10},
    },
}

# datetime variants
NOW1 = datetime.datetime.fromisoformat('2020-01-01T00:00+00:00')
NOW2 = datetime.datetime.fromisoformat('2020-02-02T00:00+00:00')

# fleet-parks response variants
RESPONSE_FLEET_PARKS1 = {
    'id': 'park1',
    'login': 'login1',
    'name': 'super_park1',
    'is_active': True,
    'city_id': 'city1',
    'locale': 'locale1',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'demo_mode': False,
    'country_id': 'rus',
    'provider_config': {'clid': 'clid1', 'type': 'production'},
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}
RESPONSE_FLEET_PARKS2 = {
    'id': 'park2',
    'login': 'login2',
    'name': 'super_park2',
    'is_active': True,
    'city_id': 'city2',
    'locale': 'locale2',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'demo_mode': False,
    'country_id': 'rus',
    'provider_config': {'clid': 'clid2', 'type': 'production'},
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}
RESPONSE_FLEET_PARKS2_AUS_COUNTRY = {
    **RESPONSE_FLEET_PARKS2,
    **{'country_id': 'aus'},
}
RESPONSE_FLEET_PARKS3 = {
    'id': 'park3',
    'login': 'login3',
    'name': 'super_park3',
    'is_active': True,
    'city_id': 'city3',
    'locale': 'locale3',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'demo_mode': False,
    'country_id': 'rus',
    'provider_config': {'clid': 'clid3', 'type': 'production'},
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}
RESPONSE_FLEET_PARKS4 = {
    'id': 'park4',
    'login': 'login4',
    'name': 'super_park3',
    'is_active': False,
    'city_id': 'city6',
    'locale': 'locale4',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'demo_mode': False,
    'country_id': 'deu',
    'provider_config': {'clid': 'clid3', 'type': 'production'},
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}

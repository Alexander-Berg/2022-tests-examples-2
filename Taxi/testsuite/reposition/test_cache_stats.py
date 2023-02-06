CACHES = {
    'AgglomerationsCache': {
        'clean_update_interval': 3600,
        'update_interval': 3600,
    },
    'DisplayRulesCache': {'clean_update_interval': 5, 'update_interval': 5},
    'DriverGeoHierarchiesCache': {
        'clean_update_interval': 600,
        'update_interval': 1,
    },
    'DriverIdsCache': {'clean_update_interval': 3600, 'update_interval': 1},
    'DriverInfosCache': {'clean_update_interval': 300, 'update_interval': 5},
    'DriverWorkModesCache': {
        'clean_update_interval': 3600,
        'update_interval': 1,
    },
    'Experiments3ClientsCache': {
        'clean_update_interval': 0,
        'update_interval': 1,
    },
    'GeoareasCache': {'clean_update_interval': 86400, 'update_interval': 60},
    'GeoindexCache': {'clean_update_interval': 60, 'update_interval': 60},
    'ModesCache': {'clean_update_interval': 5, 'update_interval': 5},
    'ParkTimezonesCache': {'clean_update_interval': 300, 'update_interval': 5},
    'TagsCache': {'clean_update_interval': 86400, 'update_interval': 10},
    'TariffZonesCache': {'clean_update_interval': 60, 'update_interval': 60},
    'TranslationsCache': {'clean_update_interval': 60, 'update_interval': 60},
    'UniqueIdsCache': {'clean_update_interval': 300, 'update_interval': 5},
    'ZonesCache': {'clean_update_interval': 1, 'update_interval': 1},
    'cached-surge-map': {'clean_update_interval': 5, 'update_interval': 5},
    'StateEtagsCache-v2': {
        'clean_update_interval': 31556952,
        'update_interval': 1,
    },
    'ModeEtagsCache-v2': {
        'clean_update_interval': 31556952,
        'update_interval': 1,
    },
    'OfferedModeEtagsCache-v2': {
        'clean_update_interval': 31556952,
        'update_interval': 1,
    },
}


def test_cache_stats(taxi_reposition):
    response = taxi_reposition.get('/cache-stats')

    assert response.status_code == 200
    resp = response.json()
    assert set(resp.keys()) == set(CACHES.keys())

    for k, v in resp.items():
        assert set(v.keys()) == {
            'clean_update_interval',
            'last_clean_update',
            'last_update',
            'update_interval',
        }
        assert CACHES[k]['update_interval'] == v['update_interval']
        assert CACHES[k]['clean_update_interval'] == v['clean_update_interval']

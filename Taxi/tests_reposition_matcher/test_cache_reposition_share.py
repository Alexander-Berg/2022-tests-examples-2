import pytest


@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
async def test_cache(
        taxi_reposition_matcher_monitor,
        reposition_share_cache,
        mockserver,
        testpoint,
):
    zones = ['moscow']
    share = {'comfort': 50, 'econom': 80}

    await reposition_share_cache.update(zones, share)

    metrics = await taxi_reposition_matcher_monitor.get_metric(
        'reposition-share-cache',
    )

    assert metrics == {
        '$meta': {'solomon_children_labels': 'reposition-share-zone'},
        'moscow': {
            '$meta': {'solomon_children_labels': 'reposition-share-tariff'},
            '__total__': {
                '$meta': {'solomon_children_labels': 'reposition-share-type'},
                'reposition-free-of-total-free': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 65,
                },
                'reposition-onorder-of-reposition-any': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 0,
                },
            },
            'comfort': {
                '$meta': {'solomon_children_labels': 'reposition-share-type'},
                'reposition-free-of-total-free': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 50,
                },
                'reposition-onorder-of-reposition-any': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 0,
                },
            },
            'econom': {
                '$meta': {'solomon_children_labels': 'reposition-share-type'},
                'reposition-free-of-total-free': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 80,
                },
                'reposition-onorder-of-reposition-any': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                    'reposition-share-value': 0,
                },
            },
        },
        '__any__': {
            '$meta': {'solomon_children_labels': 'reposition-share-tariff'},
            '__any__': {
                '$meta': {'solomon_children_labels': 'reposition-share-type'},
                'reposition-free-of-total-free': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                },
                'reposition-onorder-of-reposition-any': {
                    '$meta': {
                        'solomon_children_labels': 'reposition-share-data',
                    },
                    'reposition-share-threshold-exceeded': 0,
                },
            },
        },
    }

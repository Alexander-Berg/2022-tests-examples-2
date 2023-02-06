from taxi.internal.airport_queue.ml_class_mapper import get_same_classes_for_zone, make_ml_classes_mapping_inv


def make_config():
    return {
            'platov_airport': {
                'ml_composite_classes': {
                    'econom': ['econom', 'start', 'uberx'],
                    'business': ['start']
                }
            },
            'svo': {},
            'empty_ml_classes': {'ml_composite_classes': {}},
            'super_airport': {
                'ml_composite_classes': {
                    'econom': ['start'],
                    'start': ['econom'],
                }
            }
    }


def test_class_mapper():
    config = make_config()
    mapper = make_ml_classes_mapping_inv(config)
    zone = 'platov_airport'

    expected = {'start', 'econom', 'business'}
    assert get_same_classes_for_zone('start', zone, mapper) == expected

    expected = {'econom'}
    assert get_same_classes_for_zone('econom', zone, mapper) == expected

    expected = {'uberx', 'econom'}
    assert get_same_classes_for_zone('uberx', zone, mapper) == expected

    expected = set()
    assert get_same_classes_for_zone('business', zone, mapper) == expected

    expected = {'comfort'}
    assert get_same_classes_for_zone('comfort', zone, mapper) == expected

    for zone in ['svo', 'missing_zone', 'empty_ml_classes']:
        expected = {'comfort'}
        assert get_same_classes_for_zone('comfort', zone, mapper) == expected

        expected = {'econom'}
        assert get_same_classes_for_zone('econom', zone, mapper) == expected

        expected = {'business'}
        assert get_same_classes_for_zone('business', zone, mapper) == expected

        expected = {'start'}
        assert get_same_classes_for_zone('start', zone, mapper) == expected

    zone = 'super_airport'
    expected = {'econom'}
    assert get_same_classes_for_zone('start', zone, mapper) == expected

    expected = {'start'}
    assert get_same_classes_for_zone('econom', zone, mapper) == expected

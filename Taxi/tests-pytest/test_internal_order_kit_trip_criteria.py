import pytest

from taxi.internal.order_kit import trip_criteria


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('value, distance, duration, expected', [
    ({'distance': 10, 'duration': 10, 'apply': 'either'}, 9, 9, False),
    ({'distance': 10, 'duration': 10, 'apply': 'both'}, 9, 9, False),
    ({'distance': 10, 'duration': 10, 'apply': 'either'}, 11, 9, True),
    ({'distance': 10, 'duration': 10, 'apply': 'both'}, 11, 9, False),
    ({'distance': 10, 'duration': 10, 'apply': 'either'}, 11, 11, True),
    ({'distance': 10, 'duration': 10, 'apply': 'both'}, 11, 11, True),
    ({'distance': 10, 'duration': 10, 'apply': 'either'}, 9, 10, True),
    ({'distance': 10, 'duration': 10, 'apply': 'both'}, 9, 10, False),
    ({'distance': 10, 'duration': 10}, 9, 10, True),
    ({'distance': 10, 'duration': 10}, 10, 10, True),
])
def test_criteria_creation(value, distance, duration, expected):
    criteria = trip_criteria.LongTripCriteria(value)
    assert expected == criteria.is_long_order(distance, duration)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('distance, duration, either, expected', [
    (10, 10, True, '[distance >= 10 met. or duration >= 10 sec.]'),
    (10, 10, False, '[distance >= 10 met. and duration >= 10 sec.]'),
    (10, 10, None, '[distance >= 10 met. or duration >= 10 sec.]'),
])
def test_criteria_log(distance, duration, either, expected):
    value = {
        'distance': distance,
        'duration': duration
    }
    if either is not None:
        value['apply'] = 'either' if either else 'both'
    criteria = trip_criteria.LongTripCriteria(value)
    assert expected == str(criteria)


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(LONG_TRIP_CRITERIA={
    '__default__': {
        '__default__': {'distance': 10, 'duration': 10, 'apply': 'either'},
        'econom': {'distance': 20, 'duration': 20, 'apply': 'both'},
    },
    'moscow': {
        '__default__': {'distance': 20, 'duration': 20, 'apply': 'both'},
        'business': {'distance': 30, 'duration': 30}
    }
})
@pytest.mark.parametrize('calc, zone, tariff, expected', [
    (None, None, None, None),
    ({'distance': 15, 'time': 5}, None, None, True),
    ({'distance': 5, 'time': 5}, None, None, False),
    ({'distance': 15, 'time': 15}, 'spb', 'business', True),
    ({'distance': 15, 'time': 15}, 'spb', 'econom', False),
    ({'distance': 25, 'time': 25}, 'moscow', 'uberx', True),
    ({'distance': 25, 'time': 25}, 'moscow', 'business', False),
    ({'dist': 25, 'time': 25}, 'moscow', 'uberx', False),
])
@pytest.inline_callbacks
def test_long_order(calc, zone, tariff, expected):
    is_long_order = yield trip_criteria.is_long_order(calc, zone, tariff)
    assert expected == is_long_order


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    LONG_TRIP_SKIP_FIELDS={
        '__default__': {
            '__default__': '',
            'business': 'def_bus',
            'econom': 'def_eco',
        },
        'moscow': {
            '__default__': 'msc_def',
            'econom': 'msc_eco'
        }
    },
    LONG_TRIP_CRITERIA={
        '__default__': {
            '__default__': {
                'distance': 100,
                'duration': 100,
                'apply': 'either'
            },
            'econom': {
                'distance': 200,
                'duration': 200,
                'apply': 'both'
            }
        },
        'ekb': {
            '__default__': {
                'distance': 500,
                'duration': 500,
            },
            'econom': {
                'distance': 300,
                'duration': 300,
            },
            'business': {
                'distance': 100,
                'duration': 100,
            }
        }
    },
)
@pytest.mark.parametrize(
    'distance, duration, zone, tariff, expected', [
        (250, 250, 'moscow', 'econom', 'msc_eco'),
        (250, 250, 'moscow', 'business', 'msc_def'),
        (50, 50, 'moscow', None, ''),
        (50, 50, None, None, ''),
        (150, 50, 'moscow', 'econom', ''),
        (150, 150, 'spb', 'business', 'def_bus'),
        (150, 150, 'spb', 'econom', ''),
        (250, 250, 'ekb', 'business', 'def_bus'),
        (250, 250, 'ekb', 'econom', ''),
        (250, 250, 'ekb', 'uberx', ''),
        (None, None, None, None, ''),
        (550, 550, 'ekb', 'econom', 'def_eco'),
        (550, 550, 'ekb', 'uberx', ''),
])
@pytest.inline_callbacks
def test_get_skip_fields(distance, duration, zone, tariff, expected):
    calc = {}
    if distance is not None:
        calc['distance'] = distance
    if duration is not None:
        calc['time'] = duration

    skip_fields = yield trip_criteria.get_long_trip_skip_fields(
        calc, zone, tariff
    )
    assert expected == skip_fields

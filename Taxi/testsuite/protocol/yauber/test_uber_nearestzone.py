import pytest

from protocol.yauber import yauber


@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(ALL_CATEGORIES=['econom', 'uberx'])
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 200, 'moscow'),
        ([37.617348, 54.193122], 200, 'tula'),
    ],
)
def test_uber_nearestzone_all(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.filldb(tariff_settings='none')
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'econom': {'visible_by_default': True},
            'uberx': {'visible_by_default': False},
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [([37.588144, 55.733842], 404, None), ([37.617348, 54.193122], 404, None)],
)
def test_uber_nearestzone_none(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.filldb(tariff_settings='exp1')
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'uberx': {'visible_by_default': False}},
        'moscow': {
            'uberx': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_moscow',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 200, 'moscow'),
        ([37.617348, 54.193122], 404, None),
    ],
)
@pytest.mark.user_experiments('show_moscow')
def test_uber_nearestzone_experiment1(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.filldb(tariff_settings='exp3_1')
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_moscow',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'uberx': {'visible_by_default': False}},
        'moscow': {
            'uberx': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 200, 'moscow'),
        ([37.617348, 54.193122], 404, None),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_moscow',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_uber_nearestzone_experiment3_1(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.filldb(tariff_settings='exp2')
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_tula',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'uberx': {'visible_by_default': False}},
        'tula': {
            'uberx': {
                'visible_by_default': False,
                'show_experiment': 'show_tula',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 404, None),
        ([37.617348, 54.193122], 200, 'tula'),
    ],
)
@pytest.mark.user_experiments('show_tula')
def test_uber_nearestzone_experiment2(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.filldb(tariff_settings='exp3_2')
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_tula',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'uberx': {'visible_by_default': False}},
        'tula': {
            'uberx': {
                'visible_by_default': False,
                'show_experiment': 'show_tula',
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 404, None),
        ([37.617348, 54.193122], 200, 'tula'),
    ],
)
def test_uber_nearestzone_experiment3_2(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [([37.588144, 55.733842], 404, None), ([37.617348, 54.193122], 404, None)],
)
def test_uber_nearestzone_another_service(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_basic(taxi_protocol, point, expected_status, expected_nz)


def _test_basic(taxi_protocol, point, expected_status, expected_nz):
    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'test-user', 'point': point},
        headers=yauber.headers,
    )
    assert response.status_code == expected_status
    if expected_nz:
        assert expected_nz == response.json()['nearest_zone']

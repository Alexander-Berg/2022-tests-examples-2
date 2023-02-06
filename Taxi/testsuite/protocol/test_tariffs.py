import pytest


# with intervals
def test_tariffs(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': True,
            'with_intervals': True,
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['max_tariffs']) > 0
    assert 'currency_rules' in content
    assert len(content['max_tariffs'][0]['intervals']) > 0


# without intervals
def test_tariffs_no_intervals(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'size_hint': 32,
            'format_currency': False,
            'skin_version': 0,
            'with_intervals': False,
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['max_tariffs']) > 0
    assert not ('intervals' in content['max_tariffs'][0])


# missing params
# missing city
def test_tariffs_no_city(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'size_hint': 32,
            'format_currency': False,
            'skin_version': 0,
            'with_intervals': True,
        },
    )
    assert response.status_code == 400


# missing size_hint
def test_tariffs_no_size_hint(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': False,
            'skin_version': 0,
            'with_intervals': False,
        },
    )
    assert response.status_code == 400


# wrong city
def test_tariffs_wrong_city(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Rlyegh',
            'size_hint': 32,
            'format_currency': False,
            'skin_version': 0,
            'with_intervals': True,
        },
    )
    assert response.status_code == 406


def test_tariffs_with_id(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': True,
            'with_intervals': True,
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
        },
    )
    assert response.status_code == 200


def test_tariffs_with_wrong_id(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': True,
            'with_intervals': True,
            'id': '-1',
        },
    )
    assert response.status_code == 200


@pytest.mark.user_experiments('disable_econom')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
                'use_legacy_experiments': True,
            },
        },
    },
)
def test_tariffs_tariff_hidden_by_legacy_exp(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': True,
            'with_intervals': True,
        },
    )
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 0


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_econom',
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
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
            },
        },
    },
)
def test_tariffs_tariff_hidden_by_exp3(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/tariffs',
        json={
            'city': 'Москва',
            'format_currency': True,
            'with_intervals': True,
        },
    )
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 0

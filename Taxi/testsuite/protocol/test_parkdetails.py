import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


def test_parkdetails_ok(taxi_protocol):
    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': '999011'})
    assert response.status_code == 200
    content = response.json()
    assert content['long_name'] == 'Organization'
    assert content['ogrn'] == '1233231231'
    assert content['legal_address'] == 'Street'
    assert len(content['tariffs']) > 0
    assert len(content['tariffs'][0]['intervals']) > 0
    classes = [tariff['class'] for tariff in content['tariffs']]
    assert set(classes) == set(
        ['business', 'comfortplus', 'econom', 'minivan', 'vip'],
    )


def test_parkdetails_wrong_parkid(taxi_protocol):
    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': '00000'})
    assert response.status_code == 404


def test_parkdetails_parkid_with_id(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/parkdetails',
        json={'parkid': '999011', 'id': '0a8a55832e7b4621afddfc7239b24ee4'},
    )
    assert response.status_code == 200


def test_parkdetails_parkid_with_wrong_id(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/parkdetails', json={'parkid': '999011', 'id': '-1'},
    )
    assert response.status_code == 200


def test_parkdetails_bad_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/parkdetails', json={'parksid': '999012'},
    )
    assert response.status_code == 400


@pytest.mark.user_experiments('disable_econom')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
                'use_legacy_experiments': True,
            },
        },
    },
)
def test_parkdetails_tariff_hidden_by_exp_legacy(taxi_protocol):
    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': '999011'})
    data = response.json()

    matches = [trf for trf in data['tariffs'] if trf['id'] == 'econom']
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
        '__default__': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
            },
        },
    },
)
def test_parkdetails_tariff_hidden_by_exp3(taxi_protocol):
    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': '999011'})
    data = response.json()

    matches = [trf for trf in data['tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 0


@pytest.mark.filldb(parks='deactivated')
@pytest.mark.parametrize(
    ('park_id', 'hide_by_deactivation', 'expected_code'),
    (
        pytest.param('activated', True, 200, id='shown_by_activation'),
        pytest.param('deactivated', False, 200, id='shown_by_config'),
        pytest.param('deactivated', True, 404, id='hidden'),
    ),
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_parkdetails_hidden_by_deactivation(
        taxi_protocol,
        config,
        park_id,
        hide_by_deactivation,
        expected_code,
        individual_tariffs_switch_on,
):
    config.set_values(dict(PARKS_HIDE_ALL_DEACTIVATED=hide_by_deactivation))

    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': park_id})
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    ('hide_ids', 'expected_code'),
    (
        pytest.param(['bad_id'], 200, id='shown_id_not_match'),
        pytest.param(['999011'], 404, id='hide_id_match'),
    ),
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_parkdetails_hidden_by_ids(
        taxi_protocol,
        config,
        hide_ids,
        expected_code,
        individual_tariffs_switch_on,
):
    config.set_values(dict(PARKS_HIDE_IDS=hide_ids))

    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': '999011'})
    assert response.status_code == expected_code


@pytest.mark.parametrize('hide_individuals', [True, False])
@pytest.mark.parametrize(
    ('park_id', 'expected_code'),
    (['999011', 404], ['999012', 404], ['999024', 200]),
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_parkdetails_hide_individuals(
        taxi_protocol,
        config,
        hide_individuals,
        park_id,
        expected_code,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(
            PARKS_DETAILS_HIDE_INDIVIDUALS={
                'hide_individuals': hide_individuals,
                'hidden_set': ['yandex', 'self_assign', 'selfemployed_fns'],
            },
        ),
    )

    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': park_id})
    assert response.status_code == expected_code if hide_individuals else 200


@pytest.mark.parametrize('hide_individuals', [True, False])
@pytest.mark.parametrize(
    ('park_id', 'expected_code'),
    (['999011', 404], ['999012', 200], ['999024', 200]),
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_parkdetails_hide_individuals_other_set(
        taxi_protocol,
        config,
        hide_individuals,
        park_id,
        expected_code,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(
            PARKS_DETAILS_HIDE_INDIVIDUALS={
                'hide_individuals': hide_individuals,
                'hidden_set': ['self_assign', 'selfemployed_fns'],
            },
        ),
    )

    response = taxi_protocol.post('3.0/parkdetails', json={'parkid': park_id})
    assert response.status_code == expected_code if hide_individuals else 200

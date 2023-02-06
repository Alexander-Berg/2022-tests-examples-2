# -*- coding: utf-8 -*-
import itertools

import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


API_OVER_DATA_WORK_MODE = {
    '__default__': {'__default__': 'oldway'},
    'parks-activation-client': {'protocol': 'newway'},
}


@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_ru(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/pricecat?page=0',
        {'zone_name': 'moscow'},
        headers={'Accept-Language': 'ru'},
    )
    res = response.json()
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    assert response.headers['Vary'] == 'Accept-Language'
    names = [i['name'] for i in res['parks']]
    names.sort()
    assert names == ['City', 'Главное Такси', 'Сити']
    park_tariffs = [park['tariffs'] for park in res['parks']]
    all_tariffs = list(itertools.chain.from_iterable(park_tariffs))
    classes = [tariff['class'] for tariff in all_tariffs]
    assert set(classes) == set(
        ['business', 'comfortplus', 'econom', 'minivan', 'vip'],
    )


@pytest.mark.config(
    PROTOCOL_PRICECAT_HIDE_PARKS={'by_zone': ['spb', 'moscow']},
)
@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_hide_by_zone(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/pricecat?page=0',
        {'zone_name': 'moscow'},
        headers={'Accept-Language': 'ru'},
    )
    res = response.json()
    assert response.status_code == 200
    assert res['parks'] == []


@pytest.mark.parks_activation(
    [
        {
            'park_id': '999011',
            'city_id': 'Москва',
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': False,
                'can_coupon': True,
                'can_corp': False,
            },
        },
        {
            'park_id': '999012',
            'city_id': 'Москва',
            'revision': 2,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': True,
                'deactivated_reason': 'test_reason',
                'can_cash': True,
                'can_card': False,
                'can_coupon': True,
                'can_corp': False,
            },
        },
    ],
)
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_parks_activation(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/pricecat?page=0',
        {'zone_name': 'moscow'},
        headers={'Accept-Language': 'ru'},
    )
    res = response.json()
    assert response.status_code == 200
    assert len(res['parks']) == 1


@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_back_compatibility(taxi_protocol, load_json):
    response = taxi_protocol.post(
        '3.0/pricecat',
        {'zone_name': 'moscow'},
        headers={
            'Accept-Language': 'en',
            'User-Agent': 'yandex-taxi/3.37.1.9863 Android/4.2.2',
        },
    )
    old_res = load_json('old_results.en.json')
    new_res = {
        'parks': list(
            [x for x in response.json()['parks'] if x['parkid'] != '999024'],
        ),
    }
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    assert response.headers['Vary'] == 'Accept-Language'
    assert new_res == old_res


@pytest.mark.config(PROTOCOL_PRICECAT_RESULTS_ON_PAGE=1)
@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_config_results_on_page(taxi_protocol, load_json):
    response = taxi_protocol.post(
        '3.0/pricecat?page=0',
        {'zone_name': 'moscow'},
        headers={'Accept-Language': 'ru'},
    )
    res = response.json()
    assert response.status_code == 200
    assert len(res['parks']) == 1


@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_bad_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/pricecat?page=0', {}, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400


@pytest.mark.now('2017-02-02T13:00:00+0300')
@pytest.mark.parametrize(
    'search_query,expected_names',
    [
        (None, ['City', 'Главное Такси', 'Сити']),
        ('', ['City', 'Главное Такси', 'Сити']),
        ('си', ['Главное Такси', 'Сити']),
        ('иТи', ['Сити']),
        ('сити', ['Сити']),
        ('СИТИ', ['Сити']),
        ('ситии', []),
        ('СИТИИ', []),
        ('sit', ['Сити']),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_pricecat_search_query(
        taxi_protocol,
        search_query,
        expected_names,
        individual_tariffs_switch_on,
):
    params = {'zone_name': 'moscow'}
    if search_query is not None:
        params['search_query'] = search_query
    response = taxi_protocol.post(
        '3.0/pricecat?page=0', params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    res = response.json()

    response_names = [park['name'] for park in res['parks']]
    response_names.sort()
    assert response_names == expected_names


@pytest.mark.now('2017-02-02T13:00:00+0300')
@pytest.mark.parametrize(
    'search_query,expected_names',
    [
        (None, ['City']),
        ('', ['City']),
        ('си', []),
        ('иТи', []),
        ('сити', []),
        ('СИТИ', []),
        ('ситии', []),
        ('СИТИИ', []),
        ('sit', []),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_hide_individuals(
        taxi_protocol,
        search_query,
        expected_names,
        config,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(
            PRICECAT_HIDE_INDIVIDUALS={
                'hide_individuals': True,
                'hidden_set': ['yandex', 'self_assign', 'selfemployed_fns'],
            },
        ),
    )

    params = {'zone_name': 'moscow'}
    if search_query is not None:
        params['search_query'] = search_query
    response = taxi_protocol.post(
        '3.0/pricecat?page=0', params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    res = response.json()

    response_names = [park['name'] for park in res['parks']]
    assert response_names == expected_names


@pytest.mark.now('2017-02-02T13:00:00+0300')
@pytest.mark.parametrize(
    'search_query,expected_names',
    [
        (None, ['Главное Такси', 'City']),
        ('', ['Главное Такси', 'City']),
        ('си', ['Главное Такси']),
        ('иТи', []),
        ('сити', []),
        ('СИТИ', []),
        ('ситии', []),
        ('СИТИИ', []),
        ('sit', []),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_hide_individuals_other_set(
        taxi_protocol,
        search_query,
        expected_names,
        config,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(
            PRICECAT_HIDE_INDIVIDUALS={
                'hide_individuals': True,
                'hidden_set': ['self_assign', 'selfemployed_fns'],
            },
        ),
    )

    params = {'zone_name': 'moscow'}
    if search_query is not None:
        params['search_query'] = search_query
    response = taxi_protocol.post(
        '3.0/pricecat?page=0', params, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    res = response.json()

    response_names = [park['name'] for park in res['parks']]
    assert response_names == expected_names

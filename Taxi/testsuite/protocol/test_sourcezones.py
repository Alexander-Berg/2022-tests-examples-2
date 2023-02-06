import operator

import pytest

uber = 'uber'
yandex = 'yandex'

yandex_categories = [
    'express',
    'econom',
    'business',
    'comfortplus',
    'vip',
    'minivan',
    'pool',
    'poputka',
    'business2',
    'kids',
]
yauber_categories = ['uberx', 'uberselect', 'uberblack', 'uberkids']
all_categories = yandex_categories + yauber_categories

web_user_agent = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/74.0.3729.169 YaBrowser/19.6.2.594 (beta) Yowser/2.5 Safari/537.36'
)


def update_headers_for_source(headers, source):
    if source == uber:
        headers['X-Requested-Uri'] = 'uber'
        headers['X-Taxi'] = 'uber-frontend'
        headers['User-Agent'] = web_user_agent


@pytest.mark.config(
    ALL_CATEGORIES=all_categories,
    UBER_CATEGORIES=yauber_categories,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'web_uber': 'yauber'},
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': yandex_categories,
        'yauber': yauber_categories,
    },
    APPLICATION_TO_REQUEST_SOURCE_MAP={
        '__default__': 'yataxi',
        'web_uber': 'yauber',
    },
)
@pytest.mark.parametrize(
    'source, valid_response',
    [
        pytest.param(
            uber,
            {
                'countries': [
                    {
                        'region_id': 159,
                        'name': 'Kazakhstan',
                        'zones': [
                            {
                                'id': 'almaty',
                                'name': 'Almaty',
                                'geo_id': 162,
                                'center': [76.5, 43.5],
                            },
                        ],
                    },
                    {
                        'region_id': 225,
                        'name': 'Russia',
                        'zones': [
                            {
                                'id': 'moscow',
                                'name': 'Moscow',
                                'geo_id': 213,
                                'center': [36.5, 56.5],
                            },
                            {
                                'id': 'tula',
                                'name': 'Tula',
                                'geo_id': 15,
                                'center': [37.5, 54.5],
                            },
                        ],
                    },
                ],
            },
        ),
        pytest.param(
            yandex,
            {
                'countries': [
                    {
                        'region_id': 159,
                        'name': 'Kazakhstan',
                        'zones': [
                            {
                                'id': 'almaty',
                                'name': 'Almaty',
                                'geo_id': 162,
                                'center': [76.5, 43.5],
                            },
                        ],
                    },
                    {
                        'region_id': 225,
                        'name': 'Russia',
                        'zones': [
                            {
                                'id': 'tula',
                                'name': 'Tula',
                                'geo_id': 15,
                                'center': [37.5, 54.5],
                            },
                        ],
                    },
                ],
            },
        ),
        pytest.param(
            yandex,
            {
                'countries': [
                    {
                        'region_id': 225,
                        'name': 'Russia',
                        'zones': [
                            {
                                'id': 'tula',
                                'name': 'Tula',
                                'geo_id': 15,
                                'center': [37.5, 54.5],
                            },
                        ],
                    },
                ],
            },
            marks=(
                pytest.mark.config(
                    APPLICATION_BRAND_FILTERS={
                        'yataxi': {'countries': ['rus']},
                    },
                ),
            ),
        ),
        pytest.param(
            yandex,
            {
                'countries': [
                    {
                        'region_id': 159,
                        'name': 'Kazakhstan',
                        'zones': [
                            {
                                'id': 'almaty',
                                'name': 'Almaty',
                                'geo_id': 162,
                                'center': [76.5, 43.5],
                            },
                        ],
                    },
                    {
                        'region_id': 225,
                        'name': 'Russia',
                        'zones': [
                            {
                                'id': 'tula',
                                'name': 'Tula',
                                'geo_id': 15,
                                'center': [37.5, 54.5],
                            },
                        ],
                    },
                ],
            },
            marks=(
                pytest.mark.config(APPLICATION_BRAND_FILTERS={'yataxi': {}}),
            ),
        ),
    ],
)
@pytest.mark.filldb(geoareas='centroids')
@pytest.mark.geoareas(filename='geoareas_centroids.json')
def test_source(taxi_protocol, source, valid_response, db, config):
    """
    Checks responses.

    Almaty:
        yandex: vip,
        uber: uberselect

    Moscow:
        uber: uberx

    Tula:
        yandex: vip, econom
        uber: uberx

    PS:
    if you'll change dbs you may need manually sort zones in 'source' test arg
    """
    headers = {'Accept-Language': 'en_EN'}
    update_headers_for_source(headers, source)

    response = taxi_protocol.post(
        '3.0/sourcezones',
        json={'source': source},
        bearer='test_token',
        headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    # Force data order
    content['countries'].sort(key=operator.itemgetter('region_id'))
    for country in content['countries']:
        country['zones'].sort(key=operator.itemgetter('id'))

    assert content == valid_response


@pytest.mark.config(
    ALL_CATEGORIES=all_categories,
    UBER_CATEGORIES=yauber_categories,
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'vip': {
                'hide_experiment': 'hide_vip',
                'visible_by_default': True,
                'use_legacy_experiments': True,
            },
        },
    },
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
)
@pytest.mark.filldb(geoareas='centroids')
@pytest.mark.geoareas(filename='geoareas_centroids.json')
@pytest.mark.user_experiments('hide_vip')
def test_hidden_classes_legacy_exp(taxi_protocol, db, config):
    """

    Account classes visibility info from TARIFF_CATEGORIES_VISIBILITY.
    Yandex source, Almaty contains 'vip', Tula 'vip' and 'econom'.
    will be showed only Tula,
    as 'vip' is hidden by experiment 'hide_vip' in TARIFF_CATEGORIES_VISIBILITY

    Almaty:
        yandex: vip,
        uber: uberselect

    Moscow:
        uber: uberx

    Tula:
        yandex: vip, econom
        uber: uberx

    PS:
    if you'll change dbs you may need manually sort zones in 'source' test arg
    """

    source = yandex
    valid_response = {
        'countries': [
            {
                'region_id': 225,
                'name': 'Russia',
                'zones': [
                    {
                        'id': 'tula',
                        'name': 'Tula',
                        'geo_id': 15,
                        'center': [37.5, 54.5],
                    },
                ],
            },
        ],
    }

    response = taxi_protocol.post(
        '3.0/sourcezones',
        json={'source': source},
        bearer='test_token',
        headers={'Accept-Language': 'en_EN'},
    )

    assert response.status_code == 200
    content = response.json()
    content['countries'].sort(key=operator.itemgetter('region_id'))
    valid_response['countries'].sort(key=operator.itemgetter('region_id'))
    assert content == valid_response


@pytest.mark.config(
    ALL_CATEGORIES=all_categories,
    UBER_CATEGORIES=yauber_categories,
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'vip': {'hide_experiment': 'hide_vip', 'visible_by_default': True},
        },
    },
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
)
@pytest.mark.filldb(geoareas='centroids')
@pytest.mark.geoareas(filename='geoareas_centroids.json')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='hide_vip',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_hidden_classes_exp3(taxi_protocol, db, config):
    """

    Account classes visibility info from TARIFF_CATEGORIES_VISIBILITY.
    Yandex source, Almaty contains 'vip', Tula 'vip' and 'econom'.
    will be showed only Tula,
    as 'vip' is hidden by experiment 'hide_vip' in TARIFF_CATEGORIES_VISIBILITY

    Almaty:
        yandex: vip,
        uber: uberselect

    Moscow:
        uber: uberx

    Tula:
        yandex: vip, econom
        uber: uberx

    PS:
    if you'll change dbs you may need manually sort zones in 'source' test arg
    """

    source = yandex
    valid_response = {
        'countries': [
            {
                'region_id': 225,
                'name': 'Russia',
                'zones': [
                    {
                        'id': 'tula',
                        'name': 'Tula',
                        'geo_id': 15,
                        'center': [37.5, 54.5],
                    },
                ],
            },
        ],
    }

    response = taxi_protocol.post(
        '3.0/sourcezones',
        json={'source': source},
        bearer='test_token',
        headers={'Accept-Language': 'en_EN'},
    )

    assert response.status_code == 200
    content = response.json()
    content['countries'].sort(key=operator.itemgetter('region_id'))
    valid_response['countries'].sort(key=operator.itemgetter('region_id'))
    assert content == valid_response


@pytest.mark.config(
    ALL_CATEGORIES=all_categories, UBER_CATEGORIES=yauber_categories,
)
@pytest.mark.parametrize(
    'source,valid_response',
    [
        (
            yandex,
            {
                'countries': [
                    {
                        'region_id': 225,
                        'name': 'Россия',
                        'zones': [
                            {
                                'id': 'tula',
                                'name': 'Тула',
                                'geo_id': 15,
                                'center': [37.5, 54.5],
                            },
                        ],
                    },
                    {
                        'region_id': 159,
                        'name': 'Казахстан',
                        'zones': [
                            {
                                'id': 'almaty',
                                'name': 'Алматы',
                                'geo_id': 162,
                                'center': [76.5, 43.5],
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.filldb(geoareas='centroids')
@pytest.mark.geoareas(filename='geoareas_centroids.json')
def test_locale(taxi_protocol, source, valid_response, db, config):
    """
    In test_source was en_EN, here is ru_RU

    PS:
    if you'll change dbs you may need manually sort zones in 'source' test arg
    """

    response = taxi_protocol.post(
        '3.0/sourcezones',
        json={'source': source},
        bearer='test_token',
        headers={'Accept-Language': 'ru_RU'},
    )

    assert response.status_code == 200
    content = response.json()
    content['countries'].sort(key=operator.itemgetter('region_id'))
    valid_response['countries'].sort(key=operator.itemgetter('region_id'))
    assert content == valid_response


@pytest.mark.config(
    ALL_CATEGORIES=all_categories, UBER_CATEGORIES=yauber_categories,
)
@pytest.mark.parametrize(
    'source',
    [
        pytest.param('unknown', id='not_valid_source'),
        pytest.param('uber', id='uber_source'),
        pytest.param('yandex', id='yandex_source'),
    ],
)
@pytest.mark.filldb(geoareas='centroids')
@pytest.mark.geoareas(filename='geoareas_centroids.json')
def test_source_deprecated(taxi_protocol, source, db, config):
    """
    Check that the `source` parameter from request body is deprecated and
    does not influence the behaviour.
    """
    response = taxi_protocol.post(
        '3.0/sourcezones',
        json={'source': source},
        bearer='test_token',
        headers={'Accept-Language': 'en_EN'},
    )

    assert response.status_code == 200
    content = response.json()

    # Force data order
    content['countries'].sort(key=operator.itemgetter('region_id'))
    for country in content['countries']:
        country['zones'].sort(key=operator.itemgetter('id'))

    assert content == {
        'countries': [
            {
                'region_id': 159,
                'name': 'Kazakhstan',
                'zones': [
                    {
                        'id': 'almaty',
                        'name': 'Almaty',
                        'geo_id': 162,
                        'center': [76.5, 43.5],
                    },
                ],
            },
            {
                'region_id': 225,
                'name': 'Russia',
                'zones': [
                    {
                        'id': 'tula',
                        'name': 'Tula',
                        'geo_id': 15,
                        'center': [37.5, 54.5],
                    },
                ],
            },
        ],
    }

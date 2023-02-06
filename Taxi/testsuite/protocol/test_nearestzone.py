import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom', 'uberx'])
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 200, 'moscow'),
        ([76.945465, 43.238293], 200, 'almaty'),
    ],
)
def test_common(taxi_protocol, point, expected_status, expected_nz):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'econom': {'visible_by_default': False},
            'uberx': {'visible_by_default': True},
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [([37.588144, 55.733842], 404, None), ([76.945465, 43.238293], 404, None)],
)
def test_404(taxi_protocol, point, expected_status, expected_nz):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,has_id,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], True, 200, 'moscow'),
        ([37.588144, 55.733842], False, 200, 'moscow'),
        ([76.945465, 43.238293], True, 404, None),
        ([76.945465, 43.238293], False, 404, None),
    ],
)
@pytest.mark.user_experiments('show_moscow')
def test_experiment_moscow(
        taxi_protocol, point, has_id, expected_status, expected_nz,
):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,has_id,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], True, 200, 'moscow'),
        ([37.588144, 55.733842], False, 200, 'moscow'),
        ([76.945465, 43.238293], True, 404, None),
        ([76.945465, 43.238293], False, 404, None),
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
def test_experiment3_moscow(
        taxi_protocol, point, has_id, expected_status, expected_nz,
):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': True}},
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,has_id,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], True, 404, None),
        ([37.588144, 55.733842], False, 404, None),
        ([76.945465, 43.238293], True, 200, 'almaty'),
        ([76.945465, 43.238293], False, 200, 'almaty'),
    ],
)
def test_experiment_moscow_noexp(
        taxi_protocol, point, has_id, expected_status, expected_nz,
):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
        'almaty': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_almaty',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 404, None),
        ([76.945465, 43.238293], 200, 'almaty'),
    ],
)
@pytest.mark.user_experiments('show_almaty')
def test_experiment_almaty(taxi_protocol, point, expected_status, expected_nz):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
        'almaty': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_almaty',
            },
        },
    },
)
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [
        ([37.588144, 55.733842], 404, None),
        ([76.945465, 43.238293], 200, 'almaty'),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_almaty',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_experiment3_almaty(
        taxi_protocol, point, expected_status, expected_nz,
):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


@pytest.mark.config(ALL_CATEGORIES=['uberx'])
@pytest.mark.parametrize(
    'point,expected_status,expected_nz',
    [([37.588144, 55.733842], 404, None), ([37.617348, 54.193122], 404, None)],
)
def test_another_service(taxi_protocol, point, expected_status, expected_nz):
    _test_base(taxi_protocol, point, expected_status, expected_nz)


def _test_base(
        taxi_protocol, point, expected_status, expected_nz, has_id=True,
):
    args = {'point': point}
    if has_id:
        args['id'] = 'b300bda7d41b4bae8d58dfa93221ef16'
    response = taxi_protocol.post('3.0/nearestzone', args)
    assert response.status_code == expected_status
    if expected_nz:
        assert expected_nz == response.json()['nearest_zone']


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'], NEAREST_ZONE_SHOW_MESSAGE_404=True,
)
@pytest.mark.translations(
    client_messages={
        'nearestzone.not_supported_default': {
            'ru': '%(ZONE_LOCALITY)s еще не поддерживается сервисом',
            'en': '%(ZONE_LOCALITY)s is not supported yet',
        },
        'nearestzone.not_supported_default_without_locality': {
            'ru': 'Регион еще не поддерживается сервисом',
            'en': 'This region is not supported yet',
        },
    },
)
@pytest.mark.parametrize(
    'maps_response,has_locality',
    [('maps_search.json', True), ('maps_search_without_locality.json', False)],
)
def test_404_message(
        maps_response, has_locality, taxi_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        geo_docs = load_json(maps_response)
        return geo_docs

    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'point': [37.0, 55.0]},
        headers={'Accept-Language': 'en-US'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {
            'message': (
                'Moscow is not supported yet'
                if has_locality
                else 'This region is not supported yet'
            ),
        },
    }


@pytest.mark.config(
    ZONES_COMING_SOON_WITH_URLS={
        'tel_aviv': {
            'message': 'nearestzone.tel_aviv_coming_soon_text',
            'url': {
                '__default': 'https://yango.yandex.com/action/isr',
                'ru': 'https://yango.yandex.com/action/isr-ru',
                'en': 'https://yango.yandex.com/action/isr-en',
                'he': 'https://yango.yandex.com/action/isr-he',
            },
            'url_text': 'nearestzone.tel_aviv_coming_soon_url_text',
        },
    },
    LOCALES_SUPPORTED=['ru', 'en', 'he', 'uk'],
)
@pytest.mark.translations(
    client_messages={
        'nearestzone.tel_aviv_coming_soon_text': {
            'en': 'Tel-aviv is coming soon!!! en',
            'he': 'Tel-aviv is coming soon!!! he',
        },
        'nearestzone.tel_aviv_coming_soon_url_text': {
            'en': 'See more... en',
            'he': 'See more... he',
        },
    },
)
@pytest.mark.filldb(geoareas='tel_aviv')
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.parametrize(
    'point,is_in_coming_soon_zone',
    [([37.588144, 55.733842], False), ([34.80, 32.10], True)],
)
def test_tel_aviv(point, is_in_coming_soon_zone, taxi_protocol):
    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'point': point},
        headers={'Accept-Language': 'he-IL'},
    )
    assert response.status_code == 404
    error = response.json()['error']
    if is_in_coming_soon_zone:
        assert error == {
            'message': 'Tel-aviv is coming soon!!! he',
            'url': 'https://yango.yandex.com/action/isr-he',
            'url_text': 'See more... he',
        }
    else:
        assert error == {'text': 'no zone found'}


def test_bad_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/nearestzone', {'id': 'b300bda7d41b4bae8d58dfa93221ef16'},
    )
    assert response.status_code == 400

    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'point': []},
    )
    assert response.status_code == 400


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'], NEAREST_ZONE_SHOW_MESSAGE_404=True,
)
@pytest.mark.translations(
    client_messages={
        'nearestzone.not_supported_default': {
            'ru': '%(ZONE_LOCALITY)s еще не поддерживается сервисом',
            'en': '%(ZONE_LOCALITY)s is not supported yet',
        },
        'nearestzone.not_supported_default_without_locality': {
            'ru': 'Регион еще не поддерживается сервисом',
            'en': 'This region is not supported yet',
        },
    },
)
def test_search_fail(taxi_protocol, mockserver, load_json):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return mockserver.make_response('-1', status=200)

    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'point': [37.0, 55.0]},
        headers={'Accept-Language': 'en-US'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'message': 'This region is not supported yet'},
    }

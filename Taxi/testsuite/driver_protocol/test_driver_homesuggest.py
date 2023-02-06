import json

import pytest

_POINTS = ([30.324, 59.793], [30.35, 59.838], [30.349, 59.741])


def process_point(request, t='', accept=False):
    return {
        'checked_points': [
            {
                'position': point['position'],
                'mode': point['mode'],
                'accepted': point['position'] not in _POINTS or accept,
                'message': (
                    None
                    if point['position'] not in _POINTS or accept
                    else 'you cant setup pulkovo home point' + t
                ),
            }
            for point in json.loads(request.get_data())['check_points']
        ],
    }


def test_bad_request(taxi_driver_protocol):
    # no parts parameter specified
    response = taxi_driver_protocol.post('driver/homesuggest')
    assert response.status_code == 400

    # no parts parameter specified
    response = taxi_driver_protocol.post(
        'driver/homesuggest?bases=street,house',
    )
    assert response.status_code == 400

    # wrong results value
    response = taxi_driver_protocol.get(
        'driver/homesuggest?part=Mosco&bases=street,house&results=-1',
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'req,mode,ans',
    [
        ('bases=street,house&', '', 'street,house'),
        ('bases=street,house&', 'home', 'street,house'),
        ('', '', 'home_bases'),
        ('', 'unknown', 'default_bases'),
        ('', 'home', 'home_bases'),
        ('', 'poi', 'poi_bases'),
    ],
)
@pytest.mark.config(
    HOME_BUTTON_SUGGEST_BASES_PARAM_FALLBACK_MODES={
        '__default__': 'default_bases',
        'home': 'home_bases',
        'poi': 'poi_bases',
    },
)
def test_good_request(taxi_driver_protocol, mockserver, req, mode, ans):
    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': ans,
            'part': 'Mosco',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'lang': 'en',
        }

    url = 'driver/homesuggest?' + req + 'part=Mosco&mode=' + mode

    response = taxi_driver_protocol.post(url)
    assert response.status_code == 200

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'params,expected',
    [
        ('check_point=30.234,57.232&lang=en', 200),
        ('check_point=10,10', 200),
        ('check_point=10,', 400),
        ('check_point=30.234,57.232&lang=en', 200),
        ('lang=ru', 400),
    ],
)
def test_check_point_request(
        taxi_driver_protocol, params, expected, mockserver,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return mockserver.make_response(
            json.dumps(process_point(request)), status=expected,
        )

    url = 'driver/homesuggest?' + params
    response = taxi_driver_protocol.post(url)
    assert response.status_code == expected

    response = taxi_driver_protocol.get(url)
    assert response.status_code == expected


def test_ll_request(taxi_driver_protocol, mockserver):
    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'Mosco',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '37.5368,55.7495',
            'lang': 'en',
        }

    url = 'driver/homesuggest?bases=street,house&part=Mosco&ll=37.5368,55.7495'

    response = taxi_driver_protocol.post(url)
    assert response.status_code == 200


def test_pulkovo(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request, accept=True)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '59.96,30.41',
            'lang': 'en',
        }
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&ll=59.96,30.41'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_updated.json')
    assert response.json() == expected


def test_empty_results(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request, accept=True)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '59.96,30.41',
            'lang': 'en',
        }
        return load_json('empty_results.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&ll=59.96,30.41'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('empty_results.json')
    assert response.json() == expected


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'en': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'en': 'you cant setup pulkovo home point',
        },
    },
)
def test_pulkovo_circle_rejected(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '59.96,30.41',
            'lang': 'en',
        }
        assert request.headers['Accept-Language'][0:2] == 'en'
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&ll=59.96,30.41'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_rejected.json')
    assert response.json() == expected


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={
        '__default__': 'deny_default',
        'airport': 'deny_pulkovo',
    },
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'en': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'en': 'you cant setup pulkovo home point',
        },
    },
)
def test_pulkovo_rejected_prohibition_fallback(
        taxi_driver_protocol, mockserver, load_json,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '59.96,30.41',
            'lang': 'en',
        }
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&ll=59.96,30.41'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_rejected.json')
    assert response.json() == expected


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'polygon',
                'data': [
                    [30.19, 59.84],
                    [30.4, 59.84],
                    [30.4, 59.72],
                    [30.19, 59.72],
                ],
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'en': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'en': 'you cant setup pulkovo home point',
        },
    },
)
def test_pulkovo_poly_rejected(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'ull': '59.96,30.41',
            'lang': 'en',
        }
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&ll=59.96,30.41'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_rejected.json')
    assert response.json() == expected


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'ru': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'ru': 'you cant setup pulkovo home point',
        },
    },
)
@pytest.mark.parametrize('lang', ['ru', 'ru_RU'])
def test_pulkovo_lang_specified(
        taxi_driver_protocol, mockserver, load_json, lang,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'lang': 'ru',
        }
        assert request.headers['Accept-Language'] == lang
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bases=street,house&lang=' + lang

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_rejected.json')
    assert response.json() == expected


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'aze': {'override_keysets': {'taximeter_messages': 'override_az'}},
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {
            'ru': 'you cant setup this home point says Yandex',
        },
        'home_button.deny_pulkovo': {
            'ru': 'you cant setup pulkovo home point says Yandex',
        },
    },
    override_az={
        'home_button.deny_default': {
            'ru': 'you cant setup this home point says Uber',
        },
        'home_button.deny_pulkovo': {
            'ru': 'you cant setup pulkovo home point says Uber',
        },
    },
)
@pytest.mark.parametrize('lang', ['ru', 'ru_RU'])
def test_az_l10n(taxi_driver_protocol, mockserver, load_json, lang):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request, ' says Uber')

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'lang': 'ru',
        }
        assert request.headers['Accept-Language'] == lang
        return load_json('pulkovo_response.json')

    url = (
        'driver/homesuggest?part=пулко&bases=street,' 'house&lang={}&db={}'
    ).format(lang, 'dbf0d2bb16d9492798ad3e2a3cc0a00e')

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200

    expected = load_json('pulkovo_rejected_az.json')
    assert response.json() == expected


@pytest.mark.parametrize('lang', ['en', 'ru', 'en-US', 'ru_RU'])
def test_pulkovo_without_lang(
        taxi_driver_protocol, mockserver, load_json, lang,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.headers['Accept-Language'] == lang
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко'
    response = taxi_driver_protocol.get(url, headers={'Accept-Language': lang})
    assert response.status_code == 200


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_BASES_PARAM_FALLBACK_MODES={
        '__default__': 'test_fallback',
    },
)
def test_bases_param_fallback(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'test_fallback',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'lang': 'en',
        }
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200


def test_bbox_param(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'bases': 'street,house',
            'part': 'пулко',
            'v': '9',
            'search_type': 'taxi',
            'callback': '',
            'bbox': '30,40,50,60',
            'lang': 'en',
        }
        return load_json('pulkovo_response.json')

    url = 'driver/homesuggest?part=пулко&bbox=30,40,50,60'

    response = taxi_driver_protocol.get(url)
    assert response.status_code == 200


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'ru': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'ru': 'you cant setup pulkovo home point',
        },
    },
)
def test_pos_parsing(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        return load_json('pos_specified_response.json')

    response = taxi_driver_protocol.get(
        'driver/homesuggest?part=пулко&lang=ru',
    )
    assert response.status_code == 200

    expected = load_json('pos_specified_rejected.json')
    assert response.json() == expected


def test_position_without_location(
        taxi_driver_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        return load_json('without_position_response.json')

    # Если suggest-geo предлагает локацию без определенённого расположения,
    # значит, скорее всего, передан bases=biz или другой некорректный параметр
    response = taxi_driver_protocol.get(
        'driver/homesuggest?part=пулко&lang=ru',
    )
    assert response.status_code == 500


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_PROHIBITION_KEYS={'__default__': 'deny_default'},
    HOME_BUTTON_SUGGEST_DENIED_ZONES={
        'pulkovo': {
            'zone': {
                'type': 'circle',
                'data': {'center': [30.324, 59.793], 'radius': 10000},
            },
            'prohibition_type': 'airport',
            'tanker_key': 'deny_pulkovo',
        },
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'home_button.deny_default': {'ru': 'you cant setup this home point'},
        'home_button.deny_pulkovo': {
            'ru': 'you cant setup pulkovo home point',
        },
    },
)
@pytest.mark.parametrize(
    'lonlat,denied,check_point',
    [
        (
            '30.324,59.793',
            True,
            {
                'accepted': False,
                'message': 'you cant setup pulkovo home point',
            },
        ),
        ('31.1,60.1', False, {'accepted': True}),
    ],
)
def test_check_point(
        taxi_driver_protocol, lonlat, denied, check_point, mockserver,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request)

    url = 'driver/homesuggest?lang=ru&check_point=' + lonlat
    response = taxi_driver_protocol.post(url)
    assert response.status_code == 200

    assert response.json() == {
        'pos': lonlat,
        'wrong_point_flag': denied,
        'wrong_point_message': (
            'you cant setup pulkovo home point' if denied else None
        ),
    }


@pytest.mark.parametrize(
    'lang, short_lang',
    [('da, en-gb;q=0.8, en;q=0.7', 'en'), ('ru', 'ru'), ('en-US', 'en')],
)
@pytest.mark.config(
    HOME_BUTTON_SUGGEST_BASES_PARAM_FALLBACK_MODES={
        '__default__': 'default_bases',
        'home': 'home_bases',
        'poi': 'poi_bases',
    },
)
def test_lang(taxi_driver_protocol, mockserver, lang, short_lang):
    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict()['lang'] == short_lang

    url = 'driver/homesuggest?bases=street,house&part=Mosco&mode=home'

    response = taxi_driver_protocol.post(
        url, headers={'Accept-Language': lang},
    )
    assert response.status_code == 200

    response = taxi_driver_protocol.get(url, headers={'Accept-Language': lang})
    assert response.status_code == 200


@pytest.mark.config(
    HOME_BUTTON_SUGGEST_BASES_PARAM_FALLBACK_MODES={
        '__default__': 'default_bases',
        'poi': 'geo,street,metro,district,railway',
    },
    LOCALES_SUPPORTED=['en', 'ru', 'he'],
)
def test_israel(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        return process_point(request, accept=True)

    @mockserver.json_handler('/suggest-geo')
    def mock_suggest_geo(request):
        assert request.args.to_dict() == {
            'v': '9',
            'part': 'פת ',
            'lang': 'he',
            'bases': 'geo,street,metro,district,railway',
            'search_type': 'taxi',
            'callback': '',
            'ull': '34.7945017,32.0789949',
        }
        return load_json('israel_response.json')

    url = (
        'driver/homesuggest?'
        'part=%D7%A4%D7%AA%20&'
        'll=34.7945017%2C32.0789949&'
        'mode=poi&'
        'proxy_block_id=default&'
        'device_id=354651103860740&'
        'session=d974a9e417ef44bea10588a713b1426f&'
        'db=607a0e7b9a3a42d29fea4f5a05049242&'
        'park_id=607a0e7b9a3a42d29fea4f5a05049242'
    )

    response = taxi_driver_protocol.get(url, headers={'Accept-Language': 'he'})
    assert response.status_code == 200

    expected = load_json('israel_updated.json')
    assert response.json() == expected

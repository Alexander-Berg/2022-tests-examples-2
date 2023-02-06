import copy
import typing

import pytest

# pylint: disable=import-only-modules
from .conftest import exp3_decorator

URL = 'eda-shortcuts/v1/market-shortcuts'

MARKET_RESPONSE = {
    'results': [
        {
            'handler': 'resolveGoEntryPoints',
            'result': {
                'search': {'url': '/search'},
                'searchIntents': [
                    {
                        'name': 'Умные часы и браслеты',
                        'nid': 18034270,
                        'picture': (
                            '//a.com/img_id1802013495366049977.jpeg/orig'
                        ),
                        'url': '/18034270/list',
                    },
                    {
                        'name': 'Смарт-часы и браслеты',
                        'nid': 18034269,
                        'picture': (
                            '//a.com/img_id1802013495366049977.jpeg/orig'
                        ),
                        'url': '/18034269/list',
                    },
                ],
            },
        },
    ],
    'collections': {},
}

BASE_MARKET_REQUEST: typing.Dict[str, typing.Any] = {
    'params': [{'gps': '39.60258,52.569089'}],
}

BASE_REQUEST = {
    'user_context': {
        'bbox': [37.211375, 55.477065, 38.02277, 55.98304],
        'pin_position': [39.60258, 52.569089],
        'show_at': '2018-05-14T20:09:43.66744+03:00',
    },
}

EXP3_MARKET_MOCK = exp3_decorator(
    name='eda-shortcuts-market-mock', value=MARKET_RESPONSE,
)


def make_response(
        color: typing.Optional[str] = None,
        params_map: typing.Optional[dict] = None,
        shortcuts: typing.Optional[typing.List[dict]] = None,
        urls_map: typing.Optional[dict] = None,
):
    params_map = params_map or {}
    urls_map = urls_map or {}

    def get_url(url):
        return urls_map.get(url, url)

    shortcuts = (
        shortcuts
        if shortcuts is not None
        else [
            {
                'id': 'market-26e4457824e3428ba5de98bd7d8e8227',
                'scenario': 'market_category',
                'content': {
                    'image_tag': params_map.get(18034270, {}).get(
                        'image_tag', 'shortcuts_market_category_18034270',
                    ),
                    'title': params_map.get(18034270, {}).get(
                        'title', 'Умные часы и браслеты',
                    ),
                    'color': color or '#FFFFFF',
                },
                'scenario_params': {
                    'market_category_params': {
                        'url': get_url('/18034270/list'),
                    },
                },
            },
            {
                'id': 'market-a1cd09dbf5974255b2050da32130e227',
                'scenario': 'market_category',
                'content': {
                    'image_tag': params_map.get(18034269, {}).get(
                        'image_tag', 'shortcuts_market_category_18034269',
                    ),
                    'title': params_map.get(18034269, {}).get(
                        'title', 'Смарт-часы и браслеты',
                    ),
                    'color': color or '#FFFFFF',
                },
                'scenario_params': {
                    'market_category_params': {
                        'url': get_url('/18034269/list'),
                    },
                },
            },
        ]
    )
    return {
        'search_url': get_url('/search'),
        'scenario_tops': [
            {'scenario': 'market_category', 'shortcuts': shortcuts},
        ],
    }


@pytest.fixture(name='mock_market_ipa_internal')
def _mock_market_ipa_internal(mockserver):
    def _inner(search_intents: typing.Optional[typing.List[dict]] = None):
        @mockserver.json_handler('/market-ipa-internal/api/v1')
        def _market_ipa_internal_mock(request):
            assert request.query == {'name': 'resolveGoEntryPoints'}
            assert request.json == BASE_MARKET_REQUEST
            market_response = copy.deepcopy(MARKET_RESPONSE)
            if search_intents is not None:
                market_response['results'][0]['result'][
                    'searchIntents'
                ] = search_intents
            return market_response

        return _market_ipa_internal_mock

    return _inner


def cleanup_response_body(response_body):
    body = copy.deepcopy(response_body)
    for scenario_top in body['scenario_tops']:
        for shortcut in scenario_top['shortcuts']:
            shortcut.pop('id')

    return body


async def test_simple(taxi_eda_shortcuts, mock_market_ipa_internal):
    market_ipa_internal_mock = mock_market_ipa_internal()

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)
    assert market_ipa_internal_mock.times_called == 1
    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        make_response(),
    )


@pytest.mark.parametrize(
    'fail_on_empty_categories, expected_code',
    [(None, 200), (False, 200), (True, 500)],
)
async def test_fail_on_empty_categories(
        taxi_eda_shortcuts,
        taxi_config,
        mock_market_ipa_internal,
        fail_on_empty_categories,
        expected_code,
):
    if fail_on_empty_categories is not None:
        taxi_config.set(
            EDA_SHORTCUTS_FAIL_ON_EMPTY_MARKET_CATEGORIES=fail_on_empty_categories,  # noqa: E501 pylint: disable=line-too-long
        )
    market_ipa_internal_mock = mock_market_ipa_internal(search_intents=[])

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)
    assert market_ipa_internal_mock.times_called == 1
    assert response.status_code == expected_code
    if expected_code == 200:
        assert cleanup_response_body(response.json()) == cleanup_response_body(
            make_response(shortcuts=[]),
        )


@pytest.mark.config(
    EDA_SHORTCUTS_MARKET_CATEGORY_SHORTCUT_DEFAULT_COLOR='#foobar',
)
async def test_default_color(taxi_eda_shortcuts, mock_market_ipa_internal):
    market_ipa_internal_mock = mock_market_ipa_internal()

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)
    assert market_ipa_internal_mock.times_called == 1
    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        make_response(color='#foobar'),
    )


@pytest.mark.config(
    EDA_SHORTCUTS_MARKET_CATEGORIES_PARAMS_MAP={
        18034270: {'image_tag': 'some_image', 'title': 'some_title'},
    },
)
async def test_params_map(taxi_eda_shortcuts, mock_market_ipa_internal):
    market_ipa_internal_mock = mock_market_ipa_internal()

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)
    assert market_ipa_internal_mock.times_called == 1
    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        make_response(
            params_map={
                18034270: {'image_tag': 'some_image', 'title': 'some_title'},
            },
        ),
    )


@EXP3_MARKET_MOCK
async def test_mock(taxi_eda_shortcuts, mock_market_ipa_internal):
    market_ipa_internal_mock = mock_market_ipa_internal()

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)
    assert market_ipa_internal_mock.times_called == 0
    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        make_response(),
    )


@pytest.mark.parametrize(
    'params_exp_value, urls_map',
    [
        (
            {
                'return_all_categories': True,
                'url_wrapper': {
                    'url': 'redirect?key=a.b&to={}',
                    'market_url_prefix': 'https://m.market.yandex.ru',
                },
            },
            {
                '/search': (
                    'redirect?key=a.b&to='
                    'https%3A%2F%2Fm.market.yandex.ru%2Fsearch'
                ),
                '/18034269/list': (
                    'redirect?key=a.b&to='
                    'https%3A%2F%2Fm.market.yandex.ru%2F18034269%2Flist'
                ),
                '/18034270/list': (
                    'redirect?key=a.b&to='
                    'https%3A%2F%2Fm.market.yandex.ru%2F18034270%2Flist'
                ),
            },
        ),
        ({'return_all_categories': False}, None),
    ],
)
async def test_market_shortcuts_params_exp(
        taxi_eda_shortcuts,
        mockserver,
        experiments3,
        params_exp_value,
        urls_map,
):
    experiments3.add_experiment(
        name='market_shortcuts_params',
        consumers=['eda-shortcuts/market-shortcuts'],
        match={'enabled': True, 'predicate': {'type': 'true', 'init': {}}},
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': params_exp_value,
            },
        ],
    )

    expected_request = copy.deepcopy(BASE_MARKET_REQUEST)
    expected_request['params'][0]['returnAllCategories'] = params_exp_value[
        'return_all_categories'
    ]

    @mockserver.json_handler('/market-ipa-internal/api/v1')
    def _market_ipa_internal_mock(request):
        assert request.query == {'name': 'resolveGoEntryPoints'}
        assert request.json == expected_request
        return copy.deepcopy(MARKET_RESPONSE)

    await taxi_eda_shortcuts.invalidate_caches()

    response = await taxi_eda_shortcuts.post(URL, json=BASE_REQUEST)

    assert _market_ipa_internal_mock.times_called == 1
    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        make_response(urls_map=urls_map),
    )

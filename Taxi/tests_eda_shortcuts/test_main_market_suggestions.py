import pytest

URL = 'eda-shortcuts/v1/main-market-suggestions'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Yandex-UID': '4073058016',
    'X-AppMetrica-UUID': 'AM-UUID',
    'X-AppMetrica-DeviceId': 'AM-DEV',
}

TITLE = 'Товары маркета для вас'
TITLE_PROMO = 'Скидка 500 рублей на первый заказ'
MARKET_URL = 'https://m.market.yandex.ru/special/yandex-go?topic=kids'
MARKET_URL_PROMO = (
    'https://m.market.yandex.ru/special/yandex-go-promo?topic=kids'
)
SUGGESTIONS = {
    'item1': {
        'id': 'item1',
        'title': 'Гаджеты для детей',
        'picture': (
            '//avatars.mds.yandex.net/get-mpic/4076910/'
            'img_id5242431969172854530.jpeg/orig'
        ),
        'url': (
            'https://m.market.yandex.ru/special/yandex-go?'
            'pinned-thematic=430&topic=kids'
        ),
        'url_promo': (
            'https://m.market.yandex.ru/special/yandex-go-promo?'
            'pinned-thematic=430&topic=kids'
        ),
    },
    'item2': {
        'id': 'item2',
        'title': 'Игрушки для девочек',
        'picture': (
            '//avatars.mds.yandex.net/get-mpic/5279750/'
            'img_id6368324281567284578.jpeg/orig'
        ),
        'url': (
            'https://m.market.yandex.ru/special/yandex-go?'
            'pinned-thematic=128&topic=kids'
        ),
        'url_promo': (
            'https://m.market.yandex.ru/special/yandex-go-promo?'
            'pinned-thematic=128&topic=kids'
        ),
    },
    'item3': {
        'id': 'item3',
        'title': 'Игрушки для мальчиков',
        'picture': (
            '//avatars.mds.yandex.net/get-mpic/4696638/'
            'img_id2089379247190121738.jpeg/orig'
        ),
        'url': (
            'https://m.market.yandex.ru/special/yandex-go?'
            'pinned-thematic=127&topic=kids'
        ),
        'url_promo': (
            'https://m.market.yandex.ru/special/yandex-go-promo?'
            'pinned-thematic=127&topic=kids'
        ),
    },
    'item4': {
        'id': 'item4',
        'title': 'Детский транспорт',
        'picture': (
            '//avatars.mds.yandex.net/get-mpic/5287649/'
            'img_id5683060033074204724.png/orig'
        ),
        'url': (
            'https://m.market.yandex.ru/special/yandex-go?'
            'pinned-thematic=174&topic=kids'
        ),
        'url_promo': (
            'https://m.market.yandex.ru/special/yandex-go-promo?'
            'pinned-thematic=174&topic=kids'
        ),
    },
}


@pytest.mark.parametrize(
    'tags, suggestions, is_promo',
    [
        pytest.param(
            ['has-child'], SUGGESTIONS, True, id='child_category_suggestion',
        ),
        pytest.param(
            ['has-pet', 'some-tag'],
            SUGGESTIONS,
            True,
            id='pet_category_suggestions',
        ),
        pytest.param(['some-tag'], None, False, id='no_target_tag'),
        pytest.param(
            ['has-child', 'installed-market'],
            SUGGESTIONS,
            False,
            id='market_already_installed',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_main_market_suggestions.json')
async def test_suggestions(
        taxi_eda_shortcuts, mockserver, tags, suggestions, is_promo,
):
    @mockserver.json_handler('/market-dj-recommender/recommend')
    def _market_dj_recommender_mock(request):
        items = list(suggestions.values())
        return {
            'title': TITLE,
            'title_promo': TITLE_PROMO,
            'url': MARKET_URL,
            'url_promo': MARKET_URL_PROMO,
            'items': items,
        }

    body = {'tags': tags} if tags else {}

    response = await taxi_eda_shortcuts.post(URL, headers=HEADERS, json=body)

    if not suggestions:
        expected_response = {'collections': [], 'suggestions': []}
    else:
        expected_suggestions = []
        for item in suggestions.values():
            expected_suggestions.append(
                {
                    'id': item['id'],
                    'title': item['title'],
                    'image_url': item['picture'],
                    'url': item['url_promo'] if is_promo else item['url'],
                },
            )
        expected_response = {
            'title': TITLE_PROMO if is_promo else TITLE,
            'url': MARKET_URL_PROMO if is_promo else MARKET_URL,
            'collections': [
                {
                    'id': 'main_market_suggestions',
                    'title': TITLE_PROMO if is_promo else TITLE,
                    'items': list(suggestions.keys()),
                },
            ],
            'suggestions': expected_suggestions,
        }

    assert response.status_code == 200
    assert response.json() == expected_response

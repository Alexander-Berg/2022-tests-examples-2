import pytest

from tests_eats_restaurant_menu import experiment
from tests_eats_restaurant_menu import util


def themed_text(text: str):
    return {'value': text, 'color': {'light': '#000000', 'dark': '#ffffff'}}


def themed_image():
    return {
        'light': 'http://eda.yandex.ru/image/light.png',
        'dark': 'http://eda.yandex.ru/image/dark.png',
    }


def themed_rgba():
    return {
        'light': {'red': 255, 'green': 255, 'blue': 255},
        'dark': {'red': 0, 'green': 0, 'blue': 0},
    }


def deeplink_action():
    return {
        'type': 'deeplink',
        'deeplink': {
            'app': 'eda.yandex://deeplink',
            'web': 'http://eda.yandex.ru/deeplink',
        },
    }


def bottom_sheet_action(title: str, text: str):
    return {'type': 'bottom_sheet', 'title': title, 'text': text}


@experiment.ENABLE_INFORMERS_CATEGORY
async def test_add_informers_category_error(
        taxi_eats_restaurant_menu, mockserver,
):
    @mockserver.handler('/eats-catalog/internal/v1/place/promos')
    def eats_catalog(request):
        return mockserver.make_response(
            status=500, json={'message': 'Test error'},
        )

    request = {'slug': 'test_slug', 'payload': {'categories': []}}

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'x-eats-user': 'user_id=21'},
    )

    assert eats_catalog.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'payload': {'categories': []}}


@experiment.ENABLE_INFORMERS_CATEGORY
@pytest.mark.translations(
    **{'eats-restaurant-menu': {'promo.category.title': {'ru': 'Акции'}}},
)
async def test_add_informers_category(taxi_eats_restaurant_menu, mockserver):
    valid_informers = [
        {
            'id': 'no_action',
            'text': themed_text('No action'),
            'icon': themed_image(),
            'background': themed_rgba(),
        },
        {
            'id': 'with_bottom_sheet',
            'text': themed_text('With bottom sheet'),
            'icon': themed_image(),
            'background': themed_rgba(),
            'action': {
                'type': 'bottom_sheet',
                'payload': bottom_sheet_action(
                    'Bottom sheet title', 'Bottom sheet text',
                ),
            },
        },
        {
            'id': 'with_deeplink',
            'text': themed_text('With deeplink'),
            'icon': themed_image(),
            'background': themed_rgba(),
            'action': {'type': 'deeplink', 'payload': deeplink_action()},
        },
    ]

    @mockserver.json_handler('/eats-catalog/internal/v1/place/promos')
    def eats_catalog(request):
        informers = valid_informers.copy()
        informers.append({'id': 'invalid', 'text': 'invalid text'})

        return {'informers': informers}

    request = {'slug': 'test_slug', 'payload': {'categories': []}}

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'x-eats-user': 'user_id=21', 'x-request-language': 'ru'},
    )

    assert eats_catalog.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'payload': {
            'categories': [
                {
                    'id': 1,
                    'name': 'Акции',
                    'available': True,
                    'categories': [],
                    'gallery': [],
                    'items': [],
                    'informers': valid_informers,
                },
            ],
        },
    }


@experiment.ENABLE_INFORMERS_CATEGORY
@pytest.mark.translations(
    **{'eats-restaurant-menu': {'promo.category.title': {'ru': 'Акции'}}},
)
@pytest.mark.parametrize(
    'handler_params, catalog_request',
    [
        pytest.param(
            {
                'latitude': '1.000000',
                'longitude': '2.000000',
                'deliveryTime': '',
            },
            {
                'position': {'lat': 1.0, 'lon': 2.0},
                'shipping_type': 'delivery',
                'slug': 'test_slug',
            },
            id='delivery_time empty string',
        ),
        pytest.param(
            {'latitude': '1.000000', 'longitude': '2.000000'},
            {
                'position': {'lat': 1.0, 'lon': 2.0},
                'shipping_type': 'delivery',
                'slug': 'test_slug',
            },
            id='no delivery_time',
        ),
        pytest.param(
            {
                'latitude': '1.000000',
                'longitude': '2.000000',
                'deliveryTime': '2022-07-11T14:28:11+03:00',
            },
            {
                'position': {'lat': 1.0, 'lon': 2.0},
                'shipping_type': 'delivery',
                'slug': 'test_slug',
                'delivery_time': '2022-07-11T11:28:11+00:00',
            },
            id='with delivery_time',
        ),
        pytest.param(
            {},
            {'shipping_type': 'delivery', 'slug': 'test_slug'},
            id='no params',
        ),
    ],
)
async def test_request_query(
        taxi_eats_restaurant_menu, mockserver, handler_params, catalog_request,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/place/promos')
    def eats_catalog(request):
        assert request.json == catalog_request

        return {'informers': []}

    request = {'slug': 'test_slug', 'payload': {'categories': []}}

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        params=handler_params,
        headers={'x-eats-user': 'user_id=21', 'x-request-language': 'ru'},
    )

    assert eats_catalog.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'payload': {'categories': []}}

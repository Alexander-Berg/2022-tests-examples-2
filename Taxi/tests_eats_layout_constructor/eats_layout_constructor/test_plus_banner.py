import pytest

from . import configs


@configs.keep_empty_layout()
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template_plus',
    },
)
@pytest.mark.experiments3(
    name='eats_layout_template_plus',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'plus_layout'},
        },
    ],
    default_value=True,
)
async def test_layout_plus_banner(taxi_eats_layout_constructor, mockserver):
    """ EDACAT-264: проверяет работу виджета баннера Яндекс.Плюс
    """

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/layout',
    )
    def plus(request):
        assert request.headers['x-yandex-uid'] == 'test_uid'
        assert request.json == {
            'location': {'latitude': 1.0, 'longitude': 2.0},
        }

        return {
            'banner': {
                'deeplink': 'http://localhost/plus',
                'icon_url': 'http://localhost/icon',
                'text_parts': [
                    {'text': 'random'},
                    {'text': 'rainbow', 'styles': {'rainbow': True}},
                    {'text': 'text', 'styles': {}},
                ],
            },
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'uuu',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
            'x-yandex-uid': 'test_uid',
        },
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    assert response.status_code == 200
    assert plus.times_called == 1

    assert response.json() == {
        'layout': [
            {
                'id': '1_plus_banner',
                'type': 'yandex_plus_banner',
                'payload': {'title': 'widget title'},
            },
        ],
        'data': {
            'yandex_plus_banners': [
                {
                    'id': '1_plus_banner',
                    'template_name': 'Plus Banner Template',
                    'payload': {
                        'deeplink': 'http://localhost/plus',
                        'icon_url': 'http://localhost/icon',
                        'text_parts': [
                            {'text': 'random'},
                            {'text': 'rainbow', 'styles': {'rainbow': True}},
                            {'text': 'text', 'styles': {}},
                        ],
                    },
                },
            ],
        },
    }

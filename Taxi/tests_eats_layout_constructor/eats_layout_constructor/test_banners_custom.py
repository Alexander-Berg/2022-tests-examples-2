import pytest

from testsuite.utils import matching

from . import configs

BANNERS_RESPONSE = {
    'payload': {
        'blocks': [],
        'banners': [
            {
                'id': 1,
                'kind': 'info',
                'formats': ['classic'],
                'payload': {'some': 'data_1'},
            },
        ],
        'header_notes': [],
    },
}


@configs.keep_empty_layout()
@pytest.mark.experiments3(
    name='layout_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'banners_custom_layout'},
        },
    ],
    default_value=True,
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'layout_template',
    },
)
@pytest.mark.parametrize(
    'expected',
    [
        (
            {
                'data': {
                    'banners': [
                        {
                            'id': '1_banners',
                            'template_name': 'Banners',
                            'payload': {
                                'design': {'type': 'classic'},
                                'banners': [
                                    {
                                        'some': 'data_1',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                        {
                            'id': '2_banners',
                            'template_name': 'Banners',
                            'payload': {
                                'design': {'type': 'classic', 'width': 'full'},
                                'banners': [
                                    {
                                        'some': 'data_1',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_banners',
                        'payload': {'title': 'Баннер как было раньше'},
                        'type': 'banners',
                    },
                    {
                        'id': '2_banners',
                        'payload': {'title': 'Баннер с новым полем'},
                        'type': 'banners',
                    },
                ],
            }
        ),
    ],
)
async def test_layout_wide_banners(
        taxi_eats_layout_constructor, mockserver, expected,
):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return BANNERS_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert banners.times_called == 1

from . import configs
from . import experiments
from . import translations
from . import utils


LAYOUT_SLUG = 'my_layout'


PLACEHOLDER_TEXT = 'Поиск по всей Еде'


@configs.keep_empty_layout()
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout(LAYOUT_SLUG, 'eats_layout_template')
@translations.eats_layout_constructor_ru(
    {'placeholder_text': PLACEHOLDER_TEXT},
)
async def test_search_bar(taxi_eats_layout_constructor, single_widget_layout):
    """
    Проверяем, что LC перекладывает ответ баннеров
    в виджет карусели
    """

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='search_bar',
        name='banners_carousel',
        meta={'placeholder': {'text': PLACEHOLDER_TEXT}},
        payload={},
        payload_schema={},
    )
    single_widget_layout(LAYOUT_SLUG, widget_template)

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

    data = response.json()
    assert data['data']['search_bar'][0]['payload'] == {
        'placeholder': {'text': PLACEHOLDER_TEXT},
    }
    assert data['layout'][0]['type'] == 'search_bar'

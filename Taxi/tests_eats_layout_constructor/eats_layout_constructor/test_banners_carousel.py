from . import configs
from . import experiments
from . import utils

LAYOUT_SLUG = 'my_layout'


def make_banner(idx: str, width: str = 'single') -> dict:
    return {
        'id': idx,
        'url': 'http://yandex.ru',
        'app_link': 'http://yandex.ru/mobile',
        'images': [
            {'url': 'img', 'theme': 'light', 'platform': 'web'},
            {'url': 'img', 'theme': 'dark', 'platform': 'web'},
        ],
        'width': width,
        'meta': {'analytics': ''},
    }


@configs.keep_empty_layout()
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout(LAYOUT_SLUG, 'eats_layout_template')
async def test_banners_carousel(
        taxi_eats_layout_constructor, mockserver, single_widget_layout,
):
    """
    Проверяем, что LC перекладывает ответ баннеров
    в виджет карусели
    """

    exps = ['exp1', 'exp2']

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='banners_carousel',
        name='banners_carousel',
        meta={'experiments': exps},
        payload={},
        payload_schema={},
    )
    single_widget_layout(LAYOUT_SLUG, widget_template)

    block_id = f'{exps[0]}_{exps[1]}'
    block_type = 'banners_carousel'

    banners = {
        'block_type': block_type,
        'pages': [
            {
                'banners': [
                    make_banner('1', 'double'),
                    make_banner('2', 'single'),
                ],
            },
        ],
    }

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def eats_comminications(request):
        blocks = request.json['blocks']
        assert len(blocks) == 1

        block = blocks[0]
        assert block['block_id'] == block_id
        assert block['type'] == block_type
        assert sorted(block['experiments']) == exps

        return {
            'payload': {
                'banners': [],
                'header_notes': [],
                'blocks': [
                    {
                        'block_id': block_id,
                        'type': block_type,
                        'payload': banners,
                    },
                ],
            },
        }

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

    assert eats_comminications.times_called == 1
    assert response.status_code == 200

    data = response.json()
    assert data['data']['banners_carousel'][0]['payload'] == banners
    assert data['layout'][0]['type'] == block_type

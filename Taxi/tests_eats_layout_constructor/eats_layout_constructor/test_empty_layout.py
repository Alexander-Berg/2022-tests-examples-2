import pytest

from . import configs
from . import utils

EXPERIMENT_NAME = 'eats_layout_template'
METRIC = 'layout-component'

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


@pytest.fixture(name='layout_metrics')
def metrics(taxi_eats_layout_constructor_monitor):
    async def get_metrics():
        data = await taxi_eats_layout_constructor_monitor.get_metrics(METRIC)
        return data['layout-component']

    return get_metrics


LAYOUT = pytest.mark.layout(
    slug='layout',
    autouse=True,
    widgets=[
        utils.Widget(
            type='banners',
            name='Banners',
            meta={'format': 'classic'},
            payload={'title': 'Баннеры'},
            payload_schema={},
        ),
        utils.Widget(
            type='separator',
            name='Separator',
            meta={'depends_on_any': ['1_banners']},
            payload={},
            payload_schema={},
        ),
        utils.Widget(
            type='search_bar',
            name='Search bar',
            meta={'placeholder': {'text': 'Поиск'}},
            payload={},
            payload_schema={},
        ),
        utils.Widget(
            type='places_collection',
            name='Places collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    ],
)


@LAYOUT
async def test_empty_layout(layout_constructor, mockserver):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return BANNERS_RESPONSE

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': 'open', 'list': []}],
        }

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert response.json() == {'layout': [], 'data': {}}
    assert catalog.times_called == 1
    assert banners.times_called == 1


@LAYOUT
@pytest.mark.parametrize(
    'diff_seen,diff_kept',
    [
        pytest.param(1, 0, id='no kept'),
        pytest.param(
            1,
            1,
            marks=configs.keep_empty_layout('layout'),
            id='kept by config',
        ),
    ],
)
async def test_empty_layout_metrics(
        layout_constructor, mockserver, layout_metrics, diff_seen, diff_kept,
):
    metrics_before = await layout_metrics()
    empty_seen = metrics_before['layouts.empty.seen']
    empty_kept = metrics_before['layouts.empty.kept']

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return BANNERS_RESPONSE

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': 'open', 'list': []}],
        }

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert catalog.times_called == 1
    assert banners.times_called == 1

    metrics_after = await layout_metrics()
    assert metrics_after['layouts.empty.seen'] == empty_seen + diff_seen
    assert metrics_after['layouts.empty.kept'] == empty_kept + diff_kept

import copy
import typing

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=unused-variable, redefined-outer-name
import pytest

from eats_layout_constructor_plugins import *  # noqa: F403 F401

from eats_layout_constructor import communications
from eats_layout_constructor import experiments
from eats_layout_constructor import utils


DEFAULT_LOCATION = {'latitude': 55.750028, 'longitude': 37.534397}

DEFAULT_HEADERS = {
    'x-device-id': 'dev_id',
    'x-platform': 'ios_app',
    'x-app-version': '12.11.12',
    'cookie': '{}',
    'X-Eats-User': 'user_id=12345',
    'x-request-application': 'application=1.1.0',
    'x-request-language': 'ru',
    'Content-Type': 'application/json',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_regions_cache: [eats_regions_cache] '
        'fixture for regions cache',
    )
    config.addinivalue_line(
        'markers', 'layout: [layout] ' 'fixture for creating layouts',
    )


@pytest.fixture(autouse=True)
def taxi_exp_mock_server(mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def mock_taxi_exp(request):
        return {
            'default_value': {'layout_slug': 'layout_100'},
            'clauses': [
                {'title': '1', 'value': {'layout_slug': 'layout_101'}},
            ],
        }


@pytest.fixture(autouse=True)
def meta_widgets(pgsql):
    class Context:
        def add_meta_widget(self, meta_widget: utils.MetaWidget):
            utils.add_meta_widget(pgsql, meta_widget)

    return Context()


@pytest.fixture(name='layouts')
def layouts(pgsql):
    class Context:
        def add_layout(self, layout: utils.Layout):
            utils.add_layout(pgsql, layout)

    return Context()


@pytest.fixture(name='widget_templates')
def widget_templates(pgsql):
    class Context:
        def add_widget_template(self, widget_template: utils.WidgetTemplate):
            utils.add_widget_template(pgsql, widget_template)

    return Context()


@pytest.fixture(autouse=True, name='layout_widgets')
def layout_widgets(pgsql):
    class Context:
        def add_layout_widget(self, layout_widget: utils.LayoutWidget):
            utils.add_widget(pgsql, layout_widget)

    return Context()


@pytest.fixture(autouse=True, name='single_widget_layout')
def single_widget_layout(layouts, widget_templates, layout_widgets):
    """
    Вспомогательная фикстура, чтобы за 1 вызов
    создавать лейаут с одним заданным виджетом
    """

    def set_widget_layout(
            layout_slug: str, widget_template: utils.WidgetTemplate,
    ):
        layout = utils.Layout(layout_id=1, name=layout_slug, slug=layout_slug)
        layouts.add_layout(layout)

        widget_templates.add_widget_template(widget_template)

        layout_widget = utils.LayoutWidget(
            name='widget',
            widget_template_id=widget_template.widget_template_id,
            layout_id=layout.layout_id,
            meta={},
            payload={},
        )
        layout_widgets.add_layout_widget(layout_widget)

    return set_widget_layout


@pytest.fixture(name='layout', autouse=True)
async def layout(
        request,
        taxi_eats_layout_constructor,
        pgsql,
        experiments3,
        taxi_config,
):
    experiment_name = 'this_is_layout_experiment'

    async def create_layout(
            slug: str,
            widgets: typing.List[utils.Widget],
            autouse: bool = False,
    ):
        utils.create_layout(pgsql, slug, widgets)
        if autouse:
            taxi_config.set_values(
                {
                    'EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS': {
                        'check_experiment': True,
                        'refresh_period_ms': 1000,
                        'experiment_name': experiment_name,
                        'recommendations_experiment_name': None,
                        'collections_experiment_name': None,
                        'filters_experiment_name': None,
                        'map_experiment_name': None,
                    },
                },
            )

            experiments3.add_experiment(
                name=experiment_name,
                match=experiments.ALWAYS,
                consumers=['layout-constructor/layout'],
                clauses=[
                    {
                        'title': 'Always match',
                        'value': {'layout_slug': slug},
                        'predicate': {'type': 'true'},
                    },
                ],
            )

        await taxi_eats_layout_constructor.invalidate_caches()

    for marker in request.node.iter_markers('layout'):
        if 'slug' not in marker.kwargs:
            raise Exception(
                'missing required argument "slug" in layout marker',
            )

        await create_layout(
            slug=marker.kwargs['slug'],
            widgets=marker.kwargs.get('widgets', []),
            autouse=marker.kwargs.get('autouse', False),
        )

    return create_layout


@pytest.fixture(name='layout_constructor')
def eats_layout_constructor(taxi_eats_layout_constructor):
    class Context:
        async def post(
                self,
                location: dict = None,
                filters_v2: dict = None,
                headers: dict = None,
                region_id: int = None,
        ):
            request_headers = copy.deepcopy(DEFAULT_HEADERS)
            if headers is not None:
                request_headers.update(headers)

            if location is None:
                location = DEFAULT_LOCATION

            request_body = {
                'location': location,
                'region_id': region_id,
                **({'filters_v2': filters_v2} if filters_v2 else {}),
            }
            return await taxi_eats_layout_constructor.post(
                'eats/v1/layout-constructor/v1/layout',
                headers=request_headers,
                json=request_body,
            )

    return Context()


@pytest.fixture(name='eats_communications')
def _mock_eats_communications(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.status = 200
            self.banners = []
            self.blocks = []
            self.request_assertion_callback = do_nothing

        def set_status(self, status: int) -> None:
            self.status = status

        def add_banner(self, banner: communications.LayoutBanner) -> None:
            self.banners.append(banner)

        def add_banners(
                self, banners: typing.List[communications.LayoutBanner],
        ) -> None:
            self.banners.extend(banners)

        def add_block(self, block: communications.Block) -> None:
            self.blocks.append(block)

        def add_blocks(
                self, blocks: typing.List[communications.Block],
        ) -> None:
            self.blocks.extend(blocks)

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        @property
        def times_called(self) -> int:
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def handler(request):
        ctx.request_assertion_callback(request)

        blocks = [block.asdict() for block in ctx.blocks]
        banners = [banner.asdict() for banner in ctx.banners]

        return mockserver.make_response(
            status=ctx.status,
            json={
                'payload': {
                    'blocks': blocks,
                    'banners': banners,
                    'header_notes': [],
                },
            },
        )

    return ctx


@pytest.fixture(name='eats_order_stats', autouse=True)
async def eats_order_stats(
        mockserver, retail_orders=3, restaurant_orders=3, error_code=None,
):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    async def _mock_eats_order_stats():
        if error_code:
            return mockserver.make_response(status=error_code)

        return utils.order_stats_response(
            retail_orders_count=retail_orders,
            restaurant_orders_count=restaurant_orders,
        )

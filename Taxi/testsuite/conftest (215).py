import typing

import pytest

from tests_eats_communications import adverts

# root conftest for service eats-communications
pytest_plugins = ['eats_communications_plugins.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'grocery_tags' 'fixture for grocery user tags',
    )
    config.addinivalue_line(
        'markers', 'bigb: [bigb]' 'fixture for bigb client',
    )
    config.addinivalue_line(
        'markers',
        (
            'bulk_experiments: [bulk_experiments]'
            'fixture for bulk creation experiments '
            'with same value and different name'
        ),
    )


@pytest.fixture(autouse=True)
def catalog(mockserver):
    @mockserver.handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(_):
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(autouse=True)
def collections(mockserver):
    @mockserver.handler('/eats-collections/internal/v1/collections')
    def _collections(_):
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(autouse=True)
def inapp_communications(mockserver):
    @mockserver.handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _eda_communications(_):
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(autouse=True)
def corp_users(mockserver):
    @mockserver.handler('/corp-users/v1/users-limits/eats/fetch')
    def _corp_users(_):
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(autouse=True)
def use_promo(mockserver):
    @mockserver.handler('/eda-delivery-price/v1/user-promo')
    def _eda_delivery_price(_):
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(autouse=True)
def grocery_tags(request, mockserver):

    response: typing.Optional[typing.Dict] = None

    marker = request.node.get_closest_marker('grocery_tags')
    if marker and marker.args:
        response = marker.args[0]

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/user-tags',
    )
    def _grocery_tags(_):
        if response is not None:
            return response
        return mockserver.make_response(json={}, status=500)


@pytest.fixture(name='eats_catalog')
def eats_catalog_mock(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.blocks = list()

        def set_status_code(self, status_code: int) -> None:
            self.status_code = status_code

        def add_block(self, block: dict) -> None:
            if 'stats' not in block:
                block['stats'] = {'places_count': len(block['list'])}

            self.blocks.append(block)

        def add_blocks(self, blocks: typing.List[dict]) -> None:
            self.blocks.extend(blocks)

        @property
        def times_called(self) -> int:
            return v1_places.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-catalog/internal/v1/places')
    def v1_places(request):
        return mockserver.make_response(
            status=ctx.status_code, json={'blocks': ctx.blocks},
        )

    return ctx


@pytest.fixture(name='yabs')
def yabs_mock(mockserver):
    class Context:
        def __init__(self, page_id: int = 1):
            self.status_code = 200
            self.page_id = page_id
            self.assertion = None
            self.response = adverts.MetaBannersetResponse()

        def set_status_code(self, status_code: int) -> None:
            self.status_code = status_code

        def set_page_id(self, page_id: int) -> None:
            self.page_id = page_id

        def set_assertion(self, assertion) -> None:
            self.assertion = assertion

        def set_response(
                self, response: adverts.MetaBannersetResponse,
        ) -> None:
            self.response = response

        @property
        def times_called(self) -> int:
            return meta_bannerset.times_called

    ctx = Context()

    @mockserver.json_handler(f'/yabs/meta_bannerset/{ctx.page_id}')
    def meta_bannerset(request):
        if ctx.assertion:
            ctx.assertion(request)

        return mockserver.make_response(
            status=ctx.status_code, json=ctx.response.asdict(),
        )

    return ctx


@pytest.fixture(name='bulk_experiments', autouse=True)
def bulk_experiments(request, experiments3):
    def wrapper(consumer, names, value):
        for name in names:
            experiments3.add_experiment(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name=name,
                consumers=[consumer],
                clauses=[
                    {
                        'title': 'Always match',
                        'value': value,
                        'predicate': {'type': 'true'},
                    },
                ],
            )

    for marker in request.node.iter_markers('bulk_experiments'):
        wrapper(**marker.kwargs)

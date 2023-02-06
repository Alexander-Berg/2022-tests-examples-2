import pytest

# pylint: disable=import-error
# pylint: disable=C0302
from eats_analytics import eats_analytics
from testsuite.utils import matching


from . import communications
from . import configs
from . import experiments
from . import utils

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
            {
                'id': 2,
                'kind': 'place',
                'formats': ['shortcut'],
                'payload': {'some': 'data_2'},
            },
            {
                'id': 3,
                'kind': 'collection',
                'formats': ['classic', 'shortcut'],
                'payload': {'some': 'data_3'},
            },
            {
                'id': 4,
                'kind': 'info',
                'formats': ['wide_and_short'],
                'payload': {'some': 'data_4'},
            },
        ],
        'header_notes': [],
    },
}


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@pytest.mark.parametrize(
    'platform,expected',
    [
        pytest.param(
            'android_app',
            {
                'layout': [
                    {
                        'id': '1_banners',
                        'payload': {'title': 'Баннеры'},
                        'type': 'banners',
                    },
                ],
                'data': {
                    'banners': [
                        {
                            'id': '1_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'classic'},
                                'banners': [
                                    {
                                        'some': 'data_1',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            marks=experiments.layout('layout_1'),
        ),
        pytest.param(
            'ios_app',
            {
                'layout': [
                    {
                        'id': '2_banners',
                        'payload': {'title': 'Баннеры'},
                        'type': 'banners',
                    },
                ],
                'data': {
                    'banners': [
                        {
                            'id': '2_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'classic'},
                                'banners': [
                                    {
                                        'some': 'data_1',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            marks=experiments.layout('layout_2'),
        ),
        pytest.param(
            'mobile_web',
            {
                'layout': [
                    {
                        'id': '3_banners',
                        'payload': {'title': 'Баннеры'},
                        'type': 'banners',
                    },
                ],
                'data': {
                    'banners': [
                        {
                            'id': '3_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'shortcut'},
                                'banners': [
                                    {
                                        'some': 'data_2',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            marks=experiments.layout('layout_3'),
        ),
        pytest.param(
            'superapp_pp_web',
            {
                'layout': [
                    {
                        'id': '4_banners',
                        'payload': {'title': 'Баннеры'},
                        'type': 'banners',
                    },
                ],
                'data': {
                    'banners': [
                        {
                            'id': '4_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'classic'},
                                'banners': [
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            marks=experiments.layout('layout_4'),
        ),
        pytest.param(
            'desktop_web',
            {
                'layout': [
                    {
                        'id': '5_banners',
                        'payload': {'title': 'Баннеры'},
                        'type': 'banners',
                    },
                ],
                'data': {
                    'banners': [
                        {
                            'id': '5_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'classic'},
                                'banners': [
                                    {
                                        'some': 'data_1',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            marks=experiments.layout('layout_5'),
        ),
        pytest.param(
            'superapp_taxi_web',
            {
                'data': {
                    'banners': [
                        {
                            'id': '6_banners',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'design': {'type': 'shortcut'},
                                'banners': [
                                    {
                                        'some': 'data_2',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                        {
                            'id': '8_banners',
                            'template_name': 'Widget template 1',
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
                    ],
                },
                'layout': [
                    {
                        'id': '6_banners',
                        'payload': {'title': 'Баннеры shortcut'},
                        'type': 'banners',
                    },
                    {
                        'id': '8_banners',
                        'payload': {
                            'title': (
                                'Попадет только первый баннер из-за limit'
                            ),
                        },
                        'type': 'banners',
                    },
                ],
            },
            marks=experiments.layout('layout_6'),
        ),
    ],
)
async def test_layout_banners(
        layout_constructor, mockserver, platform, expected,
):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return BANNERS_RESPONSE

    response = await layout_constructor.post(headers={'x-platform': platform})

    assert response.status_code == 200
    assert response.json() == expected
    assert banners.times_called == 1


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('source_not_required')
async def test_layout_headers(layout_constructor, mockserver):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        assert request.headers['cookie'] == 'foo_cookie'
        assert request.headers['user-agent'] == '007'
        assert request.headers['x-request-id'] == '123'
        assert request.headers['X-Yandex-Login'] == 'foo_login'
        assert request.headers['X-YaTaxi-UserId'] == 'foo_user'
        assert request.headers['X-YaTaxi-PhoneId'] == 'foo_phone'
        return BANNERS_RESPONSE

    response = await layout_constructor.post(
        headers={
            'x-platform': 'ios_app',
            'cookie': 'foo_cookie',
            'user-agent': '007',
            'x-request-id': '123',
            'X-Yandex-Login': 'foo_login',
            'X-YaTaxi-UserId': 'foo_user',
            'X-YaTaxi-PhoneId': 'foo_phone',
        },
    )

    assert response.status_code == 200
    assert banners.times_called == 1


@configs.keep_empty_layout()
@pytest.mark.experiments3(
    name='wide_banners',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'shortcut_wide'},
        },
    ],
    default_value=True,
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'wide_banners',
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
                            'id': '11_banners',
                            'template_name': 'shortcuts',
                            'payload': {
                                'design': {'type': 'shortcut'},
                                'banners': [
                                    {
                                        'some': 'data_2',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'some': 'data_3',
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                            },
                        },
                        {
                            'id': '12_banners',
                            'template_name': 'wide_banner',
                            'payload': {
                                'design': {'type': 'wide_and_short'},
                                'banners': [
                                    {
                                        'some': 'data_4',
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
                        'id': '11_banners',
                        'payload': {'title': 'шорткаты'},
                        'type': 'banners',
                    },
                    {'id': '12_banners', 'payload': {}, 'type': 'banners'},
                ],
            }
        ),
    ],
)
async def test_layout_wide_banners(layout_constructor, mockserver, expected):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return BANNERS_RESPONSE

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert response.json() == expected
    assert banners.times_called == 1


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('source_not_required')
@pytest.mark.parametrize(
    'platform,expected,code',
    [pytest.param('ios_app', {'data': {}, 'layout': []}, 200)],
)
async def test_banners_not_available(
        layout_constructor, mockserver, platform, expected, code,
):
    @mockserver.handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return mockserver.make_response('{}', status=500)

    response = await layout_constructor.post(headers={'x-platform': platform})

    assert response.status_code == code
    assert response.json() == expected
    assert banners.times_called == 1


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('random_banners')
async def test_banners_randomize(layout_constructor, mockserver):
    """
    EDACAT-1138: тест проверяет, что в случае галки `randomize`, порядок
    баннеров между запросами не сохраняется.

    NOTE: этот тест может флапать, т.к. фактически проверятеся рандом.
    """

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def _banners(request):
        banners = []
        for i in range(1, 100):
            banners.append(
                {
                    'id': i,
                    'kind': 'info',
                    'formats': ['classic', 'shortcut'],
                    'payload': {'id': i},
                },
            )
        return {
            'payload': {'blocks': [], 'banners': banners, 'header_notes': []},
        }

    async def request_layout(layout_constructor):
        response = await layout_constructor.post()
        assert response.status_code == 200

        data = response.json()['data']
        assert 'banners' in data
        assert data['banners']

        banners = data['banners'][0]['payload']['banners']
        assert banners

        banner_ids = []
        for banner in banners:
            banner_ids.append(banner['id'])

        return banner_ids

    first_banner_ids = await request_layout(layout_constructor)
    second_banner_ids = await request_layout(layout_constructor)

    assert first_banner_ids != second_banner_ids


@configs.keep_empty_layout()
@pytest.mark.experiments3(
    name='layout_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'conditional_banners'},
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
    'surge_count, has_banner',
    [
        pytest.param(10, True, id='has block'),
        pytest.param(0, False, id='no block'),
    ],
)
async def test_conditional_banners(
        layout_constructor, mockserver, surge_count, has_banner,
):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return {
            'payload': {
                'blocks': [],
                'banners': [
                    {
                        'id': 1,
                        'kind': 'info',
                        'formats': ['classic'],
                        'payload': {'id': 1},
                    },
                ],
                'header_notes': [],
            },
        }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json == {
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'blocks': [
                {
                    'id': '17_banners',
                    'type': 'open',
                    'disable_filters': False,
                    'no_data': True,
                    'limit': 10,
                    'round_eta_to_hours': False,
                    'condition': {
                        'type': 'all_of',
                        'predicates': [
                            {
                                'type': 'neq',
                                'init': {
                                    'arg_name': 'business',
                                    'arg_type': 'string',
                                    'value': 'shop',
                                },
                            },
                        ],
                    },
                },
            ],
        }

        return {
            'blocks': [
                {
                    'id': '17_banners',
                    'list': [],
                    'stats': {
                        'places_count': 10,
                        'native_surge_places_count': surge_count,
                        'market_surge_places_count': 1,
                        'orders_count': 0,
                        'radius_surge_orders_count': 0,
                    },
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert banners.times_called == 1
    assert catalog.times_called == 1

    data = response.json()
    if has_banner:
        assert 'banners' in data['data']
        assert data['data']['banners']
        assert len(data['data']['banners'][0]['payload']['banners']) == 1
    else:
        assert 'banners' not in data['data']


@pytest.mark.layout(
    slug='banners_radius_surge_orders',
    widgets=[
        utils.Widget(
            name='banners_1',
            type='banners',
            meta={
                'format': 'classic',
                'surge_condition': {
                    'limit': 10,
                    'min_radius_surge_orders_percent': 50,
                },
            },
            payload={'title': 'Баннеры'},
            payload_schema={},
        ),
    ],
)
@experiments.layout('banners_radius_surge_orders')
@configs.layout_experiment_name()
@configs.keep_empty_layout()
@pytest.mark.parametrize(
    'radius_surge_orders, orders, has_banner',
    [
        pytest.param(50, 100, True, id='has block'),
        pytest.param(49, 100, False, id='no block'),
    ],
)
async def test_conditional_radius_surge_orders_banners(
        layout_constructor,
        mockserver,
        radius_surge_orders,
        orders,
        has_banner,
):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        return {
            'payload': {
                'blocks': [],
                'banners': [
                    {
                        'id': 1,
                        'kind': 'info',
                        'formats': ['classic'],
                        'payload': {'id': 1},
                    },
                ],
                'header_notes': [],
            },
        }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json == {
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'blocks': [
                {
                    'id': '1_banners',
                    'type': 'open',
                    'round_eta_to_hours': False,
                    'disable_filters': False,
                    'no_data': True,
                    'limit': 10,
                },
            ],
        }

        return {
            'blocks': [
                {
                    'id': '1_banners',
                    'list': [],
                    'stats': {
                        'places_count': 10,
                        'native_surge_places_count': 0,
                        'market_surge_places_count': 0,
                        'orders_count': orders,
                        'radius_surge_orders_count': radius_surge_orders,
                    },
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert banners.times_called == 1
    assert catalog.times_called == 1

    data = response.json()
    if has_banner:
        assert 'banners' in data['data']
        assert data['data']['banners']
        assert len(data['data']['banners'][0]['payload']['banners']) == 1
    else:
        assert 'banners' not in data['data']


@pytest.mark.layout(
    slug='banners_limit_offset',
    widgets=[
        utils.Widget(
            name='banners_0_2',
            type='banners',
            meta={'format': 'classic', 'limit': 2},
            payload={'title': 'Баннеры'},
            payload_schema={},
        ),
        utils.Widget(
            name='banners_0_2_again',
            type='banners',
            meta={'format': 'classic', 'offset': 0, 'limit': 2},
            payload={'title': 'Баннеры'},
            payload_schema={},
        ),
        utils.Widget(
            name='banners_2_4',
            type='banners',
            meta={'format': 'classic', 'offset': 2, 'limit': 2},
            payload={'title': 'Еще баннеры'},
            payload_schema={},
        ),
    ],
)
@experiments.layout('banners_limit_offset')
@configs.layout_experiment_name()
@configs.keep_empty_layout()
async def test_banner_offset_limit(layout_constructor, mockserver):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(_):
        banners = []
        for i in range(1, 100):
            banners.append(
                {
                    'id': i,
                    'kind': 'info',
                    'formats': ['classic', 'shortcut'],
                    'payload': {'id': i},
                },
            )
        return {
            'payload': {'blocks': [], 'banners': banners, 'header_notes': []},
        }

    response = await layout_constructor.post()

    assert response.status_code == 200

    assert banners.times_called == 1

    data = response.json()

    ids = [[1, 2], [1, 2], [3, 4]]

    widgets = data['data']['banners']
    assert len(widgets) == len(ids)

    index = 0
    for widget_data in widgets:
        assert len(widget_data['payload']['banners']) == 2
        assert ids[index] == [
            banner['id'] for banner in widget_data['payload']['banners']
        ]
        index += 1


@pytest.mark.layout(
    slug='banners',
    widgets=[
        utils.Widget(
            name='banners',
            type='banners',
            meta={'format': 'classic'},
            payload={'title': 'Заголовок виджета'},
            payload_schema={},
        ),
    ],
)
@experiments.layout('banners')
@configs.layout_experiment_name()
@configs.keep_empty_layout()
async def test_analytics_context(layout_constructor, mockserver):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def eats_communications(_):
        banners = []
        for i in range(1, 10):
            banners.append(
                {
                    'id': i,
                    'kind': 'info',
                    'formats': ['classic', 'shortcut'],
                    'payload': {
                        'id': i,
                        'meta': {
                            'analytics': eats_analytics.encode(
                                eats_analytics.AnalyticsContext(
                                    item_id=str(i),
                                    banner_width=(
                                        eats_analytics.BannerWidth.SINGLE
                                    ),
                                ),
                            ),
                        },
                    },
                },
            )
        return {
            'payload': {'blocks': [], 'banners': banners, 'header_notes': []},
        }

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert eats_communications.times_called == 1

    data = response.json()

    widgets = data['data']['banners']
    assert len(widgets) == 1

    banners = widgets[0]['payload']['banners']

    i = 1
    for banner in banners:
        expected_context = eats_analytics.AnalyticsContext(
            item_id=str(i),
            widget_id='1_banners',
            widget_template_id='banners_template',
            item_position=eats_analytics.Position(column=i - 1, row=0),
            widget_title='Заголовок виджета',
            banner_type=eats_analytics.BannerType.CLASSIC,
            banner_width=eats_analytics.BannerWidth.SINGLE,
        )

        assert (
            eats_analytics.decode(banner['meta']['analytics'])
            == expected_context
        )
        i += 1


@pytest.mark.layout(
    slug='banners_with_filters',
    widgets=[
        utils.Widget(
            name='banners',
            type='banners',
            meta={'format': 'classic'},
            payload={'title': 'Заголовок виджета'},
            payload_schema={},
        ),
        utils.Widget(
            name='filters',
            type='filters',
            meta={},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='filters_layout',
                slug='my_meta_widget',
                name='Filters Meta Widget',
                settings={
                    'bottom_sheet': {
                        'filters_blocks': [
                            {
                                'condition': 'or',
                                'groups': ['filter_group'],
                                'slug': 'first',
                            },
                        ],
                        'filters_groups': [
                            {
                                'include_slugs': ['sushi', 'burgers'],
                                'include_types': ['quickfilter'],
                                'slug': 'filter_group',
                                'style': 'grid',
                            },
                        ],
                        'icon': {
                            'name': 'Все фильтры',
                            'url': 'assets://all_filters',
                        },
                        'layout': [
                            {
                                'name': 'Кухни',
                                'slug': 'first',
                                'type': 'filters',
                            },
                        ],
                    },
                    'filters_v2': True,
                    'list': {
                        'filters_groups': [
                            {'include_slugs': ['sushi', 'burgers', 'pizza']},
                        ],
                    },
                },
            ),
        ),
    ],
)
@configs.layout_experiment_name()
@experiments.layout('banners_with_filters')
@experiments.meta_widget('my_meta_widget')
async def test_pass_filters_with_groups_to_banners(
        layout_constructor, mockserver,
):
    """
    Тест проверяет, что фильтры 2.0 передаются в запрос баннеров из
    eats-communications и объединяются в логические группы
    """

    expected_fiters_v2 = {
        'groups': [
            {
                'type': 'or',
                'filters': [
                    {'type': 'quickfilter', 'slug': 'burgers'},
                    {'type': 'quickfilter', 'slug': 'sushi'},
                ],
            },
            {
                'type': 'and',
                'filters': [{'type': 'quickfilter', 'slug': 'pizza'}],
            },
        ],
    }

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def banners(request):
        assert request.json['filters_v2'] == expected_fiters_v2
        return {'payload': {'blocks': [], 'banners': [], 'header_notes': []}}

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return {
            'blocks': [],
            'sort': {
                'current': 'default',
                'default': 'default',
                'list': [{'slug': 'default'}],
            },
            'timepicker': [],
        }

    response = await layout_constructor.post(
        filters_v2={
            'filters': [
                {'type': 'quickfilter', 'slug': 'burgers'},
                {'type': 'quickfilter', 'slug': 'sushi'},
                {'type': 'quickfilter', 'slug': 'pizza'},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'data': {}, 'layout': []}

    assert banners.times_called == 1
    assert catalog.times_called == 1


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('layout')
@pytest.mark.layout(
    slug='layout',
    widgets=[
        utils.Widget(
            name='widget_1',
            type='banners',
            meta={'format': 'shortcut'},
            payload={'title': 'Шорткаты'},
            payload_schema={},
        ),
        utils.Widget(
            name='widget_2',
            type='banners',
            meta={'format': 'classic', 'offset': 0, 'limit': 2},
            payload={'title': 'Немного классики'},
            payload_schema={},
        ),
        utils.Widget(
            name='widget_3',
            type='banners',
            meta={'format': 'classic', 'offset': 2, 'limit': 3},
            payload={'title': 'Еще немного классики'},
            payload_schema={},
        ),
    ],
)
async def test_banners_offset_limit_filters(
        layout_constructor, eats_communications,
):
    """
    EDACAT-2464: проверяет, что баннеры корректно раскладываются по виджетам.
    """

    banners = [
        communications.LayoutBanner(
            id=1,
            formats=[
                communications.Format.Classic,
                communications.Format.Shortcut,
            ],
        ),
        communications.LayoutBanner(
            id=2, formats=[communications.Format.Shortcut],
        ),
        communications.LayoutBanner(
            id=3, formats=[communications.Format.Shortcut],
        ),
        communications.LayoutBanner(
            id=4, formats=[communications.Format.Classic],
        ),
        communications.LayoutBanner(
            id=5, formats=[communications.Format.Shortcut],
        ),
        communications.LayoutBanner(
            id=6, formats=[communications.Format.Classic],
        ),
        communications.LayoutBanner(
            id=7, formats=[communications.Format.Classic],
        ),
        communications.LayoutBanner(
            id=8, formats=[communications.Format.Classic],
        ),
        communications.LayoutBanner(
            id=9, formats=[communications.Format.Classic],
        ),
    ]

    eats_communications.add_banners(banners)

    response = await layout_constructor.post()
    assert response.status_code == 200
    assert eats_communications.times_called == 1

    banners_ids = [[1, 2, 3, 5], [1, 4], [6, 7, 8]]

    data = response.json()['data']
    assert 'banners' in data

    banner_widgets = data['banners']
    assert len(banners_ids) == len(banner_widgets)

    for banner_ids, banner_widget in zip(banners_ids, banner_widgets):
        payload = banner_widget['payload']
        assert 'banners' in payload

        widget_banners = payload['banners']
        assert len(banner_ids) == len(widget_banners)
        assert banner_ids == [banner['id'] for banner in widget_banners]

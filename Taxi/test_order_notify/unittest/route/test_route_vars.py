import typing

import pytest

from order_notify.generated.service.swagger.models.api import TemplateData
from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.route import route_vars
from order_notify.repositories.route.route_info import RouteData

DEFAULT_ORDER_DATA = OrderData(
    brand='yataxi',
    country='rus',
    order={},
    order_proc={
        '_id': '1',
        'order': {'application': 'yataxi', 'calc': {'distance': 1287.6}},
    },
)

DEFAULT_ROUTE_DATA = RouteData(
    source={'short_text': 'short'},
    destinations=[{'short_text': 'dst'}],
    final_destination=None,
    track_points=[[2.2, 3.3]],
)

LOCALIZED_ROUTE_DATA = RouteData(
    source={'short_text': 'шорт'},
    destinations=[{'short_text': 'дст'}],
    final_destination={'short_text': 'По требованию'},
    track_points=[[2.2, 3.3]],
)


@pytest.fixture(name='mock_functions')
def mock_template_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_route_data = Counter()
            self.create_map_url = Counter()
            self.localize_route_data_short_text = Counter()
            self.is_destinations_changed = Counter()
            self.round_distance = Counter()

    counters = Counters()

    @patch('order_notify.repositories.route.route_info.get_route_data')
    async def _get_route_data(
            context: stq_context.Context, order_data: OrderData,
    ) -> RouteData:
        counters.get_route_data.call()
        assert order_data == DEFAULT_ORDER_DATA
        return DEFAULT_ROUTE_DATA

    @patch('order_notify.repositories.route.map.create_map_url')
    def _create_map_url(*args, **kwargs) -> str:
        counters.create_map_url.call()
        return 'map'

    @patch(
        'order_notify.repositories.localization.geo_objects.'
        'localize_route_data',
    )
    async def _localize_route_data(
            context: stq_context.Context,
            route_data: RouteData,
            locale: typing.Optional[str],
    ) -> RouteData:
        counters.localize_route_data_short_text.call()
        assert route_data == DEFAULT_ROUTE_DATA
        assert locale == 'ru'
        return LOCALIZED_ROUTE_DATA

    @patch(
        'order_notify.repositories.route.route_vars.'
        'is_destinations_changed',
    )
    def _is_destinations_changed(order_data: OrderData) -> bool:
        counters.is_destinations_changed.call()
        assert order_data == DEFAULT_ORDER_DATA
        return False

    @patch('order_notify.repositories.route.route_vars.round_distance')
    def _round_distance(
            context: stq_context.Context, meters: float, locale: str,
    ) -> str:
        counters.round_distance.call()
        assert meters == 1287.6
        assert locale == 'ru'
        return '1,2 км'

    return counters


@pytest.mark.translations(
    notify={'report.unknown_destination': {'ru': 'По требованию'}},
)
async def test_get_route_vars(
        stq3_context: stq_context.Context, mock_functions,
):
    expected_route_section_vars = {
        'src_pt': 'шорт',
        'dst_points': ['дст'],
        'dst_pt': 'По требованию',
        'destination_changed': False,
        'sizeless_maps_url': 'map',
        'map_size': '&size=500,256',
        'ride_dist_round': '1,2 км',
    }

    route_section_vars = await route_vars.get_route_vars(
        context=stq3_context,
        order_data=DEFAULT_ORDER_DATA,
        template_data=TemplateData(
            logo_url='logo_url_yango',
            map_size='500,256',
            from_name='yango',
            taxi_host='yango.yandex.com',
            from_email='yango@yandex.ru',
            support_url='https://yandex.com/support/yango/',
            campaign_slug='OS9GFZ94-YMV1',
            show_fare_with_vat_only=True,
            show_ogrn_and_unp=False,
            show_order_id=True,
            show_user_fullname=False,
            receipt_mode='receipt',
            send_pdf=False,
            extended_uber_report=False,
            map_first_point_color='comma_solid_red',
            map_last_point_color='comma_solid_blue',
            map_line_color='3C3C3CFF',
            map_line_width=3,
            map_mid_point_color='trackpoint',
            map_url='https://{}/get-map/1.x/',
        ),
        locale='ru',
    )
    assert route_section_vars == expected_route_section_vars
    assert mock_functions.get_route_data.times_called == 1
    assert mock_functions.create_map_url.times_called == 1
    assert mock_functions.localize_route_data_short_text.times_called == 1
    assert mock_functions.is_destinations_changed.times_called == 1
    assert mock_functions.round_distance.times_called == 1


@pytest.mark.parametrize(
    'order_proc, is_dst_changed_expected',
    [
        pytest.param({}, False, id='no_changes'),
        pytest.param({'changes': {}}, False, id='no_objects'),
        pytest.param(
            {'changes': {'objects': [{'n': 'smth', 's': 'applying'}]}},
            False,
            id='no_destinations_but_applying',
        ),
        pytest.param(
            {'changes': {'objects': [{'n': 'smth', 's': 'applied'}]}},
            False,
            id='no_destinations_but_applied',
        ),
        pytest.param(
            {'changes': {'objects': [{'n': 'destinations', 's': 'failed'}]}},
            False,
            id='destinations_not_applied_or_applying',
        ),
        pytest.param(
            {'changes': {'objects': [{'n': 'destinations', 's': 'applied'}]}},
            True,
            id='destinations_applied_not_applying',
        ),
        pytest.param(
            {'changes': {'objects': [{'n': 'destinations', 's': 'applying'}]}},
            True,
            id='destinations_not_applied_but_applying',
        ),
    ],
)
def test_is_destinations_changed(order_proc, is_dst_changed_expected: bool):
    is_dst_changed = route_vars.is_destinations_changed(
        OrderData(brand='', country='', order={}, order_proc=order_proc),
    )
    assert is_dst_changed == is_dst_changed_expected

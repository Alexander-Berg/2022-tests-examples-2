import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.route import map as map_url
from order_notify.repositories.route.route_info import RouteData
from test_order_notify.conftest import DEFAULT_TEMPLATE_DATA


@pytest.mark.config(
    {'__default__': {'l': 'map'}, 'yauber': {'l': 'external_taxi'}},
)
@pytest.mark.parametrize(
    'brand, locale, route_data, template_data, expected_url',
    [
        pytest.param(
            'yataxi',
            'ru',
            RouteData(
                source={'geopoint': [45.758991, 28.597506]},
                destinations=[{'geopoint': [57.534, 15.750]}],
                final_destination={'geopoint': [2.340111, 48.855311]},
                track_points=[[37.534, 55.750]],
            ),
            DEFAULT_TEMPLATE_DATA,
            'https://tc.tst.mobile.yandex.net/get-map/1.x/?l=map&cr=0&lg=0'
            '&scale=1&lang=ru&pt=45.75899,28.59751,comma_solid_red~57.53400'
            ',15.75000,trackpoint~2.34011,48.85531,trackpoint&bbox=-2.25754,'
            '12.41800~62.13165,59.08200',
        ),
    ],
)
async def test_create_map_url(
        stq3_context: stq_context.Context,
        brand,
        locale,
        route_data,
        template_data,
        expected_url,
):
    url = map_url.create_map_url(
        context=stq3_context,
        brand=brand,
        locale=locale,
        template_data=template_data,
        route_data=route_data,
    )
    assert url == expected_url

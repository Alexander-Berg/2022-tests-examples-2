# flake8: noqa: I100
# pylint: disable=broad-except
import pytest
from aiohttp import web

from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    get_order_price,
)


@pytest.mark.config(
    APPLICATION_MAP_BRAND={'call_center': 'some_brand'},
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+799976543321': {
            'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
            'application': 'call_center',
        },
    },
    TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
)
async def test_get_order_price(web_context, mockserver, mock_user_api):
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
                {
                    'key': 'recognized_point_a_pos',
                    'value': [37.6175675721, 55.744319908],
                },
                {'key': 'recognized_point_b_pos', 'value': [37.612, 55.75]},
                {'key': 'probable_tariff', 'value': 'some tariff'},
                {'key': 'application_name', 'value': 'call_center'},
            ],
        ),
    )

    action = get_order_price.GetOrderPrice('test', 'get_order_price', '0', [])

    @mockserver.json_handler('/yandex-int-api/v1/orders/estimate')
    async def _(_):
        return web.json_response(
            data={
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'is_fixed_price': True,
                'offer': 'offer_id',
                'service_levels': [
                    {
                        'class': 'some tariff',
                        'cost_message_details': {
                            'cost_breakdown': [
                                {
                                    'display_amount': (
                                        '692 руб., ~17 мин в пути'
                                    ),
                                    'display_name': 'cost',
                                },
                            ],
                        },
                        'details_tariff': [
                            {'type': 'price', 'value': 'от 468 руб.'},
                        ],
                        'estimated_waiting': {
                            'message': 'через 3 мин',
                            'seconds': 160,
                        },
                        'fare_disclaimer': 'высокий спрос',
                        'is_fixed_price': True,
                        'price': '692 руб.',
                        'price_raw': 692.0,
                        'time': '17 мин',
                        'time_raw': 17,
                    },
                ],
                'user_id': 'user_id',
            },
        )

    _state = await action(web_context, state)

    assert 'offer_id' in _state.features
    assert 'order_price' in _state.features

    assert _state.features['offer_id'] == 'offer_id'
    assert _state.features['order_price'] == 692

    assert _state.features['application_name'] == 'call_center'
    assert _state.features['application_brand'] == 'some_brand'

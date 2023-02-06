# flake8: noqa: I100
# pylint: disable=broad-except
import pytest
from aiohttp import web

from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    create_order,
)
from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    get_order_price,
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
            '+799976543321': {
                'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
                'application': 'call_center',
            },
        },
        TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
    ),
]


@pytest.mark.parametrize(
    'point_a_order_comment', ['коммент для точки А', None],
)
@pytest.mark.parametrize(
    'point_b_order_comment', ['коммент для точки Б', None],
)
async def test_create_order(
        web_context,
        mockserver,
        mock_user_api,
        point_a_order_comment,
        point_b_order_comment,
):
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
                {'key': 'recognized_point_a', 'value': 'Точка 1'},
                {'key': 'recognized_point_b', 'value': 'Точка 2'},
                {'key': 'offer_id', 'value': 'offer_id'},
                {'key': 'probable_tariff', 'value': 'some tariff'},
                {'key': 'application_name', 'value': 'call_center'},
            ],
        ),
    )
    expected_comment_parts = []

    if point_a_order_comment:
        state.features['point_a_order_comment'] = point_a_order_comment
        expected_comment_parts.append(
            f'Уточнение адреса подачи: {point_a_order_comment}',
        )
    if point_b_order_comment:
        state.features['point_b_order_comment'] = point_b_order_comment
        expected_comment_parts.append(
            f'Уточнение конечного адреса: {point_b_order_comment}',
        )

    expected_order_comment = '; '.join(expected_comment_parts)

    action = create_order.CreateOrder('test', 'create_order', '0', [])

    @mockserver.json_handler('/yandex-int-api/v1/orders/draft')
    async def _(request):
        assert request.json['comment'] == expected_order_comment
        return web.json_response(data={'orderid': 'order_id'})

    @mockserver.json_handler('/yandex-int-api/v1/orders/commit')
    async def _(_):
        return web.json_response(
            data={'orderid': 'order_id', 'status': 'search'},
        )

    _state = await action(web_context, state)

    assert 'order_id' in _state.features

    assert _state.features['order_id'] == 'order_id'


@pytest.mark.parametrize(
    'error',
    [
        None,
        'error_estimate_order',
        'no_offer_id',
        'error_order_draft',
        'no_order_id',
        'error_commit_order',
    ],
)
async def test_create_order_taximeter(
        web_context, mockserver, mock_user_api, error,
):
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
                {
                    'key': 'recognized_point_a_pos',
                    'value': [37.6175675721, 55.744319908],
                },
                {'key': 'recognized_point_a', 'value': 'Точка 1'},
                {'key': 'taximeter_order', 'value': True},
                {'key': 'probable_tariff', 'value': 'some tariff'},
                {'key': 'application_name', 'value': 'some_app'},
            ],
        ),
    )

    get_order_price_action = get_order_price.GetOrderPrice(
        'test', 'create_order', '0', [],
    )
    create_order_action = create_order.CreateOrder(
        'test', 'create_order', '0', [],
    )

    @mockserver.json_handler('/yandex-int-api/v1/orders/estimate')
    async def _(_):
        status = 200
        data = {}
        if error == 'error_estimate_order':
            status = 400
        if error not in ('error_estimate_order', 'no_offer_id'):
            data = {'offer': 'offer_id'}
        return web.json_response(data=data, status=status)

    @mockserver.json_handler('/yandex-int-api/v1/orders/draft')
    async def _(request):
        status = 200
        data = {}
        if error in ('error_estimate_order', 'no_offer_id'):
            assert False

        assert request.json['offer'] == 'offer_id'
        if error == 'error_order_draft':
            status = 400
        if error not in ('error_order_draft', 'no_order_id'):
            data = {'orderid': 'order_id'}
        return web.json_response(data=data, status=status)

    @mockserver.json_handler('/yandex-int-api/v1/orders/commit')
    async def _(request):
        if error in (
                'error_estimate_order',
                'no_order_id',
                'error_order_draft',
                'no_order_id',
        ):
            assert False

        assert request.json['orderid'] == 'order_id'
        if error == 'error_commit_order':
            return web.json_response(data={}, status=400)
        return web.json_response(
            data={'orderid': 'order_id', 'status': 'search'},
        )

    new_state = await get_order_price_action(web_context, state)
    new_state = await create_order_action(web_context, new_state)
    assert 'offer_id' in new_state.features
    assert 'order_id' in new_state.features

    if error is None:
        assert 'get_order_price_error_message' not in new_state.features
        assert 'create_order_error_message' not in new_state.features
        assert new_state.features['offer_id'] == 'offer_id'
        assert new_state.features['order_id'] == 'order_id'
        return

    assert new_state.features['order_id'] is None
    assert 'create_order_error_message' in new_state.features

    if error not in ('error_estimate_order', 'no_offer_id'):
        assert 'get_order_price_error_message' not in new_state.features
        assert new_state.features['offer_id'] == 'offer_id'
        return

    assert new_state.features['offer_id'] is None
    assert 'get_order_price_error_message' in new_state.features

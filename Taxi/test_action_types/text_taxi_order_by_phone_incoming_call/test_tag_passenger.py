from aiohttp import web
import pytest

from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    tag_passenger,
)
from supportai_actions.actions import params as params_module


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+799976543321': {
            'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
            'application': 'call_center',
        },
    },
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'recently_called_tag_params': {
            'tag_lifetime_s': 10,
            'tag_name': 'passenger_called_to_robot_recently',
            'tag_provider_id': 'supportai_taxi_order_by_phone',
            'entity_type': 'personal_phone_id',
        },
    },
    TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
)
@pytest.mark.parametrize(
    ('tag_response_status', 'custom_tag_lifetime_s'),
    [(200, 2), (200, None), (202, None), (400, None)],
)
async def test_tag_passenger(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        tag_response_status,
        custom_tag_lifetime_s,
):
    @mockserver.handler('passenger-tags/v2/upload')
    async def _(request):
        assert request.headers.get('X-Idempotency-Token') is not None
        request_json = request.json
        provider_id = request_json.get('provider_id')
        assert provider_id == 'supportai_taxi_order_by_phone'

        append = request_json.get('append')
        assert isinstance(append, list) and len(append) == 1
        assert append[0] == {
            'entity_type': 'personal_phone_id',
            'tags': [
                {
                    'name': 'passenger_called_to_robot_recently',
                    'entity': 'personal_phone_id_value',
                    'ttl': 10 if not custom_tag_lifetime_s else 2,
                },
            ],
        }

        if tag_response_status == 202:
            return web.json_response(
                data={'code': 'some_error', 'message': 'some_error_occurred'},
                status=202,
            )
        if tag_response_status == 400:
            return web.json_response(data=None, status=400)
        return web.json_response(data={'status': 'ok'})

    _call_params = (
        [params_module.ActionParam({'tag_lifetime_s': custom_tag_lifetime_s})]
        if custom_tag_lifetime_s
        else []
    )

    action = tag_passenger.TagPassenger(
        'test', 'tag_passenger', '1', _call_params,
    )

    new_state = await action.call(web_context, default_state)
    if tag_response_status == 200:
        assert new_state.features.get('passenger_has_been_tagged') is True
        assert 'upload_tag_error_description' not in new_state.features
    else:
        assert not new_state.features.get('passenger_has_been_tagged')
        assert 'upload_tag_error_description' in new_state.features


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+799976543321': {
            'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
            'application': 'call_center',
        },
    },
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'recently_called_tag_params': {
            'tag_name': 'passenger_called_to_robot_recently',
            'tag_provider_id': 'supportai_taxi_order_by_phone',
            'entity_type': 'personal_phone_id',
        },
    },
    TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
)
async def test_tag_passenger_no_tag_lifetime_in_config(
        web_context, mockserver, mock_user_api, default_state,
):
    @mockserver.handler('passenger-tags/v2/upload')
    async def _(_):
        assert False

    action = tag_passenger.TagPassenger('test', 'tag_passenger', '1', [])

    new_state = await action.call(web_context, default_state)
    assert new_state.features.get('passenger_has_been_tagged') is False
    assert new_state.features.get('upload_tag_error_description') is None

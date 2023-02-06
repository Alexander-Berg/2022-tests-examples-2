import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.requestconfirm_helpers as rch

CANCEL_REASON = 'seenimpossible'

INVALID_UUID = '1111'

SOME_DATE = '2019-05-01T16:18:00.000000Z'


@pytest.mark.parametrize('driver_profile_id', ['driver_profile_id'])
@pytest.mark.parametrize('park_id', ['park_id'])
@pytest.mark.parametrize(
    'multioffer_id', [INVALID_UUID, 'c9831935-a2d9-4b06-89a1-397ce12178af'],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_requestconfirm_reject_multioffer(
        taxi_driver_orders_app_api,
        contractor_orders_multioffer,
        driver_authorizer,
        yataxi_client,
        park_id,
        driver_profile_id,
        multioffer_id,
):
    user_agent = auth.USER_AGENT_TAXIMETER

    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, 'session', driver_profile_id,
    )
    yataxi_client.taximeter_version = user_agent
    data = {
        'multioffer_id': multioffer_id,
        'order': 'some_order',
        'comment': CANCEL_REASON,
    }

    response = await taxi_driver_orders_app_api.post(
        '/driver/v1/orders-app-api/v2/requestconfirm/reject',
        headers=rch.get_headers(user_agent, park_id, driver_profile_id),
        json=data,
    )

    if multioffer_id == INVALID_UUID:
        assert response.status_code == 400
        assert contractor_orders_multioffer.offer_decline.times_called == 0
    else:
        assert response.status_code == 200
        assert contractor_orders_multioffer.offer_decline.times_called == 1
        next_call = contractor_orders_multioffer.offer_decline.next_call()
        request_json = next_call['self'].json
        assert request_json['comment'] == CANCEL_REASON

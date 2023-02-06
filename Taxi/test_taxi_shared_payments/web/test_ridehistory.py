from aiohttp import web
import pytest

MOCK_UID = 'user1'


@pytest.mark.parametrize(
    'uid, account_id, ridehistory_status, expected_status',
    [
        pytest.param(MOCK_UID, '1', 200, 200, id='ok'),
        pytest.param(MOCK_UID, '1', 400, 400, id='ridehistory bad request'),
        pytest.param(MOCK_UID, '1', 401, 401, id='ridehistory unauthorized'),
        pytest.param(MOCK_UID, '1', 404, 404, id='ridehistory not found'),
        pytest.param(MOCK_UID, '1', 500, 500, id='ridehistory server error'),
        pytest.param(MOCK_UID, '2', 200, 403, id='wrong_account_id'),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'ridehistory_resp, expected_resp',
    [
        pytest.param(
            'ridehistory_list_response.json',
            'expected_list_response.json',
            id='simple',
        ),
        pytest.param(
            'ridehistory_list_response_no_destination.json',
            'expected_list_response_no_destination.json',
            id='no_destination',
        ),
    ],
)
async def test_coop_acc_ridehistory_list(
        web_app_client,
        mock_user_api,
        mock_ridehistory,
        load_json,
        uid,
        account_id,
        ridehistory_status,
        expected_status,
        ridehistory_resp,
        expected_resp,
):
    @mock_ridehistory('/v2/list')
    def _list(request):
        return web.json_response(
            status=ridehistory_status,
            data=load_json(ridehistory_resp)
            if ridehistory_status == 200
            else {'code': '', 'message': ''},
        )

    response = await web_app_client.post(
        '/4.0/coop_account/ridehistory_list',
        headers={
            'X-Yandex-UID': uid,
            'X-Request-Application': 'app=android',
            'X-YaTaxi-PhoneId': '00aaaaaaaaaaaaaaaaaaaa01',
            'X-Request-Language': 'ru',
        },
        json={'account_id': account_id, 'range': {'results': 10}},
    )

    assert response.status == expected_status
    if expected_status == 200:
        assert await response.json() == load_json(expected_resp)


@pytest.mark.parametrize(
    'uid, account_id, payment_change, ridehistory_status, expected_status',
    [
        pytest.param(MOCK_UID, '1', {}, 200, 200, id='ok'),
        pytest.param(
            MOCK_UID, '1', {}, 400, 400, id='ridehistory bad request',
        ),
        pytest.param(
            MOCK_UID, '1', {}, 401, 401, id='ridehistory unauthorized',
        ),
        pytest.param(MOCK_UID, '1', {}, 404, 404, id='ridehistory not found'),
        pytest.param(
            MOCK_UID, '1', {}, 500, 500, id='ridehistory server error',
        ),
        pytest.param(MOCK_UID, '2', {}, 200, 403, id='wrong_account_id'),
        pytest.param(
            MOCK_UID,
            '1',
            {'payment_tech_type': 'card'},
            200,
            403,
            id='wrong_payment_type',
        ),
        pytest.param(
            MOCK_UID,
            '1',
            {'payment_method_id': '9'},
            200,
            403,
            id='wrong_payment_method_id',
        ),
    ],
)
@pytest.mark.parametrize(
    'ridehistory_resp, expected_resp',
    [
        pytest.param(
            'ridehistory_item_response.json',
            'expected_item_response.json',
            id='simple',
        ),
        pytest.param(
            'ridehistory_item_response_no_destination.json',
            'expected_item_response_no_destination.json',
            id='no_destination',
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_coop_acc_ridehistory_item(
        web_app_client,
        mock_user_api,
        mock_ridehistory,
        load_json,
        uid,
        account_id,
        payment_change,
        ridehistory_status,
        expected_status,
        ridehistory_resp,
        expected_resp,
):
    @mock_ridehistory('/v2/item')
    def _item(request):
        json = load_json(ridehistory_resp)
        json['meta']['payment_tech'].update(payment_change)
        return web.json_response(
            status=ridehistory_status,
            data=json
            if ridehistory_status == 200
            else {'code': '', 'message': ''},
        )

    response = await web_app_client.post(
        '/4.0/coop_account/ridehistory_item',
        headers={
            'X-Yandex-UID': uid,
            'X-Request-Application': 'app=android',
            'X-YaTaxi-PhoneId': '00aaaaaaaaaaaaaaaaaaaa01',
            'X-Request-Language': 'ru',
        },
        json={'account_id': account_id, 'order_id': '1'},
    )

    assert response.status == expected_status
    if expected_status == 200:
        assert await response.json() == load_json(expected_resp)

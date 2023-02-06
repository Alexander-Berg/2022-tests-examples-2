import copy

import pytest

from test_iiko_integration import get_order_stubs

RES_GROUP_INFO = get_order_stubs.CONFIG_RESTAURANT_GROUP_INFO
RES_INFO = get_order_stubs.CONFIG_RESTAURANT_INFO


@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=RES_GROUP_INFO,
    IIKO_INTEGRATION_RESTAURANT_INFO=RES_INFO,
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
)
@pytest.mark.translations(
    qr_payment={
        'restaurants.restaurant_01_key': {
            'RU': 'Ресторан 01',
            'EN': 'Restaurant 01',
        },
    },
)
@pytest.mark.parametrize(
    ('locale', 'name'),
    (
        pytest.param('RU', 'Ресторан 01', id='ru'),
        pytest.param('EN', 'Restaurant 01', id='en'),
    ),
)
@pytest.mark.parametrize(
    ('order_id', 'expected_status', 'expected_response', 'with_complement'),
    (
        pytest.param(
            '01',
            200,
            get_order_stubs.ORDER_OK_RESPONSE_FOR_USER,
            False,
            id='ok',
        ),
        pytest.param(
            '01',
            200,
            get_order_stubs.user_order_with_complement(),
            True,
            id='with complement payment method',
        ),
        pytest.param(
            'invalid_order_id',
            404,
            get_order_stubs.ORDER_NOT_FOUND_RESPONSE,
            False,
            id='order not found',
        ),
    ),
)
@pytest.mark.pgsql('iiko_integration', directories=['test_get_order'])
async def test_get_order(
        web_app_client,
        pgsql,
        locale: str,
        name: str,
        order_id: str,
        expected_response: dict,
        expected_status: int,
        with_complement: bool,
):
    if with_complement:
        get_order_stubs.add_complement_to_db(pgsql)

    response = await web_app_client.get(
        f'/v1/order?id={order_id}&locale={locale}&for_user=true',
    )
    expected_response = copy.deepcopy(expected_response)
    if 'restaurant_info' in expected_response:
        expected_response['restaurant_info']['name'] = name

    assert response.status == expected_status
    response_json = await response.json()
    assert response_json == expected_response
    # for key, value in expected_response.items():
    #     assert key in response_json
    #     assert response_json[key] == value
    # if expected_status == 200:
    #     assert stats_counter.count == 1
    # else:
    #     assert stats_counter.count == 0


@pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=False)
async def test_service_unavailable(web_app_client):
    response = await web_app_client.get(f'/v1/order?id=01&locale=RU')
    assert response.status == 400


@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=RES_GROUP_INFO,
    IIKO_INTEGRATION_RESTAURANT_INFO=RES_INFO,
)
@pytest.mark.translations(
    qr_payment={'restaurants.restaurant_01_key': {'RU': 'Ресторан 01'}},
)
@pytest.mark.parametrize(
    ('order_id', 'for_user', 'stats_called'),
    (
        pytest.param('01', True, False, id='Not init order for user'),
        pytest.param('01', False, False, id='Not init order not for user'),
        pytest.param('02', True, True, id='init order for user'),
        pytest.param('02', False, False, id='init order not for user'),
    ),
)
@pytest.mark.pgsql('iiko_integration', directories=['test_get_order'])
async def test_stats(
        web_app_client, mock_stats, order_id, for_user, stats_called,
):
    stats_counter = mock_stats(
        'order.events.viewing_order', 'restaurant01', 'restaurant_group_01',
    )
    response = await web_app_client.get(
        f'/v1/order?id={order_id}&for_user={for_user}&locale=EN',
    )
    assert response.status == 200
    if stats_called:
        assert stats_counter.count == 1
    else:
        assert stats_counter.count == 0

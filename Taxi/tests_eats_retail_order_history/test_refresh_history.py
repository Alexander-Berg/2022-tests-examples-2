import pytest

from . import utils

HANDLE = '/eats/v1/retail-order-history/customer/order/picking/refresh-history'
HEADERS = {
    'X-Eats-User': f'user_id={utils.CUSTOMER_ID}',
    'X-Yandex-UID': utils.YANDEX_UID,
}


def get_element_if_tuple(value, i):
    return value[i] if isinstance(value, (list, tuple)) else value


@pytest.fixture(name='check_response')
def _check_response(
        taxi_eats_retail_order_history, assert_response, assert_mocks,
):
    async def do_check_response(
            expected_status_refresh_history,
            expected_status_get_history,
            expected_response_get_history,
            orders_retrieve_called=0,
            order_revision_list_called=0,
            order_revision_details_called=0,
            place_assortment_details_called=0,
            retrieve_places_called=0,
            get_picker_order_called=0,
            cart_diff_called=0,
            eda_candidates_list_called=0,
            performer_location_called=0,
            vgw_api_forwardings_called=0,
            cargo_driver_voiceforwardings_called=0,
    ):
        for i in range(2):
            response = await taxi_eats_retail_order_history.post(
                HANDLE, params={'order_nr': utils.ORDER_ID}, headers=HEADERS,
            )
            assert response.status == expected_status_refresh_history
            assert_mocks(
                get_element_if_tuple(orders_retrieve_called, i),
                get_element_if_tuple(order_revision_list_called, i),
                get_element_if_tuple(order_revision_details_called, i),
                get_element_if_tuple(place_assortment_details_called, i),
                get_element_if_tuple(retrieve_places_called, i),
                get_element_if_tuple(get_picker_order_called, i),
                get_element_if_tuple(cart_diff_called, i),
                get_element_if_tuple(eda_candidates_list_called, i),
                get_element_if_tuple(performer_location_called, i),
                get_element_if_tuple(vgw_api_forwardings_called, i),
                get_element_if_tuple(cargo_driver_voiceforwardings_called, i),
            )
            await assert_response(
                expected_status_get_history, expected_response_get_history,
            )

    return do_check_response


async def test_refresh_history_no_yandex_uid_400(
        taxi_eats_retail_order_history, create_order,
):
    create_order(yandex_uid=None)
    response = await taxi_eats_retail_order_history.post(
        HANDLE,
        params={'order_nr': utils.ORDER_ID},
        headers={'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 400


async def test_refresh_history_unauthorized_401(
        taxi_eats_retail_order_history,
):
    response = await taxi_eats_retail_order_history.post(
        HANDLE, params={'order_nr': utils.ORDER_ID},
    )
    assert response.status_code == 401
    assert response.json()['code'] == 'unauthorized'


@utils.polling_config3()
async def test_refresh_history_order_not_found_404(
        taxi_eats_retail_order_history,
        create_order,
        environment,
        assert_mocks,
):
    create_order()
    response = await taxi_eats_retail_order_history.post(
        HANDLE, params={'order_nr': utils.ORDER_ID}, headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'
    assert response.headers['X-Polling-Delay'] == '30'

    assert_mocks(orders_retrieve_called=1)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
async def test_refresh_history_200(
        create_order, environment, load_json, check_response,
):
    create_order()
    environment.set_default()
    await check_response(
        expected_status_refresh_history=200,
        expected_status_get_history=200,
        expected_response_get_history=load_json('expected_response.json'),
        orders_retrieve_called=(1, 2),
        order_revision_list_called=(1, 2),
        # детали ревизий запрашиваются один раз, если последняя ревизия
        # не изменилась
        order_revision_details_called=2,
        # картинки для товаров подтягиваются один раз
        place_assortment_details_called=2,
        # информация о магазине подтягивается один раз
        retrieve_places_called=1,
        # в первом запросе был получен picking_status=complete,
        # значит второй раз информация из пикерки запрашиваться не будет
        get_picker_order_called=1,
        cart_diff_called=1,
        # телефоны подтягиваются один раз, так как не успевают протухнуть
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
    )

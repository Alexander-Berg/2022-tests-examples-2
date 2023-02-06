# pylint: disable=too-many-lines

import pytest

from tests_eats_orders_info import utils


@pytest.fixture(name='check_response')
def _check_response(assert_response, assert_mocks):
    async def do_check_response(
            expected_status,
            core_orders_retrieve_called,
            core_revision_list_called,
            core_revision_details_called,
            place_assortment_details_called,
            catalog_retrieve_places_called,
            tracking_claims_called,
            cargo_driver_vfwd_called,
            expected_response=None,
    ):
        await assert_response(expected_status, expected_response)
        assert_mocks(
            core_orders_retrieve_called,
            core_revision_list_called,
            core_revision_details_called,
            place_assortment_details_called,
            catalog_retrieve_places_called,
            tracking_claims_called,
            cargo_driver_vfwd_called,
        )

    return do_check_response


def set_def_donations(
        local_services, amount='1', donation_status='unauthorized',
):
    local_services.exp_order_ids = [[utils.ORDER_NR_ID], []]
    amounts = {utils.ORDER_NR_ID: [amount, donation_status]}
    donations = utils.generate_donations(amounts)
    local_services.brands_response = utils.generate_brands_response(
        local_services.exp_order_ids, donations,
    )


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_change_item(
        load_json, local_services, check_response,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    local_services.add_order_customer_service(
        revision_id='1',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='110.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    set_def_donations(local_services)
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=2,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json('expected_response_change_item.json'),
    )


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_no_last_revision_data_200(
        mockserver, load_json, local_services, check_response,
):
    local_services.set_default()
    set_def_donations(local_services)

    order_revisions = local_services.order_revisions[utils.ORDER_NR_ID]
    first_revision_id = next(iter(order_revisions))
    local_services.add_order_customer_service(
        revision_id=first_revision_id,
        customer_service_id='delivery',
        customer_service_name='Стоимость доставки',
        cost_for_customer='0.0',
        type_='delivery',
    )

    prev_mock = local_services.mock_core_revision_details

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services/details',
    )
    async def _eats_core_order_revision_details(request):
        assert request.method == 'POST'
        order_id = request.json['order_id']
        revision_id = request.json['revision_id']
        order_revisions = local_services.order_revisions.get(order_id, {})
        if not order_revisions or revision_id != next(iter(order_revisions)):
            return mockserver.make_response(status=404)
        return await prev_mock(request)

    local_services.mock_core_revision_details = (
        _eats_core_order_revision_details
    )

    expected_response = load_json(
        'expected_response_cooking_no_last_revision.json',
    )
    expected_response['original_total_cost_for_customer'] = expected_response[
        'original_cost_for_customer'
    ]
    expected_response['total_cost_for_customer'] = expected_response[
        'final_cost_for_customer'
    ]
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=2,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=expected_response,
    )


@utils.order_updater_config3()
@pytest.mark.parametrize(
    'retrieve_places_response',
    [{'status': 500}, {'json': {'places': [], 'not_found_place_ids': []}}],
)
async def test_order_updater_place_not_found_404(
        mockserver, local_services, retrieve_places_response, check_response,
):
    local_services.set_default()
    set_def_donations(local_services)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _eats_catalog_storage_retrieve_places(request):
        return mockserver.make_response(**retrieve_places_response)

    local_services.mock_catalog_retrieve_places = (
        _eats_catalog_storage_retrieve_places
    )
    await check_response(
        expected_status=500,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=2,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.order_updater_config3()
@pytest.mark.parametrize(
    'place_assortment_response',
    [
        {'status': 500},
        {
            'status': 400,
            'json': {
                'isSuccess': False,
                'statusCode': 400,
                'type': 'bad_request',
                'errors': [{'message': 'плохой запрос'}],
                'context': 'some_context',
            },
        },
        {
            'status': 404,
            'json': {
                'isSuccess': False,
                'statusCode': 404,
                'type': 'not_found',
            },
        },
    ],
)
@utils.order_details_titles_config3()
async def test_order_updater_place_assortment_not_found_200(  # for images
        mockserver,
        load_json,
        local_services,
        place_assortment_response,
        check_response,
):
    local_services.set_default()
    set_def_donations(local_services)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/ordershistory-place-menu',
    )
    def _eats_products_place_ordershistory_details(request):
        return mockserver.make_response(**place_assortment_response)

    local_services.mock_place_history_details = (
        _eats_products_place_ordershistory_details
    )
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=2,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json(
            'expected_response_no_place_assortment.json',
        ),
    )


@utils.order_updater_config3()
async def test_order_updater_revisions_not_found_404(
        local_services, check_response,
):
    local_services.set_default()
    set_def_donations(local_services)
    local_services.order_revisions = {}
    await check_response(
        expected_status=500,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=0,
        place_assortment_details_called=0,
        catalog_retrieve_places_called=0,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'business', ['restaurant', 'store', 'pharmacy', 'shop', 'zapravki'],
)
@pytest.mark.parametrize(
    'claim, is_expiring_phone, has_phone',
    [
        (None, False, False),
        (  # expiring
            {
                'id': utils.CLAIM_ID,
                'phone': {
                    'phone': '+7(800)5553535',
                    'ext': '1234',
                    'ttl_seconds': 0,
                },
            },
            True,
            True,
        ),
        ({'id': utils.CLAIM_ID, 'phone': utils.COURIER_PHONE}, False, True),
    ],
)
@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_courier_phone_200(
        local_services,
        load_json,
        check_response,
        business,
        claim,
        is_expiring_phone,
        has_phone,
):
    local_services.set_default(status='taken')
    local_services.claims = {}  # clean default
    local_services.order_claims.clear()  # clean default
    set_def_donations(local_services)
    local_services.add_place_info(business=business)
    if has_phone:
        local_services.add_claim(
            utils.ORDER_NR_ID, claim['id'], claim['phone'],
        )

    expected_response = load_json('expected_response_for_different_phone.json')
    expected_response['place']['business'] = business
    if has_phone and not is_expiring_phone:
        expected_response['forwarded_courier_phone'] = '+7(800)5553535,,1234'
    else:
        del expected_response['forwarded_courier_phone']
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=2,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=1,
        cargo_driver_vfwd_called=1,
        expected_response=expected_response,
    )


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_with_option(
        load_json, local_services, check_response,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='413.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(
                id_='item_111-1',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(
                id_='item_222-0',
                name='Помидоры Black',
                cost_for_customer='200.00',
                origin_id='item-2',
            ),
            local_services.make_composition_product(
                id_='option-111-0',
                parent_id='item_111-0',
                name='Золотая посыпка',
                cost_for_customer='3.00',
                type_='option',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    set_def_donations(local_services)
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=1,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json('expected_response_with_option.json'),
    )


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_empty_origin(
        load_json,
        local_services,
        check_response,
        taxi_eats_orders_info_monitor,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='313.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(  # not exist origin_id,
                # will be skipped, and its option too
                id_='item_111-1',
                name='Яблоки Gold',
                cost_for_customer='110.00',
            ),
            local_services.make_composition_product(
                id_='item_222-0',
                name='Помидоры Black',
                cost_for_customer='200.00',
                origin_id='item-2',
            ),
            local_services.make_composition_product(  # will be skipped
                # (type = product), forcing is turned off
                id_='option-111-0',
                parent_id='item_111-1',
                name='Золотая посыпка',
                cost_for_customer='3.00',
            ),
            local_services.make_composition_product(  # will be skipped
                # (type = option)
                id_='option-111-0',
                parent_id='item_111-1',
                type_='option',
                name='Голубая посыпка',
                cost_for_customer='3.00',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    set_def_donations(local_services)
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=1,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json(
            'expected_response_with_wrong_option.json',
        ),
    )

    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'eats-orders-info-metrics',
    )
    assert metrics['product_empty_origin_id'] == 2


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_option_without_parent_id(
        load_json,
        local_services,
        check_response,
        taxi_eats_orders_info_monitor,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='313.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(
                id_='item_222-0',
                name='Помидоры Black',
                cost_for_customer='200.00',
                origin_id='item-2',
            ),
            local_services.make_composition_product(  # will be skipped
                id_='option-111-0',
                name='Золотая посыпка',
                cost_for_customer='3.00',
                type_='option',
            ),
            local_services.make_composition_product(  # will be skipped
                id_='option-111-0',
                name='Голубая посыпка',
                cost_for_customer='3.00',
                type_='option',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    set_def_donations(local_services)
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=1,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json(
            'expected_response_with_wrong_option.json',
        ),
    )

    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'eats-orders-info-metrics',
    )
    assert metrics['option_empty_parent_id'] == 2


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_not_exist_parent(
        load_json,
        local_services,
        check_response,
        taxi_eats_orders_info_monitor,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='313.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Яблоки Gold',
                cost_for_customer='110.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(
                id_='item_222-0',
                name='Помидоры Black',
                cost_for_customer='200.00',
                origin_id='item-2',
            ),
            local_services.make_composition_product(  # will be skipped
                id_='option-111-0',
                parent_id='not_exist',
                name='Золотая посыпка',
                cost_for_customer='3.00',
                type_='option',
            ),
            local_services.make_composition_product(  # will be skipped
                id_='option-111-1',
                parent_id='not_exist',
                name='Голубая посыпка',
                cost_for_customer='3.00',
                type_='option',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    set_def_donations(local_services)
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=1,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json(
            'expected_response_with_wrong_option.json',
        ),
    )

    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'eats-orders-info-metrics',
    )
    assert metrics['not_existed_parent_product'] == 2


# not_existed_parent_product_final is unreal now,
# because if origin_id is not empty, then value is exist in revision_details
# (was checked by code by erasing value with specific key "erase_me" and
# checked "not_existed_parent_product")


@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_updater_use_revision_standalone(
        load_json,
        local_services,
        check_response,
        taxi_eats_orders_info_monitor,
        taxi_eats_orders_info,
):
    local_services.add_user_order(status='finished')
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='605.00',
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_111-0',
                name='Пирожок',
                cost_for_customer='100.00',
                origin_id='item-1',
            ),
            local_services.make_composition_product(
                id_='item_222-0',
                name='Мак Комбо',
                cost_for_customer='0.00',
                origin_id='item-2',
            ),
            local_services.make_composition_product(
                id_='item_option-0',
                name='Картошка',
                stand_alone_item_parent_id='item_222-0',
                cost_for_customer='50.00',
            ),
            local_services.make_composition_product(
                id_='item_option-1',
                name='Бургер',
                stand_alone_item_parent_id='item_222-0',
                cost_for_customer='100.00',
            ),
            local_services.make_composition_product(
                id_='item_option-2',
                name='Напиток',
                stand_alone_item_parent_id='item_222-0',
                cost_for_customer='100.00',
            ),
            local_services.make_composition_product(
                id_='item_333-0',
                name='Салат',
                cost_for_customer='100.00',
                origin_id='item-3',
            ),
            local_services.make_composition_product(
                id_='option-333-0',
                name='Соус цезарь',
                cost_for_customer='50.00',
                type_='option',
                parent_id='item_333-0',
            ),
            local_services.make_composition_product(
                id_='item_444-0',
                name='Напиток',
                cost_for_customer='0.00',
                origin_id='item-4',
            ),
            local_services.make_composition_product(
                id_='option-444-2',
                name='С пирожком',
                cost_for_customer='5.00',
                type_='option',
                parent_id='item_444-0',
            ),
            local_services.make_composition_product(
                id_='option-444-0',
                name='Большой',
                stand_alone_item_parent_id='item_444-0',
                cost_for_customer='100.00',
            ),
            local_services.make_composition_product(
                id_='option-444-1',
                name='Без льда',
                stand_alone_item_parent_id='item_444-0',
                cost_for_customer='0.00',
            ),
        ],
    )
    local_services.add_place_info(
        business='restaurant', brand_slug='with_standalone',
    )
    set_def_donations(local_services)
    await taxi_eats_orders_info.tests_control(reset_metrics=True)
    await taxi_eats_orders_info.invalidate_caches()
    await check_response(
        expected_status=200,
        core_orders_retrieve_called=1,
        core_revision_list_called=1,
        core_revision_details_called=1,
        place_assortment_details_called=1,
        catalog_retrieve_places_called=1,
        tracking_claims_called=0,
        cargo_driver_vfwd_called=0,
        expected_response=load_json(
            'expected_response_standalone_product.json',
        ),
    )

    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'eats-orders-info-metrics',
    )
    assert metrics['product_empty_origin_id'] == 0
    assert (
        'forced_last_full_product_id' not in metrics
        or not metrics['forced_last_full_product_id']
    )

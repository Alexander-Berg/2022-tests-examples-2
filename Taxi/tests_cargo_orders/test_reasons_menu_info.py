import pytest


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.fixture(name='get_reasons_menu_info')
def _get_reasons_menu_info(taxi_cargo_orders):
    async def reasons_menu_info(
            order_id, claim_point_id, menu_type='skip_source_point',
    ):
        response = await taxi_cargo_orders.get(
            '/driver/v1/cargo-claims/v1/cargo/reasons-menu-info'
            f'?cargo_ref_id=order/{order_id}'
            f'&claim_point_id={claim_point_id}'
            f'&menu_type={menu_type}',
            headers=DEFAULT_HEADERS,
        )
        return response

    return reasons_menu_info


TRANSLATIONS = {
    'menu_title_tanker_key': {'en': 'menu_title'},
    'menu_text_tanker_key': {'en': 'menu_text'},
    'button_title_tanker_key': {'en': 'button_title'},
    'button_subtitle_tanker_key': {'en': 'button_subtitle'},
    'reason_title_tanker_key': {'en': 'reason_title'},
    'reason_subtitle_tanker_key': {'en': 'reason_subtitle'},
}


DEFAULT_CONFIG_MENU_CLAUSE = {
    'title_tanker_key': 'menu_title_tanker_key',
    'text_tanker_key': 'menu_text_tanker_key',
    'button_text_tanker_key': 'menu_button_text_tanker_key',
    'reasons_list': [
        {
            'id': 'reason_id',
            'title_tanker_key': 'reason_title_tanker_key',
            'subtitle_tanker_key': 'reason_subtitle_tanker_key',
        },
    ],
    'button': {
        'title_tanker_key': 'button_title_tanker_key',
        'subtitle_tanker_key': 'button_subtitle_tanker_key',
    },
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_performer_reasons_menu',
    consumers=['cargo-orders/performer-reasons-menu'],
    clauses=[],
    default_value={'menu': DEFAULT_CONFIG_MENU_CLAUSE},
)
@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_happy_path(
        taxi_cargo_orders,
        mock_waybill_info,
        my_waybill_info,
        default_order_id,
        get_reasons_menu_info,
):
    response = await get_reasons_menu_info(
        default_order_id, claim_point_id=642499,
    )
    assert response.status_code == 200
    assert response.json() == {
        'title': 'menu_title',
        'text': 'menu_text',
        'reasons_list': [
            {
                'id': 'reason_id',
                'reason_title': 'reason_title',
                'reason_subtitle': 'reason_subtitle',
            },
        ],
        'button': {'title': 'button_title', 'subtitle': 'button_subtitle'},
    }


async def test_bad_claim_point_id(
        taxi_cargo_orders,
        mock_waybill_info,
        my_waybill_info,
        default_order_id,
        get_reasons_menu_info,
):
    response = await get_reasons_menu_info(
        default_order_id, claim_point_id=123,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'point_not_found',
        'message': 'No point 123 in waybill_info',
    }


@pytest.mark.parametrize(
    ('claim_point_id', 'menu_type', 'message'),
    [
        pytest.param(
            642500,
            'cancel',
            'Non source point\'s type: destination',
            id='Non source',
        ),
        pytest.param(
            642500,
            'skip_source_point',
            'Non source point\'s type: destination',
            id='Non source',
        ),
        pytest.param(
            642499,
            'return',
            'Non destination point\'s type: source',
            id='Non destination',
        ),
    ],
)
async def test_invalid_point_type_for_menu_type(
        taxi_cargo_orders,
        mock_waybill_info,
        my_waybill_info,
        default_order_id,
        get_reasons_menu_info,
        claim_point_id,
        menu_type,
        message,
):
    response = await get_reasons_menu_info(
        default_order_id, claim_point_id, menu_type,
    )
    assert response.status_code == 400
    assert response.json() == {'code': 'bad_request', 'message': message}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_performer_reasons_menu',
    consumers=['cargo-orders/performer-reasons-menu'],
    clauses=[],
    default_value={},
)
async def test_no_config_clause(
        taxi_cargo_orders,
        mock_waybill_info,
        my_waybill_info,
        default_order_id,
        get_reasons_menu_info,
):
    response = await get_reasons_menu_info(
        default_order_id, claim_point_id=642499,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_performer_reasons_menu',
    consumers=['cargo-orders/performer-reasons-menu'],
    clauses=[
        {
            'title': 'Cancel menu',
            'enabled': True,
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'menu_type',
                    'arg_type': 'string',
                    'value': 'cancel',
                },
            },
            'value': {'menu': DEFAULT_CONFIG_MENU_CLAUSE},
        },
    ],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_performer_fines_performer_cancellations_limits',
    consumers=['cargo-orders/performer-cancellations-limits'],
    clauses=[],
    default_value={
        'free_cancellation_limit': 2,
        'required_completed_orders_to_reset_cancellation_limit': 30,
        'title_tanker_key': 'performer_cancel_limit_title',
        'subtitle_tanker_key': 'performer_cancel_limit_subtitle',
        'detail_tanker_key': 'performer_cancel_limit_detail',
        'right_icon_payload': {
            'text_tanker_key': 'performer_cancel_limit_right_icon',
        },
    },
)
@pytest.mark.translations(cargo=TRANSLATIONS)
@pytest.mark.now('2020-12-11 13:01:53.000000+03')
async def test_cancel_reasons_menu(
        taxi_cargo_orders,
        mock_waybill_info,
        my_batch_waybill_info,
        insert_performer_order_cancel_statistics,
        default_order_id,
        get_reasons_menu_info,
):
    insert_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1', cancel_count=3,
    )

    response = await get_reasons_menu_info(
        default_order_id, claim_point_id=3, menu_type='cancel',
    )
    assert response.status_code == 200
    assert response.json() == {
        'title': 'menu_title',
        'text': 'menu_text',
        'reasons_list': [
            {
                'id': 'reason_id',
                'reason_title': 'reason_title',
                'reason_subtitle': 'reason_subtitle',
            },
        ],
        'button': {
            'title': 'button_title',
            'subtitle': 'button_subtitle',
            'constructor_items': [
                {
                    'accent': True,
                    'right_icon': 'more_info',
                    'type': 'detail',
                    'detail': '2 из 2',
                    'subtitle': 'Дальше штраф',
                    'title': 'Количество бесплатных отмен',
                    'right_icon_payload': {
                        'type': 'show_tooltip',
                        'tooltip': {
                            'text': (
                                'Нужно выполнить 30 заказов, '
                                'чтобы обнулить счётчик'
                            ),
                        },
                    },
                },
            ],
        },
    }

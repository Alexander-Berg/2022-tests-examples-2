# pylint: disable=too-many-lines

import pytest

from tests_eats_payments import consts
from tests_eats_payments import configs
from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models


TEST_ORDER_ID = 'test_order'
TEST_PAYMENT_ID = '123'
NOW = '2020-08-12T07:20:00+00:00'


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('payment_type', ['card', 'applepay', 'googlepay'])
@pytest.mark.parametrize('service', ['eats', 'grocery'])
async def test_card_like_payment_methods(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        billing_service='food_payment',
        service=service,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
            helpers.make_transactions_item(
                item_id='service_fee', amount='9.00',
            ),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type,
    )
    items = [
        helpers.make_item(item_id='big_mac', amount='2.00'),
        helpers.make_item(
            item_id='service_fee',
            item_type=models.ItemType.service_fee,
            amount='9.00',
        ),
    ]
    await check_create_order(
        payment_type=payment_type, items=items, service=service,
    )
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, payment_type)
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_badge_payment_method(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mock_blackbox,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='badge',
        payment_method_id='badge:yandex_badge:RUB',
        billing_service='food_payment_badge',
        payer_login='foo',
        billing_id=None,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='badge',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='badge', payment_method_id='badge:yandex_badge:RUB',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        items=items,
    )
    assert_db_order_payment(TEST_ORDER_ID, 'badge:yandex_badge:RUB', 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert mock_blackbox.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_fiscal_info_passed(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        fetch_items_from_db,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create()
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='big_mac',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': 'Big Mac Burger',
                },
            ),
            helpers.make_transactions_item(
                item_id='long_title',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': consts.LONG_ITEM_TITLE_TRIMMED,
                },
            ),
            helpers.make_transactions_item(
                item_id='not_long_title',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': consts.NOT_LONG_ITEM_TITLE,
                },
            ),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment()
    items = [
        helpers.make_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': 'Big Mac Burger',
            },
        ),
        helpers.make_item(
            item_id='long_title',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': consts.LONG_ITEM_TITLE,
            },
        ),
        helpers.make_item(
            item_id='not_long_title',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': consts.NOT_LONG_ITEM_TITLE,
            },
        ),
    ]
    await check_create_order(payment_type='card', items=items)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_no_billing_and_fiscal_info_ok(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        fetch_items_from_db,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create()
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment()
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(payment_type='card', items=items)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_personal_phone_id(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='card',
        billing_service='food_payment',
        personal_phone_id='456',
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='card',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    headers = {
        **consts.BASE_HEADERS,
        **{'X-YaTaxi-User': 'personal_phone_id=456'},
    }
    await check_create_order(payment_type='card', items=items, headers=headers)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_additional_params(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    pass_params = {
        'user_info': {
            'accept_language': '',
            'is_portal': False,
            'personal_phone_id': '',
        },
    }
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='corp',
        billing_service='food_payment_corp',
        pass_params=pass_params,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='corp',
        items=[
            helpers.make_transactions_item(
                item_id='big_mac', amount='2.00', commission_category=600,
            ),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='corp',
    )
    items = [
        helpers.make_item(
            item_id='big_mac', amount='2.00', commission_category=600,
        ),
    ]
    await check_create_order(payment_type='corp', items=items)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'pass_flags_header, is_portal',
    [('ololo', False), ('pdd', True), ('portal', True), ('pdd,portal', True)],
)
async def test_corp_payment_method_is_portal(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        pass_flags_header,
        is_portal,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    pass_params = {
        'user_info': {
            'accept_language': '',
            'is_portal': is_portal,
            'personal_phone_id': '',
        },
    }
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='corp',
        billing_service='food_payment_corp',
        pass_params=pass_params,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='corp',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='corp',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    headers = {
        **consts.BASE_HEADERS,
        **{'X-YaTaxi-Pass-Flags': pass_flags_header},
    }
    await check_create_order(payment_type='corp', items=items, headers=headers)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'extra_headers, accept_language',
    [({}, ''), ({'Accept-Language': 'fr-CH'}, 'fr-CH')],
)
async def test_corp_payment_method_accept_language(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        extra_headers,
        accept_language,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    pass_params = {
        'user_info': {
            'accept_language': accept_language,
            'is_portal': False,
            'personal_phone_id': '',
        },
    }
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='corp',
        billing_service='food_payment_corp',
        pass_params=pass_params,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='corp',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='corp',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    headers = {**consts.BASE_HEADERS, **extra_headers}
    await check_create_order(payment_type='corp', items=items, headers=headers)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    [
        'extra_headers',
        'app_metrica_device_id',
        'pass_afs_params',
        'pass_3ds_params',
        'trust_afs_params',
        'trust_developer_payload',
    ],
    [
        (
            {},  # extra_headers
            None,  # app_metrica_device_id
            False,  # pass_afs_params
            False,  # pass_3ds_params
            None,  # trust_afs_params
            None,  # trust_developer_payload
        ),
        (
            {'X-AppMetrica-DeviceId': 'Some id'},  # extra_headers
            'Some id',  # app_metrica_device_id
            False,  # pass_afs_params
            False,  # pass_3ds_params
            None,  # trust_afs_params
            None,  # trust_developer_payload
        ),
        (
            {'X-AppMetrica-DeviceId': 'Some id'},  # extra_headers
            'Some id',  # app_metrica_device_id
            True,  # pass_afs_params
            False,  # pass_3ds_params
            {
                'login_id': 'test_login_id',
                'metrica_device_id': 'Some id',
            },  # trust_afs_params
            None,  # trust_developer_payload
        ),
        (
            {'X-AppMetrica-DeviceId': 'Some id'},  # extra_headers
            'Some id',  # app_metrica_device_id
            False,  # pass_afs_params
            True,  # pass_3ds_params
            None,  # trust_afs_params
            None,  # trust_developer_payload
        ),
        (
            {'X-AppMetrica-DeviceId': 'Some id'},  # extra_headers
            'Some id',  # app_metrica_device_id
            True,  # pass_afs_params
            True,  # pass_3ds_params
            {
                'login_id': 'test_login_id',
                'metrica_device_id': 'Some id',
                '3ds_availability': True,
            },  # trust_afs_params
            '{"selected_card_id":"123","auto_start_payment":true,'
            '"template":"checkout"}',  # trust_developer_payload
        ),
    ],
)
async def test_afs_payloades_passed(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        extra_headers,
        app_metrica_device_id,
        experiments3,
        pass_afs_params,
        pass_3ds_params,
        trust_afs_params,
        trust_developer_payload,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )
    experiments3.add_experiment(
        **helpers.make_pass_3ds_params_experiment(pass_3ds_params),
    )
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='card',
        billing_service='food_payment',
        app_metrica_device_id=app_metrica_device_id,
        trust_afs_params=trust_afs_params,
        trust_developer_payload=trust_developer_payload,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='card',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    headers = {**consts.BASE_HEADERS, **extra_headers}
    await check_create_order(payment_type='card', items=items, headers=headers)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'extra_headers, personal_phone_id',
    [({}, None), ({'X-YaTaxi-User': 'personal_phone_id=456'}, '456')],
)
async def test_corp_payment_method_personal_phone_id(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        extra_headers,
        personal_phone_id,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    pass_params = {
        'user_info': {
            'accept_language': '',
            'is_portal': False,
            # test case has None so that personal_phone_id is not
            # in response body but here we need empty string
            # if there was no phone_id
            'personal_phone_id': personal_phone_id or '',
        },
    }
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='corp',
        billing_service='food_payment_corp',
        personal_phone_id=personal_phone_id,
        pass_params=pass_params,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='corp',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='corp',
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    headers = {**consts.BASE_HEADERS, **extra_headers}
    await check_create_order(payment_type='corp', items=items, headers=headers)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_items_info_inserted(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        fetch_items_from_db,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    mock_transactions_invoice_create(
        payment_type='card', billing_service='food_payment',
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    mock_user_state_save_last_payment(payment_type='card')
    items = [
        helpers.make_item(
            item_id='big_mac',
            amount='2.00',
            billing_info={
                'place_id': '100500',
                'balance_client_id': '123456',
                'item_type': 'product',
            },
        ),
    ]
    await check_create_order(payment_type='card', items=items)

    db_items = fetch_items_from_db('test_order')
    assert db_items == [helpers.make_db_row(item_id='big_mac')]
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'payment_type, billing_service',
    [
        ('card', 'food_payment'),
        ('applepay', 'food_payment'),
        ('googlepay', 'food_payment'),
    ],
)
@pytest.mark.parametrize('service', ['eats', 'grocery'])
async def test_save_last_payment_method_card_like(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        billing_service,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        billing_service=billing_service,
        service=service,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type, validate_request=True, service=service,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type=payment_type, items=items, service=service,
    )
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, payment_type)
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_save_last_payment_method_corp(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    pass_params = {
        'user_info': {
            'accept_language': '',
            'is_portal': False,
            'personal_phone_id': '',
        },
    }
    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='corp',
        billing_service='food_payment_corp',
        pass_params=pass_params,
        service=service,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='corp',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='corp', validate_request=True, service=service,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(payment_type='corp', items=items, service=service)
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_save_last_payment_method_badge(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mock_blackbox,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type='badge',
        payment_method_id='badge:yandex_badge:RUB',
        billing_service='food_payment_badge',
        payer_login='foo',
        billing_id=None,
        service=service,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='badge',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type='badge',
        payment_method_id='badge:yandex_badge:RUB',
        validate_request=True,
        service=service,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        items=items,
        service=service,
    )
    assert_db_order_payment(TEST_ORDER_ID, 'badge:yandex_badge:RUB', 'corp')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert mock_blackbox.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    (
        'invoice_create_response,'
        'invoice_update_response,'
        'response_status,'
        'response_body,'
        'invoice_update_times_called,'
        'save_last_payment_times_called'
    ),
    [
        (
            {'status': 200, 'json': {}},
            {'status': 200, 'json': {}},
            200,
            {},
            1,
            1,
        ),
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            {'status': 200, 'json': {}},
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while creating invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
            0,
            0,
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            {'status': 200, 'json': {}},
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while creating invoice. '
                    'Error: `conflict happened`'
                ),
            },
            0,
            0,
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            {'status': 200, 'json': {}},
            500,
            None,
            0,
            0,
        ),
        (
            {'status': 200, 'json': {}},
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while updating invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
            1,
            0,
        ),
        (
            {'status': 200, 'json': {}},
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while updating invoice. '
                    'Error: `conflict happened`'
                ),
            },
            1,
            0,
        ),
        (
            {'status': 200, 'json': {}},
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            None,
            1,
            0,
        ),
    ],
)
async def test_errors(
        taxi_eats_payments,
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        invoice_create_response,
        invoice_update_response,
        response_status,
        response_body,
        invoice_update_times_called,
        save_last_payment_times_called,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        invoice_create_response=invoice_create_response,
    )
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response=invoice_update_response,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        save_last_payment_response={'status': 200, 'json': {}},
    )
    await check_create_order(
        payment_type='card', items=[], response_status=response_status,
    )
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == invoice_update_times_called
    assert (
        save_last_payment_mock.times_called == save_last_payment_times_called
    )


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_no_payment_id(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    invoice_create_mock = mock_transactions_invoice_create(
        invoice_create_response={'status': 200, 'json': {}},
    )
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response={'status': 200, 'json': {}},
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        save_last_payment_response={'status': 200, 'json': {}},
    )
    await check_create_order(
        payment_type='card',
        additional_request_part={'payment_method': {'type': 'card'}},
        items=[],
        response_status=400,
    )
    assert_db_order_payment(TEST_ORDER_ID, expect_no_payment=True)
    assert not invoice_create_mock.has_calls
    assert not invoice_update_mock.has_calls
    assert not save_last_payment_mock.has_calls


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_timeout_error(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mockserver,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    invoice_create_mock = mock_transactions_invoice_create(
        invoice_create_response={'status': 200, 'json': {}},
    )
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response={'status': 200, 'json': {}},
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        error=mockserver.TimeoutError(),
    )
    await check_create_order(payment_type='card', items=[])
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_save_last_payment_server_error(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mockserver,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        invoice_create_response={'status': 200, 'json': {}},
    )
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response={'status': 200, 'json': {}},
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        save_last_payment_response={
            'status': 500,
            'json': {'code': 'internal-server-error', 'message': 'exception'},
        },
    )
    await check_create_order(payment_type='card', items=[])
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_create_order_for_rosneft_business(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        pgsql,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    pass_params = {'terminal_route_data': {'description': 'food'}}
    mock_transactions_invoice_create(
        payment_type='card',
        billing_service='food_fuel_payment',
        pass_params=pass_params,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='big_mac', amount='2.00', commission_category=600,
            ),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items],
        operation_id='create:abcd',
        version=1,
        payment_timeout=180,
    )
    mock_user_state_save_last_payment(payment_type='card')
    items = [
        helpers.make_item(
            item_id='big_mac',
            amount='2.00',
            billing_info={
                'place_id': '100500',
                'balance_client_id': '123456',
                'item_type': 'product',
            },
        ),
    ]
    business = {'business': {'type': 'zapravki', 'specification': ['rosneft']}}
    await check_create_order(
        payment_type='card', items=items, additional_request_part=business,
    )

    order = db_order.DBOrder.fetch(pgsql=pgsql, order_id='test_order')
    actual_order = {
        'business_specification': order.business_specification,
        'complement_amount': order.complement_amount,
        'complement_payment_id': order.complement_payment_id,
        'complement_payment_type': order.complement_payment_type,
        'business_type': order.business_type,
        'currency': order.currency,
        'order_id': order.order_id,
        'service': order.service,
    }
    expected_order = {
        'business_specification': ['rosneft'],
        'complement_amount': None,
        'complement_payment_id': None,
        'complement_payment_type': None,
        'business_type': 'zapravki',
        'currency': 'RUB',
        'order_id': 'test_order',
        'service': 'eats',
    }

    assert actual_order == expected_order
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, 'card')


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('payment_type', ['card', 'applepay', 'googlepay'])
@pytest.mark.parametrize('service', ['eats', 'grocery'])
async def test_passing_ttl_to_transactions(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        billing_service='food_payment',
        service=service,
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items],
        operation_id='create:abcd',
        version=1,
        ttl=600,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type=payment_type, items=items, service=service, ttl=10,
    )
    assert_db_order_payment(TEST_ORDER_ID, TEST_PAYMENT_ID, payment_type)
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.parametrize(
    'blackbox_response, expected_code, stq_times_called',
    [
        (
            {
                'users': [
                    {
                        'aliases': {'13': None},
                        'dbfields': {'subscription.suid.669': '1'},
                        'uid': {'value': '100500'},
                    },
                ],
            },
            200,
            1,
        ),
        ({}, 400, 0),
        ({'users': [{'uid': {'value': '100500'}}]}, 200, 1),
    ],
)
async def test_badge_no_staff(
        check_create_order,
        stq,
        mockserver,
        blackbox_response,
        expected_code,
        stq_times_called,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return blackbox_response

    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        items=items,
        response_status=expected_code,
    )

    assert mock_blackbox.times_called == 1
    assert (
        stq.eats_corp_orders_payment_callback.times_called == stq_times_called
    )


@configs.MAPPING_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_originators_config_name_mapping(
        check_create_order,
        pgsql,
        mock_transactions,
        mock_user_state_save_last_payment,
):
    mock_user_state_save_last_payment()
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='card', items=items, response_status=200,
    )
    order = db_order.DBOrder.fetch(pgsql=pgsql, order_id=consts.TEST_ORDER_ID)
    assert order.originator == consts.PERSEY_ORIGINATOR


@configs.MAPPING_CONFIG
@pytest.mark.tvm2_eda_core
async def test_originators_config_bad_name_mapping(check_create_order):
    await check_create_order(payment_type='card', response_status=503)


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_enable_badge_payment_id(
        check_create_order, mockserver, mock_user_state_save_last_payment,
):
    mock_user_state_save_last_payment()

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {'users': [{'uid': {'value': '100500'}}]}

    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        response_status=200,
    )


@configs.DISABLE_BADGE_CONFIG
@pytest.mark.tvm2_eats_corp_orders
async def test_disable_badge_payment_id(check_create_order):
    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        response_status=400,
    )

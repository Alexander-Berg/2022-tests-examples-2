import pytest


@pytest.mark.redis_store(file='redis_user_headers_set')
@pytest.mark.parametrize(
    (
        'balance_left',
        'overspending_enabled',
        'b2c_enabled',
        'card_exists',
        'payment_type',
    ),
    [
        ('100', True, True, True, 'corp'),
        ('200', True, True, True, 'corp'),
        (None, True, True, True, 'corp'),
        ('1', True, True, True, 'corp_card'),
        ('1', True, False, True, 'corp_card'),
        ('1', False, True, True, 'error'),
        ('1', True, True, False, 'error'),
        ('0', True, True, True, 'card'),
        ('0', False, True, True, 'error'),
        ('0', True, False, True, 'error'),
        ('0', False, False, True, 'error'),
        ('0', True, True, False, 'error'),
    ],
)
@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'places.sql'],
)
async def test_pay_success(
        stq_runner,
        order_id,
        mock_eats_payments_py3,
        mock_eats_taxi_corp_integration,
        mock_corp_users,
        mock_eats_payment_methods_availability,
        mock_eats_catalog_storage,
        mock_personal,
        load_json,
        check_redis_array,
        user_id,
        terminal_id,
        place_id,
        idempotency_key,
        balance_client_id,
        taxi_config,
        fill_db,
        balance_left,
        payment_type,
        overspending_enabled,
        b2c_enabled,
        card_exists,
):
    taxi_config.set_values(
        {
            'EATS_CORP_ORDERS_PAYMENT_SETTINGS': {
                '__default__': {
                    'overspending_enabled': overspending_enabled,
                    'payment_enabled': True,
                    'wait_for_payment_result': True,
                },
            },
            'EATS_CORP_ORDERS_B2C_SETTINGS': {
                'allow_card_only_payments': b2c_enabled,
            },
        },
    )

    if card_exists:
        fill_db('add_card_payment_method.sql')

    @mock_eats_payments_py3('/v1/orders/create')
    async def eats_payments_handler(request):
        # assert request.json == {}
        assert request.json == load_json(f'{payment_type}_pay_request.json')
        return {}

    @mock_corp_users('/v1/users-limits/eats/fetch')
    async def _users_limits(request):
        return {
            'users': [
                {
                    'id': 'id',
                    'client_id': 'client_id',
                    'client_name': 'client_name',
                    'limits': [
                        {
                            'limit_id': 'limit_id',
                            'limits': {
                                'orders_cost': {
                                    'currency': 'RUB',
                                    'currency_sign': 'p',
                                    'balance': '500',
                                    'value': '1000',
                                    'period': 'day',
                                },
                            },
                        },
                    ],
                },
            ],
        }

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def eats_catalog_storage_handler(request):
        place_id = int(request.json['place_ids'][0])
        res = load_json('eats-catalog-storage.json')
        res['places'][0]['place_id'] = place_id
        return res

    @mock_eats_payment_methods_availability('/v1/payment-methods/availability')
    async def epma_handler(request):
        balance_info = (
            {'balance_left': balance_left} if balance_left is not None else {}
        )
        return {
            'payment_methods': [
                {
                    'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                    'type': 'corp',
                    'name': 'corp-test',
                    'currency': 'RUB',
                    'availability': {'available': True, 'disabled_reason': ''},
                    'description': f'Осталось N из 1000 ₽',
                    **balance_info,
                },
            ],
        }

    @mock_personal('/v1/tins/bulk_store')
    async def personal_handler(request):
        return {'items': [{'id': 'tin_id', 'value': ''}]}

    await stq_runner.eats_corp_orders_pay.call(
        task_id='',
        args=(),
        kwargs={
            'user_id': user_id,
            'originator': 'terminal',
            'order_id': None,
            'terminal_id': terminal_id,
            'idempotency_key': idempotency_key,
            'is_confirmation_required': False,
            'place_id': place_id,
            'balance_client_id': balance_client_id,
            'currency': 'RUB',
            'mcc': 1,
            'serialized_items': [
                {
                    'price': '100.0',
                    'quantity': '1.0',
                    'tin': '',
                    'title': 'Мороженое',
                    'vat': 'nds_0',
                },
            ],
        },
    )

    check_redis_array(f'order_{user_id}', load_json(f'order_redis.json'))

    assert not eats_catalog_storage_handler.has_calls
    assert epma_handler.has_calls

    if payment_type != 'error':
        assert eats_payments_handler.has_calls
        assert personal_handler.has_calls
    else:
        assert not eats_payments_handler.has_calls
        assert not personal_handler.has_calls


# todo: 1. test order meta info is saving to db
# todo: 2. test personal_phone_id is required in user_headers
# todo: 3. test stq exits when is_cancelling=True
# todo: 4. test originator cheque
# todo: 5. test it works with different errors from
# EATS_CORP_ORDERS_ERROR_MAPPING_SETTINGS

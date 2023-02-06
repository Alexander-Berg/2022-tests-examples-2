import pytest


def get_data(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = (
            'order_id',
            'author',
            'params',
            'results',
            'apply_time',
            'recalc_id',
        )
        cursor.execute(
            f'SELECT {", ".join(fields)}' f' FROM cache.orders_recalc;', (),
        )
        db_result = cursor.fetchall()
        if db_result:
            return {field: value for field, value in zip(fields, db_result[0])}
        return None


@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        '__default__': {'__default__': 0},
        'RUB': {'__default__': 2, 'iso4217': 2},
    },
)
@pytest.mark.parametrize(
    'case_json, code, recalc_id',
    [
        ('case_1.json', 200, None),
        ('case_2.json', 200, 'uuid1'),
        ('case_3.json', 200, 'uuid1'),
        ('case_4.json', 200, 'uuid1'),
        ('case_5.json', 200, 'uuid1'),
        ('case_6.json', 200, 'uuid1'),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_order_calc_recalculate(
        taxi_pricing_admin,
        case_json,
        load_json,
        order_archive_mock,
        code,
        pgsql,
        recalc_id,
):
    order_id = '00000000000000000000000000000001'
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    case = load_json(case_json)
    expected_json = case['results']

    params = {'order_id': order_id}
    if recalc_id:
        params['recalc_id'] = recalc_id

    response = await taxi_pricing_admin.post(
        'v1/order-calc/recalculate',
        params=params,
        json=case['params'],
        headers={'X-Yandex-Login': 'an_author'},
    )
    assert response.status_code == code
    assert response.json() == expected_json

    dbdata = get_data(pgsql)
    if recalc_id:
        case['db']['recalc_id'] = recalc_id
        assert dbdata == case['db']
    else:
        assert not dbdata


REASONS = {
    'reasons': [
        {'code': 'OTHER', 'name': 'Другое'},
        {'code': 'DOUBLE_PAY', 'name': 'Двойная оплата'},
        {'code': 'DRIVER_REQUEST', 'name': 'Просьба водителя'},
        {'code': 'OTHER_USER', 'name': 'Перепутал пассажиров'},
    ],
}


@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        '__default__': {'__default__': 0},
        'RUB': {'__default__': 2, 'iso4217': 2},
    },
)
@pytest.mark.parametrize(
    'pay_method, window, recalc_id',
    [
        ('card', 'window_1.json', '777'),
        ('cash', 'window_2.json', '777'),
        ('corp', 'window_3.json', '777'),
        ('corp', 'window_3.json', '404'),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['offer_recalc.sql'])
async def test_v1_order_calc_recalculate_apply_draft(
        taxi_pricing_admin,
        load_json,
        pay_method,
        window,
        mockserver,
        recalc_id,
):
    params = {'recalc_id': recalc_id}

    @mockserver.json_handler('/taxi-admin/api/payments/reason_codes/')
    def _mock_reasons(_request):
        return REASONS

    @mockserver.json_handler('/taxi-admin/api/payments/orders_info/')
    def _mock_order_info(_request):
        resp = load_json('payments_info.json')
        resp['orders'][0]['payment_type'] = pay_method
        return resp

    response = await taxi_pricing_admin.get(
        'v1/order-calc/recalculate/apply/draft',
        params=params,
        headers={'X-Yandex-Login': 'an_author', 'Accept-Language': 'ru'},
    )

    if recalc_id == '404':
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert response.json() == load_json(window)


@pytest.mark.parametrize(
    'body, billing_handler, billing_req',
    [
        (
            {
                'billing_version': 1,
                'action_id': 'change_user_price',
                'parameters': {
                    'ticket': 'YANDEXTAXI-666',
                    'user_price': '200',
                    'user_reason': 'DRIVER_REQUEST',
                },
            },
            'change_user',
            {
                'order_id': '00000000000000000000000000000001',
                'reason_code': 'DRIVER_REQUEST',
                'sum': 200.0,
                'ticket_type': 'startrack',
                'version': 1,
                'zendesk_ticket': 'YANDEXTAXI-666',
            },
        ),
        (
            {
                'billing_version': 1,
                'action_id': 'rebill_order',
                'parameters': {'price': '400', 'ticket': 'b22'},
            },
            'rebill_order',
            {
                'cost_for_driver': '400',
                'order_id': '00000000000000000000000000000001',
                'ticket_type': 'chatterbox',
                'zendesk_ticket': 'b22',
            },
        ),
        (
            {
                'billing_version': 1,
                'action_id': 'change_driver_price',
                'parameters': {
                    'ticket': 'YANDEXTAXI-666',
                    'driver_price': '250',
                    'driver_reason': 'OTHER_USER',
                },
            },
            'change_driver',
            {
                'order_id': '00000000000000000000000000000001',
                'reason_code': 'OTHER_USER',
                'sum': 250.0,
                'ticket_type': 'startrack',
                'version': 1,
                'zendesk_ticket': 'YANDEXTAXI-666',
            },
        ),
        (
            {
                'billing_version': 1,
                'action_id': 'change_user_and_driver_prices',
                'parameters': {
                    'user_ticket': 'YANDEXTAXI-666',
                    'driver_ticket': 'YANDEXTAXI-777',
                    'driver_price': '250',
                    'user_price': '255',
                    'user_reason': 'DOUBLE_PAY',
                    'driver_reason': 'DOUBLE_PAY',
                },
            },
            'change_both',
            {
                'driver_reason_code': 'DOUBLE_PAY',
                'driver_sum': 250.0,
                'driver_ticket_type': 'startrack',
                'driver_zendesk_ticket': 'YANDEXTAXI-777',
                'order_id': '00000000000000000000000000000001',
                'user_reason_code': 'DOUBLE_PAY',
                'user_sum': 255.0,
                'user_ticket_type': 'startrack',
                'user_zendesk_ticket': 'YANDEXTAXI-666',
                'version': 1,
            },
        ),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['offer_recalc.sql'])
async def test_v1_order_calc_recalculate_apply(
        taxi_pricing_admin, mockserver, body, billing_handler, billing_req,
):
    params = {'recalc_id': '777'}

    @mockserver.json_handler(
        '/taxi-admin/api/payments/update_order_ride_sum_to_pay/',
    )
    def _change_user(request):
        assert billing_handler == 'change_user'
        assert request.json == billing_req
        return {}

    @mockserver.json_handler('/taxi-admin/api/payments/rebill_order/')
    def _rebill_order(request):
        assert billing_handler == 'rebill_order'
        assert request.json == billing_req
        return {'doc': {'id': 15}}

    @mockserver.json_handler(
        '/taxi-admin/api/payments/update_order_driver_ride_sum_to_pay/',
    )
    def _change_driver(request):
        assert billing_handler == 'change_driver'
        assert request.json == billing_req
        return {}

    @mockserver.json_handler(
        '/taxi-admin/api/payments/update_order_decoupling_ride_sum_to_pay/',
    )
    def _change_both(request):
        assert billing_handler == 'change_both'
        assert request.json == billing_req
        return {}

    response = await taxi_pricing_admin.post(
        'v1/order-calc/recalculate/apply',
        params=params,
        json=body,
        headers={'X-Yandex-Login': 'an_author', 'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

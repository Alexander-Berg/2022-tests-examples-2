import contextlib
import copy

import pytest


BASE_CONFIRMED_KWARGS = {
    'order_id': '777',
    'yandex_uid': 'phonish_uid',
    'x_login_id': 'some_login_id',
    'amount': '56',
    'currency_code': 'RUB',
    'payment_tech_type': 'card',
    'payment_method_id': 'card-x777',
    'x_remote_ip': '127.0.0.1',
    'personal_phone_id': 'phone777',
    'grocery_country_iso3': 'RUS',
    'region_id': 2809,
    'x_yataxi_session': 'stub',
    'x_request_language': 'ru',
    'x_request_application': None,
    'x_yataxi_user_id': '971461edca184584a5f05a9277e4fa6e',
    'billing_settings_version': '666',
}
BASE_DELIVERED_KWARGS = {'order_id': '777', 'grocery_country_iso3': 'RUS'}
BASE_CANCELLED_KWARGS = {
    'order_id': '777',
    'yandex_uid': 'phonish_uid',
    'x_login_id': 'some_login_id',
    'x_remote_ip': '127.0.0.1',
    'personal_phone_id': 'phone777',
    'grocery_country_iso3': 'RUS',
    'x_yataxi_user_id': '971461edca184584a5f05a9277e4fa6e',
    'billing_settings_version': '666',
}
BASE_DONATION = (
    'friends',
    'phonish_uid',
    '4',
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    1,
    'lavka',
    '777',
)
BASE_DONATION_STATUSES = {
    ('lavka', '777'): 'started',
    ('lavka', '778'): 'not_authorized',
    ('lavka', '779'): 'finished',
}


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_gp_request',
        'expected_create_times_called',
        'expected_zalogin_times_called',
    ],
    [
        (
            BASE_CONFIRMED_KWARGS,
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            1,
            1,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'currency_code': 'USD'}},
            [],
            None,
            0,
            0,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'payment_tech_type': 'cash'}},
            [],
            None,
            0,
            0,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'yandex_uid': 'no_subs'}},
            [],
            None,
            0,
            1,
        ),
        ({**BASE_CONFIRMED_KWARGS, **{'amount': '10'}}, [], None, 0, 1),
        (
            {**BASE_CONFIRMED_KWARGS, **{'grocery_country_iso3': 'ISR'}},
            [],
            None,
            0,
            0,
        ),
        (
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            1,
            1,
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            1,
            1,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                    'lavka': ['ios', 'android'],
                },
            ),
        ),
        pytest.param(
            BASE_CONFIRMED_KWARGS,
            [],
            None,
            0,
            0,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'lavka': ['ios']},
            ),
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [],
            None,
            0,
            0,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'lavka': ['ios']},
            ),
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            1,
            1,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'lavka': ['android:exp3'],
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_allow_app',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'lavka'},
                    ],
                    value={'allowed': True},
                ),
            ],
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [],
            None,
            0,
            0,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'lavka': ['android:exp3'],
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_allow_app',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'lavka'},
                    ],
                    value={'allowed': False},
                ),
            ],
        ),
    ],
)
async def test_confirmed(
        mockserver,
        load_json,
        stq_runner,
        get_donations,
        mock_grocery_payments,
        mock_zalogin,
        stq_kwargs,
        expected_donations,
        expected_gp_request,
        expected_create_times_called,
        expected_zalogin_times_called,
):
    zalogin_mock = mock_zalogin(stq_kwargs['yandex_uid'], None, True)

    @mock_grocery_payments('/payments/v1/create')
    async def create_mock(request):
        exp_request = load_json(expected_gp_request)
        assert request.json == exp_request['body']

        return mockserver.make_response(
            status=200,
            json={
                'invoice_id': '1',
                'invoice_version': 2,
                'operation_id': '3',
            },
        )

    await stq_runner.persey_payments_grocery_order_confirmed.call(
        task_id='1', args=[], kwargs=stq_kwargs,
    )

    assert create_mock.times_called == expected_create_times_called
    assert zalogin_mock.times_called == expected_zalogin_times_called
    assert get_donations() == expected_donations


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'cancelled_times_called, delivered_times_called',
    [
        (0, 0),
        pytest.param(
            1,
            0,
            marks=pytest.mark.pgsql(
                'persey_payments', files=['billing_events_cancel.sql'],
            ),
        ),
        pytest.param(
            0,
            1,
            marks=pytest.mark.pgsql(
                'persey_payments', files=['billing_events_clear.sql'],
            ),
        ),
    ],
)
async def test_confirmed_billing_events(
        stq,
        stq_runner,
        mock_zalogin,
        mock_grocery_payments,
        cancelled_times_called,
        delivered_times_called,
):
    mock_zalogin('phonish_uid', None, True)

    @mock_grocery_payments('/payments/v1/create')
    async def _create_mock(request):
        return {'invoice_id': '1', 'invoice_version': 2, 'operation_id': '3'}

    await stq_runner.persey_payments_grocery_order_confirmed.call(
        task_id='1', args=[], kwargs=BASE_CONFIRMED_KWARGS,
    )

    assert (
        stq.persey_payments_grocery_order_cancelled.times_called
        == cancelled_times_called
    )
    assert (
        stq.persey_payments_grocery_order_delivered.times_called
        == delivered_times_called
    )


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_started.sql'],
)
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_gp_request',
        'clear_resp_code',
        'expected_stq_fail',
    ],
    [
        (
            BASE_DELIVERED_KWARGS,
            [BASE_DONATION + ('started',)],
            'expected_clear_request.json',
            None,
            False,
        ),
        (
            BASE_DELIVERED_KWARGS,
            [BASE_DONATION + ('started',)],
            None,
            500,
            True,
        ),
        (
            {**BASE_DELIVERED_KWARGS, **{'order_id': '123'}},
            [BASE_DONATION + ('started',)],
            None,
            404,
            False,
        ),
    ],
)
async def test_delivered(
        mockserver,
        load_json,
        stq_runner,
        get_billing_events,
        get_donations,
        mock_grocery_payments,
        stq_kwargs,
        expected_donations,
        expected_gp_request,
        clear_resp_code,
        expected_stq_fail,
):
    @mock_grocery_payments('/payments/v1/clear')
    async def clear_mock(request):
        if clear_resp_code is not None:
            return mockserver.make_response(
                status=clear_resp_code,
                json={'code': 'code', 'message': 'message'},
            )

        exp_request = load_json(expected_gp_request)
        assert request.json == exp_request['body']

        return mockserver.make_response(status=200, json={})

    with pytest.raises(
            RuntimeError,
    ) if expected_stq_fail else contextlib.nullcontext():
        await stq_runner.persey_payments_grocery_order_delivered.call(
            task_id='1', args=[], kwargs=stq_kwargs,
        )

    assert clear_mock.times_called >= 1
    assert get_donations() == expected_donations
    assert get_billing_events() == [('lavka', stq_kwargs['order_id'], 'clear')]


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_started.sql'],
)
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_gp_request',
        'cancel_resp_code',
    ],
    [
        (
            BASE_CANCELLED_KWARGS,
            [BASE_DONATION + ('started',)],
            'expected_cancel_request.json',
            None,
        ),
        (
            {**BASE_CANCELLED_KWARGS, **{'order_id': '123'}},
            [BASE_DONATION + ('started',)],
            None,
            404,
        ),
    ],
)
async def test_cancelled(
        mockserver,
        load_json,
        stq_runner,
        get_billing_events,
        get_donations,
        mock_grocery_payments,
        stq_kwargs,
        expected_donations,
        expected_gp_request,
        cancel_resp_code,
):
    @mock_grocery_payments('/payments/v1/cancel')
    async def cancel_mock(request):
        if cancel_resp_code is not None:
            return mockserver.make_response(
                status=cancel_resp_code,
                json={'code': 'code', 'message': 'message'},
            )

        exp_request = load_json(expected_gp_request)
        assert request.json == exp_request['body']

        return mockserver.make_response(
            status=200,
            json={
                'invoice_id': '1',
                'invoice_version': 2,
                'operation_type': 'cancel',
                'operation_id': '3',
            },
        )

    await stq_runner.persey_payments_grocery_order_cancelled.call(
        task_id='1', args=[], kwargs=stq_kwargs,
    )

    assert cancel_mock.times_called == 1
    assert get_donations() == expected_donations
    assert get_billing_events() == [
        ('lavka', stq_kwargs['order_id'], 'cancel'),
    ]


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_callback.sql'],
)
@pytest.mark.parametrize(
    'order_id, donation_status',
    [('777', 'started'), ('778', 'not_authorized'), ('779', 'finished')],
)
@pytest.mark.parametrize(
    'operation, status, slug',
    [
        ('hold', 'success', 'create_success'),
        ('hold', 'failure', 'create_fail'),
        ('clear', 'success', 'clear_success'),
        ('clear', 'failure', 'clear_fail'),
        ('cancel', 'success', 'cancel_fail'),
    ],
)
async def test_callback(
        load_json,
        stq_runner,
        get_donation_statuses,
        order_id,
        donation_status,
        operation,
        status,
        slug,
):
    await stq_runner.persey_payments_grocery_callback.call(
        task_id='1',
        args=[],
        kwargs={
            'order_id': order_id,
            'operation': operation,
            'status': status,
        },
    )

    exp_donation_statuses = copy.deepcopy(BASE_DONATION_STATUSES)
    if slug in ['create_success', 'clear_success']:
        if donation_status == 'started':
            exp_donation_statuses['lavka', order_id] = 'finished'
    else:
        exp_donation_statuses['lavka', order_id] = 'not_authorized'

    assert get_donation_statuses() == exp_donation_statuses

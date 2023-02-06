import contextlib
import copy

import pytest

from test_persey_payments import conftest


BASE_CONFIRMED_KWARGS = {
    'order_id': '777',
    'brand': 'eats',
    'yandex_uid': 'phonish_uid',
    'x_yataxi_bound_uids': '',
    'amount': '56',
    'currency_code': 'RUB',
    'payment_tech_type': 'card',
    'payment_method_id': 'card-x777',
    'x_remote_ip': '127.0.0.1',
    'x_login_id': 'some_login_id',
    'x_yataxi_pass_flags': 'portal,cashback-plus,credentials=token-bearer',
    'x_request_language': 'ru',
    'country_code': 'rus',
    'mcc': 8888,
    'billing_balance_client_id': 'some_client_id',
    'accept_language': 'ru-RU',
    'x_yataxi_user': 'personal_phone_id=phone777',
    'x_yataxi_user_id': '971461edca184584a5f05a9277e4fa6e',
    'x_yataxi_phone_id': '5dedaac57984b5db62c5e46e',
    'x_request_application': None,
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
    'eats',
    '777',
)
BASE_DONATION_STATUSES = {
    ('eats', '777'): 'started',
    ('eats', '778'): 'not_authorized',
    ('eats', '779'): 'finished',
}


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@conftest.ride_subs_config({'allowed_brands': ['eats', 'lavka']})
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_ep_request',
        'expected_ep_headers',
        'expected_create_times_called',
        'expected_stq_fail',
    ],
    [
        (
            BASE_CONFIRMED_KWARGS,
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            'expected_create_headers.json',
            1,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'currency_code': 'USD'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'payment_tech_type': 'cash'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'brand': 'lavka'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'brand': 'not_allowed'}},
            [],
            None,
            None,
            0,
            True,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'yandex_uid': 'no_subs'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'amount': '10'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {**BASE_CONFIRMED_KWARGS, **{'country_code': 'afg'}},
            [],
            None,
            None,
            0,
            False,
        ),
        (
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            'expected_create_headers.json',
            1,
            False,
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            'expected_create_headers.json',
            1,
            False,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                    'eats': ['ios', 'android'],
                },
            ),
        ),
        pytest.param(
            BASE_CONFIRMED_KWARGS,
            [],
            None,
            None,
            0,
            False,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'eats': ['ios']},
            ),
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [],
            None,
            None,
            0,
            False,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'eats': ['ios']},
            ),
        ),
        pytest.param(
            {
                **BASE_CONFIRMED_KWARGS,
                **{'x_request_application': 'app_name=android'},
            },
            [BASE_DONATION + ('started',)],
            'expected_create_request.json',
            'expected_create_headers.json',
            1,
            False,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'eats': ['android:exp3'],
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
                            'name': 'phone_id',
                            'type': 'string',
                            'value': '5dedaac57984b5db62c5e46e',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'eats'},
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
            None,
            0,
            False,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'eats': ['android:exp3'],
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
                            'name': 'phone_id',
                            'type': 'string',
                            'value': '5dedaac57984b5db62c5e46e',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'eats'},
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
        mock_eats_payments_py3,
        stq_kwargs,
        expected_donations,
        expected_ep_request,
        expected_ep_headers,
        expected_create_times_called,
        expected_stq_fail,
):
    @mock_eats_payments_py3('/v1/orders/create')
    async def create_order_mock(request):
        assert request.json == load_json(expected_ep_request)
        for header, value in load_json(expected_ep_headers).items():
            assert request.headers[header] == value

        return mockserver.make_response(status=200, json={})

    with pytest.raises(
            RuntimeError,
    ) if expected_stq_fail else contextlib.nullcontext():
        await stq_runner.persey_payments_eats_order_confirmed.call(
            task_id='1', args=[], kwargs=stq_kwargs,
        )

    assert create_order_mock.times_called == expected_create_times_called
    assert get_donations() == expected_donations


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@conftest.ride_subs_config({'allowed_brands': ['eats', 'lavka']})
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
        mock_eats_payments_py3,
        cancelled_times_called,
        delivered_times_called,
):
    @mock_eats_payments_py3('/v1/orders/create')
    async def _create_order_mock(request):
        return {}

    await stq_runner.persey_payments_eats_order_confirmed.call(
        task_id='1', args=[], kwargs=BASE_CONFIRMED_KWARGS,
    )

    assert (
        stq.persey_payments_eats_order_cancelled.times_called
        == cancelled_times_called
    )
    assert (
        stq.persey_payments_eats_order_delivered.times_called
        == delivered_times_called
    )


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_created.sql'],
)
@conftest.ride_subs_config({'allowed_brands': ['eats', 'lavka']})
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_ep_request',
        'close_resp_code',
        'expected_stq_fail',
    ],
    [
        (
            {'order_id': '777', 'brand': 'eats'},
            [BASE_DONATION + ('started',)],
            'expected_close_request.json',
            None,
            False,
        ),
        (
            {'order_id': '777', 'brand': 'eats'},
            [BASE_DONATION + ('started',)],
            None,
            500,
            True,
        ),
        (
            {'order_id': '123', 'brand': 'eats'},
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
        get_donations,
        get_billing_events,
        mock_eats_payments_py3,
        stq_kwargs,
        expected_donations,
        expected_ep_request,
        close_resp_code,
        expected_stq_fail,
):
    @mock_eats_payments_py3('/v1/orders/close')
    async def close_order_mock(request):
        if close_resp_code is not None:
            return mockserver.make_response(
                status=close_resp_code,
                json={'code': 'code', 'message': 'message'},
            )

        assert request.json == load_json(expected_ep_request)

        return mockserver.make_response(status=200, json={})

    with pytest.raises(
            RuntimeError,
    ) if expected_stq_fail else contextlib.nullcontext():
        await stq_runner.persey_payments_eats_order_delivered.call(
            task_id='1', args=[], kwargs=stq_kwargs,
        )

    assert close_order_mock.times_called >= 1
    assert get_donations() == expected_donations
    assert get_billing_events() == [
        (stq_kwargs['brand'], stq_kwargs['order_id'], 'clear'),
    ]


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_created.sql'],
)
@conftest.ride_subs_config({'allowed_brands': ['eats', 'lavka']})
@pytest.mark.parametrize(
    [
        'stq_kwargs',
        'expected_donations',
        'expected_cancel_request',
        'expected_retrieve_request',
        'retrieve_response',
        'retrieve_resp_code',
        'cancel_times_called',
    ],
    [
        (
            {'order_id': '777', 'brand': 'eats'},
            [BASE_DONATION + ('started',)],
            'expected_cancel_request.json',
            'expected_retrieve_request.json',
            'retrieve_response.json',
            None,
            1,
        ),
        (
            {'order_id': '123', 'brand': 'eats'},
            [BASE_DONATION + ('started',)],
            None,
            None,
            None,
            404,
            0,
        ),
    ],
)
async def test_cancelled(
        mockserver,
        load_json,
        stq_runner,
        get_donations,
        get_billing_events,
        mock_eats_payments_py3,
        stq_kwargs,
        expected_donations,
        expected_cancel_request,
        expected_retrieve_request,
        retrieve_response,
        retrieve_resp_code,
        cancel_times_called,
):
    @mock_eats_payments_py3('/v1/orders/retrieve')
    async def retrieve_order_mock(request):
        if retrieve_resp_code is not None:
            return mockserver.make_response(
                status=retrieve_resp_code,
                json={'code': 'code', 'message': 'message'},
            )

        assert request.json == load_json(expected_retrieve_request)

        return mockserver.make_response(
            status=200, json=load_json(retrieve_response),
        )

    @mock_eats_payments_py3('/v1/orders/cancel')
    async def cancel_order_mock(request):
        assert request.json == load_json(expected_cancel_request)

        return mockserver.make_response(status=200, json={})

    await stq_runner.persey_payments_eats_order_cancelled.call(
        task_id='1', args=[], kwargs=stq_kwargs,
    )

    assert retrieve_order_mock.times_called == 1
    assert cancel_order_mock.times_called == cancel_times_called
    assert get_donations() == expected_donations
    assert get_billing_events() == [
        (stq_kwargs['brand'], stq_kwargs['order_id'], 'cancel'),
    ]


@pytest.mark.pgsql(
    'persey_payments', files=['simple.sql', 'donation_callback.sql'],
)
@conftest.ride_subs_config({'allowed_brands': ['eats', 'lavka']})
@pytest.mark.parametrize(
    ['brand', 'order_id', 'eats_payments_order_id', 'donation_status'],
    [
        ('eats', '777', 'donation-eats-777', 'started'),
        ('eats', '778', 'donation-eats-778', 'not_authorized'),
        ('eats', '779', 'donation-eats-779', 'finished'),
    ],
)
@pytest.mark.parametrize(
    'action, status, slug',
    [
        ('purchase', 'confirmed', 'create_success'),
        ('purchase', 'rejected', 'create_fail'),
        ('cancel', 'confirmed', 'cancel_success'),
    ],
)
async def test_callback(
        load_json,
        stq_runner,
        get_donations,
        get_donation_statuses,
        brand,
        order_id,
        eats_payments_order_id,
        donation_status,
        action,
        status,
        slug,
):
    await stq_runner.persey_payments_eats_callback.call(
        task_id='1',
        args=[],
        kwargs={
            'order_id': eats_payments_order_id,
            'action': action,
            'status': status,
            'revision': 'irrelevant',
        },
    )

    exp_donation_statuses = copy.deepcopy(BASE_DONATION_STATUSES)
    if slug == 'create_success':
        if donation_status == 'started':
            exp_donation_statuses[brand, order_id] = 'finished'
    else:
        exp_donation_statuses[brand, order_id] = 'not_authorized'

    assert get_donation_statuses() == exp_donation_statuses

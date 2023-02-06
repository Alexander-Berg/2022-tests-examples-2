import uuid

import pytest


@pytest.mark.parametrize(
    'kwargs, expected_deposit_requests, expected_call',
    [
        pytest.param(
            {
                'order_id': 'test_order_id',
                'currency': 'RUB',
                'discounts': [
                    {'discount_id': 1, 'discount_value': 100},
                    {'discount_id': 2, 'discount_value': 200},
                ],
                'time': '2022-03-25T00:00:00+00:00',
                'personal_phone_id': 'test_personal_phone_id',
                'eater_id': 'test_eater_id',
                'yandex_uid': 'test_yandex_uid',
            },
            [],
            {
                'discounts': [{'discount_id': 1, 'discount_value': 100.0}],
                'eater_id': 'test_eater_id',
                'order_id': 'test_order_id',
                'personal_phone_id': 'test_personal_phone_id',
                'time': '1970-01-01T00:00:00+00:00',
                'yandex_uid': 'test_yandex_uid',
            },
            id='ok',
        ),
        pytest.param(
            {
                'order_id': 'test_order_id',
                'currency': 'RUB',
                'discounts': [{'discount_id': 3, 'discount_value': 200}],
                'time': '2022-03-25T00:00:00+00:00',
                'personal_phone_id': 'test_personal_phone_id',
                'eater_id': 'test_eater_id',
                'yandex_uid': 'test_yandex_uid',
            },
            [
                {
                    'amount': '200.000000',
                    'currency': 'RUB',
                    'event_at': '2022-03-25T00:00:00+0000',
                    'limit_ref': 'eats-discounts_3',
                },
            ],
            None,
            id='with_limit',
        ),
        pytest.param(
            {
                'order_id': 'test_order_id',
                'currency': 'RUB',
                'discounts': [{'discount_id': 2, 'discount_value': 200}],
                'time': '2022-03-25T00:00:00+00:00',
                'personal_phone_id': 'test_personal_phone_id',
                'eater_id': 'test_eater_id',
                'yandex_uid': 'test_yandex_uid',
            },
            [],
            None,
            id='empty',
        ),
    ],
)
@pytest.mark.pgsql('eats_discounts', files=['match_data.sql'])
async def test_eats_discounts_discount_usages_add(
        mockserver,
        stq,
        stq_runner,
        kwargs,
        expected_deposit_requests,
        expected_call,
):
    deposit_requests = []

    @mockserver.json_handler('/billing-limits/v1/deposit')
    def _deposit_handler(request):
        deposit_requests.append(request.json)
        return {}

    await stq_runner.eats_discounts_discount_usages_add.call(
        task_id=str(uuid.uuid4()), kwargs=kwargs,
    )
    call = None
    if stq.eats_discounts_statistics_add.has_calls:
        call = stq.eats_discounts_statistics_add.next_call()['kwargs']
        call.pop('log_extra')
    assert call == expected_call
    assert deposit_requests == expected_deposit_requests


@pytest.mark.parametrize(
    'kwargs, expected_deposit_requests, expected_call',
    [
        pytest.param(
            {
                'order_id': 'test_order_id',
                'time': '2022-03-25T00:00:00+00:00',
                'currency': 'RUB',
                'discounts': [
                    {'discount_id': 1, 'discount_value': 100},
                    {'discount_id': 2, 'discount_value': 200},
                ],
            },
            [],
            {
                'discounts': [{'discount_id': 1, 'discount_value': 100.0}],
                'order_id': 'test_order_id',
            },
            id='ok',
        ),
        pytest.param(
            {
                'order_id': 'test_order_id',
                'time': '2022-03-25T00:00:00+00:00',
                'currency': 'RUB',
                'discounts': [{'discount_id': 3, 'discount_value': 200}],
            },
            [
                {
                    'amount': '-200.000000',
                    'currency': 'RUB',
                    'event_at': '2022-03-25T00:00:00+0000',
                    'limit_ref': 'eats-discounts_3',
                },
            ],
            None,
            id='with_limit',
        ),
        pytest.param(
            {
                'order_id': 'test_order_id',
                'time': '2022-03-25T00:00:00+00:00',
                'currency': 'RUB',
                'discounts': [{'discount_id': 2, 'discount_value': 200}],
            },
            [],
            None,
            id='empty',
        ),
    ],
)
@pytest.mark.pgsql('eats_discounts', files=['match_data.sql'])
async def test_eats_discounts_discount_usages_cancel(
        mockserver,
        stq,
        stq_runner,
        kwargs,
        expected_deposit_requests,
        expected_call,
):
    deposit_requests = []

    @mockserver.json_handler('/billing-limits/v1/deposit')
    def _deposit_handler(request):
        deposit_requests.append(request.json)
        return {}

    await stq_runner.eats_discounts_discount_usages_cancel.call(
        task_id=str(uuid.uuid4()), kwargs=kwargs,
    )
    call = None
    if stq.eats_discounts_statistics_cancel.has_calls:
        call = stq.eats_discounts_statistics_cancel.next_call()['kwargs']
        call.pop('log_extra')
    assert call == expected_call
    assert deposit_requests == expected_deposit_requests

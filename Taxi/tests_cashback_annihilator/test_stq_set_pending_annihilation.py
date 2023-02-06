import datetime

import pytest


BASIC_STQ_KWARGS = {
    'yandex_uid': '123',
    'wallet_id': 'w/123',
    'originator': 'table_upload',
}
FAILED_STQ_KWARGS = {
    'yandex_uid': '123_failed',
    'wallet_id': 'w/123_failed',
    'originator': 'table_upload',
}


@pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'general_annihilation_date': (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'stq_kwargs',
    [
        pytest.param(BASIC_STQ_KWARGS),
        pytest.param(
            {
                'yandex_uid': '123',
                'wallet_id': 'w/123',
                'originator': 'table_upload',
            },
        ),
    ],
)
async def test_set_annihilation_happy_path(
        stq_runner, mockserver, pgsql, stq_kwargs,
):
    @mockserver.json_handler(
        '/billing-wallet/v1/balance/set_pending_annihilation',
    )
    async def _set_annihilation(request):
        assert request.json['version'] == 1
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/billing-wallet/v1/balance/get_pending_annihilation',
    )
    async def _get_annihilation(request):
        response = {
            'yandex_uid': request.json['yandex_uid'],
            'wallet_id': request.json['wallet_id'],
            'amount': '120.0000',
            'version': 1,
        }
        return mockserver.make_response(status=200, json=response)

    cursor = pgsql['cashback_annihilator'].cursor()
    cursor.execute(
        'INSERT INTO cashback_annihilator.balances '
        '(yandex_uid, wallet_id, balance_to_expire,'
        ' currency, annihilation_date) '
        'VALUES (%s, %s, \'140.000\', \'RUB\', \'2024-07-10T10:00:00.00Z\');',
        [stq_kwargs['yandex_uid'], stq_kwargs['wallet_id']],
    )

    await stq_runner.cashback_set_pending_annihilation.call(
        task_id='task_id', kwargs=stq_kwargs, expect_fail=False,
    )

    assert _set_annihilation.has_calls
    assert _get_annihilation.has_calls


@pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'general_annihilation_date': (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'enabled': True,
    },
)
async def test_set_annihilation_already_actual_amount(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler(
        '/billing-wallet/v1/balance/set_pending_annihilation',
    )
    async def _set_annihilation(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/billing-wallet/v1/balance/get_pending_annihilation',
    )
    async def _get_annihilation(request):
        response = {
            'yandex_uid': request.json['yandex_uid'],
            'wallet_id': request.json['wallet_id'],
            'amount': '120.0000',
            'version': 1,
        }
        return mockserver.make_response(status=200, json=response)

    cursor = pgsql['cashback_annihilator'].cursor()
    cursor.execute(
        'INSERT INTO cashback_annihilator.balances '
        '(yandex_uid, wallet_id, balance_to_expire,'
        ' currency, annihilation_date) '
        'VALUES (%s, %s, \'120.000\', \'RUB\', \'2024-07-10T10:00:00.00Z\');',
        [BASIC_STQ_KWARGS['yandex_uid'], BASIC_STQ_KWARGS['wallet_id']],
    )

    await stq_runner.cashback_set_pending_annihilation.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=False,
    )

    assert _get_annihilation.has_calls
    assert _set_annihilation.has_calls


@pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'general_annihilation_date': (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'enabled': False,
    },
)
async def test_set_annihilation_config_disabled(stq_runner, mockserver):
    @mockserver.json_handler(
        '/billing-wallet/v1/balance/set_pending_annihilation',
    )
    async def _set_annihilation(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/billing-wallet/v1/balance/get_pending_annihilation',
    )
    async def _get_annihilation(request):
        response = {
            'yandex_uid': request.json['yandex_uid'],
            'wallet_id': request.json['wallet_id'],
            'amount': '120.0000',
            'version': 1,
        }
        return mockserver.make_response(status=200, json=response)

    await stq_runner.cashback_set_pending_annihilation.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=False,
    )

    assert not _set_annihilation.has_calls
    assert not _get_annihilation.has_calls


@pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'general_annihilation_date': (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'stq_kwargs, error',
    [
        pytest.param(FAILED_STQ_KWARGS, 'not_in_base', id='not_in_base'),
        pytest.param(FAILED_STQ_KWARGS, 'bw_error_set', id='set_error'),
        pytest.param(FAILED_STQ_KWARGS, 'bw_error_get', id='get_error'),
    ],
)
async def test_set_annihilation_include_errors(
        stq_runner, mockserver, pgsql, stq_kwargs, error, stq,
):
    @mockserver.json_handler(
        '/billing-wallet/v1/balance/set_pending_annihilation',
    )
    async def _set_annihilation(request):
        if error == 'bw_error_set':
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/billing-wallet/v1/balance/get_pending_annihilation',
    )
    async def _get_annihilation(request):
        response = {
            'yandex_uid': request.json['yandex_uid'],
            'wallet_id': request.json['wallet_id'],
            'amount': '120.0000',
            'version': 1,
        }
        if error == 'bw_error_get':
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=200, json=response)

    if error != 'not_in_base':
        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            'INSERT INTO cashback_annihilator.balances '
            '(yandex_uid, wallet_id, balance_to_expire,'
            ' currency, annihilation_date) '
            'VALUES (%s, %s, \'140.000\', \'RUB\','
            ' \'2024-07-10T10:00:00.00Z\');',
            [stq_kwargs['yandex_uid'], stq_kwargs['wallet_id']],
        )

    await stq_runner.cashback_set_pending_annihilation.call(
        task_id='task_id', kwargs=stq_kwargs, expect_fail=False,
    )

    if error == 'not_in_base':
        assert not _set_annihilation.has_calls
        assert not _get_annihilation.has_calls
        return

    if error == 'bw_error_set':
        assert _get_annihilation.has_calls
        assert _set_annihilation.has_calls
    if error == 'bw_error_get':
        assert _get_annihilation.has_calls
        assert not _set_annihilation.has_calls

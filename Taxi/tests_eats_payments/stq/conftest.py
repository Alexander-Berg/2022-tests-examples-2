import typing

import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers


# pylint: disable=invalid-name
@pytest.fixture(name='check_eda_callback')
def check_eda_callback_fixture(stq):
    def _inner(**kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.eda_order_processing_payment_events_callback,
            task_id='test_task_id',
            queue='eda_order_processing_payment_events_callback',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_persey_callback')
def check_persey_callback_fixture(stq):
    def _inner(**kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.persey_payments_eats_callback,
            task_id='test_task_id',
            queue='persey_payments_eats_callback',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_corp_orders_callback')
def check_corp_orders_callback_fixture(stq):
    def _inner(**kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.eats_corp_orders_payment_callback,
            task_id='test_task_id',
            queue='eats_corp_orders_payment_callback',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_ei_offline_orders_callback')
def check_ei_offline_orders_callback_fixture(stq):
    def _inner(**kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.ei_offline_orders_eats_payments_callback,
            task_id='test_task_id',
            queue='ei_offline_orders_eats_payments_callback',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_billing_callback')
def check_billing_callback_fixture(stq):
    def _inner(task_id: str = 'some_task_id', **kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.eats_payments_billing_proxy_callback,
            task_id=task_id,
            queue='eats_payments_billing_proxy_callback',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_cashback_callback')
def check_cashback_callback_fixture(stq):
    def _inner(**kwargs):
        service = kwargs.get('service', consts.DEFAULT_SERVICE)
        helpers.check_callback_mock(
            callback_mock=stq.universal_cashback_processing,
            task_id=f'{service}_test_order',
            queue='universal_cashback_processing',
            **kwargs,
        )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_send_receipt')
def check_send_receipt_fixture(stq_runner, stq):
    async def _inner(
            send_receipt_times_called,
            task_id: typing.Optional[str] = None,
            exec_tries: typing.Optional[int] = None,
    ):
        assert (
            stq.eats_payments_send_receipt.times_called
            == send_receipt_times_called
        )
        for _ in range(send_receipt_times_called):
            next_call = stq.eats_payments_send_receipt.next_call()
            next_task_id = next_call['id']
            if task_id is not None:
                assert task_id == next_task_id
            kwargs = next_call['kwargs']
            await stq_runner.eats_payments_send_receipt.call(
                task_id=next_task_id, kwargs=kwargs, exec_tries=exec_tries,
            )

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_send_receipt_callback')
def check_send_receipt_callback_fixture(stq):
    def _inner(task_id: str = 'some_task_id', **kwargs):
        helpers.check_callback_mock(
            callback_mock=stq.eats_payments_send_receipt,
            task_id=task_id,
            queue='eats_payments_send_receipt',
            **kwargs,
        )

    return _inner


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    def _inner(
            data_type: str,
            personal_id: typing.Optional[str] = None,
            value: typing.Optional[str] = None,
            personal_response=None,
            error=None,
            **kwargs,
    ):
        # pylint: disable=invalid-name
        @mockserver.json_handler(f'/personal/v1/{data_type}/retrieve')
        def personal_retrieve_handler(request):
            if personal_response is not None:
                return mockserver.make_response(**personal_response)

            if error is not None:
                raise error

            if personal_id is not None:
                assert request.json == {
                    'id': personal_id,
                    'primary_replica': False,
                }
            return {'id': personal_id, 'value': value}

        return personal_retrieve_handler

    return _inner


@pytest.fixture(name='mock_personal_retrieve_emails')
def _mock_personal_retrieve_emails(mock_personal):
    def _inner():
        return mock_personal(
            'emails',
            personal_id='personal-email-id',
            value='user@example.com',
        )

    return _inner


@pytest.fixture(name='mock_personal_retrieve_phones')
def _mock_personal_retrieve_phones(mock_personal):
    def _inner():
        return mock_personal(
            'phones', personal_id='personal-phone-id', value='+79999999999',
        )

    return _inner


@pytest.fixture(name='mock_personal_retrieve_tins')
def _mock_personal_retrieve_tins(mock_personal):
    def _inner():
        return mock_personal(
            'tins', personal_id='personal-tin-id', value='123456',
        )

    return _inner

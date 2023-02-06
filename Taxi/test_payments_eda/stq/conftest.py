import typing

import pytest

from taxi.stq import async_worker_ng

from payments_eda.generated.stq3 import stq_context
from payments_eda.stq import callback
from test_payments_eda.stq import consts as stq_consts


@pytest.fixture(name='mock_invoice_retrieve')
def mock_invoice_retrieve_fixture(mockserver):
    def _mock_invoice_retrieve_fixture(**extra):
        @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
        def _invoice_retrieve(request):
            return {**stq_consts.DEFAULT_INVOICE, **extra}

        return _invoice_retrieve

    return _mock_invoice_retrieve_fixture


class Sentinel:
    pass


_SENTINEL = Sentinel()


@pytest.fixture(name='mock_eda_event')
def mock_eda_event_fixture(mockserver):
    def _mock_eda_event_fixture(
            base_url: typing.Optional[str] = None,
            expected_action: typing.Optional[str] = None,
            expected_data: typing.Optional[dict] = None,
            expected_full_sum: typing.Union[
                typing.Optional[typing.Dict[str, typing.List[dict]]], Sentinel,
            ] = _SENTINEL,
            expected_extra_query_data: typing.Optional[dict] = None,
            expected_account_type: typing.Optional[str] = None,
    ):
        base_url = 'eda_superapp' if base_url is None else base_url
        url = f'/{base_url}/internal-api/v1/payment/taxi/events'

        @mockserver.json_handler(url)
        def _eda_events(request):
            if expected_action is not None:
                expected_query = {
                    'external_ref': 'test_order',
                    'service': 'eats',
                    'action': expected_action,
                }
                if expected_extra_query_data is not None:
                    expected_query.update(expected_extra_query_data)
                assert request.query == expected_query
            if expected_full_sum is not _SENTINEL:
                assert expected_full_sum == request.json.get('full_sum')
            if expected_account_type:
                assert request.json['account_type'] == expected_account_type
            if expected_data is not None:
                assert request.json['data'] == expected_data
            return {}

        return _eda_events

    return _mock_eda_event_fixture


@pytest.fixture(name='mock_user_api')
def mock_user_api_fixture(mockserver):
    def _inner(user_data: typing.Optional[dict] = None):
        @mockserver.json_handler('/user_api-api/users/get')
        def _get_user(request):
            return user_data or {}

        return _get_user

    return _inner


@pytest.fixture(name='invoke_callback_task')
def invoke_callback_task_fixture(
        stq3_context: stq_context.Context, mockserver, patch,
):
    async def _invoke_callback_task_fixture(
            operation_id: str = 'change:123',
            invoice_id: str = 'test_order',
            status: str = 'done',
            task_exec_retries: int = 0,
            # TODO: make required
            notification_type: typing.Optional[str] = None,
    ):
        task_info = async_worker_ng.TaskInfo(
            id='some-task-id',
            exec_tries=task_exec_retries,
            reschedule_counter=0,
            queue='some-queue',
        )
        await callback.task(
            context=stq3_context,
            task_info=task_info,
            invoice_id=invoice_id,
            operation_id=operation_id,
            status=status,
            notification_type=notification_type,
        )

    return _invoke_callback_task_fixture

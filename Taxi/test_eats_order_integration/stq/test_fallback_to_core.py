import pytest

from eats_order_integration import stq as exceptions
from eats_order_integration.internal import entities
from eats_order_integration.stq import fallback_to_core
from test_eats_order_integration import stq as stq_test


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_fallback_to_core_send_order(
        stq_runner, mock_eats_core_order_send, pgsql,
):
    @mock_eats_core_order_send('/send-to-place')
    async def order_send_mock(request):
        return {}

    await stq_test.check_order_flow(
        pgsql, 'idempotency_key', True, entities.OrderFlowStatus.NEW.value,
    )

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'sync': False,
            'idempotency_key': 'idempotency_key',
        },
    )

    assert order_send_mock.has_calls
    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_CORE.value,
    )


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_fallback_to_core_send_order_should_not_run_twice(
        stq_runner, mock_eats_core_order_send, pgsql,
):
    @mock_eats_core_order_send('/send-to-place')
    async def order_send_mock(request):
        return {}

    async def run_stq():
        await stq_runner.eats_order_integration_fallback_to_core.call(
            args=(),
            kwargs={
                'action': entities.Action.SEND_ORDER.value,
                'order_id': 'order_id',
                'sync': False,
                'idempotency_key': 'idempotency_key',
            },
        )

    await stq_test.check_order_flow(
        pgsql, 'idempotency_key', True, entities.OrderFlowStatus.NEW.value,
    )

    await run_stq()

    assert order_send_mock.has_calls
    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_CORE.value,
    )

    await run_stq()
    assert order_send_mock.times_called == 1
    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_CORE.value,
    )


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_fallback_to_core_send_order_should_exit_if_not_new(
        stq_runner, mock_eats_core_order_send, pgsql,
):
    @mock_eats_core_order_send('/send-to-place')
    async def order_send_mock(request):
        return {}

    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key_sent_to_partner',
        True,
        entities.OrderFlowStatus.SENT_TO_PARTNER.value,
    )

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'sync': False,
            'idempotency_key': 'idempotency_key_sent_to_partner',
        },
    )

    assert not order_send_mock.has_calls
    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key_sent_to_partner',
        True,
        entities.OrderFlowStatus.SENT_TO_PARTNER.value,
    )


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_fallback_to_core_cancel_order(
        stq_runner, mock_eats_core_order_send,
):
    @mock_eats_core_order_send('/cancel')
    async def order_cancel_mock(request):
        return {}

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.CANCEL_ORDER.value,
            'order_id': 'order_id',
        },
    )

    assert order_cancel_mock.has_calls


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_call_check_order_status(  # noqa: E501
        stq_runner, mock_eats_core_order_integration,
):
    @mock_eats_core_order_integration('/v1/fallbacks/status-check')
    async def check_order_status_mock(request):
        return {}

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.CHECK_STATUS.value,
            'order_id': 'order_id',
        },
    )

    assert check_order_status_mock.has_calls


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_call_order_update(
        stq_runner, mock_eats_core_order_integration,
):
    @mock_eats_core_order_integration('/v1/fallbacks/order-update')
    async def check_order_status_mock(request):
        return {}

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.UPDATE_ORDER.value,
            'order_id': 'order_id',
        },
    )

    assert check_order_status_mock.has_calls


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_to_support(
        stq_runner, mock_eats_core_order_integration, pgsql,
):
    @mock_eats_core_order_integration('/v1/send-to-support')
    async def send_to_support_mock(request):
        return {}

    await stq_test.check_order_flow(
        pgsql, 'idempotency_key', True, entities.OrderFlowStatus.NEW.value,
    )

    await stq_runner.eats_order_integration_fallback_to_core.call(
        args=(),
        kwargs={
            'action': entities.Action.FALLBACK_TO_SUPPORT.value,
            'event': entities.OrderEvent.ORDER_SEND_SUCCESS.value,
            'order_id': 'order_id',
            'sync': False,
            'idempotency_key': 'idempotency_key',
        },
    )

    assert send_to_support_mock.has_calls
    await stq_test.check_order_flow(
        pgsql,
        'idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_SUPPORT.value,
    )


@pytest.mark.parametrize(
    'kwargs',
    [
        {
            'order_id': 'order_id',
            'sync': False,
            'idempotency_key': 'idempotency_key',
        },
        {
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'sync': False,
        },
        {
            'action': entities.Action.SEND_ORDER.value,
            'sync': False,
            'idempotency_key': 'idempotency_key',
        },
        {
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'idempotency_key': 'idempotency_key',
        },
        {
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'sync': 5,
            'idempotency_key': 'idempotency_key',
        },
        {
            'action': entities.Action.SEND_ORDER.value,
            'order_id': 'order_id',
            'sync': False,
            'idempotency_key': None,
        },
        {'action': entities.Action.CANCEL_ORDER.value},
        {'action': entities.Action.CHECK_STATUS.value},
        {
            'action': entities.Action.FALLBACK_TO_SUPPORT.value,
            'order_id': 'order_id',
        },
        {
            'action': entities.Action.FALLBACK_TO_SUPPORT.value,
            'idempotency_key': 'idempotency_key',
        },
        {'action': entities.Action.SEND_TO_SUPPORT.value},
        {'action': entities.Action.UPDATE_ORDER.value},
    ],
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_raises_on_wrong_kwargs(stq3_context, kwargs):
    with pytest.raises(exceptions.ArgumentsException):
        await fallback_to_core.task(stq3_context, **kwargs)

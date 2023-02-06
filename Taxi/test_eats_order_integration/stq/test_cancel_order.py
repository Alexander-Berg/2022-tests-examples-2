import pytest

from eats_order_integration.generated.service.swagger.models import (
    api as models,
)
from eats_order_integration.internal import entities
from test_eats_order_integration import stq as stq_test

CANCELLATION_REASON = 'some_cancel_reason'
CANCELLED_BY = 'someone'
PLACE_ID = '1'


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.fixture(name='order_meta_info_mock')
def _order_meta_info_mock(mock_eats_core_orders, mockserver, load_json):
    @mock_eats_core_orders(
        r'/internal-api/v1/order/(?P<order_nr>\w+)/metainfo$', regex=True,
    )
    async def _order_get(request, order_nr='order_id'):
        responses = load_json('order_meta_info.json')

        return responses


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_default_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_order(
        stq_runner,
        mock_eats_core_order_integration,
        order_meta_info_mock,
        partner_mocks,
        stq,
        pgsql,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):
        return {
            'order_nr': 'order_id',
            'external_id': 'some_external_id',
            'place_group_id': 'place_group_id_1',
        }

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute(
        'SELECT is_cancelling from order_flow WHERE order_nr=\'order_id\'',
    )
    assert all([not row[0] for row in cursor])

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=1,
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_CANCEL_SEND_SUCCESS.value,
    )

    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_CANCEL_SEND_DUPLICATE_TO_VENDOR.value,  # noqa: E501
        order_id='order_id',
        success=True,
    )

    assert get_order_mock.has_calls
    assert partner_mocks['order_status'].times_called == 1

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute(
        'SELECT is_cancelling from order_flow WHERE order_nr=\'order_id\'',
    )
    assert all(row[0] for row in cursor)


@pytest.mark.client_experiments3(
    file_with_default_response='send_cancel_to_partner_disabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_order_send_to_partner_disabled(
        stq_runner,
        mock_eats_core_order_integration,
        order_meta_info_mock,
        partner_mocks,
        stq,
        pgsql,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):  # pylint: disable=unused-variable
        return {
            'order_nr': 'order_id',
            'external_id': 'some_external_id',
            'place_group_id': 'place_group_id_1',
        }

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute(
        'SELECT is_cancelling from order_flow WHERE order_nr=\'order_id\'',
    )
    assert all([not row[0] for row in cursor])

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=1,
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    assert get_order_mock.has_calls
    assert not partner_mocks['order_status'].has_calls

    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_CANCEL_SEND_FILTERED.value,
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_default_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_not_existing_order(
        mockserver,
        stq_runner,
        mock_eats_core_order_integration,
        order_meta_info_mock,
        partner_mocks,
        stq,
        pgsql,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=404, json={'message': '', 'code': '', 'details': {}},
        )

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute(
        'SELECT is_cancelling from order_flow WHERE order_nr=\'order_id3\'',
    )
    assert not [row for row in cursor]

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=1,
            order_id='order_id3',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute(
        'SELECT is_cancelling from order_flow WHERE order_nr=\'order_id3\'',
    )
    result = [row[0] for row in cursor]
    assert result
    assert all(row for row in result)

    assert get_order_mock.has_calls
    assert not partner_mocks['order_status'].has_calls

    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id3',
        action=entities.Action.CANCEL_ORDER.value,
    )


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_not_affect_other_orders_if_cancelled(
        stq_runner,
        mock_eats_core_order_integration,
        partner_mocks,
        stq,
        pgsql,
):
    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute('SELECT order_nr, is_cancelling from order_flow')
    result = [row for row in cursor]
    assert all(
        (row[1] if row[0] == 'order_id_cancelled' else not row[1])
        for row in result
    )

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=1,
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    cursor = pgsql['eats_order_integration'].cursor()
    cursor.execute('SELECT order_nr, is_cancelling from order_flow')
    result = [row for row in cursor]
    assert all(
        (
            row[1]
            if row[0] in ['order_id_cancelled', 'order_id']
            else not row[1]
        )
        for row in result
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_default_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_order_should_run_without_engine_id_provided(
        stq_runner,
        mock_eats_core_order_integration,
        order_meta_info_mock,
        partner_mocks,
        stq,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):
        return {
            'order_nr': 'order_id',
            'external_id': 'some_external_id',
            'place_group_id': 'place_group_id_1',
        }

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    assert stq.eats_order_integration_fallback_to_core.has_calls
    assert get_order_mock.has_calls
    assert partner_mocks['order_status'].has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_CANCEL_SEND_SUCCESS.value,
    )

    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_CANCEL_SEND_DUPLICATE_TO_VENDOR.value,  # noqa: E501
        order_id='order_id',
        success=True,
    )


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_order_not_supported_engine(stq_runner, stq):
    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=2,
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    assert stq.eats_order_integration_fallback_to_core.has_calls

    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.CANCEL_ORDER.value,
        order_id='order_id',
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_default_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_cancel_order_fallback_to_core_if_core_return_error(
        stq_runner,
        mock_eats_core_order_integration,
        order_meta_info_mock,
        partner_mocks,
        stq,
        mockserver,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):
        return mockserver.make_response(status=500)

    await stq_runner.eats_order_integration_cancel_order.call(
        task_id='task_id',
        args=(),
        kwargs=models.StqCancelOrderKwargs(
            integration_engine_id=1,
            order_id='order_id',
            place_id=PLACE_ID,
            cancellation_reason=CANCELLATION_REASON,
            cancelled_by=CANCELLED_BY,
        ).serialize(),
    )

    assert stq.eats_order_integration_fallback_to_core.has_calls
    assert get_order_mock.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.CANCEL_ORDER.value,
        order_id='order_id',
    )

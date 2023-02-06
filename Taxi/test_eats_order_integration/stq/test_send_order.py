import asyncpg
import pytest

from taxi.pg import exceptions as taxi_pg_exceptions
from taxi.stq import async_worker_ng


from eats_order_integration.generated.service.swagger.models import (
    api as models,
)
from eats_order_integration.internal import entities
from eats_order_integration.stq import send_order
from test_eats_order_integration import stq as stq_test


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.fixture(name='order_send_stq_runner')
def _order_send_stq_runner(stq_runner, load_json):
    async def call_stq(kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'

        await stq_runner.eats_order_integration_send_order.call(
            task_id='task_id',
            args=(),
            kwargs=models.StqSendOrderKwargs(
                **load_json('send_order_kwargs.json')[kwargs_name],
            ).serialize(),
        )

    return call_stq


@pytest.mark.client_experiments3(file_with_default_response='exp3_empty.json')
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_send_order_if_cannot_find_experiment(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        load_json,
        client_experiments3,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_send_stq_runner()
    assert not stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_disabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_send_order_if_disabled_in_experiments(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        partner_mocks,
        processing_mocks,
        order_tech_info_mock,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_send_stq_runner()
    assert not stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_check_status.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_order_should_call_check_status(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        processing_mocks,
        pgsql,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    await stq_test.check_order_flow(pgsql, 'new_idempotency_key', False)
    processing_mocks()
    await order_send_stq_runner()
    assert stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_update_order.has_calls
    await stq_test.check_order_flow(
        pgsql,
        'new_idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_PARTNER.value,
    )
    assert order_integration_context.order_get_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_order_should_run_without_engine_id_provided(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        processing_mocks,
        mockserver,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_send_stq_runner('without_engine_id')
    assert stq.eats_order_integration_check_status.has_calls
    assert order_integration_context.order_get_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_order_not_supported_engine(
        order_send_stq_runner,
        stq,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    await order_send_stq_runner('not_existing_integration_engine')
    assert not order_integration_context.order_get_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_order_fallback_to_core_if_core_return_error(
        stq,
        order_send_stq_runner,
        mock_eats_core_order_integration,
        order_tech_info_mock,
        partner_mocks,
        mockserver,
        stq3_client,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order_mock(request):
        return mockserver.make_response(status=500)

    @mock_eats_core_order_integration('/v1/order/add-send-mark')
    async def add_send_mark(request):  # pylint:disable=W0612
        return mockserver.make_response(status=200)

    await stq3_client.invalidate_caches()
    await order_send_stq_runner()
    assert stq.eats_order_integration_fallback_to_core.has_calls

    assert not stq.eats_order_integration_check_status.has_calls
    assert get_order_mock.has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_send_order_should_not_run_twice(
        order_send_stq_runner,
        stq,
        pgsql,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        processing_mocks,
        mockserver,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await stq_test.check_order_flow(pgsql, 'new_idempotency_key', False)
    await order_send_stq_runner()
    assert stq.eats_order_integration_check_status.times_called == 1
    assert order_integration_context.order_get_calls == 1
    assert order_integration_context.order_post_calls == 1
    await stq_test.check_order_flow(
        pgsql,
        'new_idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_PARTNER.value,
    )

    await order_send_stq_runner()
    assert stq.eats_order_integration_check_status.times_called == 1
    assert order_integration_context.order_get_calls == 1
    assert order_integration_context.order_post_calls == 1
    await stq_test.check_order_flow(
        pgsql,
        'new_idempotency_key',
        True,
        entities.OrderFlowStatus.SENT_TO_PARTNER.value,
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_send_order_if_in_cancelled_status(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        mockserver,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    order_integration_context.order_json_name = 'cancelled'
    await order_send_stq_runner()
    assert not partner_mocks['fetch_token'].has_calls
    assert stq.eats_order_integration_fallback_to_core.times_called == 0


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_send_order_if_have_external_id_and_not_sync(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    order_integration_context.order_json_name = 'external_id'
    await order_send_stq_runner()
    assert not partner_mocks['update_order'].has_calls
    assert not partner_mocks['create_order'].has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_send_order_if_have_external_id_and_sync(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        order_integration_context,
        partner_mocks,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        processing_mocks,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    order_integration_context.order_json_name = 'external_id'
    await order_send_stq_runner('with_sync')
    assert partner_mocks['update_order'].has_calls
    assert not partner_mocks['create_order'].has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_send_to_support_data_when_order_send_fail(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        processing_mocks,
        stq3_context,
        stq3_client,
):
    @mock_eats_partner_engine_yandex_eda('/security/oauth/token')
    def fetch_token(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=400, json=[{'code': 111, 'description': '1222'}],
        )

    @mock_eats_partner_engine_yandex_eda('/order')
    def _order(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=400, json=[{'code': 111, 'description': '1222'}],
        )

    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_send_stq_runner()
    assert stq.eats_order_integration_fallback_to_core.times_called == 2
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        idempotency_key='new_idempotency_key',
        action=entities.Action.FALLBACK_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_FAIL.value,
        human_readable_error='Необходимо передать событие в поддержку: '
        'Ошибка на стороне партнера при отправке заказа через движок '
        'YandexEdaEngine',
        exception_message='eats-partner-engine-yandex-eda response, '
        'status: 400, body: [ErrorListItem(code=111, description=\'1222\', '
        'extra={})], headers: {\'cache_control\': None, \'expires\': None, '
        '\'etag\': None, \'vary\': None, \'pragma\': None}',
    )
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        idempotency_key='new_idempotency_key',
        action=entities.Action.FALLBACK_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_DUPLICATE_TO_VENDOR.value,
        human_readable_error='Необходимо передать событие в поддержку: '
        'Ошибка на стороне партнера при отправке заказа через движок '
        'YandexEdaEngine',
        exception_message='eats-partner-engine-yandex-eda response, '
        'status: 400, body: [ErrorListItem(code=111, description=\'1222\', '
        'extra={})], headers: {\'cache_control\': None, \'expires\': None, '
        '\'etag\': None, \'vary\': None, \'pragma\': None}',
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_send_to_support_data_when_procaas_not_available(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        stq3_client,
):
    @mock_eats_partner_engine_yandex_eda('/security/oauth/token')
    def fetch_token(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=500, json=[{'code': 111, 'description': '1222'}],
        )

    await stq3_client.invalidate_caches()
    await order_send_stq_runner()
    assert stq.eats_order_integration_fallback_to_core.times_called == 2
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.FALLBACK_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_FAIL.value,
        order_id='order_id',
        idempotency_key='new_idempotency_key',
        human_readable_error='Необходимо передать событие в поддержку: '
        'Ошибка procaas',
        exception_message='Not defined in schema processing response, '
        'status: 500, body: b\'Internal error: '
        'mockserver handler not found\'',
    )
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.FALLBACK_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_DUPLICATE_TO_VENDOR.value,
        order_id='order_id',
        idempotency_key='new_idempotency_key',
        human_readable_error='Необходимо передать событие в поддержку: '
        'Ошибка procaas',
        exception_message='Not defined in schema processing response, '
        'status: 500, body: b\'Internal error: '
        'mockserver handler not found\'',
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_send_to_support_if_order_send_success(
        stq,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_send_stq_runner()
    assert stq.eats_order_integration_fallback_to_core.times_called == 2
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_SUCCESS.value,
        order_id='order_id',
    )
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_SEND_DUPLICATE_TO_VENDOR.value,
        order_id='order_id',
        success=True,
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_STQ_TASKS_RETRY_SETTINGS={
        'eats_order_integration_send_order_database_error': {
            'max_reschedules': 1,
        },
    },
)
@pytest.mark.parametrize(
    'database_exception',
    [asyncpg.PostgresError, taxi_pg_exceptions.BaseError],
)
async def test_should_fallback_to_core_if_have_error_in_database_when_try_to_lock(  # noqa:E501
        stq,
        stq3_context,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        patch,
        database_exception,
        stq3_client,
):
    @patch('taxi.pg.pool.Pool.fetchrow')
    async def fetchrow(*args, **kwargs):  # pylint: disable=unused-variable
        raise database_exception()

    await stq3_client.invalidate_caches()
    processing_mocks()

    await send_order.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id='1', exec_tries=0, reschedule_counter=2, queue='',
        ),
        idempotency_key='new_idempotency_key',
        sync=True,
        order_id='new_idempotency_key',
    )

    assert (
        stq.eats_order_integration_send_order.times_called == 0
    )  # не перезапускаем
    assert stq.eats_order_integration_fallback_to_core.times_called == 1


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.config(
    EATS_ORDER_INTEGRATION_STQ_TASKS_RETRY_SETTINGS={
        'eats_order_integration_send_order_database_error': {
            'max_reschedules': 2,
        },
    },
)
@pytest.mark.parametrize(
    'database_exception',
    [asyncpg.PostgresError, taxi_pg_exceptions.BaseError],
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_restart_task_if_have_error_in_database_when_try_to_lock(
        stq,
        stq3_context,
        order_send_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        patch,
        database_exception,
        stq3_client,
):
    @patch('taxi.pg.pool.Pool.fetchrow')
    async def fetchrow(*args, **kwargs):  # pylint: disable=unused-variable
        raise database_exception('some error')

    # await stq3_client.invalidate_caches()
    processing_mocks()

    await send_order.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id='1', exec_tries=0, reschedule_counter=1, queue='',
        ),
        idempotency_key='new_idempotency_key',
        sync=True,
        order_id='new_idempotency_key',
    )

    assert (
        stq.eats_order_integration_send_order.times_called == 1
    )  # перезапустили один раз


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_enabled.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
@pytest.mark.parametrize('at_start', [True, False])
@pytest.mark.parametrize('before_perform', [True, False])
async def test_should_not_send_order_if_cancelled(
        order_send_stq_runner,
        stq,
        pgsql,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        stq3_client,
        at_start,
        before_perform,
        taxi_config,
):
    taxi_config.set(
        EATS_ORDER_INTEGRATION_CANCEL_CHECK_SETTINGS={
            'send_order_start': at_start,
            'send_order_before_perform': before_perform,
        },
    )
    await stq3_client.invalidate_caches()
    processing_mocks()
    await stq_test.check_order_flow(pgsql, 'new_idempotency_key', False)
    await order_send_stq_runner('cancelled')
    assert stq.eats_order_integration_check_status.times_called == (
        0 if at_start or before_perform else 1
    )

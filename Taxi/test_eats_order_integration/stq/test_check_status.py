import pytest

from eats_order_integration.generated.service.swagger.models import (
    api as models,
)
from eats_order_integration.internal import entities
from test_eats_order_integration import stq as stq_test


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.fixture(name='order_status_check_stq_runner')
def _order_status_check_stq_runner(stq_runner, load_json):
    async def call_stq(kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'

        await stq_runner.eats_order_integration_check_status.call(
            task_id='task_id',
            args=(),
            kwargs=models.StqCheckOrderStatusKwargs(
                **load_json('check_status_kwargs.json')[kwargs_name],
            ).serialize(),
        )

    return call_stq


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_check_status_if_disabled_in_experiment(
        stq,
        order_status_check_stq_runner,
        order_integration_mock,
        partner_mocks,
        processing_mocks,
        order_tech_info_mock,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_status_check_stq_runner()
    assert not stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_check_status.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
@pytest.mark.parametrize(
    'testcase',
    ['pickup_finished_at', 'marketplace_finished_at', 'native_finished_at'],
)
async def test_should_not_requeue_if_pickup_order_is_finished(
        stq,
        order_status_check_stq_runner,
        order_integration_mock,
        order_integration_context,
        order_tech_info_mock,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        processing_mocks,
        stq3_context,
        stq3_client,
        testcase,
):
    order_integration_context.order_json_name = testcase
    await order_status_check_stq_runner()

    assert not stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.SEND_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_STATUS_CHECK_SUCCESS.value,
    )


@pytest.mark.client_experiments3(file_with_default_response='exp3_empty.json')
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_fallback_to_core_if_cannot_find_engine(
        stq,
        order_status_check_stq_runner,
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
    await order_status_check_stq_runner()
    assert not stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.CHECK_STATUS.value,
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_check_status.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_send_to_support_fail_if_have_error(
        stq,
        order_status_check_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        mock_eats_partner_engine_yandex_eda,
        processing_mocks,
        load_json,
        client_experiments3,
        stq3_client,
        mockserver,
):
    @mock_eats_partner_engine_yandex_eda('/security/oauth/token')
    def fetch_token(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=400, json=[{'code': 111, 'description': '1222'}],
        )

    @mock_eats_partner_engine_yandex_eda('/order/1111/status')
    def _order(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=400, json=[{'code': 111, 'description': '1222'}],
        )

    await stq3_client.invalidate_caches()
    await order_status_check_stq_runner()
    assert stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        idempotency_key='',
        action=entities.Action.FALLBACK_TO_SUPPORT.value,
        event=entities.OrderEvent.ORDER_STATUS_CHECK_FAIL.value,
        human_readable_error='Необходимо передать событие в поддержку: '
        'Ошибка на стороне партнера при отправке заказа через движок '
        'YandexEdaEngine',
        exception_message='eats-partner-engine-yandex-eda response, '
        'status: 400, body: [ErrorListItem(code=111, description=\'1222\', '
        'extra={})], headers: {\'cache_control\': None, \'expires\': None, '
        '\'etag\': None, \'vary\': None, \'pragma\': None}',
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_check_status.json',
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_requeue_after_success_checks(
        stq,
        order_status_check_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        mock_eats_partner_engine_yandex_eda,
        processing_mocks,
        load_json,
        client_experiments3,
        stq3_client,
        mockserver,
):
    await stq3_client.invalidate_caches()
    await order_status_check_stq_runner()
    processing_mocks()
    assert stq.eats_order_integration_check_status.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls

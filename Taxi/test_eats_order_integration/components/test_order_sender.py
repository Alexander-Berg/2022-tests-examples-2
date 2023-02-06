import pytest

from order_send_procaas import internal as procaas_internal

from eats_order_integration.generated.service.swagger.models import (
    api as models,
)
from eats_order_integration.internal import exceptions


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.fixture(name='send_order_data')
def _send_order_data(load_json):
    return models.StqSendOrderKwargs(**load_json('send_order_kwargs.json'))


async def test_should_raise_fallback_to_core_if_cannot_find_integration_engine(
        stq3_context, send_order_data,
):
    with pytest.raises(exceptions.NeedFallbackToCore):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_fallback_to_core_if_cannot_get_info_about_order(
        stq3_context,
        send_order_data,
        mock_eats_core_order_integration,
        mockserver,
):
    @mock_eats_core_order_integration('/v1/order')
    async def get_order(request):  # pylint: disable=unused-variable
        return mockserver.make_response(status=500, json='{}')

    with pytest.raises(exceptions.NeedFallbackToCore):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_fallback_to_core_if_cannot_add_order_sent_mark(
        stq3_context,
        send_order_data,
        order_integration_mock,
        mock_eats_core_order_integration,
        mockserver,
):
    @mock_eats_core_order_integration('/v1/order/add-send-mark')
    async def get_order(request):  # pylint: disable=unused-variable
        return mockserver.make_response(status=500, json='{}')

    with pytest.raises(exceptions.NeedFallbackToCore):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_raise_order_already_cancelled(
        stq3_context,
        send_order_data,
        order_integration_mock,
        order_integration_context,
):
    order_integration_context.order_json_name = 'cancelled'
    with pytest.raises(exceptions.OrderAlreadyCancelled):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_raise_order_already_sent(
        stq3_context,
        send_order_data,
        order_integration_mock,
        order_integration_context,
):
    order_integration_context.order_json_name = 'external_id'
    with pytest.raises(exceptions.OrderAlreadySended):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_raise_fail_to_support_when_error_in_procaas(
        stq3_context,
        send_order_data,
        order_integration_mock,
        processing_mocks,
):
    processing_mocks(True)
    with pytest.raises(exceptions.NeedSendFailToSupport):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_raise_fail_to_support_when_error_in_partner(
        stq3_context,
        send_order_data,
        order_integration_mock,
        processing_mocks,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
):
    @mock_eats_partner_engine_yandex_eda('/security/oauth/token')
    async def _request(request):
        return mockserver.make_response(500, json={})

    processing_mocks()
    with pytest.raises(exceptions.NeedSendFailToSupport):
        await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_raise_exception_if_error_in_procaas_after_sending_order(  # noqa: E501
        stq3_context,
        send_order_data,
        order_integration_mock,
        mock_processing,
        partner_mocks,
        mockserver,
        load_json,
):
    @mock_processing('/v1/eda/orders_client/create-event')
    def create_event(request):  # pylint: disable=unused-variable
        if (
                request.json['order_event']
                == procaas_internal.ProcaasOrderEventType.SENT.value
        ):
            return mockserver.make_response(
                400, json={'code': 400, 'message': ''},
            )

        return load_json('processing.json')[request.json['order_event']]

    await stq3_context.order_sender.perform(send_order_data)


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_raise_exception_if_cannot_set_status(
        stq3_context,
        send_order_data,
        order_integration_mock,
        processing_mocks,
        partner_mocks,
        patch,
):
    processing_mocks()

    @patch('eats_order_integration.components.order_flow.OrderFlow.set_status')
    async def _set_status_mock(
            *args, **kwargs,
    ):  # pylint: disable=unused-variable
        raise exceptions.CannotSetStatus()

    await stq3_context.order_sender.perform(send_order_data)
    assert len(_set_status_mock.calls) == 1

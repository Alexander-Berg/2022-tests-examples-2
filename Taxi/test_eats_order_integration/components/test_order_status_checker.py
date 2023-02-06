import pytest


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


@pytest.fixture(name='order_event_mock')
def _order_event_mock(mock_eats_core_orders, mockserver, load_json):
    @mock_eats_core_orders('/internal-api/v1/order/event')
    async def _event(request):
        event = request.json['event']
        request_body = load_json('order_event.json')['request'][event]
        assert request.json == request_body

        return mockserver.make_response(status=204)

    return _event


@pytest.fixture(name='check_status_order_data')
def _check_status_order_data(load_json):
    return models.StqCheckOrderStatusKwargs(
        **load_json('check_status_kwargs.json'),
    )


@pytest.fixture(name='partner_get_status')
def _partner_get_status_mock(
        load_json, mock_eats_partner_engine_yandex_eda, mockserver,
):
    def _mock(status):
        @mock_eats_partner_engine_yandex_eda(
            r'/order/(?P<order_id>\w+)/status', regex=True,
        )
        def check_order_status(request, order_id):
            token = load_json('partner_mocks_data.json')['access_token']

            assert request.method == 'GET'
            assert request.headers['Authorization'] == f'Bearer {token}'

            return load_json('partner_mocks_data.json')[
                'check_order_status_response'
            ][status]

        return check_order_status

    return _mock


@pytest.mark.parametrize(
    'order_status, transition, expected_event',
    [
        # transition move_to_delivery
        ['ACCEPTED_BY_RESTAURANT', 'place_confirm', 'confirm_by_place'],
        ['COOKING', 'place_confirm', 'confirm_by_place'],
        ['READY', 'place_confirm', 'confirm_by_place'],
        ['TAKEN_BY_COURIER', 'place_confirm', 'confirm_by_place'],
        ['DELIVERED', 'place_confirm', 'confirm_by_place'],
        # transition deliver
        ['TAKEN_BY_COURIER', 'deliver', 'taken_by_courier'],
        # transition deliver
        ['DELIVERED', 'deliver', 'delivered'],
    ],
)
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_call_correct_event(
        partner_mocks,
        partner_get_status,
        stq3_context,
        order_integration_mock,
        order_event_mock,
        check_status_order_data,
        order_status,
        transition,
        expected_event,
):
    partner_get_status(order_status)

    with pytest.raises(exceptions.ShouldRescheduleCheckStatus):
        await stq3_context.order_status_checker.perform(
            check_status_order_data,
        )
    assert order_event_mock.has_calls


@pytest.mark.parametrize(
    'transition, expected_event',
    [
        # transition move_to_delivery
        # cooked statuses for native order and from place_group
        ['move_to_delivery', 'cooked'],
    ],
)
@pytest.mark.pgsql(
    'eats_order_integration', files=['engines.sql', 'cooked_statuses.sql'],
)
async def test_should_call_correct_event_for_cooked(
        partner_mocks,
        partner_get_status,
        stq3_context,
        order_integration_mock,
        order_event_mock,
        check_status_order_data,
        transition,
        expected_event,
):
    partner_get_status('COOKING')

    with pytest.raises(exceptions.ShouldRescheduleCheckStatus):
        await stq3_context.order_status_checker.perform(
            check_status_order_data,
        )
    assert order_event_mock.has_calls


@pytest.mark.parametrize(
    'transition, expected_event',
    [
        # transition cancel
        # cancelled statuses from place group
        ['cancel', 'cancel'],
    ],
)
@pytest.mark.pgsql(
    'eats_order_integration', files=['engines.sql', 'cancelled_statuses.sql'],
)
async def test_should_call_correct_event_for_cancelled(
        partner_mocks,
        partner_get_status,
        stq3_context,
        order_integration_mock,
        order_event_mock,
        check_status_order_data,
        transition,
        expected_event,
):
    partner_get_status('CANCELLED')

    with pytest.raises(exceptions.ShouldRescheduleCheckStatus):
        await stq3_context.order_status_checker.perform(
            check_status_order_data,
        )
    assert order_event_mock


# @pytest.mark.client_experiments3(
#     file_with_default_response='exp3_check_status.json',
# )
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
@pytest.mark.parametrize(
    'testcase',
    ['pickup_finished_at', 'marketplace_finished_at', 'native_finished_at'],
)
async def test_raise_if_pickup_order_is_finished(
        partner_mocks,
        partner_get_status,
        stq3_context,
        order_integration_mock,
        order_event_mock,
        check_status_order_data,
        order_integration_context,
        order_tech_info_mock,
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        processing_mocks,
        stq3_client,
        testcase,
):
    order_integration_context.order_json_name = testcase

    if testcase == 'pickup_finished_at':
        template = 'Pickup order has final status. No status checks needed.'
    else:
        template = 'Order has final status. No status checks needed. '

    with pytest.raises(exceptions.OrderAlreadyInFinalStatus, match=template):
        await stq3_context.order_status_checker.perform(
            check_status_order_data,
        )
        assert order_event_mock

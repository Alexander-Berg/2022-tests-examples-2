# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_order_revision_plugins import *  # noqa: F403 F401


@pytest.fixture(name='check_create_raw_revision')
def check_create_raw_fixture(taxi_eats_order_revision):
    async def _inner(
            order_id: str,
            origin_revision_id: str,
            cost_for_customer: str,
            document,
            tags: list,
            initiator: str = 'system',
            is_applied: bool = True,
            response_status: int = 200,
    ):
        payload = {
            'order_id': order_id,
            'origin_revision_id': origin_revision_id,
            'cost_for_customer': cost_for_customer,
            'document': document,
            'initiator': initiator,
            'tags': tags,
            'is_applied': is_applied,
        }

        response = await taxi_eats_order_revision.post(
            'v1/revision/raw/create', json=payload,
        )
        assert response.status == response_status
        return response

    return _inner


@pytest.fixture(name='mock_core_customer_services')
def _mock_core_customer_services(mockserver):
    def _inner(order_id, revision_id, response, status=200):
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/v1/order-revision/'
            'customer-services',
        )
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/v1/order-revision/'
            'customer-services/details',
        )
        def core_customer_services_handler(request):
            assert request.json == {
                'order_id': order_id,
                'revision_id': revision_id,
            }
            if status == 200:
                response['order_id'] = order_id
                response['revision_id'] = revision_id
                response['created_at'] = '2022-01-01T15:15:15.01+00:00'
            return mockserver.make_response(status=status, json=response)

        return core_customer_services_handler

    return _inner


@pytest.fixture(name='mock_core_revision_list')
def _mock_core_revision_list(mockserver):
    def _inner(order_id, response, status=200):
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/v1/order-revision/list',
        )
        def core_revision_list_handler(request):
            if status == 200:
                response['order_id'] = order_id
            return mockserver.make_response(status=status, json=response)

        return core_revision_list_handler

    return _inner


@pytest.fixture(name='mock_order_billing_data')
def _mock_order_billing_data(mockserver):
    def _inner(order_id, response, status=200):
        @mockserver.json_handler(
            '/order-billing-data/order/billing-data/' + order_id,
        )
        def order_billing_data_handler(request):
            return mockserver.make_response(status=status, json=response)

        return order_billing_data_handler

    return _inner


@pytest.fixture(name='mock_eats_billing_processor')
def _mock_eats_billing_processor(mockserver):
    def _inner(response, status=200):
        @mockserver.json_handler('/eats-billing-processor/v1/deal_id')
        def eats_billing_processor_handler(request):
            return mockserver.make_response(status=status, json=response)

        return eats_billing_processor_handler

    return _inner


@pytest.fixture(name='mock_eats_core_cancel_order')
def _mock_eats_core_cancel_order(mockserver):
    def _inner(response, status=200):
        @mockserver.json_handler(
            '/eats-core-cancel-order/internal-api/v1/cancel-order',
        )
        def eats_core_cancel_order_handler(request):
            return mockserver.make_response(status=status, json=response)

        return eats_core_cancel_order_handler

    return _inner


@pytest.fixture(name='mock_billing_limits_deposit')
def _mock_billing_limits_deposit(mockserver):
    def _inner(expected_request, response=None, status=200):
        @mockserver.json_handler('/billing-limits/v1/deposit')
        def billing_limits_deposit_handler(request):
            assert request.json['amount'] == expected_request['amount']
            assert request.json['limit_ref'] == expected_request['limit_ref']
            assert request.json['currency'] == expected_request['currency']

            handler_response = response if response else {}

            return mockserver.make_response(
                status=status, json=handler_response,
            )

        return billing_limits_deposit_handler

    return _inner


@pytest.fixture(name='mock_eats_ordershistory_get_eater')
def _mock_eats_ordershistory_get_eater(mockserver):
    def _inner(order_id, response, status=200):
        @mockserver.json_handler('/eats-ordershistory/internal/v1/get-eater')
        def get_eater_handler(request):
            assert request.json['order_nr'] == order_id
            return mockserver.make_response(status=status, json=response)

        return get_eater_handler

    return _inner

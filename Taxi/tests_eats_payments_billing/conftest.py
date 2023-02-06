import logging

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_payments_billing_plugins import *  # noqa: F403 F401

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.fixture(name='mock_order_billing_data')
def _mock_order_billing_data(mockserver):
    def _inner(
            order_id=consts.ORDER_ID,
            response_code=200,
            transaction_date=consts.TRANSACTION_DATE,
            courier_id=consts.COURIER_ID,
            picker_id=consts.PICKER_ID,
            order_type=consts.ORDER_TYPE,
            flow_type=consts.FLOW_TYPE,
            processing_type=None,
            error=None,
    ):
        @mockserver.json_handler(
            f'/order-billing-data/order/billing-data/{order_id}',
        )
        def order_billing_data_order_id_get(request):
            if error:
                raise error

            if response_code == 200:
                return mockserver.make_response(
                    json={
                        'transactionDate': transaction_date,
                        'courierId': courier_id,
                        'pickerId': picker_id,
                        'orderType': order_type,
                        'flowType': flow_type,
                        'processingType': processing_type,
                    },
                    status=response_code,
                )
            return mockserver.make_response(
                status=response_code,
                json={'message': 'error', 'status': 'error'},
            )

        return order_billing_data_order_id_get

    return _inner


@pytest.fixture(name='mock_eats_billing_storage')
def _mock_eats_billing_storage(mockserver):
    def _inner(expected_data=None, response_code=200, error=None):
        @mockserver.json_handler(
            '/eats-billing-storage/billing-storage/create/bulk',
        )
        def billing_storage_create(request):
            if error:
                raise error

            if expected_data:
                result = helpers.billing_doc_lists_are_equal(
                    request.json, expected_data,
                )
                if not result:
                    logging.getLogger(__name__).log(
                        logging.ERROR,
                        '-----> Request json is %s',
                        request.json,
                    )
                    logging.getLogger(__name__).log(
                        logging.ERROR,
                        '-----> Expected data is %s',
                        expected_data,
                    )

                assert result, 'see error logs'

            return mockserver.make_response(
                json={'message': 'OK', 'status': 'success'},
                status=response_code,
            )

        return billing_storage_create

    return _inner


@pytest.fixture(name='mock_eats_billing_processor')
def _mock_eats_billing_processor(mockserver):
    def _inner(
            expected_requests=None,
            responses=None,
            response_code=200,
            error=None,
    ):
        expected_requests_copy = None
        if expected_requests:
            expected_requests_copy = expected_requests.copy()

        responses_copy = None
        if responses:
            responses_copy = responses.copy()

        @mockserver.json_handler('/eats-billing-processor/v1/create')
        def eats_billing_processor_create(request):
            if error:
                raise error

            nonlocal expected_requests_copy
            if expected_requests_copy:
                expected_requests_copy[0].pop('event_at')
                request.json.pop('event_at')

                if 'event_at' in expected_requests_copy[0]['data']:
                    expected_requests_copy[0]['data'].pop('event_at')
                    request.json['data'].pop('event_at')

                if 'transaction_date' in expected_requests_copy[0]['data']:
                    expected_requests_copy[0]['data'].pop('transaction_date')
                    request.json['data'].pop('transaction_date')

                assert expected_requests_copy[0] == request.json
                expected_requests_copy.pop(0)

            # ответы выдаем по назначенному порядку
            response = None
            if responses_copy:
                response = responses_copy[0]
                responses_copy.pop(0)
            else:
                response = {'event_id': 'test'}

            return mockserver.make_response(
                json=response, status=response_code,
            )

        return eats_billing_processor_create

    return _inner


@pytest.fixture(name='mock_stq_reschedule')
def _mock_stq_reschedule(mockserver):
    def _inner(response_code=200):
        @mockserver.json_handler(f'/stq-agent/queues/api/reschedule')
        def stq_reschedule(request):
            return mockserver.make_response(status=response_code, json={})

        return stq_reschedule

    return _inner

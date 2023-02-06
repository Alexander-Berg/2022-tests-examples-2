import asyncio
import logging

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_billing_processor_plugins import *  # noqa: F403 F401

from tests_eats_billing_processor import helpers


@pytest.fixture(name='client_info_mock')
def _core_client_mock(mockserver):
    def _inner(client_info):
        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/info',
        )
        def _info(request):
            client_dict = {}
            key = ''
            if 'place_id' in request.json.keys():
                client_dict = client_info['places']
                key = request.json['place_id']
            elif 'courier_id' in request.json.keys():
                client_dict = client_info['couriers']
                key = request.json['courier_id']
            elif 'picker_id' in request.json.keys():
                client_dict = client_info['pickers']
                key = request.json['picker_id']
            else:
                return mockserver.make_response(
                    status=400,
                    json={'status': 'error', 'message': 'Bad request'},
                )

            if key not in client_dict.keys():
                return mockserver.make_response(
                    status=400,
                    json={'status': 'error', 'message': 'Not found'},
                )

            return mockserver.make_response(status=200, json=client_dict[key])

        return _info

    return _inner


@pytest.fixture(name='business_rules_mock')
def _business_rules_mock(taxi_config, mockserver):
    def _inner(commissions, fines):
        @mockserver.json_handler('/eats-business-rules/v1/', prefix=True)
        def _service_handler(request):

            if request.path == '/eats-business-rules/v1/commission':
                counterparty_id = request.json['counterparty_id']
                if counterparty_id not in commissions.keys():
                    return mockserver.make_response(
                        status=400,
                        json={
                            'code': 'NOT_FOUND',
                            'message': 'Cannot find counterparty',
                        },
                    )
                rule = commissions[counterparty_id]
                com_type = request.json['commission_type']
                if com_type not in rule.keys():
                    return mockserver.make_response(
                        status=400,
                        json={
                            'code': 'NOT_FOUND',
                            'message': 'Cannot find commission',
                        },
                    )
                result = {
                    'rule_id': rule[com_type]['rule_id'],
                    'client_id': rule['client_id'],
                    'commission_params': rule[com_type]['params'],
                }

                if 'billing_frequency' in rule[com_type]:
                    result['billing_frequency'] = rule[com_type][
                        'billing_frequency'
                    ]

                return mockserver.make_response(status=200, json=result)

            if request.path == '/eats-business-rules/v1/fine':
                client_id = request.json['client_id']
                if client_id not in fines.keys():
                    return mockserver.make_response(
                        status=400,
                        json={
                            'code': 'NOT_FOUND',
                            'message': 'Cannot find client',
                        },
                    )
                rule = fines[client_id]
                business_type = request.json['business_type']
                delivery_type = request.json['delivery_type']
                fine_reason = request.json['reason']
                fine_key = f'{business_type}_{delivery_type}_{fine_reason}'
                if fine_key not in rule.keys():
                    return mockserver.make_response(
                        status=400,
                        json={
                            'code': 'NOT_FOUND',
                            'message': 'Cannot find fine',
                        },
                    )
                return mockserver.make_response(
                    status=200,
                    json={
                        'rule_id': rule[fine_key]['rule_id'],
                        'client_id': client_id,
                        'fine_params': rule[fine_key]['params'],
                        'billing_frequency': rule[fine_key][
                            'billing_frequency'
                        ],
                    },
                )

            return mockserver.make_response(
                status=500,
                json={
                    'code': 'INTERNAL_ERROR',
                    'message': f'Unknown path: {request.path}',
                },
            )

        return _service_handler

    return _inner


@pytest.fixture(name='billing_orders_mock')
def _billing_orders_mock(mockserver):
    class BillingOrders:
        def __init__(self, mockserver):
            self._async_fail = False
            self._requests = []
            self._responses = []
            self._counter = 1

            def make_handler():
                @mockserver.json_handler('/billing-orders/v2/process/async')
                def _handler(request):
                    if self._async_fail:
                        response = {'message': 'BAD REQUEST', 'code': '400'}
                        self._responses.append(response)
                        return mockserver.make_response(
                            json=response, status=400,
                        )

                    response = {'orders': []}
                    for order in request.json['orders']:
                        response['orders'].append(
                            {
                                'topic': order.pop('topic'),
                                'external_ref': order.pop('external_ref'),
                                'doc_id': self._counter,
                            },
                        )
                        self._counter += 1
                    self._requests.append(request.json)
                    self._responses.append(response)
                    return mockserver.make_response(json=response, status=200)

                return _handler

            self._handler = make_handler()

        def should_fail(self):
            self._async_fail = True

        @property
        def requests(self):
            return self._requests

        @property
        def responses(self):
            return self._responses

        @property
        def times_called(self):
            return self._handler.times_called

    return BillingOrders(mockserver)


@pytest.fixture(name='mock_storage_search')
def _mock_storage_search(mockserver):
    def _inner(
            expected_request=None,
            response=None,
            response_code=200,
            error=None,
            sleep_and_wait_cancellation=False,
    ):
        @mockserver.json_handler(
            '/eats-billing-storage/billing-storage/search',
        )
        async def storage_search(request):
            try:
                if sleep_and_wait_cancellation:
                    await asyncio.sleep(9999)
                    return

                if error:
                    raise error

                if expected_request:
                    assert expected_request == request.json

                nonlocal response
                if not response:
                    response = {'docs': []}

                return mockserver.make_response(
                    json=response, status=response_code,
                )
            except asyncio.CancelledError:
                if not sleep_and_wait_cancellation:
                    raise

        return storage_search

    return _inner


@pytest.fixture(name='mock_storage_store')
def _mock_storage_store(mockserver):
    def _inner(
            expected_request=None,
            response=None,
            response_code=200,
            error=None,
    ):
        @mockserver.json_handler(
            '/eats-billing-storage/billing-storage/create/bulk',
        )
        def storage_store(request):
            if error:
                raise error

            if expected_request:
                result = helpers.billing_doc_lists_are_equal(
                    request.json, expected_request,
                )
                if not result:
                    logging.getLogger(__name__).log(
                        logging.ERROR,
                        '-----> Request json is %s',
                        request.json,
                    )
                    logging.getLogger(__name__).log(
                        logging.ERROR,
                        '-----> Expected request is %s',
                        expected_request,
                    )

                assert result

            nonlocal response
            if not response:
                response = {'message': 'OK', 'status': 'success'}

            return mockserver.make_response(
                json=response, status=response_code,
            )

        return storage_store

    return _inner


@pytest.fixture(name='mock_storage_finish')
def _mock_storage_finish(mockserver):
    def _inner(
            expected_requests=None,
            response=None,
            response_code=200,
            error=None,
    ):
        expected_requests_copy = None
        if expected_requests:
            expected_requests_copy = expected_requests.copy()

        @mockserver.json_handler(
            '/eats-billing-storage/billing-storage/finish-processing',
        )
        def storage_finish(request):
            if error:
                raise error

            nonlocal expected_requests_copy
            if expected_requests_copy:
                assert expected_requests_copy[0] == request.json
                expected_requests_copy.pop(0)

            nonlocal response
            if not response:
                response = {'finished': True, 'status': 'complete'}

            return mockserver.make_response(
                json=response, status=response_code,
            )

        return storage_finish

    return _inner


@pytest.fixture(name='mock_business_rules')
def _mock_business_rules(mockserver):
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

        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/business-rules',
        )
        def business_rules(request):
            if error:
                raise error

            # проверяем порядок поступления запросов
            nonlocal expected_requests_copy
            if expected_requests_copy:
                assert (
                    expected_requests_copy[0]['billing_date']
                    == request.json['billing_date']
                )
                expected_requests_copy[0].pop('billing_date')
                request.json.pop('billing_date')

                assert expected_requests_copy[0] == request.json
                expected_requests_copy.pop(0)

            # ответы выдаем по назначенному порядку
            response = None
            if responses_copy:
                response = responses_copy[0]
                responses_copy.pop(0)
            else:
                response = {
                    'client_id': '',
                    'commissions': {
                        'commission': '0',
                        'acquiring_commission': '0',
                        'fix_commission': '0',
                    },
                }

            return mockserver.make_response(
                json=response, status=response_code,
            )

        return business_rules

    return _inner


@pytest.fixture(name='mock_create_handler')
def _mock_create_handler(mockserver, testpoint):
    def _inner():
        @mockserver.json_handler('/eats-billing-processor/v1/create')
        def create(request):  # pylint: disable=unused-variable
            return mockserver.make_response(status=200, json={'event_id': '1'})

        @testpoint('handler_error')
        def _handler_error(data):
            pass

        return _handler_error

    return _inner


@pytest.fixture(name='billing_reports_mock')
def _billing_reports_mock(mockserver):
    class BillingReports:
        def __init__(self, mockserver):
            self._async_fail = False
            self._response = None
            self._docs = None

            def make_handler():
                @mockserver.json_handler('/billing-reports/v1/docs/by_tag')
                def _handler(request):
                    if self._async_fail:
                        response = {'message': 'BAD REQUEST', 'code': '500'}
                        return mockserver.make_response(
                            json=response, status=500,
                        )
                    docs = []
                    for doc in self._docs:
                        transaction = {
                            'doc_id': doc['doc_id'],
                            'kind': 'arbitrary_payout',
                            'external_event_ref': '220329-493724/63976',
                            'external_obj_id': '220329-493724/63976',
                            'data': {'payments': [doc['data']['payments']]},
                            'event_version': 1,
                            'schema_version': 'v2',
                            'topic_begin_at': '2022-03-21T08:26:53+00:00',
                            'template_entries': [],
                            'event_at': '2022-03-21T08:26:53.000000+00:00',
                            'created': '2022-03-21T09:03:35.775550+00:00',
                            'process_at': '2022-03-21T09:03:35.764477+00:00',
                            'service': 'billing-orders',
                            'entry_ids': [],
                            'revision': 1239007143,
                            'tags': [],
                            'status': 'complete',
                            'source': 'pg',
                        }
                        docs.append(transaction)
                    response = {'docs': docs, 'cursor': 'cursor'}
                    return mockserver.make_response(json=response, status=200)

                return _handler

            self._handler = make_handler()

        @property
        def times_called(self):
            return self._handler.times_called

        def docs(self, docs):
            self._docs = docs
            return self

        def should_fail(self):
            self._async_fail = True

    return BillingReports(mockserver)

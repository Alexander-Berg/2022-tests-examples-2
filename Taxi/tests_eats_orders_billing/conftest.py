import asyncio
import json
import logging
import typing

import pytest


# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_orders_billing_plugins import *  # noqa: F403 F401

from tests_eats_orders_billing import helpers


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


@pytest.fixture(name='mock_eats_billing_processor_create')
def _mock_eats_billing_processor_create(mockserver):
    def _inner():
        @mockserver.json_handler('/eats-billing-processor/v1/create')
        def create(request):  # pylint: disable=unused-variable
            return mockserver.make_response(status=200, json={'event_id': '1'})

        return create

    return _inner


@pytest.fixture(name='mock_customer_service_retrieve')
def _mock_customer_service_retrieve(mockserver, load_json):
    response = load_json('customer_service_response.json')

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services',
    )
    def _transactions_invoice_retrieve(request):
        return mockserver.make_response(json.dumps(response), 200)


@pytest.fixture(name='mock_customer_service_retrieve_new')
def _mock_customer_service_retrieve_new(mockserver, load_json):
    response = load_json('customer_service_response_new.json')

    @mockserver.json_handler(
        '/eats-order-revision/v1' '/order-revision/customer-services',
    )
    def _transactions_invoice_retrieve(request):
        return mockserver.make_response(json.dumps(response), 200)


@pytest.fixture(name='mock_order_revision_list')
def _mock_order_revision_list(mockserver):
    def _inner(revisions: typing.List[dict] = None):
        if revisions is None:
            revisions = [
                {'revision_id': 'aaaa'},
                {'revision_id': 'bbbb'},
                {'revision_id': 'abcd'},
            ]

        # pylint: disable=invalid-name
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/' 'v1/order-revision/list',
        )
        def transactions_create_invoice_handler(request):
            return mockserver.make_response(
                status=200,
                json={'order_id': 'test_order', 'revisions': revisions},
            )

        return transactions_create_invoice_handler

    return _inner


@pytest.fixture(name='mock_order_revision_list_new')
def _mock_order_revision_list_new(mockserver):
    def _inner(revisions: typing.List[dict] = None):
        if revisions is None:
            revisions = [
                {'origin_revision_id': 'aaaa'},
                {'origin_revision_id': 'bbbb'},
                {'origin_revision_id': 'abcd'},
            ]

        # pylint: disable=invalid-name
        @mockserver.json_handler('/eats-order-revision/' 'v1/revision/list')
        def transactions_create_invoice_handler(request):
            return mockserver.make_response(
                status=200,
                json={'order_id': 'test_order', 'revisions': revisions},
            )

        return transactions_create_invoice_handler

    return _inner


@pytest.fixture()
def select_billing_input_events(pgsql):
    def _select_billing_input_events(event_id):
        cursor = pgsql['eats_orders_billing'].cursor()
        cursor.execute(
            f"""
            SELECT id, kind, external_obj_id, external_event_ref, event_at,
            service, service_user_id, data, status
            FROM eats_orders_billing.input_events
            WHERE id = '{event_id}'
            """,
        )
        return list(cursor)

    return _select_billing_input_events


@pytest.fixture()
def insert_billing_input_events(pgsql):
    def _insert_billing_input_events(input_events: typing.List[dict]):
        item_fields = [
            'kind',
            'external_obj_id',
            'external_event_ref',
            'event_at',
            'service',
            'service_user_id',
            'data',
            'status',
        ]

        def _build_value(event: dict) -> str:
            item_values = [event[field] for field in item_fields]
            sql_values = [f'\'{value}\'' for value in item_values]
            return ','.join(sql_values)

        inserted_item_fields = ', '.join(item_fields)
        inserted_values = ','.join(
            f'({_build_value(event)})' for event in input_events
        )
        query = (
            f'INSERT INTO eats_orders_billing.input_events'
            f' ({inserted_item_fields})'
            f' VALUES {inserted_values}'
        )
        cursor = pgsql['eats_orders_billing'].cursor()
        cursor.execute(query)

    return _insert_billing_input_events

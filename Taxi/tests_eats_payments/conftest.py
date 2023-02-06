# pylint: disable=too-many-lines
import typing

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_payments_plugins import *  # noqa: F403 F401
import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers
from tests_eats_payments import models

TEST_ORDER_ID = 'test_order'
TEST_PAYMENT_ID = '27affbc7-de68-4a79-abba-d9bdf48e6e09'
TEST_CURRENCY = 'RUB'
TEST_CARGO_PAYMENT_REVISION = 1234
TEST_CARGO_PAYMENT_STATUS = 'new'
TEST_CARGO_PAYMENT_CREATED_AT = '2020-03-30T08:29:06+00:00'
TEST_DEFAULT_VIRTUAL_CLIENT_ID = 'b8671563-47fa-42ff-8159-4118eee9fb1f'
TEST_PERSONAL_PHONE_ID = '456'

LIST_PAYMENT_METHODS_RESPONSE_BASE: typing.Dict[str, typing.Any] = {
    'last_used_payment_method': {
        'id': 'badge:yandex_badge:RUB',
        'type': 'corp',
    },
    'payment_methods': [],
}


@pytest.fixture(name='mock_eats_notifications_notification')
def _mock_eats_notifications_notification(mockserver):
    def _inner():
        # pylint: disable=invalid-name
        @mockserver.json_handler('/eats-notifications/v1/notification')
        def notification_handler(request):
            return mockserver.make_response(
                status=200, json={'token': 'token'},
            )

        return notification_handler

    return _inner


@pytest.fixture(name='mock_order_revision_customer_services')
def _mock_order_revision_customer_services(mockserver):
    def _inner(customer_services: typing.List[dict]):
        # pylint: disable=invalid-name
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/'
            'v1/order-revision/customer-services',
        )
        @mockserver.json_handler(
            '/eats-order-revision/v1/' 'order-revision/customer-services',
        )
        def transactions_create_invoice_handler(request):
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )

        return transactions_create_invoice_handler

    return _inner


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
        @mockserver.json_handler('/eats-order-revision/v1/revision/list')
        def transactions_create_invoice_handler(request):
            for i, revision in enumerate(revisions):
                revisions[i]['origin_revision_id'] = revision['revision_id']
            return mockserver.make_response(
                status=200,
                json={'order_id': 'test_order', 'revisions': revisions},
            )

        return transactions_create_invoice_handler

    return _inner


@pytest.fixture(name='mock_order_revision_customer_services_details')
def _mock_order_revision_customer_services_details(mockserver):
    def _inner(
            customer_services: typing.List[dict], expected_revision_id=None,
    ):
        # pylint: disable=invalid-name
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/'
            'v1/order-revision/customer-services/details',
        )
        @mockserver.json_handler(
            '/eats-order-revision/v1/order-revision/customer-services/details',
        )
        def transactions_create_invoice_handler(request):
            if expected_revision_id is not None:
                if 'revision_id' in request.json:
                    assert request.json['revision_id'] == expected_revision_id
                if 'origin_revision_id' in request.json:
                    assert (
                        request.json['origin_revision_id']
                        == expected_revision_id
                    )
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )

        return transactions_create_invoice_handler

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='mock_transactions_invoice_retrieve')
def _mock_transactions_invoice_retrieve(mockserver, load_json):
    def _inner(
            items: typing.Optional[typing.List[dict]] = None,
            invoice_retrieve_response=None,
            error=None,
            file_to_load='retrieve_invoice.json',
            **kwargs,
    ):
        # pylint: disable=invalid-name
        @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
        def transactions_retrieve_invoice_handler(request):
            if invoice_retrieve_response is not None:
                return mockserver.make_response(**invoice_retrieve_response)

            if error is not None:
                raise error

            invoice = load_json(file_to_load)
            if items is not None:
                invoice['sum_to_pay'] = helpers.sort_items(items)
            invoice.update(kwargs)
            print(invoice)

            return invoice

        return transactions_retrieve_invoice_handler

    return _inner


@pytest.fixture(name='mock_transactions_invoice_update')
def _mock_transactions_invoice_update(mockserver, load_json):
    def _inner(
            invoice_id: str = 'test_order',
            items: typing.Optional[typing.List[dict]] = None,
            payment_type: typing.Optional[str] = None,
            payment_method_id: str = '123',
            operation_id: str = 'update:abcd',
            billing_id: typing.Optional[str] = None,
            payer_login: typing.Optional[str] = None,
            version: int = 2,
            payment_timeout: typing.Optional[int] = None,
            invoice_update_response=None,
            complement_payment: typing.Optional[models.Complement] = None,
            wallet_payload: typing.Optional[typing.Any] = None,
            ttl: int = None,
            trust_afs_params: dict = None,
            pass_params: dict = None,
            transaction_payload: dict = None,
    ):
        if payment_type == 'corp':
            billing_id = ''

        # pylint: disable=invalid-name
        @mockserver.json_handler('/transactions-eda/v2/invoice/update')
        def transactions_update_invoice_handler(request):
            if invoice_update_response is not None:
                return mockserver.make_response(**invoice_update_response)

            payment_method = None
            if payment_type is not None:
                payment_method = {
                    'method': payment_method_id,
                    'type': payment_type,
                }

                if billing_id is not None:
                    payment_method['billing_id'] = billing_id

            if payment_type == 'badge':
                assert payer_login is not None
                payment_method['payer_login'] = payer_login

            request_body = request.json
            request_body['items_by_payment_type'] = helpers.sort_items(
                request_body['items_by_payment_type'],
            )

            expected_body = {
                'id': invoice_id,
                'version': version,
                'operation_id': operation_id,
                'originator': 'eats_payments',
                'items_by_payment_type': helpers.sort_items(items or []),
            }

            if payment_method is not None:
                expected_body['payments'] = [payment_method]

                if complement_payment is not None:
                    expected_body['payments'].append(
                        complement_payment.get_transaction_payment(),
                    )

            if payment_timeout is not None:
                expected_body['payment_timeout'] = payment_timeout

            if wallet_payload is not None:
                expected_body['wallet_payload'] = wallet_payload

            if ttl is not None:
                expected_body['ttl'] = ttl

            if trust_afs_params is not None:
                expected_body['trust_afs_params'] = trust_afs_params

            if pass_params:
                expected_body['pass_params'] = pass_params

            if transaction_payload:
                expected_body['transaction_payload'] = transaction_payload

            print(request_body)
            print(expected_body)
            assert request_body == expected_body
            return {}

        return transactions_update_invoice_handler

    return _inner


@pytest.fixture(name='mock_transactions_invoice_clear')
def _mock_transactions_invoice_clear(mockserver, load_json):
    def _inner():
        @mockserver.json_handler('/transactions-eda/invoice/clear')
        def handler(request):
            return mockserver.make_response(**{'status': 200, 'json': {}})

        return handler

    return _inner


@pytest.fixture
def mock_cargo_payments_info(mockserver):
    def _inner(
            expected_status=200,
            expected_payment_id=None,
            response_items=None,
            error=None,
            is_paid=False,
    ):
        if response_items is None:
            response_items = []

        @mockserver.json_handler('/cargo-payments/v1/payment/info')
        def _mock_info(request):
            if expected_payment_id is not None:
                assert request.query['payment_id'] == expected_payment_id
            if error is not None:
                raise error
            if expected_status == 200:
                final_sum = str(
                    '%.4f'
                    % (
                        sum(
                            [
                                float(item['price']) * item['count']
                                for item in response_items
                            ],
                        ),
                    ),
                )
                return {
                    'final_sum': final_sum,
                    'payment_id': TEST_PAYMENT_ID,
                    'revision': TEST_CARGO_PAYMENT_REVISION,
                    'status': TEST_CARGO_PAYMENT_STATUS,
                    'created_at': TEST_CARGO_PAYMENT_CREATED_AT,
                    'is_paid': is_paid,
                    'details': {
                        'external_id': TEST_ORDER_ID,
                        'client_id': {
                            'id': consts.BASE_HEADERS['X-Yandex-Uid'],
                            'type': 'yandex_uid',
                        },
                        'virtual_client_id': TEST_DEFAULT_VIRTUAL_CLIENT_ID,
                        'customer': {'phone_pd_id': TEST_PERSONAL_PHONE_ID},
                    },
                    'items': response_items,
                    'payment_methods': [
                        {
                            'type': 'card',
                            'title': 'Card',
                            'is_alternative': False,
                            'is_sdk_flow': True,
                        },
                        {
                            'type': 'link',
                            'title': 'Link',
                            'is_alternative': False,
                            'is_sdk_flow': False,
                        },
                        {
                            'type': 'cash',
                            'title': 'Cash',
                            'is_alternative': False,
                            'is_sdk_flow': False,
                        },
                    ],
                    'active_operations': [
                        {
                            'type': 'wait_payment',
                            'id': 123,
                            'created_at': TEST_CARGO_PAYMENT_CREATED_AT,
                            'meta': {
                                'link': 'test_url',
                                'payment_method': 'card',
                            },
                        },
                        {
                            'type': 'refund_payment',
                            'id': 456,
                            'created_at': TEST_CARGO_PAYMENT_CREATED_AT,
                            'meta': {'refund_sum': '100.55'},
                        },
                    ],
                }
            return mockserver.make_response(
                status=expected_status,
                json={'code': str(expected_status), 'message': 'some error'},
            )

        return _mock_info

    return _inner


@pytest.fixture(name='mock_eats_debt_user_scoring')
def _mock_eats_debt_user_scoring(mockserver):
    def _inner(
            allow_credit: False,
            check_request: typing.Optional[dict] = None,
            status=200,
    ):
        @mockserver.json_handler(
            '/eats-debt-user-scoring/'
            + 'internal/eats-debt-user-scoring/'
            + 'v1/eats-credit/score',
        )
        def eats_credit_score_handler(request):
            if check_request:
                assert request.json == check_request
            return mockserver.make_response(
                status=status, json={'allow_credit': allow_credit},
            )

        return eats_credit_score_handler

    return _inner


@pytest.fixture(name='mock_eats_debt_user_scoring_verdict')
def _mock_eats_debt_user_scoring_verdict(mockserver):
    def _inner(
            verdict='rejected', check_request: typing.Optional[dict] = None,
    ):
        @mockserver.json_handler(
            '/eats-debt-user-scoring/'
            + 'internal/eats-debt-user-scoring/'
            + 'v1/user-scoring-verdict',
        )
        def eats_debt_verdict_handler(request):
            if check_request:
                assert request.json == check_request
            return mockserver.make_response(
                status=200, json={'verdict': verdict, 'identity': 'identity'},
            )

        return eats_debt_verdict_handler

    return _inner


@pytest.fixture(name='mock_debt_collector_create_invoice')
def _mock_debt_collector_create_invoice(mockserver, load_json):
    def _inner():
        @mockserver.json_handler('/debt-collector/v1/debt/create')
        def handler(request):
            return mockserver.make_response(**{'status': 200, 'json': {}})

        return handler

    return _inner


@pytest.fixture(name='mock_debt_collector_update_invoice')
def _mock_debt_collector_update_invoice(mockserver, load_json):
    def _inner():
        @mockserver.json_handler('/debt-collector/v1/debt/update')
        def handler(request):
            return mockserver.make_response(**{'status': 200, 'json': {}})

        return handler

    return _inner


@pytest.fixture(name='mock_debt_collector_by_ids')
def _mock_debt_collector_by_ids(mockserver, load_json):
    def _inner(expected_status=200, debts=None, error=None, ids=None):
        if debts is None:
            debts = []

        @mockserver.json_handler('/debt-collector/v1/debts/by_id')
        def handler(request):
            if ids is not None:
                assert request.ids == ids
            if error is not None:
                raise error
            if expected_status == 200:
                return {'debts': debts}
            return mockserver.make_response(
                status=expected_status,
                json={'code': str(expected_status), 'message': 'some error'},
            )

        return handler

    return _inner


@pytest.fixture()
def insert_operations(pgsql):
    def _insert_operations(
            operation_id,
            order_id,
            revision,
            prev_revision,
            operation_type,
            status='done',
            fails_count=0,
    ):
        query = (
            f'INSERT INTO eats_payments.operations'
            f' (id, order_id, revision, prev_revision, '
            f' type, status, fails_count)'
            f' VALUES ({operation_id}, \'{order_id}\', \'{revision}\','
            f' \'{prev_revision}\', '
            f' \'{operation_type}\', \'{status}\', {fails_count})'
        )
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(query)

    return _insert_operations


@pytest.fixture()
def insert_items(pgsql):
    def _insert_items(items: typing.List[dict]):
        item_fields = [
            'item_id',
            'order_id',
            'place_id',
            'balance_client_id',
            'type',
        ]

        def _build_value(item: dict) -> str:
            item_values = [item[field] for field in item_fields]
            sql_values = [f'\'{value}\'' for value in item_values]
            return ','.join(sql_values)

        inserted_item_fields = ', '.join(item_fields)
        inserted_values = ','.join(f'({_build_value(item)})' for item in items)
        query = (
            f'INSERT INTO eats_payments.items_info'
            f' ({inserted_item_fields})'
            f' VALUES {inserted_values}'
        )
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(query)

    return _insert_items


@pytest.fixture()
def fetch_items_from_db(pgsql):
    def _fetch_items_from_db(order_id: str):
        fields = [
            'item_id',
            'order_id',
            'place_id',
            'balance_client_id',
            'type',
        ]
        selected_fields = ', '.join(fields)
        query = (
            f'SELECT {selected_fields}'
            f' FROM eats_payments.items_info'
            f' WHERE order_id = \'{order_id}\''
        )
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(zip(fields, row)) for row in rows]

    return _fetch_items_from_db


@pytest.fixture()
def assert_db_order(pgsql):
    def _assert_db_order(
            order_id,
            expected_service=consts.DEFAULT_SERVICE,
            expected_complement_payment_type=None,
            expected_complement_payment_id=None,
            expected_complement_amount=None,
            expected_business_type=None,
            expected_business_specification=None,
            expect_no_order=False,
            expected_api_version=1,
            expected_cancelled=None,
            expected_is_transparent_payment=None,
    ):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            SELECT
                order_id,
                service,
                currency,
                complement_payment_type,
                complement_payment_id,
                complement_amount,
                business_type,
                business_specification,
                api_version,
                cancelled,
                is_transparent_payment
            FROM eats_payments.orders
            WHERE order_id = '{order_id}'
            """,
        )
        if expect_no_order:
            assert not list(cursor)
        else:
            result = list(cursor)[0]
            assert result[1] == expected_service
            assert result[2] == TEST_CURRENCY
            assert result[3] == expected_complement_payment_type
            assert result[4] == expected_complement_payment_id
            assert result[5] == expected_complement_amount
            assert result[6] == expected_business_type
            assert result[7] == expected_business_specification
            assert result[8] == expected_api_version
            assert result[9] == expected_cancelled
            if expected_is_transparent_payment:
                assert result[10] == expected_is_transparent_payment

    return _assert_db_order


@pytest.fixture()
def assert_db_order_payment(pgsql):
    def _assert_db_order_payment(
            order_id,
            expected_payment_id=None,
            expected_payment_type=None,
            expect_no_payment=False,
            expected_currency=None,
            expected_available=None,
            expected_retry_count=None,
    ):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            SELECT order_id, payment_id, payment_type, currency, available,
                   retry_count
            FROM eats_payments.orders_payments
            WHERE order_id = '{order_id}'
            """,
        )
        if expect_no_payment:
            assert not list(cursor)
        else:
            result = list(cursor)[0]
            assert result[1] == expected_payment_id
            assert result[2] == expected_payment_type
            if expected_currency:
                assert result[3] == expected_currency
            assert result[4] == expected_available
            if expected_retry_count:
                assert result[5] == expected_retry_count

    return _assert_db_order_payment


@pytest.fixture()
def upsert_order(pgsql):
    def _upsert_order(
            order_id,
            service: str = consts.DEFAULT_SERVICE,
            currency: str = 'RUB',
            api_version: int = 1,
            originator: str = consts.DEFAULT_ORIGINATOR,
            business_type: str = None,
            business_specification: str = None,
            cancelled: bool = None,
    ):
        cursor = pgsql['eats_payments'].cursor()
        injection = f',\'{cancelled}\''
        cursor.execute(
            f"""
            INSERT INTO eats_payments.orders (
                order_id,
                service,
                currency,
                originator,
                api_version
                {',cancelled' if cancelled else ''}
            )
            VALUES (
                '{order_id}',
                '{service}',
                '{currency}',
                '{originator}',
                '{api_version}'
                {injection if cancelled else ''}
            )
            ON CONFLICT (order_id) DO
            UPDATE SET
                order_id = EXCLUDED.order_id,
                service = EXCLUDED.service,
                currency = EXCLUDED.currency,
                complement_payment_type = EXCLUDED.complement_payment_type,
                complement_payment_id = EXCLUDED.complement_payment_id,
                complement_amount = EXCLUDED.complement_amount,
                business_type = EXCLUDED.business_type,
                business_specification = EXCLUDED.business_specification,
                originator = EXCLUDED.originator,
                api_version = EXCLUDED.api_version
                {',cancelled = EXCLUDED.cancelled' if cancelled else ''}
            ;
            """,
        )

        if business_type is not None:
            cursor.execute(
                f"""
                UPDATE eats_payments.orders
                SET business_type = '{business_type}'
                WHERE order_id = '{order_id}';
            """,
            )
        if business_specification is not None:
            cursor.execute(
                f"""
                UPDATE eats_payments.orders
                SET business_specification = '{business_specification}'
                WHERE order_id = '{order_id}';
            """,
            )

    return _upsert_order


@pytest.fixture()
def upsert_order_payment(pgsql):
    def _upsert_order_payment(
            order_id,
            payment_id,
            payment_type,
            currency=None,
            available=None,
            retry_count=None,
    ):
        available = 'Null' if available is None else available
        retry_count = 'Null' if retry_count is None else retry_count

        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payments.orders_payments
            (order_id, payment_id, payment_type, currency, available,
             retry_count)
            VALUES ('{order_id}', '{payment_id}', '{payment_type}',
                    '{currency}', {available}, {retry_count})
            ON CONFLICT(order_id)
            DO UPDATE SET
                payment_id = EXCLUDED.payment_id,
                payment_type = EXCLUDED.payment_type,
                currency = EXCLUDED.currency,
                available = EXCLUDED.available,
                retry_count = EXCLUDED.retry_count
            ;
            """,
        )

    return _upsert_order_payment


@pytest.fixture()
def update_payment_time(pgsql):
    def _update_payment_time(order_id, updated_at):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            UPDATE eats_payments.orders_payments
            SET updated_at = '{updated_at}'
            WHERE order_id = '{order_id}';
            """,
        )

    return _update_payment_time


@pytest.fixture()
def upsert_items_payment(pgsql):
    def _upsert_items_payment(
            item_id, order_id, payment_type, plus_amount, revision_id,
    ):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payments.item_payment_type_revision
            (item_id, order_id, payment_type, plus_amount, revision_id)
            VALUES ('{item_id}', '{order_id}', '{payment_type}',
                    '{plus_amount}', '{revision_id}')
            """,
        )

    return _upsert_items_payment


@pytest.fixture()
def upsert_debt_status(pgsql):
    def _upsert_debt_status(order_id, debt_status):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payments.order_debt_status
            (order_id, debt_status)
            VALUES ('{order_id}', '{debt_status}');
            """,
        )

    return _upsert_debt_status


@pytest.fixture()
def assert_db_item_payment_type(pgsql):
    def _assert_db_item_payment_type(
            item_id,
            expected_order_id,
            expected_payment_type,
            expected_plus_amount,
            revision=None,
    ):
        cursor = pgsql['eats_payments'].cursor()

        if revision is None:
            cursor.execute(
                f"""
                SELECT item_id, order_id, payment_type, plus_amount
                FROM eats_payments.item_payment_type_revision
                WHERE item_id = '{item_id}'
                """,
            )
        else:
            cursor.execute(
                f"""
                SELECT item_id, order_id, payment_type, plus_amount
                FROM eats_payments.item_payment_type_revision
                WHERE item_id = '{item_id}' AND revision_id='{revision}'
                """,
            )
        result = list(cursor)[0]
        assert result[1] == expected_order_id
        assert result[2] == expected_payment_type
        assert result[3] == expected_plus_amount

    return _assert_db_item_payment_type


@pytest.fixture()
def get_db_items_payment_type_by_order_id(pgsql):
    def _get_db_items_payment_type_by_order_id(order_id):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            SELECT item_id, order_id, payment_type, plus_amount, revision_id
            FROM eats_payments.item_payment_type_revision
            WHERE order_id = '{order_id}'
            """,
        )

        result = list(cursor)
        return result

    return _get_db_items_payment_type_by_order_id


@pytest.fixture()
def get_db_items_payment_type_by_revision(pgsql):
    def _get_db_items_payment_type_by_revision(order_id, revision):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            SELECT item_id, order_id, payment_type, plus_amount, revision_id
            FROM eats_payments.item_payment_type_revision
            WHERE order_id = '{order_id}' AND revision_id = '{revision}'
            """,
        )

        result = list(cursor)
        return result

    return _get_db_items_payment_type_by_revision


@pytest.fixture()
def assert_stq_order_payment_task(stq):
    def _assert_stq_order_payment_task(
            expected_order_id=None,
            expected_action=None,
            expected_status=None,
            expected_revision=None,
            expected_payment_id=None,
            expect_no_task=False,
    ):
        if expect_no_task:
            assert (
                not stq.eda_order_processing_payment_events_callback.has_calls
            )
        else:
            assert (
                stq.eda_order_processing_payment_events_callback.times_called
                == 1
            )
            task_info = (
                stq.eda_order_processing_payment_events_callback.next_call()
            )
            assert task_info['id'] == expected_order_id
            assert task_info['kwargs']['order_id'] == expected_order_id
            assert task_info['kwargs']['action'] == expected_action
            assert task_info['kwargs']['status'] == expected_status
            assert task_info['kwargs']['revision'] == expected_revision
            if expected_payment_id is not None:
                assert task_info['kwargs']['payment_id'] == expected_payment_id
            else:
                assert 'payment_id' not in task_info['kwargs']

    return _assert_stq_order_payment_task


@pytest.fixture()
def insert_operation(pgsql):
    def _insert_operation(
            order_id, revision, prev_revision, op_type, status, fails_count,
    ):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payments.operations
                (order_id, revision, prev_revision, type, status, fails_count)
            VALUES
            ('{order_id}', '{revision}', '{prev_revision}',
             '{op_type}', '{status}', '{fails_count}');
            """,
        )

    return _insert_operation


@pytest.fixture()
def fetch_operation(pgsql):
    def _fetch_operation(
            order_id,
            revision,
            prev_revision=None,
            status=None,
            fails_count=None,
            operation_type=None,
            empty=None,
    ):
        cursor = pgsql['eats_payments'].cursor()
        cursor.execute(
            f"""
            SELECT
                order_id, revision, prev_revision, status, fails_count,type
            FROM eats_payments.operations
            WHERE order_id = '{order_id}' AND revision = '{revision}'
            """,
        )
        result = list(cursor)
        if empty is not None:
            assert not result
            return
        assert result[0][0] == order_id
        assert result[0][1] == revision
        if prev_revision is not None:
            assert result[0][2] == prev_revision
        if status is not None:
            assert result[0][3] == status
        if fails_count is not None:
            assert result[0][4] == fails_count
        if operation_type is not None:
            assert result[0][5] == operation_type

    return _fetch_operation


# pylint: disable=invalid-name
@pytest.fixture(name='mock_saturn')
def _mock_saturn(mockserver):
    def _inner(status: str):
        # pylint: disable=invalid-name
        @mockserver.json_handler('/saturn/api/v1/eda/search')
        def saturn_handler(request):
            return {
                'reqid': 'fff-785647',
                'puid': 76874335,
                'score': 100,
                'score_percentile': 90,
                'formula_id': '785833',
                'formula_description': 'bnpl_market',
                'data_source': 'puid/2021-06-21',
                'status': status,
            }

        return saturn_handler

    return _inner


@pytest.fixture(name='mock_api_proxy_4_list_payment_methods')
def mock_api_proxy_4_list_payment_methods_fixture(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_api_proxy_list_payment_methods(
            payment_methods=None,
            merchant_ids=None,
            merchant_id=None,
            service_token=None,
            country=False,
    ):
        @mockserver.json_handler(
            '/api-proxy-superapp-critical'
            '/4.0/payments/v1/list-payment-methods',
        )
        def _api_proxy_handler(request):
            response = {
                **LIST_PAYMENT_METHODS_RESPONSE_BASE,
                'payment_methods': (
                    [] if payment_methods is None else payment_methods
                ),
                'merchant_id_list': (
                    ['merchant.ru.yandex.ytaxi.trust']
                    if merchant_ids is None
                    else merchant_ids
                ),
            }
            if merchant_id is not None:
                response['merchant_id'] = merchant_id

            if service_token is not None:
                response['service_token'] = service_token

            if country is not None:
                response['region_id'] = country

            return response

        return _api_proxy_handler

    return _mock_api_proxy_list_payment_methods


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.fixture(name='mock_trust_payments_get')
def _mock_trust_payments_get(mockserver):
    def _inner(purchase_token):
        @mockserver.json_handler(
            '/trust-eda/trust-payments/v2/payments/' + purchase_token,
        )
        def transactions_create_invoice_handler(request):
            return mockserver.make_response(
                status=200,
                json={
                    '3ds_transaction_info': {
                        'redirect_url': (
                            'https://trust.yandex.ru/web/redirect_3ds?'
                            'purchase_token=c964a582b3b4b3dcd514ab1914a7d2a8'
                        ),
                        'process_url': (
                            'https://trust.yandex.ru/web/process_3ds?'
                            'purchase_token=c964a582b3b4b3dcd514ab1914a7d2a8'
                        ),
                        'status': 'wait_for_result',
                    },
                    'purchase_token': purchase_token,
                    'amount': '0.00',
                    'currency': 'RUB',
                    'payment_status': 'started',
                    'orders': [],
                },
            )

        return transactions_create_invoice_handler

    return _inner


# pylint: disable=invalid-name
@pytest.fixture(name='check_transactions_callback_task')
def check_transactions_callback_task_fixture(
        stq_runner, stq, mockserver, load_json,
):
    async def _inner(
            operation_id: str = 'create:123456',
            operation_status: str = 'done',
            notification_type: str = 'operation_finish',
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            transactions: typing.Optional[typing.List[dict]] = None,
    ):
        await stq_runner.eats_payments_transactions_callback.call(
            task_id='test_task_id',
            args=[
                'test_order',
                operation_id,
                operation_status,
                notification_type,
            ],
            kwargs={'transactions': transactions or []},
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner

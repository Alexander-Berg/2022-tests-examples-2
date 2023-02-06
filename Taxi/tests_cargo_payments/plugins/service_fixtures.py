"""
    Describe here service specific fixtures.
"""
import dataclasses
import datetime
import typing as tp
import uuid

import pytest


DEFAULT_CORP_CLIENT_ID = '651efc77d91b462f86a47eef39795b03'

DEFAULT_DRIVER_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driverid1',
    'X-YaTaxi-Park-Id': 'parkid1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.fixture(name='default_corp_client_id')
async def _default_corp_client_id():
    return DEFAULT_CORP_CLIENT_ID


@pytest.fixture(name='add_virtual_client')
async def _add_virtual_client(pgsql):
    def wrapper(
            *,
            virtual_client_id: str,
            comment: str = 'yandex_virtual_client',
            inn: str = None,
    ):
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'INSERT INTO cargo_payments.virtual_clients'
            '(id, comment) VALUES (%s, %s) RETURNING id',
            (virtual_client_id, comment),
        )
        client_id = cursor.fetchall()[0][0]
        if inn is not None:
            cursor.execute(
                'UPDATE cargo_payments.virtual_clients' 'SET default_inn = %s',
                (inn,),
            )
        return client_id

    return wrapper


@pytest.fixture(name='add_tid')
async def _add_tid(pgsql):
    def wrapper(*, virtual_client_id: str, tid: str):
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'INSERT INTO cargo_payments.tid_pulls'
            '(virtual_client_id, tid) VALUES (%s, %s)',
            (virtual_client_id, tid),
        )

    return wrapper


@pytest.fixture(name='init_agents_pull')
async def _init_agents_pull(pgsql):
    def wrapper():
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'INSERT INTO cargo_payments.logins_pull'
            '(pull_type, prefix)'
            'VALUES (\'agents\', %s), (\'agents\', %s), (\'agents\', %s)',
            ('tom', 'tim', 'sam'),
        )

    return wrapper


def _build_item(
        *,
        item_id,
        items_currency='RUB',
        price='10.00',
        item_type='product',
        supplier_inn='9705114405',
        item_mark=None,
        item_count=2,
        agent_type=None,
        **kwargs,
):
    report = {
        'article': f'article_{item_id}',
        'title': f'title_{item_id}',
        'nds': 'nds_20',
        'count': item_count,
        'price': price,
        'type': item_type,
        'currency': items_currency,
        'agent_type': agent_type,
    }
    if item_mark:
        report['mark'] = item_mark
    if supplier_inn:
        report['supplier_inn'] = supplier_inn
    return report


def _build_items(items_count: int = 2, **kwargs):
    items = []
    for i in range(items_count):
        items.append(_build_item(item_id=str(i + 1), **kwargs))
    return items


def _build_create_payment_request(
        *,
        virtual_client_id: str,
        idempotency_token: str = '456',
        corp_client_id: str = DEFAULT_CORP_CLIENT_ID,
        email: str = 'nsofya@yandex-team.ru_id',
        phone: str = 'ooo_id',
        supplier_inn: str,
        **kwargs,
):
    return {
        'details': {
            'external_id': idempotency_token,
            'client_id': {'type': 'corp_client_id', 'id': corp_client_id},
            'virtual_client_id': virtual_client_id,
            'customer': {'email_pd_id': email, 'phone_pd_id': phone},
            'geo_data': {'zone_id': 'moscow'},
        },
        'items': _build_items(supplier_inn=supplier_inn, **kwargs),
    }


@pytest.fixture(name='create_payment')
async def _create_payment(taxi_cargo_payments, default_corp_client_id):
    async def wrapper(
            status_code=200,
            *,
            corp_client_id: str = None,
            supplier_inn: str = '9705114405',
            **kwargs,
    ):
        if corp_client_id is None:
            corp_client_id = default_corp_client_id
        response = await taxi_cargo_payments.post(
            'v1/payment/create',
            json=_build_create_payment_request(
                corp_client_id=corp_client_id,
                supplier_inn=supplier_inn,
                **kwargs,
            ),
        )
        assert response.status_code == status_code
        return response.json()

    return wrapper


@pytest.fixture(name='validate_payment')
async def _validate_payment(taxi_cargo_payments, default_corp_client_id):
    async def wrapper(
            status_code=200,
            *,
            corp_client_id: str = None,
            supplier_inn: str = '9705114405',
            **kwargs,
    ):
        if corp_client_id is None:
            corp_client_id = default_corp_client_id
        response = await taxi_cargo_payments.post(
            'v1/payment/validate',
            json=_build_create_payment_request(
                corp_client_id=corp_client_id,
                supplier_inn=supplier_inn,
                **kwargs,
            ),
        )
        assert response.status_code == status_code

    return wrapper


@pytest.fixture(name='confirm_payment')
async def _confirm_payment(taxi_cargo_payments, driver_headers):
    async def wrapper(
            status_code=200, *, payment_id: str, revision: int, paymethod: str,
    ):
        response = await taxi_cargo_payments.post(
            'driver/v1/cargo-payments/v1/payment/confirm',
            json={
                'payment_id': payment_id,
                'revision': revision,
                'payment_method': paymethod,
            },
            headers=driver_headers,
        )
        assert response.status_code == status_code
        return response.json()

    return wrapper


@pytest.fixture(name='build_update_request')
def _build_update_request():
    def wrapper(*, payment_id: str, snapshot_token: str, **kwargs):
        return {
            'payment_id': payment_id,
            'items': _build_items(**kwargs),
            'idempotency_token': snapshot_token,
        }

    return wrapper


@pytest.fixture(name='update_items')
async def _update_items(taxi_cargo_payments, build_update_request):
    async def wrapper(status_code=200, **kwargs):
        response = await taxi_cargo_payments.post(
            'v1/payment/update', json=build_update_request(**kwargs),
        )
        assert response.status_code == status_code
        return response  # return revision ?

    return wrapper


@pytest.fixture(name='admin_update_items')
async def _admin_update_items(taxi_cargo_payments, build_update_request):
    async def wrapper(
            status_code=200,
            payment_id=None,
            snapshot_token=None,
            ticket='CARGODEV-6581',
            comment=None,
            **kwargs,
    ):
        json = build_update_request(
            payment_id=payment_id, snapshot_token=snapshot_token, **kwargs,
        )
        json['ticket'] = ticket
        json['comment'] = comment
        response = await taxi_cargo_payments.post(
            '/v1/admin/payment/update',
            json=json,
            headers={'X-Idempotency-Token': json['idempotency_token']},
        )
        assert response.status_code == status_code
        return response  # return revision ?

    return wrapper


@pytest.fixture(name='corp_cabinet_update_items')
async def _corp_cabinet_update_items(
        taxi_cargo_payments, default_corp_client_id, build_update_request,
):
    async def wrapper(status_code=200, **kwargs):
        response = await taxi_cargo_payments.post(
            '/api/b2b/cargo-payments/v1/payment/update',
            json=build_update_request(**kwargs),
            headers={'X-B2B-Client-Id': default_corp_client_id},
        )
        assert response.status_code == status_code
        return response  # return revision ?

    return wrapper


@pytest.fixture(name='get_payment')
async def _get_payment(taxi_cargo_payments):
    async def wrapper(payment_id: str):
        response = await taxi_cargo_payments.post(
            'v1/payment/info', params={'payment_id': payment_id},
        )

        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='driver_headers')
async def _driver_headers():
    def wrapper():
        return DEFAULT_DRIVER_HEADERS.copy()

    return wrapper()


@pytest.fixture(name='set_payment_status')
async def _set_payment_status(pgsql):
    """
        TODO use 2can callback instead of pgsql.
    """

    def wrapper(*, payment_id, status):
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            """
            UPDATE cargo_payments.payments
            SET
                status = %s,
                revision = revision + 1
            WHERE id = %s
            RETURNING id
        """,
            (status, payment_id),
        )
        assert cursor.fetchall()[0][0] == payment_id

    return wrapper


@pytest.fixture(name='payment_authorize_2can')
async def _payment_authorize_2can(taxi_cargo_payments, load_json_var):
    async def wrapper(*, payment_id):
        response = await taxi_cargo_payments.post(
            '2can/status',
            json=load_json_var(
                'pay_event.json', payment_id=payment_id, amount='40',
            ),
        )
        assert response.status_code == 200
        return response

    return wrapper


@pytest.fixture(name='register_agent')
async def _register_agent(
        get_agent_info, driver_headers, stq_runner, confirm_diagnostics,
):
    async def wrapper(
            *, park_id=None, driver_id=None, expect_fail=False, **kwargs,
    ):
        if park_id is None:
            park_id = driver_headers['X-YaTaxi-Park-Id']
        if driver_id is None:
            driver_id = driver_headers['X-YaTaxi-Driver-Profile-Id']

        agent = await get_agent_info(
            park_id=park_id, driver_id=driver_id, **kwargs,
        )
        await stq_runner.cargo_payments_register_agent.call(
            task_id='test',
            kwargs={
                'park_id': park_id,
                'driver_id': driver_id,
                'accept_language': 'en',
                'driver_ip': '12.34.56.78',
            },
            expect_fail=expect_fail,
        )
        return agent

    return wrapper


@pytest.fixture(name='get_agent_info')
async def _get_agent_info(taxi_cargo_payments, driver_headers):
    async def wrapper(*, park_id=None, driver_id=None):
        if park_id is not None:
            driver_headers['X-YaTaxi-Park-Id'] = park_id
        if driver_id is not None:
            driver_headers['X-YaTaxi-Driver-Profile-Id'] = driver_id

        response = await taxi_cargo_payments.post(
            '/driver/v1/cargo-payments/v1/payment/accounts',
            headers=driver_headers,
            json={'consumer': 'testsuite'},
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='delete_operations')
async def _delete_operations(pgsql):
    def wrapper():
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute('DELETE FROM cargo_payments.operations')

    return wrapper


@pytest.fixture(name='get_active_operations')
async def _get_active_operations(pgsql):
    def wrapper():
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'SELECT operation_meta, id FROM cargo_payments.operations',
        )
        result = []
        for row in cursor:
            obj = row[0]
            obj['operation_id'] = row[1]
            result.append(obj)
        return result

    return wrapper


@pytest.fixture(name='confirm_diagnostics')
async def _confirm_diagnostics(taxi_cargo_payments, driver_headers, stq):
    async def wrapper(
            *,
            park_id=None,
            driver_id=None,
            is_diagnostics_passed=True,
            idempotency_token=None,
            has_nfc=True,
            status_code=200,
            **kwargs,
    ):
        if park_id is not None:
            driver_headers['X-YaTaxi-Park-Id'] = park_id
        if driver_id is not None:
            driver_headers['X-YaTaxi-Driver-Profile-Id'] = driver_id
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())

        response = await taxi_cargo_payments.post(
            '/driver/v1/cargo-payments/v1/diagnostics/confirm',
            headers=driver_headers,
            json={
                'idempotency_token': idempotency_token,
                'consumer': 'testsuite',
                'flows': {
                    'ibox': {
                        'is_passed': is_diagnostics_passed,
                        'has_nfc': has_nfc,
                        'has_nfc_enabled': True,
                    },
                },
            },
        )
        assert response.status_code == status_code

    return wrapper


@pytest.fixture(name='cancel_payment')
async def _cancel_payment(taxi_cargo_payments):
    async def wrapper(*, status_code=200, payment_id: str):
        response = await taxi_cargo_payments.post(
            '/v1/payment/cancel', json={'payment_id': payment_id},
        )
        assert response.status_code == status_code

    return wrapper


@pytest.fixture(name='set_payment_performer')
async def _set_payment_performer(
        taxi_cargo_payments, get_agent_info, stq_runner,
):
    async def wrapper(
            *,
            payment_id,
            park_id,
            driver_id,
            performer_version=1,
            segment_revision=1,
    ):
        json = {
            'payment_id': payment_id,
            'performer': {'park_id': park_id, 'driver_id': driver_id},
            'performer_version': performer_version,  # deprecated
            'segment_revision': segment_revision,
        }
        response = await taxi_cargo_payments.post(
            '/v1/payment/set-performer', json=json,
        )
        assert response.status_code == 200

        agent = await get_agent_info(park_id=park_id, driver_id=driver_id)
        # set up agent's tid
        await stq_runner.cargo_payments_update_agent_tid.call(
            task_id='test', kwargs={'ibox_login': agent['ibox']['login']},
        )

    return wrapper


@dataclasses.dataclass
class Performer:
    park_id: str
    driver_id: str
    performer_version: int
    is_payment_finished: bool
    segment_revision: tp.Optional[int]


@pytest.fixture(name='get_payment_performer')
async def _get_payment_performer(pgsql):
    def wrapper(payment_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            """
            SELECT
                p.park_id, p.driver_id,
                p.performer_version, p.is_payment_finished, p.segment_revision
            FROM cargo_payments.payment_performers p
            WHERE p.payment_id = %s
            """,
            (payment_id,),
        )
        return Performer(**dict(cursor.fetchone()))

    return wrapper


@pytest.fixture(name='setup_virtual_clients_settings')
async def _setup_virtual_clients_settings(taxi_cargo_payments, taxi_config):
    async def wrapper(
            available_payment_methods=None,
            cashier_kind=None,
            cashier_fullname=None,
            **kwargs,
    ):
        config = {
            '07e65253-1b77-4872-b994-fd8d13c2294f': {
                'admin_account': 'default@yandex',
                'clients_settings': {
                    '651efc77d91b462f86a47eef39795b03': {
                        'provider_name': 'yandex_virtual_client',
                    },
                },
                'comment': 'yandex_virtual_client',
                'fiscalization_account': 'default@yandex',
                'provider_name': 'yandex_virtual_client_default',
            },
            'f7cc2fd6-78e3-4e97-9e64-9143d7613d45': {
                'admin_account': 'default@eats',
                'clients_settings': {
                    '651efc77d91b462f86a47eef39795b03': {
                        'provider_name': 'eats_virtual_client',
                    },
                },
                'comment': 'eats_virtual_client',
                'fiscalization_account': 'default@eats',
                'provider_name': 'eats_virtual_client_default',
            },
        }
        for settings in config.values():
            if available_payment_methods is not None:
                settings[
                    'available_payment_methods'
                ] = available_payment_methods
            if cashier_kind is not None:
                settings['cashier'] = {'kind': cashier_kind}
                if cashier_fullname is not None:
                    settings['cashier']['fullname'] = cashier_fullname

        taxi_config.set_values(dict(CARGO_PAYMENTS_VIRTUAL_CLIENTS_MAP=config))
        await taxi_cargo_payments.invalidate_caches()

    return wrapper


@pytest.fixture(name='get_performer_tid_info')
async def _get_performer_tid_info(pgsql):
    def wrapper(park_id, driver_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            """
            SELECT
                tid,
                last_order_ts
            FROM cargo_payments.performer_agents
            WHERE park_id=%s AND driver_id=%s
            """,
            (park_id, driver_id),
        )

        result = [dict(row) for row in cursor]
        if not result:
            return None
        return result[0]

    return wrapper


@pytest.fixture(name='register_billing_tasks')
async def _register_billing_tasks(taxi_cargo_payments, default_corp_client_id):
    async def wrapper():
        response = await taxi_cargo_payments.post(
            'v1/billing/register_task',
            json={
                'tasks': [
                    {
                        'order_id': '12445',
                        'meta_order_id': '12445',
                        'corp_client_id': default_corp_client_id,
                        'tariff_class': 'ndd',
                        'type': 'user_on_delivery_payment',
                        'amount': '60.80',
                        'currency': 'RUB',
                        'refund': False,
                        'payment_instant': '2021-02-12T15:11:48.6100000+03:00',
                        'order_instant': '2021-02-12T16:11:48.6100000+03:00',
                    },
                    {
                        'order_id': '12445',
                        'meta_order_id': '12445',
                        'corp_client_id': default_corp_client_id,
                        'tariff_class': 'ndd',
                        'geo_data': {'zone_id': 'moscow'},
                        'type': 'b2b_user_on_delivery_payment_fee',
                        'amount': '6.08',
                        'currency': 'RUB',
                        'refund': False,
                        'payment_instant': '2021-02-12T15:11:48.6100000+03:00',
                        'order_instant': '2021-02-12T16:11:48.6100000+03:00',
                    },
                ],
            },
        )
        assert response.status_code == 200
        return response

    return wrapper


@pytest.fixture(name='print_pg_table')
async def _print_pg_table(pgsql):
    def wrapper(table_name):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(f'select * from cargo_payments.{table_name}')
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            print(f'{table_name} row: {dict(row)}')

    return wrapper


@pytest.fixture(name='approve_billing_tasks')
async def _approve_billing_tasks(pgsql, mocked_time):
    def wrapper(*, approve_instant=None):
        if approve_instant is None:
            now = mocked_time.now() if mocked_time else datetime.datetime.now()
            approve_instant = now - datetime.timedelta(hours=24)

        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            """
            UPDATE cargo_payments.billing_tasks_history
            SET
                approve_instant = %s::TIMESTAMP AT TIME ZONE 'UTC',
                billing_doc_id=history_event_id::TEXT
            """,
            (str(approve_instant),),
        )

    return wrapper


@pytest.fixture(name='check_unprocessed_docs')
async def _check_unprocessed_docs(taxi_cargo_payments):
    async def wrapper(expected, full=False):
        response = await taxi_cargo_payments.post(
            'v1/billing/unprocessed-docs', json={'limit': 1000},
        )

        assert response.status_code == 200

        docs = response.json()['docs']
        if full:
            actual = sorted(docs, key=lambda x: x['billing_doc_id'])
        else:
            actual = sorted([d['billing_doc_id'] for d in docs])

        assert actual == expected

    return wrapper


@pytest.fixture(name='get_billing_report')
async def _get_billing_report(taxi_cargo_payments, default_corp_client_id):
    async def wrapper(*, order_id='12445', payment_order_number=None):
        request = {}
        if order_id is not None:
            request['order_id'] = order_id
        if payment_order_number is not None:
            request['payment_order_number'] = payment_order_number
        response = await taxi_cargo_payments.post(
            'api/b2b/cargo-payments/v1/billing/report',
            json=request,
            headers={'X-B2B-Client-Id': default_corp_client_id},
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='process_operation')
async def _process_operation(stq_runner):
    async def wrapper(operation_id):
        return await stq_runner.cargo_payments_process_operation.call(
            task_id='test', kwargs={'operation_id': operation_id},
        )

    return wrapper


@pytest.fixture(name='payment_success')
async def _payment_success(taxi_cargo_payments, driver_headers):
    async def wrapper(payment_id, transaction_id, *, expected_code=200):
        response = await taxi_cargo_payments.post(
            'driver/v1/cargo-payments/v1/payment/success',
            json={'payment_id': payment_id, 'transaction_id': transaction_id},
            headers=driver_headers,
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='get_payment_state')
async def _get_payment_state(taxi_cargo_payments, driver_headers):
    async def wrapper(payment_id, *, expected_code=200):
        response = await taxi_cargo_payments.post(
            'driver/v1/cargo-payments/v1/payment/state',
            json={'payment_id': payment_id},
            headers=driver_headers,
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='payment_failure')
async def _payment_failure(taxi_cargo_payments, driver_headers):
    async def wrapper(payment_id, payment_revision, *, expected_code=200):
        response = await taxi_cargo_payments.post(
            'driver/v1/cargo-payments/v1/payment/failure',
            json={
                'payment_id': payment_id,
                'payment_revision': payment_revision,
            },
            headers=driver_headers,
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='autorun_stq')
async def _autorun_stq(stq, stq_runner):
    async def wrapper(stq_name):
        for _ in range(getattr(stq, stq_name).times_called):
            call = getattr(stq, stq_name).next_call()
            if call is None:
                return
            if not call['kwargs']:
                return  # fix for empty kwargs on reschedule

            await getattr(stq_runner, stq_name).call(
                task_id='test', kwargs=call['kwargs'],
            )

    return wrapper


@pytest.fixture(name='get_last_transaction')
async def _get_last_transaction(pgsql):
    def wrapper(payment_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            'SELECT history_event_id, transaction_id, payment_id '
            'FROM cargo_payments.transactions '
            'WHERE payment_id = %s '
            'ORDER BY history_timestamp DESC LIMIT 1',
            (payment_id,),
        )
        row = cursor.fetchone()
        if row is not None:
            row = dict(row)
        return row

    return wrapper


@pytest.fixture(name='get_payment_amount')
async def _get_payment_amount(get_payment):
    async def wrapper(payment_id):
        payment = await get_payment(payment_id)
        amount = 0
        for item in payment['items']:
            amount += float(item['price']) * item['count']
        return amount

    return wrapper

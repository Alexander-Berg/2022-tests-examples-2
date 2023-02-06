import datetime
import json
import uuid

import jwt
import pytest

from tests_bank_h2h import common

HANDLE_URL = '/h2h/v1/order_statement'
MOCK_NOW = '2021-09-28T19:31:00.100+00:00'


def get_order_statement_body():
    return {
        'account': '40702810500000000001',
        'date_from': '2021-01-01',
        'date_to': '2021-01-31',
        'wait_end_of_day': False,
        'need_archive': False,
    }


def get_other_order_statement_body():
    data = get_order_statement_body()
    data['wait_end_of_day'] = True
    data['need_archive'] = True
    return data


def default_stq_kwargs(statement_id, sender=common.SENDER, eta=None):
    data = {'statement_id': statement_id, 'sender': sender}
    if eta is not None:
        data['eta'] = eta
    return data


GOOD_TOKEN = jwt.encode(
    get_order_statement_body(),
    common.JWT_VERIFIER_PRIVATE_KEY_ES256,
    algorithm='ES256',
)


@pytest.mark.now('2021-01-31T23:59:59.999999+00:00')
@pytest.mark.config(
    BANK_H2H_TIME_TO_SEND_ACC_STATEMENT_REQUEST={'hours': 0, 'minutes': 5},
)
@pytest.mark.parametrize(
    'jwtoken',
    [
        pytest.param(GOOD_TOKEN, id='ok'),
        pytest.param(
            jwt.encode(
                get_other_order_statement_body(),
                common.JWT_VERIFIER_PRIVATE_KEY_ES256,
                algorithm='ES256',
            ),
            id='other_body',
        ),
    ],
)
async def test_handle_ok(taxi_bank_h2h, pgsql, stq, jwtoken):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': jwtoken},
    )
    assert response.status_code == 200
    response = response.json()
    statement_id = response['response']['statement_id']
    assert jwt.decode(
        response['response_jwt'],
        common.JWT_SIGNER_PUBLIC_KEY_RS256,
        algorithms=['RS256'],
    ) == {'statement_id': statement_id}
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.idempotency_token == common.IDEMPOTENCY_TOKEN
    assert statement_pg.status == 'NEW'
    assert statement_pg.sender == common.SENDER
    assert statement_pg.account == '40702810500000000001'
    assert statement_pg.date_from == datetime.date(2021, 1, 1)
    assert statement_pg.date_to == datetime.date(2021, 1, 31)
    assert statement_pg.wait_end_of_day is (jwtoken != GOOD_TOKEN)
    assert statement_pg.need_archive is (jwtoken != GOOD_TOKEN)
    assert statement_pg.statement_jwt == jwtoken
    assert statement_pg.file_name is None
    assert statement_pg.file_name_id is None
    assert statement_pg.error_response is None

    assert stq.bank_h2h_acc_statement_request.times_called == 1
    stq_call = stq.bank_h2h_acc_statement_request.next_call()
    assert stq_call['id'] == 'acc_statement_request_' + statement_id
    if jwtoken != GOOD_TOKEN:
        assert stq_call['eta'].isoformat() == '2021-02-01T00:04:59.999999'
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'statement_id': statement_id,
        'sender': common.SENDER,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BANK_H2H_TIME_TO_SEND_ACC_STATEMENT_REQUEST={'hours': 0, 'minutes': 5},
)
async def test_handle_ok_no_time_offset(taxi_bank_h2h, pgsql, stq):
    token = jwt.encode(
        get_other_order_statement_body(),
        common.JWT_VERIFIER_PRIVATE_KEY_ES256,
        algorithm='ES256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': token},
    )
    assert response.status_code == 200
    response = response.json()
    statement_id = response['response']['statement_id']
    assert jwt.decode(
        response['response_jwt'],
        common.JWT_SIGNER_PUBLIC_KEY_RS256,
        algorithms=['RS256'],
    ) == {'statement_id': statement_id}
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.idempotency_token == common.IDEMPOTENCY_TOKEN
    assert statement_pg.status == 'NEW'
    assert statement_pg.sender == common.SENDER
    assert statement_pg.account == '40702810500000000001'
    assert statement_pg.date_from == datetime.date(2021, 1, 1)
    assert statement_pg.date_to == datetime.date(2021, 1, 31)
    assert statement_pg.wait_end_of_day is True
    assert statement_pg.need_archive is True
    assert statement_pg.statement_jwt == token
    assert statement_pg.file_name is None
    assert statement_pg.file_name_id is None
    assert statement_pg.error_response is None

    assert stq.bank_h2h_acc_statement_request.times_called == 1
    stq_call = stq.bank_h2h_acc_statement_request.next_call()
    assert stq_call['id'] == 'acc_statement_request_' + statement_id
    assert stq_call['eta'].isoformat() == '2021-09-28T19:31:00.100000'
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'statement_id': statement_id,
        'sender': common.SENDER,
    }


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_200(taxi_bank_h2h, pgsql, stq):
    body = get_order_statement_body()
    pg_statement_id = common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        sender=common.SENDER,
        account=body['account'],
        date_from=datetime.date.fromisoformat(body['date_from']),
        date_to=datetime.date.fromisoformat(body['date_to']),
        wait_end_of_day=body['wait_end_of_day'],
        need_archive=body['need_archive'],
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200
    assert pg_statement_id == response.json()['response']['statement_id']

    assert stq.bank_h2h_acc_statement_request.times_called == 1
    stq_call = stq.bank_h2h_acc_statement_request.next_call()
    assert stq_call['id'] == 'acc_statement_request_' + pg_statement_id
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'statement_id': pg_statement_id,
        'sender': common.SENDER,
    }


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_409(taxi_bank_h2h, pgsql, stq):
    body = get_order_statement_body()
    common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        sender=common.SENDER,
        account=(body['account'] + '0'),
        date_from=datetime.date.fromisoformat(body['date_from']),
        date_to=datetime.date.fromisoformat(body['date_to']),
        wait_end_of_day=body['wait_end_of_day'],
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 409
    assert stq.bank_h2h_acc_statement_request.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_conflict(
        taxi_bank_h2h, testpoint, pgsql, stq,
):
    @testpoint('create_other_statement')
    def _code_generated(data):
        body = get_order_statement_body()
        common.insert_statement(
            pgsql,
            common.IDEMPOTENCY_TOKEN,
            sender=common.SENDER,
            account=(body['account'] + '0'),
            date_from=datetime.date.fromisoformat(body['date_from']),
            date_to=datetime.date.fromisoformat(body['date_to']),
            wait_end_of_day=body['wait_end_of_day'],
        )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 500
    assert stq.bank_h2h_acc_statement_request.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'type_of_broke', ['type_mismatch', 'no_required_field', 'invalid_format'],
)
async def test_handle_broken_body(taxi_bank_h2h, stq, type_of_broke):
    body = get_order_statement_body()
    if type_of_broke == 'type_mismatch':
        body['account'] = 1234
    elif type_of_broke == 'no_required_field':
        body.pop('date_to')
    elif type_of_broke == 'invalid_format':
        body['date_from'] = '01/01/2000'
    token = jwt.encode(
        body, common.JWT_VERIFIER_PRIVATE_KEY_ES256, algorithm='ES256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': token},
    )
    assert response.status_code == 400
    assert stq.bank_h2h_acc_statement_request.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_no_public_key(taxi_bank_h2h, stq):
    token = jwt.encode(
        get_order_statement_body(),
        common.JWT_VERIFIER_PRIVATE_KEY_RS256,
        algorithm='RS256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': token},
    )
    assert response.status_code == 500
    assert stq.bank_h2h_acc_statement_request.times_called == 0


# keys up to 2021-09-29
@pytest.mark.now('2021-09-28T23:59:59.999+00:00')
async def test_handle_all_public_key_expired(taxi_bank_h2h, stq, mocked_time):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200
    assert stq.bank_h2h_acc_statement_request.times_called == 1

    mocked_time.sleep(1)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400
    assert stq.bank_h2h_acc_statement_request.times_called == 1


@pytest.mark.now(MOCK_NOW)
async def test_handle_unknown_sender(taxi_bank_h2h, stq):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(
            sender='YANDEX_BANK', idempotency_token=common.IDEMPOTENCY_TOKEN,
        ),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400
    assert stq.bank_h2h_acc_statement_request.times_called == 0


async def test_stq_ok(taxi_bank_h2h, testpoint, pgsql, stq_runner):
    body = get_order_statement_body()
    statement_id = common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        sender=common.SENDER,
        account=body['account'],
        date_from=datetime.date.fromisoformat(body['date_from']),
        date_to=datetime.date.fromisoformat(body['date_to']),
        wait_end_of_day=body['wait_end_of_day'],
        need_archive=body['need_archive'],
    )

    @testpoint('tp_kafka-producer-acc-statement-req')
    def acc_publish(data):
        assert data['key'] == statement_id
        assert json.loads(data['message']) == {
            'request_id': statement_id,
            'account': body['account'],
            'date_begin': body['date_from'],
            'date_end': body['date_to'],
        }

    await stq_runner.bank_h2h_acc_statement_request.call(
        task_id='acc_statement_request_' + statement_id,
        kwargs=default_stq_kwargs(statement_id),
        expect_fail=False,
    )
    await acc_publish.wait_call()
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.status == 'PROCESSING'  # status


async def test_stq_not_in_new_status(
        taxi_bank_h2h, testpoint, pgsql, stq_runner,
):
    @testpoint('tp_kafka-producer-acc-statement-req')
    def acc_publish(data):
        assert len(data) == 1

    body = get_order_statement_body()
    statement_id = common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        status='PROCESSING',
        sender=common.SENDER,
        account=body['account'],
        date_from=datetime.date.fromisoformat(body['date_from']),
        date_to=datetime.date.fromisoformat(body['date_to']),
        wait_end_of_day=body['wait_end_of_day'],
        need_archive=body['need_archive'],
    )
    await stq_runner.bank_h2h_acc_statement_request.call(
        task_id='acc_statement_request_' + statement_id,
        kwargs=default_stq_kwargs(statement_id),
        expect_fail=False,
    )
    assert not acc_publish.has_calls
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.status == 'PROCESSING'  # status


def get_message_ok(request_id):
    return json.dumps(
        {
            'request_id': request_id,
            'status_code': 0,
            'status_message': 'Выписка сформирована',
            'bucket': 'my_bucket',
            'file_name': 'file.dat',
        },
    )


async def test_kafka_ok(taxi_bank_h2h, testpoint, pgsql):
    await taxi_bank_h2h.enable_testpoints()

    statement_id = common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        status='PROCESSING',
        sender=common.SENDER,
        account='40702810500000000001',
    )

    @testpoint('tp_kafka-consumer-acc-statement-res')
    def received_messages_func(data):
        pass

    response = await taxi_bank_h2h.post(
        'tests/kafka/messages/kafka-consumer-acc-statement-res',
        data=json.dumps(
            {
                'key': 'key',
                'data': get_message_ok(statement_id),
                'topic': 'acc_statement_answ',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func.wait_call()
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.status == 'SUCCESS'
    assert statement_pg.file_name == 'file.dat'
    assert statement_pg.file_name_id is not None
    assert statement_pg.error_response is None


def get_message_fail(request_id):
    return json.dumps(
        {
            'request_id': request_id,
            'status_code': 3,
            'status_message': 'Счёт не найден',
        },
    )


async def test_kafka_fail(taxi_bank_h2h, testpoint, pgsql):
    await taxi_bank_h2h.enable_testpoints()

    statement_id = common.insert_statement(
        pgsql,
        common.IDEMPOTENCY_TOKEN,
        status='PROCESSING',
        sender=common.SENDER,
        account='40702810500000000001',
    )

    @testpoint('tp_kafka-consumer-acc-statement-res')
    def received_messages_func(data):
        pass

    response = await taxi_bank_h2h.post(
        'tests/kafka/messages/kafka-consumer-acc-statement-res',
        data=json.dumps(
            {
                'key': 'key',
                'data': get_message_fail(statement_id),
                'topic': 'acc_statement_answ',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func.wait_call()
    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg.status == 'FAIL'
    assert statement_pg.file_name is None
    assert statement_pg.file_name_id is None
    assert statement_pg.error_response == {
        'code': 'NotFound',
        'message': 'Счёт не найден',
    }


async def test_kafka_not_found(taxi_bank_h2h, testpoint, pgsql):
    await taxi_bank_h2h.enable_testpoints()
    statement_id = str(uuid.uuid4())

    @testpoint('tp_error_kafka-consumer-acc-statement-res')
    def received_messages_func_error(data):
        assert data == {'error': 'Can not update statement status'}

    response = await taxi_bank_h2h.post(
        'tests/kafka/messages/kafka-consumer-acc-statement-res',
        data=json.dumps(
            {
                'key': 'key',
                'data': get_message_fail(statement_id),
                'topic': 'acc_statement_answ',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func_error.wait_call()

    statement_pg = common.select_statement(pgsql, statement_id)
    assert statement_pg is None


async def test_kafka_not_uuid(taxi_bank_h2h, testpoint):
    await taxi_bank_h2h.enable_testpoints()
    statement_id = '1234'

    @testpoint('tp_error_kafka-consumer-acc-statement-res')
    def received_messages_func_error(data):
        assert data == {'error': 'request_id is not in uuid format'}

    response = await taxi_bank_h2h.post(
        'tests/kafka/messages/kafka-consumer-acc-statement-res',
        data=json.dumps(
            {
                'key': 'key',
                'data': get_message_fail(statement_id),
                'topic': 'acc_statement_answ',
            },
        ),
    )
    assert response.status_code == 200
    await received_messages_func_error.wait_call()


@pytest.mark.config(BANK_H2H_CLIENT_TO_ACCOUNT_NUMBERS={})
@pytest.mark.now(MOCK_NOW)
async def test_validate_sender_not_in_config(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400


@pytest.mark.config(
    BANK_H2H_CLIENT_TO_ACCOUNT_NUMBERS={'YANDEX_PRO': ['invalid']},
)
@pytest.mark.now(MOCK_NOW)
async def test_validate_account_not_in_sender(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(idempotency_token=common.IDEMPOTENCY_TOKEN),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400

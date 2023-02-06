# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_communications_plugins.generated_tests import *

import tests_bank_communications.utils as utils

import typing as tp
import pytest


def get_headers(
        idempotency_token: str = '67754336-d4d1-43c1-aadb-cabd06674ea6',
):
    return {
        'X-Idempotency-Token': idempotency_token,
        'X-Request-Application': 'platform=bad_platform,app_name=sdk_example',
    }


def get_query_params(
        buid=None,
        communication_type: str = 'empty_yasms',
        template_parameters: tp.Optional[tp.Dict[str, str]] = None,
        locale: str = 'ru',
        phone=None,
        device_id: str = '228',
        user_agent: str = 'Barry',
        client_ip: str = '1337',
):
    if template_parameters is None:
        template_parameters = {'text': '{text}'}
    params = {
        'type': communication_type,
        'template_parameters': template_parameters,
        'locale': locale,
        'antifraud_info': {
            'device_id': device_id,
            'user_agent': user_agent,
            'client_ip': client_ip,
        },
    }
    if buid is not None:
        params['buid'] = buid
    if phone is not None:
        params['phone'] = phone
    return params


def get_stq_args(params: tp.Dict[tp.Any, tp.Any], pgsql):
    return {'yasms_id': utils.get_yasms_id(pgsql), 'buid': params.get('buid')}


@pytest.mark.parametrize(
    'target',
    [
        {'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'},
        {'phone': '+72223334445'},
    ],
)
async def test_audit(
        taxi_bank_communications,
        bank_service,
        pgsql,
        stq_runner,
        testpoint,
        target,
):
    headers = get_headers()
    params = get_query_params(**target)

    @testpoint('tp_kafka-producer-audit')
    def audit_publish(data):
        assert len(data) == 1

    await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )

    # wait audit publishing about request to bank-communications
    await audit_publish.wait_call()

    # wait audit publishing about response from bank-communications
    await audit_publish.wait_call()


@pytest.mark.parametrize(
    'target,message_sent_id',
    [
        ({'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'}, '127000000003456'),
        ({'phone': '+72223334445'}, '127000000004445'),
    ],
)
async def test_yasms_was_send_and_same_idempotency_token(
        taxi_bank_communications,
        bank_service,
        pgsql,
        stq_runner,
        target,
        message_sent_id,
):
    headers = get_headers()
    params = get_query_params(**target)

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.times_called == (
        0 if 'phone' in target else 1
    )
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params.get('buid'),
        params.get('phone', '+71234567890'),
        headers,
        'SENT',
        message_sent_id=message_sent_id,
        locale='ru',
        tanker_key='text',
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)
    assert len(records_communications) == 1 and len(records_yasms) == 1

    if 'buid' in target:
        # TODO: this is not right, must reject different request for same idempotency token
        params['buid'] = '77754336-d4d1-43c1-aadb-cabd06674ea6'

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    assert bank_service.phone_number_handler.times_called == (
        0 if 'phone' in target else 1
    )
    assert bank_service.send_yasms_handler.times_called == 1


async def test_yasms_was_send_second_time(
        taxi_bank_communications, bank_service, pgsql, stq_runner,
):
    headers = get_headers()

    params = get_query_params(
        buid='22254336-d4d1-43c1-aadb-cabd06674ea6',  # for_second_time
        template_parameters={'code': '1234', 'text': '{text}'},
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=True,
    )
    assert response.status_code == 200

    assert bank_service.phone_number_handler.has_calls
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params['buid'],
        '+71112223344',
        headers,
        'NOT_SENT',
        error_code='INTERROR',
    )

    headers['X-Idempotency-Token'] = '0000'

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)
    assert len(records_communications) == 2
    assert len(records_yasms) == 2

    assert (
        records_communications[0]['bank_uid'] == params['buid']
        and records_yasms[1]['communication_id']
        == records_communications[0]['communication_id']
        and records_yasms[0]['communication_id']
        == records_communications[1]['communication_id']
    )


@pytest.mark.parametrize(
    'target,message_sent_id',
    [
        ({'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'}, '127000000003456'),
        ({'phone': '+72223334445'}, '127000000004445'),
    ],
)
async def test_yasms_was_send_many_parameters(
        taxi_bank_communications,
        bank_service,
        pgsql,
        stq_runner,
        target,
        message_sent_id,
):
    headers = get_headers()

    params = get_query_params(
        communication_type='code_yasms',
        template_parameters={
            'text': 'You\'ve got sms from bank!',
            'code': '1234',
            'name': 'Karlson',
        },
        locale='en',
        **target,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls == (
        'phone' not in target
    )
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params.get('buid'),
        params.get('phone', '+71234567890'),
        headers,
        'SENT',
        message_sent_id=message_sent_id,
        locale='en',
        tanker_key='code',
    )


async def test_bad_buid(
        taxi_bank_communications, bank_service, pgsql, stq_runner,
):
    headers = get_headers()
    params = get_query_params(
        buid='00000000-d4d1-43c1-aadb-cabd06674ea6',
    )  # bad_buid

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls
    assert not bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(pgsql, params['buid'], None, headers, 'NO_PHONE')


@pytest.mark.parametrize(
    'target',
    [
        {'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'},
        {'phone': '+72223334445'},
    ],
)
async def test_bad_communications_type(
        taxi_bank_communications, bank_service, pgsql, target,
):
    headers = get_headers()

    params = get_query_params(
        communication_type='bad_yasms', template_parameters={}, **target,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 400

    assert not bank_service.phone_number_handler.has_calls
    assert not bank_service.send_yasms_handler.has_calls

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)
    assert not records_communications
    assert not records_yasms


async def test_bad_phone_number_for_yasms(
        taxi_bank_communications, bank_service, pgsql, stq_runner,
):
    headers = get_headers()

    params = get_query_params(
        buid='40054336-d4d1-43c1-aadb-cabd06674ea6',
    )  # wrong_phone

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=True,
    )

    assert bank_service.phone_number_handler.has_calls
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql, params['buid'], '+700000000', headers, 'NOT_SENT', 'BADPHONE',
    )


async def test_phone_from_userinfo_second_try(
        taxi_bank_communications, bank_service, pgsql, stq_runner,
):
    headers = get_headers()
    params = get_query_params(
        buid='02054336-d4d1-43c1-aadb-cabd06674ea6',
    )  # second_attempt

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls
    assert not bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(pgsql, params['buid'], None, headers, 'NO_PHONE')

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.times_called == 2
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params['buid'],
        '+71234567890',
        headers,
        'SENT',
        message_sent_id='127000000003456',
    )


async def test_invalid_phone_number_from_userinfo(
        taxi_bank_communications, bank_service, pgsql, stq_runner,
):
    headers = get_headers()
    params = get_query_params(
        buid='50054336-d4d1-43c1-aadb-cabd06674ea6',
    )  # invalid_userinfo_phone

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls
    assert not bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql, params.get('buid'), params.get('phone'), headers, 'NO_PHONE',
    )

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.times_called == 2
    assert not bank_service.send_yasms_handler.has_calls

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)

    assert len(records_communications) == 1
    assert len(records_yasms) == 1

    assert (
        records_communications[0]['bank_uid'] == params['buid']
        and records_yasms[0]['communication_id']
        == records_communications[0]['communication_id']
    )


@pytest.mark.parametrize(
    'target,message_sent_id',
    [
        ({'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'}, '127000000003456'),
        ({'phone': '+72223334445'}, '127000000004445'),
    ],
)
async def test_no_tanker_parameters(
        taxi_bank_communications,
        bank_service,
        pgsql,
        stq_runner,
        target,
        message_sent_id,
):
    headers = get_headers()
    params = get_query_params(
        communication_type='empty_yasms', template_parameters={}, **target,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls == (
        'phone' not in target
    )
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params.get('buid'),
        params.get('phone', '+71234567890'),
        headers,
        'SENT',
        message_sent_id=message_sent_id,
    )


@pytest.mark.parametrize(
    'target',
    [
        {'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'},
        {'phone': '+72223334445'},
    ],
)
async def test_bad_tanker_key(
        taxi_bank_communications, bank_service, pgsql, target,
):
    headers = get_headers()
    params = get_query_params(
        communication_type='bad_tanker_yasms',
        template_parameters={},
        **target,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }

    assert not bank_service.phone_number_handler.has_calls
    assert not bank_service.send_yasms_handler.has_calls

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)
    assert records_communications[0]['bank_uid'] == params.get('buid')
    assert (
        records_communications[0]['idempotency_token']
        == headers['X-Idempotency-Token']
    )
    assert not records_yasms


@pytest.mark.parametrize(
    'locale, tanker_key, response_text, name',
    [
        ('ru', 'code_yasms', 'Привет {name}, твой код {code}!', 'Иван'),
        ('en', 'code_yasms', 'Hi {name}, your code {code}!', 'Ivan'),
        (
            'ru',
            'code_yasms_sec',
            'Привет {{name}}, твой код {{code}}!',
            'Иван',
        ),
        ('en', 'code_yasms_sec', 'Hi {{name}}, your code {{code}}!', 'Ivan'),
        ('unknown', 'code_yasms', 'Привет {name}, твой код {code}!', 'Иван'),
    ],
)
@pytest.mark.parametrize(
    'target,message_sent_id,hash',
    [
        (
            {'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6'},
            '127000000003456',
            ' ntZSCTJF0rP',
        ),
        ({'phone': '+72223334445'}, '127000000004445', ''),
    ],
)
async def test_different_languages(
        taxi_bank_communications,
        bank_service,
        pgsql,
        locale,
        response_text,
        name,
        target,
        message_sent_id,
        hash,
        tanker_key,
        stq_runner,
):
    response_text += hash
    headers = get_headers()

    params = get_query_params(
        communication_type=tanker_key,
        template_parameters={'code': '1234', 'name': name},
        locale=locale,
        **target,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls == (
        'phone' not in target
    )
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        params.get('buid'),
        params.get('phone', '+71234567890'),
        headers,
        'SENT',
        message_sent_id=message_sent_id,
        locale=locale,
        tanker_key='code' if tanker_key == 'code_yasms' else 'code_sec',
    )


@pytest.mark.parametrize(
    'locale, response_text, name, buid, phone',
    [
        (
            'ru',
            'Привет {name}, твой код {code}!',
            'Иван',
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2',
            '+71112223355',
        ),
        (
            'ru',
            'Привет {name}, твой код {code}!',
            'Иван',
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc4',
            '+71112223366',
        ),
    ],
)
async def test_problem_additional_hash(
        taxi_bank_communications,
        bank_service,
        buid,
        phone,
        pgsql,
        locale,
        response_text,
        name,
        stq_runner,
):
    headers = {'X-Idempotency-Token': buid}

    params = get_query_params(
        buid, 'code_yasms', {'code': '1234', 'name': name}, locale,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls
    assert bank_service.send_yasms_handler.has_calls

    utils.check_pg_records(
        pgsql,
        buid,
        phone,
        headers,
        'SENT',
        message_sent_id='127000000003456',
        tanker_key='code',
    )


@pytest.mark.parametrize(
    'locale, response_text, name, buid, phone',
    [
        (
            'ru',
            'Привет {name}, твой код {code}!',
            'Иван',
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2',
            '+71112223355',
        ),
    ],
)
@pytest.mark.config(
    BANK_COMMUNICATIONS_YASMS_CONFIG={
        'route': 'test_bank',
        'sender': 'test_bank-communications',
        'allow_unused_text_params': False,
    },
)
async def test_not_all_params_false(
        taxi_bank_communications,
        bank_service,
        buid,
        phone,
        pgsql,
        locale,
        response_text,
        name,
        stq_runner,
):
    headers = {'X-Idempotency-Token': buid}
    params = get_query_params(
        buid, 'code_yasms', {'code': '1234', 'name': name}, locale,
    )

    bank_service.allow_unused_text_params = False
    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )

    assert bank_service.phone_number_handler.has_calls

    assert bank_service.send_yasms_handler.has_calls


@pytest.mark.parametrize(
    'locale, response_text, name, buid, phone',
    [
        (
            'ru',
            'Привет {name}, твой код {code}!',
            'Иван',
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2',
            '+71112223355',
        ),
    ],
)
@pytest.mark.config(
    BANK_COMMUNICATIONS_YASMS_CONFIG={
        'route': 'test_bank',
        'sender': 'test_bank-communications',
        'allow_unused_text_params': True,
    },
)
async def test_not_all_params_true(
        taxi_bank_communications,
        bank_service,
        buid,
        phone,
        pgsql,
        locale,
        response_text,
        name,
        stq_runner,
):
    headers = {'X-Idempotency-Token': buid}
    params = get_query_params(
        buid, 'code_yasms', {'code': '1234', 'name': name}, locale,
    )

    bank_service.allow_unused_text_params = True
    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )
    assert bank_service.phone_number_handler.has_calls
    assert bank_service.send_yasms_handler.has_calls


@pytest.mark.parametrize(
    'locale, response_text, name, buid, phone',
    [
        (
            'ru',
            'Привет {name}, твой код {code}!',
            'Иван',
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2',
            '+71112223355',
        ),
    ],
)
async def test_antifraud_info(
        taxi_bank_communications,
        bank_service,
        buid,
        phone,
        pgsql,
        locale,
        response_text,
        name,
        stq_runner,
):
    headers = {'X-Idempotency-Token': buid}
    device_id = '228'
    user_agent = 'Barry'
    client_ip = '1337'
    params = get_query_params(
        buid,
        'code_yasms',
        {'code': '1234', 'name': name},
        locale,
        device_id=device_id,
        user_agent=user_agent,
        client_ip=client_ip,
    )

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=params,
    )
    assert response.status_code == 200

    (_, records_yasms) = utils.get_bank_communications_records(pgsql)
    assert records_yasms[0]['device_id'] == device_id
    assert records_yasms[0]['user_agent'] == user_agent
    assert records_yasms[0]['client_ip'] == client_ip

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id', kwargs=get_stq_args(params, pgsql), expect_fail=False,
    )
    assert bank_service.phone_number_handler.has_calls
    assert bank_service.send_yasms_handler.has_calls

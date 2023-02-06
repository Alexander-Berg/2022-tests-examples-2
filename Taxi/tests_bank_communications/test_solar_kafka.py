# flake8: noqa
# pylint: disable=import-error,wildcard-import,redefined-outer-name
import json
import tests_bank_communications.utils as utils


def get_message(rule_id='OTP_config') -> str:
    return json.dumps(
        {
            'header': {
                'protocol': {'name': 'solar-ws', 'version': '2.0'},
                'messageId': '1d7f2a0c-31dd-498f-b01d-07c0605c1efd',
                'messageDate': '2021-12-28T15:41:03',
                'originator': {'system': 'SOLAR'},
            },
            'body': {
                'notification': {
                    'id': 100091,
                    'creationDate': '2021-12-28T15:41:03.476034',
                    'channel': 'SMS',
                    'receiver': '+71234567890',
                    'content': (
                        f'{{ "rule_id": "{rule_id}",'
                        '"otp_code": "123456",'
                        '"card_number" :"555400 **3956",'
                        '"payment_system": "Apple Pay",'
                        '"merchant": "магазин",'
                        '"amount": "9975",'
                        '"currency":"RUB"}'
                    ),
                },
            },
        },
    )


async def test_kafka_solar(
        taxi_bank_communications, bank_service, pgsql, stq_runner, testpoint,
):
    @testpoint('tp_kafka-consumer')
    def received_messages_func(data):
        pass

    await taxi_bank_communications.enable_testpoints()

    response = await taxi_bank_communications.post(
        'tests/kafka/messages/kafka-consumer',
        data=json.dumps(
            {
                'key': 'key',
                'data': get_message(),
                'topic': 'solar-out-cards-iss-notification',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func.wait_call()

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id',
        kwargs={'yasms_id': utils.get_yasms_id(pgsql), 'buid': None},
        expect_fail=False,
    )

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)

    assert len(records_communications) == 1 and len(records_yasms) == 1

    assert (
        records_communications[0]['idempotency_token']
        == '1d7f2a0c-31dd-498f-b01d-07c0605c1efd'
    )
    assert (
        records_yasms[0]['communication_id']
        == records_communications[0]['communication_id']
    )
    assert records_yasms[0]['status'] == 'SENT'
    assert records_yasms[0]['locale'] == 'ru'
    assert records_yasms[0]['tanker_key'] == 'otp_code'

    assert bank_service.phone_number_handler.times_called == 0
    assert bank_service.send_yasms_handler.times_called == 1


async def test_kafka_solar_error(
        taxi_bank_communications, bank_service, pgsql, stq_runner, testpoint,
):
    @testpoint('tp_error_kafka-consumer')
    def received_messages_func_error(data):
        print(data)
        assert data == {'error': 'Can\'t get requested type from config'}

    @testpoint('tp_kafka-consumer')
    def received_messages_func_success(data):
        pass

    await taxi_bank_communications.enable_testpoints()

    response = await taxi_bank_communications.post(
        'tests/kafka/messages/kafka-consumer',
        data=json.dumps(
            {
                'key': 'error',
                'data': get_message('unknown'),
                'topic': 'solar-out-cards-iss-notification',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func_error.wait_call()

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)

    assert not records_communications and not records_yasms

    assert bank_service.phone_number_handler.times_called == 0
    assert bank_service.send_yasms_handler.times_called == 0

    response = await taxi_bank_communications.post(
        'tests/kafka/messages/kafka-consumer',
        data=json.dumps(
            {
                'key': 'error',
                'data': get_message('TOKEN_ACTIVATE'),
                'topic': 'solar-out-cards-iss-notification',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func_success.wait_call()

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id',
        kwargs={'yasms_id': utils.get_yasms_id(pgsql), 'buid': None},
        expect_fail=False,
    )

    (
        records_communications,
        records_yasms,
    ) = utils.get_bank_communications_records(pgsql)

    assert len(records_communications) == 1 and len(records_yasms) == 1

    assert (
        records_communications[0]['idempotency_token']
        == '1d7f2a0c-31dd-498f-b01d-07c0605c1efd'
    )
    assert (
        records_yasms[0]['communication_id']
        == records_communications[0]['communication_id']
    )
    assert records_yasms[0]['status'] == 'SENT'
    assert records_yasms[0]['locale'] == 'ru'
    assert records_yasms[0]['tanker_key'] == 'token_activate'


async def test_merchant(
        taxi_bank_communications, bank_service, pgsql, stq_runner, testpoint,
):
    @testpoint('tp_kafka-consumer')
    def received_messages_func_merchant(data):
        pass

    response = await taxi_bank_communications.post(
        'tests/kafka/messages/kafka-consumer',
        data=json.dumps(
            {
                'key': 'merchant',
                'data': get_message('3DS_OTP'),
                'topic': 'solar-out-cards-iss-notification',
            },
        ),
    )
    assert response.status_code == 200

    await received_messages_func_merchant.wait_call()

    await stq_runner.bank_communications_yasms_send.call(
        task_id='id',
        kwargs={
            'yasms_id': utils.get_yasms_id(pgsql),
            'buid': None,
            'template_parameters': '{}',
        },
        expect_fail=False,
    )

    (_, records_yasms) = utils.get_bank_communications_records(pgsql)

    assert records_yasms[0]['locale'] == 'ru'
    assert records_yasms[0]['tanker_key'] == '3ds_otp'

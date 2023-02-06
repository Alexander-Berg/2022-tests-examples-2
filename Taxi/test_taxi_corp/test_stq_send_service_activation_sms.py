# pylint: disable=redefined-outer-name
import pytest

from taxi_corp.stq import send_service_activation_sms_module as stq_module

CORP_SERVICE_INTENTS = {
    'eats2': 'taxi_corp_eda_wallet_account_created_taxi',
    'taxi': 'taxi_corp_taxi_account_created',
    'tanker': 'taxi_corp_tanker_account_created',
}

CORP_SERVICE_SMS_TEXTS = {
    'eats2': 'some_eats2_translation',
    'taxi': 'some_taxi_translation',
    'tanker': 'some_tanker_translation',
}
CORP_SERVICE_CUSTOM_SMS_TEXTS = {
    'eats2': 'some_custom_eats2_translation',
    'taxi': 'some_custom_taxi_translation',
    'tanker': 'some_custom_tanker_translation',
}


@pytest.mark.parametrize(
    ['service'],
    [pytest.param('taxi'), pytest.param('eats2'), pytest.param('tanker')],
)
@pytest.mark.parametrize(
    ['user_ids', 'client_id', 'send_sms_calls', 'is_custom_sms'],
    [
        pytest.param(
            ['user_1', 'user_11'], 'client1', 2, False, id='success path',
        ),
        pytest.param(['user_2'], 'client1', 0, False, id='without limit'),
        pytest.param(['user_3'], 'client1', 0, False, id='with zero limit'),
        pytest.param(
            ['user_4'], 'client2', 0, False, id='inactive client service',
        ),
        pytest.param(['user_5'], 'client1', 0, False, id='sms already sent'),
        pytest.param(
            ['user_6'], 'client3', 1, True, id='custom sms for client',
        ),
        pytest.param(
            ['user_7'], 'client4', 0, False, id='client wo cabinet sms',
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {
            'activation_sms_tanker_keys': {
                'eats2': 'eats2_tanker_key',
                'tanker': 'tanker_tanker_key',
                'taxi': 'sms.create_user',
            },
        },
    },
    CORP_CLIENTS_CUSTOM_SERVICE_ACTIVATION_SMS={
        'client3': {
            'eats2': 'custom_sms.eats2',
            'taxi': 'custom_sms.taxi',
            'tanker': 'custom_sms.tanker',
        },
    },
    CORP_CLIENTS_WO_CABINET_SMS=['client4'],
)
@pytest.mark.translations(
    corp={
        'eats2_tanker_key': {'ru': CORP_SERVICE_SMS_TEXTS['eats2']},
        'tanker_tanker_key': {'ru': CORP_SERVICE_SMS_TEXTS['tanker']},
        'sms.create_user': {'ru': CORP_SERVICE_SMS_TEXTS['taxi']},
        'custom_sms.eats2': {'ru': CORP_SERVICE_CUSTOM_SMS_TEXTS['eats2']},
        'custom_sms.taxi': {'ru': CORP_SERVICE_CUSTOM_SMS_TEXTS['taxi']},
        'custom_sms.tanker': {'ru': CORP_SERVICE_CUSTOM_SMS_TEXTS['tanker']},
    },
)
async def test_whole_stq_task(
        taxi_corp_app_stq,
        patch,
        service,
        user_ids,
        client_id,
        send_sms_calls,
        is_custom_sms,
):
    locale = 'ru'

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert intent == CORP_SERVICE_INTENTS[service]
        if is_custom_sms:
            assert text == CORP_SERVICE_CUSTOM_SMS_TEXTS[service]
        else:
            assert text == CORP_SERVICE_SMS_TEXTS[service]

    await stq_module.send_service_activation_sms(
        taxi_corp_app_stq,
        client_id=client_id,
        user_ids=user_ids,
        service=service,
        locale=locale,
    )
    assert len(_send_message.calls) == send_sms_calls

    for user_id in user_ids:
        if user_id in ['user_1', 'user_11', 'user_5']:
            db_user = await taxi_corp_app_stq.db.corp_users.find_one(
                {'_id': user_id},
            )
            if service == 'taxi':
                assert not db_user['services']['taxi']['send_activation_sms']
            else:
                assert db_user['services'][service]['was_sms_sent']

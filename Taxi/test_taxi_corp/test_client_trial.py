# pylint:disable=redefined-outer-name
# pylint: disable=too-many-lines

import datetime
import uuid

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)

MOCK_ID = uuid.uuid4().hex
TEST_PHONE = '+79263452242'

CREATE_REQUEST_BODY = {
    'country': 'isr',
    'name': 'Konstantin Konstantinopolsky',
    'email': 'taxi_new@yandex.ru',
    'phone': TEST_PHONE,
    'company': 'Texas Trial Taxi',
    'city': 'MSK',
    'utm': {
        'utm_source': 'yandex',
        'utm_term': 'такси для бизнеса',
        'ya_some_metric': 'check',
        'ya_source': 'businessdelivery',
    },
    'contract_type': 'taxi',
}

REGISTER_AND_CREATE_REQUEST_BODY = {
    'country': 'isr',
    'name': 'Konstantin Konstantinopolsky',
    'email': 'Taxi_New@yandex.ru',
    'phone': TEST_PHONE,
    'company': 'Texas Trial Taxi',
    'city': 'MSK',
    'captcha_key': '01',
    'captcha_answer': '13',
    'utm': {
        'utm_source': 'yandex',
        'utm_term': 'такси для бизнеса',
        'ya_some_metric': 'check',
        'ya_source': 'businessdelivery',
    },
    'contract_type': 'taxi',
}


@pytest.mark.now(NOW.isoformat())
async def test_create_handler(mock_corp_requests, taxi_corp_auth_client):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_auth_client.post(
        '/1.0/client-trial', json=CREATE_REQUEST_BODY,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['client_id'] == '_id'
    assert mock_corp_requests.client_trial.next_call()
    assert not mock_corp_requests.client_trial.has_calls


@pytest.mark.now(NOW.isoformat())
async def test_register_and_create_handler(
        mock_corp_requests, taxi_corp_auth_client,
):

    response = await taxi_corp_auth_client.post(
        '/1.0/register-trial', json=REGISTER_AND_CREATE_REQUEST_BODY,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['client_id'] == '_id'
    assert mock_corp_requests.register_trial.next_call()
    assert not mock_corp_requests.register_trial.has_calls

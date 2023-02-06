# flake8: noqa
# pylint: disable=W0621,E0102,R1705

import pytest
import logging

logger = logging.getLogger(__name__)


REQUEST_PHONE_CLEANED = '+79011111111'
HEADERS = {'X-Yandex-UID': '123', 'X-Yandex-Login': 'yandex_login_1'}


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
)
async def test_client_trial(
        mock_mds,
        mock_personal_random_gen_login,
        taxi_corp_requests_web,
        mock_corp_clients,
        patch,
        db,
        stq,
        web_context,
):
    json = {
        'phone': REQUEST_PHONE_CLEANED,
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
        },
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': 'taxi',
    }

    response = await taxi_corp_requests_web.post(
        '/v1/client-trial', json=json, headers=HEADERS,
    )

    assert response.status == 200

    response_json = await response.json()

    assert stq.corp_notices_process_event.times_called == 1

    call = stq.corp_notices_process_event.next_call()
    assert call['kwargs']['event_name'] == 'NewTrialClient'
    assert call['kwargs']['data'] == {
        'client_id': 'client_id',
        'yandex_login': 'yandex_login_1',
        'contract_type': 'taxi',
        'encrypted_password': '',
        'flow': 'client_trial',
    }

    create_call = mock_corp_clients.create_client.next_call()
    create_call_req = create_call['request'].json

    assert create_call_req['phone'] == REQUEST_PHONE_CLEANED

    request_draft = await db.corp_client_request_drafts.find(
        {'client_id': response_json['client_id']},
    ).to_list(None)

    assert len(request_draft) == 1
    assert request_draft[0]['references'] == json['utm']
    assert 'updated' in request_draft[0] and 'created' in request_draft[0]
    assert request_draft[0]['flow'] == 'client_trial'

    assert not mock_corp_clients.service_taxi.has_calls
    assert not mock_corp_clients.service_cargo.has_calls

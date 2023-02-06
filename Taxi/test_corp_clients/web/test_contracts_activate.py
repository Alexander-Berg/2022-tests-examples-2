# pylint: disable=invalid-name

import pytest

pytestmark = pytest.mark.config(
    CORP_REASONS_OF_BLOCKING_OR_ACTIVATION={
        'BlockReasons': [
            {
                'id': 'block_reason',
                'do_send_notice': True,
                'text': 'Уведомлять',
            },
        ],
        'ActivateReasons': [
            {
                'id': 'activate_reason',
                'do_send_notice': True,
                'text': 'Уведомлять',
            },
        ],
    },
)


async def test_contract_not_found(web_app_client):
    response = await web_app_client.post(
        '/v1/contracts/activate',
        params={'contract_id': 0},
        json={'is_active': True, 'reason': 'block_reason'},
    )
    assert response.status == 404


async def test_contract_activate(db, stq, web_app_client):
    response = await web_app_client.post(
        '/v1/contracts/activate',
        params={'contract_id': 102},
        json={'is_active': True, 'reason': 'activate_reason'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    contract = await db.corp_contracts.find_one({'_id': 102})
    assert contract['settings']['is_active'] is True

    # check event
    assert stq.corp_notices_process_event.times_called == 1
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'ContractSettingsChanged',
        'data': {
            'reason': 'activate_reason',
            'contract_id': contract['_id'],
            'client_id': 'client_id_1',
            'old': {'is_active': False},
            'new': {'is_active': True},
        },
    }

    assert stq.is_empty


async def test_contract_deactivate(db, stq, web_app_client):
    response = await web_app_client.post(
        '/v1/contracts/activate',
        params={'contract_id': 101},
        json={'is_active': False, 'reason': 'block_reason'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert contract['settings']['is_active'] is False

    # check event
    assert stq.corp_notices_process_event.times_called == 1
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'ContractSettingsChanged',
        'data': {
            'reason': 'block_reason',
            'contract_id': contract['_id'],
            'client_id': 'client_id_1',
            'old': {'is_active': True},
            'new': {'is_active': False},
        },
    }

    assert stq.is_empty


async def test_contract_deactivate_no_reason(db, stq, web_app_client):
    response = await web_app_client.post(
        '/v1/contracts/activate',
        params={'contract_id': 101},
        json={'is_active': False},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert contract['settings']['is_active'] is False
    assert stq.is_empty

# pylint: disable=redefined-outer-name

import json

import pytest

from taxi.clients import http_client
from taxi.clients import sender

from taxi_corp import config
from taxi_corp import settings
from taxi_corp.clients import crm
from taxi_corp.notifier import notices
from taxi_corp.notifier import notifier

CORP_FERNET_SECRET_KEYS = (
    'zbCLq520w21vF3JLsBX2owdS6w8P752nKZzWYABe7Ns=;'
    'xqt7uUt0Nf3qTEJnqyF_9GTHOhyTIqE0-XDk7fBlVfI='
)

BASE_SLUGS = {'rus': 'test_slug', 'arm': 'test_arm_slug'}
MOCK_HOST = 'http://kinda_crm_host.x'
MOCK_AUTH_TOKEN = 'token'

MOCK_CONTRACTS = {
    'contracts': [
        {
            'contract_id': 123,
            'payment_type': 'prepaid',
            'services': ['taxi', 'cargo'],
        },
        {
            'contract_id': 456,
            'payment_type': 'postpaid',
            'services': ['drive'],
        },
    ],
}


@pytest.fixture
async def http_session(loop):
    async with http_client.HTTPClient(loop=loop) as session:
        yield session


def get_notifier(
        app,
        db,
        http_session,
        notice_name,
        send_to_crm=False,
        notice_slugs=None,
) -> notifier.Notifier:
    cfg = config.Config(db)
    send_conditions = {
        notice_name: {
            'ab_testing': False,
            'enabled': True,
            'send_to_crm': send_to_crm,
        },
    }
    if notice_slugs is None:
        notice_slugs = BASE_SLUGS
    send_slugs = {notice_name: notice_slugs}
    setattr(cfg, 'CORP_NOTICES_SEND_CONDITIONS', send_conditions)
    setattr(cfg, 'CORP_NOTICE_SENDER_SLUGS', send_slugs)

    crm_client = crm.CRM(MOCK_HOST, MOCK_AUTH_TOKEN, http_session)
    sender_client = sender.SenderClient(
        settings.SENDER_HOST,
        settings.SENDER_ACCOUNT_SLUG,
        settings.SENDER_USER,
        http_session,
    )
    return notifier.Notifier(app, db, sender_client, crm_client, cfg)


@pytest.mark.parametrize('entity_id', ['succesfull_notice'])
@pytest.mark.parametrize('send_to_crm', [True, False])
@pytest.mark.parametrize(
    ['notice_name', 'client_state', 'expected_sender_params', 'crm_error'],
    [
        pytest.param(
            notices.NEW_CLIENT_POLL_NOTICE,
            {
                'contract_status': 'active',
                'is_active': True,
                'country': 'arm',
                'services.taxi.is_active': True,
            },
            {
                'contract_id': '12345/6',
                'contract_type': 'taxi',
                'manager_email': 'ya@ya.arm',
            },
            None,
            id=notices.NEW_CLIENT_POLL_NOTICE,
        ),
        pytest.param(
            notices.PREPAID_THIRD_REMIND_NOTICE,
            {
                'contract_status': 'active',
                'is_active': True,
                'services.taxi.contract_info.payment_type': 'prepaid',
                'services.taxi.contract_info.balance': 0,
                'services.taxi.is_active': True,
            },
            {'contract_id': '12345/6', 'manager_email': 'ya@ya.ru'},
            None,
            id=notices.PREPAID_THIRD_REMIND_NOTICE,
        ),
        pytest.param(
            notices.OFFER_THIRD_REMIND_NOTICE,
            {
                'contract_status': 'active',
                'is_active': True,
                'services.taxi.contract_info.payment_type': 'prepaid',
                'services.taxi.contract_info.balance': 0,
                'services.taxi.contract_info.is_offer': True,
                'services.taxi.is_active': True,
            },
            {'contract_id': '12345/6', 'manager_email': 'ya@ya.ru'},
            None,
            id=notices.OFFER_THIRD_REMIND_NOTICE,
        ),
        pytest.param(
            notices.CLIENT_ONBOARDING_1ST_NOTICE,
            {
                'contract_status': 'active',
                'is_active': True,
                'services.taxi.is_active': True,
            },
            {
                'contract_id': '12345/6',
                'contract_type': 'taxi',
                'manager_email': 'ya@ya.ru',
            },
            None,
            id=notices.CLIENT_ONBOARDING_1ST_NOTICE,
        ),
    ],
)
@pytest.mark.config(
    CORP_NOTICES_DEFAULT_EMAILS={'rus': 'ya@yandex.ru', 'arm': 'ya@ya.arm'},
    MANAGER_EMAIL_TO_SENDER=True,
)
async def test_successfull_send(
        db,
        patch,
        taxi_corp_app_stq,
        send_to_crm,
        entity_id,
        notice_name,
        client_state,
        expected_sender_params,
        mock_corp_requests,
        crm_error,
):
    if client_state is not None:
        await db.corp_clients.update_one(
            {'_id': entity_id}, {'$set': client_state},
        )

    @patch('taxi_corp.clients.crm.CRM._request')
    async def _dummy_request(*args, **kwargs):
        if crm_error:
            raise notifier.BaseNotifierError()
        elif client_state and client_state.get('country') == 'arm':
            return []
        return [{'manager_email': 'ya@ya.ru'}]

    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, data, *args, **kwargs):
        assert json.loads(data['args']) == expected_sender_params

    notifier_client = get_notifier(
        taxi_corp_app_stq, db, http_client, notice_name, send_to_crm,
    )
    await notifier_client.send_notice(notice_name, entity_id)

    condition = send_to_crm and 'manager_email' in expected_sender_params

    expected_calls = 2 if condition else 1

    patch_calls = _request.calls
    assert len(patch_calls) == expected_calls


@pytest.mark.parametrize('send_to_crm', [True])
@pytest.mark.parametrize(
    'notice_name',
    [
        notices.NEW_CLIENT_POLL_NOTICE,
        notices.FIRST_REGULAR_POLL_NOTICE,
        notices.REGULAR_POLL_NOTICE,
    ],
)
@pytest.mark.parametrize(
    ['client_state', 'expected_sender_params', 'crm_error', 'entity_id'],
    [
        pytest.param(
            {'contract_status': 'active', 'is_active': True},
            {
                'contract_id': '12345/6',
                'contract_type': 'cargo',
                'manager_email': 'ya@ya.ru',
            },
            None,
            'contract_type_notice',
            id='contract_type_from_client_requests',
        ),
        pytest.param(
            {'contract_status': 'active', 'is_active': True},
            {
                'contract_id': '12345/6',
                'contract_type': 'multi',
                'manager_email': 'ya@ya.ru',
            },
            None,
            'contract_type_notice2',
            id='multi_contract_type_from_services',
        ),
    ],
)
@pytest.mark.config(
    CORP_NOTICES_DEFAULT_EMAILS={'rus': 'ya@ya.ru'},
    MANAGER_EMAIL_TO_SENDER=True,
)
async def test_contract_type_from_services(
        db,
        patch,
        taxi_corp_app_stq,
        send_to_crm,
        entity_id,
        notice_name,
        client_state,
        expected_sender_params,
        crm_error,
        mock_corp_clients,
        mock_corp_requests,
):
    if client_state is not None:
        await db.corp_clients.update_one(
            {'_id': entity_id}, {'$set': client_state},
        )

    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, data, *args, **kwargs):
        assert json.loads(data['args']) == expected_sender_params

    mock_corp_clients.data.get_contracts_response = MOCK_CONTRACTS

    notifier_client = get_notifier(
        taxi_corp_app_stq, db, http_client, notice_name, send_to_crm,
    )
    await notifier_client.send_notice(notice_name, entity_id)


@pytest.mark.parametrize(
    'entity_id, notice_name',
    [
        pytest.param(
            'succesfull_notice', 'NewClientPollNotice', id='do not send slug',
        ),
    ],
)
async def test_do_not_send_slug(
        db, patch, taxi_corp_app_stq, http_session, entity_id, notice_name,
):
    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, data, *args, **kwargs):
        pass

    notifier_client = get_notifier(
        taxi_corp_app_stq,
        db,
        http_client,
        notice_name,
        notice_slugs={'rus': 'do_not_send'},
    )
    await notifier_client.send_notice(notice_name, entity_id)

    assert not _request.calls


@pytest.mark.parametrize(
    'entity_id, notice_name, notice_kwargs',
    [
        pytest.param(
            'cargo_client_from_manager_request',
            notices.CLIENT_ONBOARDING_1ST_NOTICE,
            {},
            id='do not send onboarding for cargo manager request',
        ),
        pytest.param(
            'cargo_client_from_offer',
            notices.CLIENT_ONBOARDING_1ST_NOTICE,
            {},
            id='do not send onboarding for cargo offer',
        ),
        pytest.param(
            'cargo_client_from_offer',
            notices.NEW_CLIENT_POLL_NOTICE,
            {},
            id='do not send poll mails for cargo',
        ),
    ],
)
async def test_do_not_send_cargo(
        db,
        patch,
        taxi_corp_app_stq,
        entity_id,
        notice_name,
        notice_kwargs,
        mock_corp_requests,
):
    @patch('taxi_corp.clients.crm.CRM._request')
    async def _dummy_request(*args, **kwargs):
        return [{'manager_email': 'ya@ya.ru'}]

    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, data, *args, **kwargs):
        pass

    send_to_crm = True
    notifier_client = get_notifier(
        taxi_corp_app_stq, db, http_client, notice_name, send_to_crm,
    )
    await notifier_client.send_notice(notice_name, entity_id, **notice_kwargs)

    assert not _request.calls

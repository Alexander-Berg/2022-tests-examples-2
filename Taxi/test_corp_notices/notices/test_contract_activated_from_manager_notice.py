# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.notices.notices import (
    contract_activated_from_manager_notice as contract_activated,
)


NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'ContractActivatedFromManagerNotice': {
                'enabled': True,
                'slugs': {'rus': 'SLUG'},
            },
        },
    ),
]


MOCK_CLIENT_RESPONSE = {
    'id': 'client_id_1',
    'name': 'Test client',
    'billing_name': 'None',
    'country': 'rus',
    'yandex_login': 'test-client',
    'description': 'Test',
    'is_trial': False,
    'email': 'test@email.com',
    'features': [],
    'billing_id': '101',
    'created': '2020-01-01T03:00:00+03:00',
}


@pytest.fixture
def broker(cron_context):
    encrypted_pass = cron_context.corp_crypto.encrypt('Qw123456')

    return contract_activated.ContractActivatedNoticeBroker.make(
        cron_context,
        client_id='client_id_1',
        notice_kwargs={
            'request_id': 'request_id_1',
            'login': 'test_login',
            'encrypted_password': encrypted_pass,
            'offer_contract_type': 'prepaid',
            'contract_service': 'taxi',
        },
    )


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() == {
        'Login': 'test_login',
        'Pass': 'Qw123456',
        'ContractType': 'prepaid',
        'contract_type': 'taxi',
    }


async def test_post_send(
        broker, mock_corp_requests, mock_corp_clients, mock_sender,
):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE

    await broker.enqueue()
    await broker.send()
    assert broker.notice.template_kwargs == {
        'Login': 'test_login',
        'Pass': 'XXXXXX',
        'ContractType': 'prepaid',
        'contract_type': 'taxi',
    }

    requests_api = mock_corp_requests.post_activation_email_sent
    assert requests_api.times_called == 1


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('CargoContractActivatedFromManagerNotice')
    assert registry.get('TaxiContractActivatedFromManagerNotice')

# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
import functools

import pytest

from taxi.clients import billing_v2

from corp_requests import consts
from corp_requests.stq import corp_accept_client_request


def raise_on(func_name, exc_class):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if func.__name__ == func_name:
                raise exc_class
            return await func(*args, **kwargs)

        return wrapper

    return decorator


@pytest.mark.parametrize(
    ['faulty_step', 'expected_tanker_key'],
    [
        pytest.param(
            '_create_user_client_association',
            consts.TankerErrors.CUSTOMER_LINKING_ERROR,
        ),
        pytest.param(
            '_create_person', consts.TankerErrors.PERSON_CREATION_ERROR,
        ),
        pytest.param(
            '_create_offer', consts.TankerErrors.OFFER_CREATION_ERROR,
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'deactivate_threshold': 50},
        'isr': {'deactivate_threshold': 50},
    },
    TVM_RULES=[
        {'dst': 'taxi-corp-admin', 'src': 'corp-requests'},
        {'dst': 'personal', 'src': 'corp-requests'},
    ],
    CORP_OFFER_BALANCE_MANAGER_UIDS={
        'rus': {'__default__': [123456789]},
        'isr': {'__default__': [123456789]},
    },
    CORP_OFFER_ACCEPT_TERMS={
        'isr': {'offer_confirmation_type': 'no'},
        'rus': {
            'offer_activation_due_term': 30,
            'offer_activation_payment_amount': '1000.00',
            'offer_confirmation_type': 'min-payment',
        },
    },
)
async def test_faulty_create_client(
        mockserver,
        patch,
        db,
        stq3_context,
        faulty_step,
        expected_tanker_key,
        stq,
        mock_personal,
        mock_corp_clients,
):
    @mockserver.json_handler('/corp-admin/v1/finish-trial-client')
    def _finish_trial(request):
        assert request.method == 'POST'
        return {'id': request.json['client_id']}

    @patch('taxi.clients.billing_v2.BalanceClient.create_client')
    async def _create_client(*args, **kwargs):
        return {'CLIENT_ID': 'BILLING_ID'}

    @patch('taxi.clients.billing_v2.BalanceClient.get_passport_by_login')
    async def _get_passport_by_login(*args, **kwargs):
        return {'Uid': 'PASSPORT_UID'}

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    @raise_on(faulty_step, billing_v2.BillingError)
    async def _create_user_client_association(*args, **kwargs):
        pass

    @patch('taxi.clients.billing_v2.BalanceClient.find_client')
    async def _find_client(*args, **kwargs):
        return {'CLIENT_ID': 'BILLING_ID'}

    @patch('taxi.clients.billing_v2.BalanceClient.create_person')
    @raise_on(faulty_step, billing_v2.BillingError)
    async def _create_person(*args, **kwargs):
        return 'PERSON_ID'

    @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
    @raise_on(faulty_step, billing_v2.BillingError)
    async def _create_offer(*args, **kwargs):
        return {'EXTERNAL_ID': 'EXTERNAL_ID', 'ID': 'CONTRACT_ID'}

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _client_contracts(*args, **kwargs):
        return []

    request_id = 'trial_client_offer'

    client_request = await db.corp_client_requests.find_one(
        {'_id': request_id},
    )

    await corp_accept_client_request.task(
        stq3_context, client_request, status='accepted', operator_uid='0',
    )

    client_request = await db.corp_client_requests.find_one(
        {'_id': request_id},
    )
    assert (
        str(client_request['last_error']['error']) == expected_tanker_key.value
    )

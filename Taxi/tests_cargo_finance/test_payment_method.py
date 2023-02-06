import pytest

CARD_ID = 'cardid'
YANDEX_UID = '12345'
CORP_CLIENT_ID = '35bf617cf19348e9a4f4a7064774fb8e'
ANOTHER_CORP_CLIENT_ID = '4bb5a0018d9641c681c1a854b21ec9ab'
BILLING_ID = '123456'
CONTRACT_ID = '1234567'
CONTRACT_ID_INT = 1234567
ORDER_PRICE = '123.456'
CONTRACT_TYPE_OFFER = 9
CONTRACT_TYPE_NOT_OFFER = 1
INACTIVE_CONTRACT_RESPONSE = {
    'code': 'inactive_contract',
    'details': {},
    'message': 'Неактивный контракт',
}


def get_default_corp_request():
    return {'corp_client_id': CORP_CLIENT_ID}


def get_default_ya_go_request():
    return {'yandex_uid': YANDEX_UID}


def _get_default_ndd_corp_request():
    return {'corp_client_id': CORP_CLIENT_ID, 'order': {'price': ORDER_PRICE}}


def make_debt(amount: int):
    return {
        'id': 'claims/agent/test_id',
        'currency': 'RUB',
        'debtor_id': 'cargo/corp_client_id/35bf617cf19348e9a4f4a7064774fb8e',
        'sum_to_pay': str(amount),
    }


@pytest.fixture(name='mock_billing_active_contracts')
def _mock_billing_active_contracts(mockserver):
    class Context:
        def __init__(self):
            self.mock = None
            self.response_code = 200
            self.is_offer = True
            self.offer_accepted = True
            self.response_data = None

    context = Context()

    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    async def _mock_billing_replication(request):
        if context.response_data is not None:
            return mockserver.make_response(
                status=context.response_code, json=context.response_data,
            )
        contract_type = (
            CONTRACT_TYPE_OFFER
            if context.is_offer
            else CONTRACT_TYPE_NOT_OFFER
        )
        offer_accepted = 1 if context.offer_accepted else 0

        response_data = [
            {
                'ID': CONTRACT_ID_INT,
                'PERSON_ID': 42,
                'CONTRACT_TYPE': contract_type,
                'OFFER_ACCEPTED': offer_accepted,
                'SERVICES': [650],
            },
        ]

        return mockserver.make_response(
            status=context.response_code, json=response_data,
        )

    context.mock = _mock_billing_replication

    return context


@pytest.fixture(name='mock_corp_clients_contracts')
def _mock_corp_clients_contracts(mockserver):
    class Context:
        def __init__(self):
            self.threshold = '0'
            self.mock = None
            self.response_code = 200
            self.no_contracts = False

    context = Context()

    @mockserver.json_handler('/corp-clients-uservices/v1/contracts')
    async def _mock_corp_clients(request):
        if context.no_contracts:
            return mockserver.make_response(
                status=context.response_code, json={'contracts': []},
            )

        response_data = {
            'contracts': [
                {
                    'contract_id': CONTRACT_ID_INT,
                    'external_id': '5239981/22',
                    'billing_client_id': '1358626391',
                    'billing_person_id': '21660505',
                    'payment_type': 'prepaid',
                    'is_offer': False,
                    'currency': 'RUB',
                    'services': ['cargo'],
                    'balances': {'balance': '100'},
                    'settings': {
                        'is_active': True,
                        'prepaid_deactivate_threshold': context.threshold,
                    },
                },
            ],
        }

        return mockserver.make_response(
            status=context.response_code, json=response_data,
        )

    context.mock = _mock_corp_clients

    return context


@pytest.fixture(name='mock_cargo_corp_card_list')
def _mock_cargo_corp_card_list(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-corp/internal/cargo-corp/v1/client/card/list',
        ),
        response_data={
            'bound_cards': [{'card_id': CARD_ID, 'yandex_uid': YANDEX_UID}],
        },
    )


@pytest.fixture(name='mock_corp_integration_api_client_can_order')
def _mock_corp_integration_api_client_can_order(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/taxi-corp-integration/v1/clients/can_order/next_day_delivery',
        ),
        response_data={
            'statuses': [
                {
                    'client_id': CORP_CLIENT_ID,
                    'can_order': True,
                    'zone_available': True,
                },
            ],
        },
    )


@pytest.fixture(name='mock_cargo_corp_payment_methods')
def _mock_cargo_corp_payment_methods(mockserver):
    class Context:
        def __init__(self):
            self.payment_method_card = 'card'
            self.payment_method_contract = 'contract'
            self.payment_method = self.payment_method_card
            self.payment_type = 'postpaid'
            self.mock = None
            self.second_corp = None
            self.no_methods = False
            self.no_corps = False
            self.request = None
            self.method_disabled = False

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/'
        'payment-methods/list',
    )
    async def _mock_cargo_corp(request):
        context.request = request
        if context.no_corps:
            return mockserver.make_response(
                status=200, json={'payment_methods': []},
            )

        response = {
            'payment_methods': [
                {
                    'corp_info': {
                        'corp_client_id': CORP_CLIENT_ID,
                        'corp_client_name': 'name1',
                        'country': 'ru',
                        'created_ts': '2021-10-28T17:54:41+0000',
                    },
                },
            ],
        }
        if context.no_methods:
            return mockserver.make_response(status=200, json=response)

        if context.method_disabled and 'Phone-Pd-Id' in request.headers:
            response['payment_methods'][0]['reason_for_unavailability'] = {
                'code': 'different_yandex_uids',
                'message': 'different yandex uids',
            }
            return mockserver.make_response(status=200, json=response)

        if context.payment_method == context.payment_method_card:
            response['payment_methods'][0]['card_info'] = {
                'card_id': CARD_ID,
                'yandex_uid': YANDEX_UID,
            }
        elif context.payment_method == context.payment_method_contract:
            response['payment_methods'][0]['contract_info'] = {
                'billing_id': BILLING_ID,
                'contract_id': CONTRACT_ID,
                'payment_type': context.payment_type,
                'contract_type': 'offer',
            }

        if context.second_corp:
            response['payment_methods'].append(context.second_corp)

        return mockserver.make_response(status=200, json=response)

    context.mock = _mock_cargo_corp

    return context


@pytest.fixture(name='mock_debts_retrieve')
def _mock_debts(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-finance/internal/cargo-finance/v1/debt/retrieve',
        ),
        response_data={'debts': []},
    )


@pytest.fixture(name='mock_cargo_corp_employee')
def _mock_cargo_corp_employee(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/list',
        ),
        response_data={
            'corp_clients': [
                {
                    'name': 'name1',
                    'id': CORP_CLIENT_ID,
                    'is_registration_finished': True,
                },
            ],
        },
    )


@pytest.fixture(name='payment_methods_v1')
async def _payment_methods_v1(
        taxi_cargo_finance,
        mock_debts_retrieve,
        mock_cargo_corp_payment_methods,
        mock_billing_active_contracts,
        mock_corp_clients_contracts,
):
    class Context:
        url = '/internal/cargo-finance/payment-methods/v1'
        payload = get_default_ya_go_request()
        mock_debts = mock_debts_retrieve
        mock_employee = mock_cargo_corp_payment_methods
        mock_active_contracts = mock_billing_active_contracts
        mock_corp_contracts = mock_corp_clients_contracts

        async def list(self, personal_phone_id=None):
            if personal_phone_id:
                self.payload['personal_phone_id'] = personal_phone_id
            return await taxi_cargo_finance.post(
                self.url, json=self.payload, headers={'Accept-Language': 'ru'},
            )

    return Context()


async def test_for_yandex_go(payment_methods_v1):
    response = await payment_methods_v1.list()
    assert (
        payment_methods_v1.mock_employee.request.headers['X-Yandex-UID']
        == YANDEX_UID
    )
    assert response.json() == {
        'methods': [
            {
                'details': {
                    'cardstorage_id': 'cardid',
                    'owner_yandex_uid': '12345',
                    'type': 'corpcard',
                    'is_disabled': False,
                },
                'display': {
                    'type': 'cargocorp',
                    'image_tag': 'corpcard',
                    'title': 'name1',
                },
                'id': (
                    f'cargocorp:{CORP_CLIENT_ID}:card:{YANDEX_UID}:{CARD_ID}'
                ),
            },
        ],
    }
    assert payment_methods_v1.mock_active_contracts.mock.times_called == 0


async def test_one_employee_two_corps(payment_methods_v1):
    new_corp = {
        'corp_info': {
            'corp_client_id': ANOTHER_CORP_CLIENT_ID,
            'corp_client_name': 'name2',
            'created_ts': '2021-10-28T17:54:41+0000',
            'country': 'ru',
        },
        'card_info': {'card_id': CARD_ID, 'yandex_uid': YANDEX_UID},
    }
    payment_methods_v1.mock_employee.second_corp = new_corp
    response = await payment_methods_v1.list()
    assert len(response.json()['methods']) == 2


async def test_method_with_debts(payment_methods_v1):
    payment_methods_v1.mock_debts.response_data['debts'] = [
        make_debt(amount=2),
        make_debt(amount=3.5),
    ]
    response = await payment_methods_v1.list()
    method = response.json()['methods'][0]
    assert method['display']['disable_reason'] == {
        'code': 'outstanding_debt',
        'details': {},
        'message': 'Долг 5.5 ₽',
    }
    assert method['details']['is_disabled'] is True


async def test_contract_payment_method(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    expected_response = {
        'methods': [
            {
                'details': {
                    'corp_client_id': CORP_CLIENT_ID,
                    'billing_id': '123456',
                    'contract_id': '1234567',
                    'is_logistic_contract': False,
                    'type': 'contract',
                    'country': 'ru',
                    'is_disabled': False,
                },
                'display': {
                    'type': 'cargocorp',
                    'image_tag': 'corpcard',
                    'title': 'name1',
                },
                'id': (
                    f'cargocorp:{CORP_CLIENT_ID}:balance:'
                    f'{BILLING_ID}:contract:{CONTRACT_ID}'
                ),
            },
        ],
    }
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    assert response.json() == expected_response

    assert payment_methods_v1.mock_debts.mock.times_called == 0
    assert payment_methods_v1.mock_active_contracts.mock.times_called == 1
    assert payment_methods_v1.mock_corp_contracts.mock.times_called == 0

    # test cache hit
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    assert response.json() == expected_response
    assert payment_methods_v1.mock_active_contracts.mock.times_called == 1


async def test_logistic_contract(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.response_data = [
        {'ID': CONTRACT_ID_INT, 'PERSON_ID': 42, 'SERVICES': [718]},
    ]
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    assert (
        response.json()['methods'][0]['details']['is_logistic_contract']
        is True
    )


async def test_different_contract_id(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.response_data = [
        {'ID': 1111, 'PERSON_ID': 42, 'SERVICES': [718]},
    ]
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    method = response.json()['methods'][0]
    assert method['display']['disable_reason'] == INACTIVE_CONTRACT_RESPONSE


async def test_contract_payment_method_inactive_contract(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.response_data = []
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    method = response.json()['methods'][0]
    assert method['display']['disable_reason'] == INACTIVE_CONTRACT_RESPONSE


async def test_offer_not_accepted(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.offer_accepted = False
    response = await payment_methods_v1.list()
    assert response.status_code == 200
    assert not response.json()['methods']


async def test_billing_replication_inaccessible(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.response_code = 500
    response = await payment_methods_v1.list()
    assert response.status_code == 500


@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=pytest.mark.config(
                CARGO_FINANCE_ALLOW_INACTIVE_CONTRACT={
                    'enable_for_everybody': True,
                    'corp_client_ids': [],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CARGO_FINANCE_ALLOW_INACTIVE_CONTRACT={
                    'enable_for_everybody': False,
                    'corp_client_ids': [CORP_CLIENT_ID],
                },
            ),
        ),
    ),
)
async def test_inactive_contracts_allowed(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_active_contracts.response_data = []
    response = await payment_methods_v1.list()
    method = response.json()['methods'][0]
    assert 'disable_reason' not in method['display']


async def test_no_payment_methods(payment_methods_v1):
    payment_methods_v1.mock_employee.no_methods = True
    response = await payment_methods_v1.list()
    assert response.status == 200
    assert not response.json()['methods']


async def test_employee_client_not_found(payment_methods_v1):
    payment_methods_v1.mock_employee.no_corps = True
    response = await payment_methods_v1.list()
    assert response.status == 200
    assert not response.json()['methods']


async def test_prepaid_ok(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_employee.payment_type = 'prepaid'
    response = await payment_methods_v1.list()
    assert response.status == 200
    method = response.json()['methods'][0]
    assert 'disable_reason' not in method['display']


async def test_threshold_exceeded(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_employee.payment_type = 'prepaid'
    payment_methods_v1.mock_corp_contracts.threshold = '200'
    response = await payment_methods_v1.list()
    assert response.status == 200
    assert payment_methods_v1.mock_corp_contracts.mock.times_called == 1
    method = response.json()['methods'][0]
    assert method['display']['disable_reason'] == {
        'code': 'insufficient_balance',
        'message': 'Недостаточно средств на балансе',
        'details': {},
    }


@pytest.mark.config(
    CARGO_FINANCE_ALLOW_INACTIVE_CONTRACT={
        'enable_for_everybody': True,
        'corp_client_ids': [],
    },
)
async def test_contracts_inaccessible(payment_methods_v1):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_employee.payment_type = 'prepaid'
    payment_methods_v1.mock_corp_contracts.response_code = 500
    response = await payment_methods_v1.list()
    assert response.status == 500


@pytest.mark.parametrize(
    'allow_inactive_contract',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_FINANCE_ALLOW_INACTIVE_CONTRACT={
                    'enable_for_everybody': True,
                    'corp_client_ids': [],
                },
            ),
            id='allow_inactive_contract',
        ),
        pytest.param(False, id='disallow_inactive_contract'),
    ],
)
async def test_no_contracts_in_corp(
        payment_methods_v1, allow_inactive_contract,
):
    payment_methods_v1.mock_employee.payment_method = (
        payment_methods_v1.mock_employee.payment_method_contract
    )
    payment_methods_v1.mock_employee.payment_type = 'prepaid'
    payment_methods_v1.mock_corp_contracts.threshold = '200'
    payment_methods_v1.mock_corp_contracts.no_contracts = True
    response = await payment_methods_v1.list()
    assert response.status == 200 if allow_inactive_contract else 500

    if response.status == 200:
        assert payment_methods_v1.mock_corp_contracts.mock.times_called == 1
        method = response.json()['methods'][0]
        if not allow_inactive_contract:
            assert 'disable_reason' not in method['display']


async def test_payment_methods_next_day_delivery_ok(
        mockserver,
        mock_corp_integration_api_client_can_order,
        taxi_cargo_finance,
):
    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/payment-methods/next-day-delivery',
        json=_get_default_ndd_corp_request(),
    )

    assert response.status == 200
    assert response.json() == {'can_order': True, 'zone_available': True}

    assert mock_corp_integration_api_client_can_order.request.json == {
        'client_ids': [CORP_CLIENT_ID],
        'order': {'order_price': ORDER_PRICE},
    }
    assert mock_corp_integration_api_client_can_order.mock.times_called == 1


async def test_payment_methods_next_day_delivery_400(
        mockserver, taxi_cargo_finance,
):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/clients/can_order/next_day_delivery',
    )
    async def _mock_corp_integration_api_client_can_order(request):
        assert request.json == {
            'client_ids': [CORP_CLIENT_ID],
            'order': {'order_price': ORDER_PRICE},
        }
        return mockserver.make_response(
            status=400, json={'code': 'bad_corp', 'message': 'hello world'},
        )

    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/payment-methods/next-day-delivery',
        json=_get_default_ndd_corp_request(),
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'invalid_argument',
        'details': {},
        'message': (
            'POST /v1/clients/can_order/next_day_delivery, status code 400'
        ),
    }

    assert _mock_corp_integration_api_client_can_order.times_called == 1


@pytest.mark.parametrize(
    'send_phone',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_FINANCE_SEARCH_PAYMENT_METHODS_BY_PHONE=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CARGO_FINANCE_SEARCH_PAYMENT_METHODS_BY_PHONE=False,
            ),
        ),
    ],
)
async def test_phonish_login(payment_methods_v1, send_phone):
    payment_methods_v1.mock_employee.method_disabled = True
    personal_phone_id = '1234'
    response = await payment_methods_v1.list(personal_phone_id)
    assert response.status == 200

    corp_request = payment_methods_v1.mock_employee.mock.next_call()['request']
    method = response.json()['methods'][0]

    if send_phone:
        assert corp_request.headers['Phone-Pd-Id'] == personal_phone_id
        assert (
            method['id']
            == f'cargocorp:{CORP_CLIENT_ID}:card:000000:card-000000'
        )
        assert method['display']['disable_reason'] == {
            'code': 'different_yandex_uids',
            'message': 'different yandex uids',
            'details': {},
        }
    else:
        assert 'Phone-Pd-Id' not in corp_request.headers

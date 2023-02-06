import pytest


#  #############################
#  System states with injections


@pytest.fixture(name='state_all_paid')
async def _state_all_paid(flush_all, get_b2b_state):
    flush_all()
    return await get_b2b_state()


@pytest.fixture(name='state_has_debts')
async def _state_has_debts(inject_debts, flush_all, get_b2b_state):
    flush_all()
    return await get_b2b_state()


@pytest.fixture(name='inject_debts')
def _inject_debts(set_debts):
    set_debts()


@pytest.fixture(name='inject_no_debts')
def _inject_no_debts(set_debts):
    set_debts({'debts': []})


@pytest.fixture(name='set_debts')
def _set_debts(load_json, debt_list_response):
    def wrapper(data=None):
        if data is None:
            data = load_json('debt_list_response.json')
        debt_list_response.data = data

    return wrapper


@pytest.fixture(name='inject_no_bound_cards')
def _inject_no_bound_cards(corp_card_list_response):
    corp_card_list_response.data['bound_cards'] = []


@pytest.fixture(name='inject_default_card')
def _inject_default_card(corp_card_list_response, default_card):
    corp_card_list_response.data['bound_cards'] = [default_card]


#  ##############################
#  Target handlers with shortcuts


@pytest.fixture(name='get_b2b_state')
def _get_b2b_state(
        taxi_cargo_finance, corp_client_id, employee_uid, employee_login,
):
    url = '/b2b/cargo-finance/debts/state'

    async def wrapper():
        headers = {
            'X-B2B-Client-Id': corp_client_id,
            'X-Yandex-Uid': employee_uid,
            'X-Yandex-Login': employee_login,
        }
        response = await taxi_cargo_finance.post(url, headers=headers)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='pay_debts')
def _pay_debts(
        request_pay_debts, corp_client_id, employee_uid, employee_login,
):
    async def wrapper(operation_token):
        response = await request_pay_debts(
            corp_client_id, employee_uid, employee_login, operation_token,
        )
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='request_pay_debts')
def _request_pay_debts(taxi_cargo_finance):
    url = '/b2b/cargo-finance/debts/pay'

    async def wrapper(
            corp_client_id, employee_uid, employee_login, operation_token,
    ):
        headers = {
            'X-B2B-Client-Id': corp_client_id,
            'X-Yandex-Uid': employee_uid,
            'X-Yandex-Login': employee_login,
        }
        data = {'operation_token': operation_token}
        response = await taxi_cargo_finance.post(
            url, headers=headers, json=data,
        )
        return response

    return wrapper


@pytest.fixture(name='run_stq')
def _run_stq(stq_runner, corp_client_id):
    async def wrapper():
        task_id = 'debts_pay/{}'.format(corp_client_id)
        kwargs = {'corp_client_id': corp_client_id}
        await stq_runner.cargo_finance_debts_pay.call(
            task_id=task_id, kwargs=kwargs,
        )

    return wrapper


#  #################
#  External handlers


@pytest.fixture(name='mock_corp_card_list')
def _mock_corp_card_list(mockserver, corp_card_list_response):
    url = '/cargo-corp/internal/cargo-corp/v1/client/card/list'

    @mockserver.json_handler(url)
    def handler(request):
        return corp_card_list_response.make(request)

    return handler


@pytest.fixture(name='corp_card_list_response')
def _corp_card_list_response(default_card):
    class CorpCardListResponse:
        def __init__(self):
            self.data = {'bound_cards': [default_card]}

        def make(self, request):
            return self.data

    return CorpCardListResponse()


@pytest.fixture(name='mock_debt_list')
def _mock_debt_list(mockserver, debt_list_response):
    url = '/cargo-finance/internal/cargo-finance/v1/debt/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return debt_list_response.make(request)

    return handler


@pytest.fixture(name='debt_list_response')
def _debt_list_response():
    class DebtListResponse:
        def __init__(self):
            self.data = {'debts': []}

        def make(self, request):
            return self.data

    return DebtListResponse()


@pytest.fixture(name='mock_change_card')
def _mock_change_card(mockserver, change_card_response):
    url = (
        '/cargo-finance/internal/cargo-finance/pay/order/applying/change-card'
    )

    @mockserver.json_handler(url)
    def handler(request):
        return change_card_response.make(request)

    return handler


@pytest.fixture(name='change_card_response')
def _change_card_response(mockserver):
    class ChangeCardResponse:
        def __init__(self):
            self.status = 200

        def make(self, request):
            if self.status == 200:
                return {}
            return mockserver.make_response(status_code=self.status, json={})

    return ChangeCardResponse()


@pytest.fixture(name='flush_all')
def _flush_all(mock_corp_card_list, mock_debt_list, mock_change_card, stq):
    def wrapper():
        mock_corp_card_list.flush()
        mock_debt_list.flush()
        mock_change_card.flush()
        stq.cargo_finance_debts_pay.flush()

    return wrapper


@pytest.fixture(autouse=True)
def _setup_environment(mock_corp_card_list, mock_debt_list, mock_change_card):
    pass


#  #############################
#  constants


@pytest.fixture(name='corp_client_id')
def _corp_client_id():
    return 'corp_client_id-11111111111111111'


@pytest.fixture(name='employee_uid')
def _employee_uid():
    return 'yandex_uid-222222222222222222222'


@pytest.fixture(name='employee_login')
def _employee_login():
    return 'yandex_login-2222222222222222222'


@pytest.fixture(name='card_owner_uid')
def _card_owner_uid():
    return 'yandex_uid-333333333333333333333'


@pytest.fixture(name='cardstorage_id')
def _cardstorage_id():
    return 'card-333333333333333333333333333'


@pytest.fixture(name='default_card')
def _default_card(cardstorage_id, card_owner_uid):
    return {'card_id': cardstorage_id, 'yandex_uid': card_owner_uid}

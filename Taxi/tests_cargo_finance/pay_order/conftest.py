import pytest


#  #############################
#  System states with injections


@pytest.fixture(name='applying_state_no_sum')
async def _applying_state_no_sum(
        inject_applying_sum2pay_no_sum,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='applying_state_holding')
async def _applying_state_holding(
        inject_applying_sum2pay_can_hold,
        inject_transactions_in_progress,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='applying_state_held')
async def _applying_state_held(
        applying_state_holding,
        inject_paid,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='inject_applying_sum2pay_no_sum')
async def _inject_applying_sum2pay_no_sum(load_json, set_applying_sum2pay):
    await set_applying_sum2pay(load_json('sum2pay_no_sum.json'))


@pytest.fixture(name='inject_applying_sum2pay_can_hold')
async def _inject_applying_sum2pay_can_hold(load_json, set_applying_sum2pay):
    await set_applying_sum2pay(load_json('sum2pay_can_hold.json'))


@pytest.fixture(name='inject_transactions_in_progress')
def _inject_transactions_in_progress(load_json, set_transactions_response):
    data = load_json('transactions_in_progress.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid')
def _inject_paid(load_json, set_transactions_response):
    data = load_json('transactions_paid.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid_less')
def _inject_paid_less(load_json, set_transactions_response):
    data = load_json('transactions_paid_less.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid_more')
def _inject_paid_more(load_json, set_transactions_response):
    data = load_json('transactions_paid_more.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid_compensated')
def _inject_paid_compensated(load_json, set_transactions_response):
    data = load_json('transactions_paid_compensated.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid_less_compensated')
def _inject_paid_less_compensated(load_json, set_transactions_response):
    data = load_json('transactions_paid_less_compensated.json')
    set_transactions_response(data)


@pytest.fixture(name='inject_paid_less_compensation_in_progress')
def _inject_paid_less_compensation_in_progress(
        load_json, set_transactions_response,
):
    data = load_json('transactions_paid_less_compensation_in_progress.json')
    set_transactions_response(data)


@pytest.fixture(name='set_transactions_response')
def _set_transactions_response(
        upsert_response, debt_response, retrieve_response,
):
    def wrapper(data):
        upsert_response.data = data
        debt_response.data = data
        retrieve_response.data = data

    return wrapper


#  ##############################
#  Target handlers with shortcuts


@pytest.fixture(name='request_dummy_init')
def _request_dummy_init(taxi_cargo_finance):
    url = '/internal/cargo-finance/pay/order/events/dummy-init'

    async def wrapper(flow, entity_id):
        params = {'flow': flow, 'entity_id': entity_id}
        response = await taxi_cargo_finance.post(url, params=params)
        return response

    return wrapper


@pytest.fixture(name='request_send_sum2pay_by_flow')
def _request_send_sum2pay_by_flow(taxi_cargo_finance):
    url = '/internal/cargo-finance/pay/order/events/flow-sum2pay'

    async def wrapper(flow, entity_id, event_id, sum2pay):
        params = {'flow': flow, 'entity_id': entity_id}
        data = {'event_id': event_id, 'sum2pay': sum2pay}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper


@pytest.fixture(name='request_calc_new_sum2pay')
def _request_calc_new_sum2pay(taxi_cargo_finance):
    url = '/internal/cargo-finance/pay/order/func/calc-new-sum2pay-to-apply'

    async def wrapper(flow, entity_id, events):
        params = {'flow': flow, 'entity_id': entity_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper


@pytest.fixture(name='get_applying_state')
def _get_applying_state(request_applying_state, claim_id):
    async def wrapper():
        response = await request_applying_state('claims', claim_id)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_applying_state')
def _request_applying_state(taxi_cargo_finance):
    url = '/internal/cargo-finance/pay/order/applying/state'

    async def wrapper(flow, entity_id):
        params = {'flow': flow, 'entity_id': entity_id}
        response = await taxi_cargo_finance.post(url, params=params)
        return response

    return wrapper


@pytest.fixture(name='set_applying_sum2pay')
def _set_applying_sum2pay(taxi_cargo_finance, claim_id):
    url = '/internal/cargo-finance/pay/order/applying/set-sum2pay'

    async def wrapper(data):
        params = {'flow': 'claims', 'entity_id': claim_id}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='change_card')
def _change_card(request_change_card, claim_id):
    async def wrapper(new_card):
        response = await request_change_card(claim_id, new_card)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='request_change_card')
def _request_change_card(taxi_cargo_finance):
    url = '/internal/cargo-finance/pay/order/applying/change-card'

    async def wrapper(claim_id, new_card):
        params = {'flow': 'claims', 'entity_id': claim_id}
        data = {'new_card': new_card}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper


@pytest.fixture(name='call_applying')
def _call_applying(taxi_cargo_finance, claim_id):
    url = '/internal/cargo-finance/pay/order/applying/call'

    async def wrapper(sum2pay):
        params = {'flow': 'claims', 'entity_id': claim_id}
        data = sum2pay
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='run_applying_stq')
def _run_applying_stq(stq_runner, claim_id):
    async def wrapper():
        flow = 'claims'
        task_id = '{}/{}'.format(flow, claim_id)
        kwargs = {'flow': flow, 'entity_id': claim_id}
        await stq_runner.cargo_finance_pay_applying.call(
            task_id=task_id, kwargs=kwargs,
        )

    return wrapper


@pytest.fixture(name='get_admin_state')
def _get_admin_state(request_admin_state):
    async def wrapper():
        response = await request_admin_state()
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_admin_state')
def _request_admin_state(
        taxi_cargo_finance, claim_id, default_uid, default_login,
):
    url = '/admin/cargo-finance/pay/order/state'

    async def wrapper(flow='claims', uid=None, login=None):
        if uid is None:
            uid = default_uid
        if login is None:
            login = default_login

        params = {'flow': flow, 'entity_id': claim_id}
        headers = {
            'X-Yandex-Uid': uid,
            'X-Yandex-Login': login,
            'Accept-Language': 'ru',
        }
        response = await taxi_cargo_finance.post(
            url, params=params, headers=headers,
        )
        return response

    return wrapper


@pytest.fixture(name='request_admin_change_order_sum')
def _request_admin_change_order_sum(
        taxi_cargo_finance,
        claim_id,
        default_uid,
        default_login,
        default_reason,
):
    url = '/admin/cargo-finance/pay/order/change-order-sum'

    async def wrapper(
            operation_token, new_sum, flow='claims', uid=None, login=None,
    ):
        if uid is None:
            uid = default_uid
        if login is None:
            login = default_login

        params = {'flow': flow, 'entity_id': claim_id}
        headers = {'X-Yandex-Uid': uid, 'X-Yandex-Login': login}
        data = {
            'operation_token': operation_token,
            'new_sum': new_sum,
            'reason': default_reason,
        }
        response = await taxi_cargo_finance.post(
            url, params=params, headers=headers, json=data,
        )
        return response

    return wrapper


@pytest.fixture(name='request_admin_change_compensation')
def _request_admin_change_compensation(
        taxi_cargo_finance,
        claim_id,
        default_uid,
        default_login,
        default_reason,
):
    url = '/admin/cargo-finance/pay/order/change-compensation'

    async def wrapper(
            operation_token,
            need_compensation,
            extra_sum=None,
            flow='claims',
            uid=None,
            login=None,
    ):
        if uid is None:
            uid = default_uid
        if login is None:
            login = default_login

        params = {'flow': flow, 'entity_id': claim_id}
        headers = {'X-Yandex-Uid': uid, 'X-Yandex-Login': login}
        data = {
            'operation_token': operation_token,
            'new_decision': {'need_compensation': need_compensation},
            'reason': default_reason,
        }
        if extra_sum is not None:
            data['new_decision']['extra_sum'] = extra_sum
        response = await taxi_cargo_finance.post(
            url, params=params, headers=headers, json=data,
        )
        return response

    return wrapper


@pytest.fixture(name='request_admin_change_billing_functions_sum')
def _request_admin_change_billing_functions_sum(
        taxi_cargo_finance,
        claim_id,
        default_uid,
        default_login,
        default_reason,
):
    url = '/admin/cargo-finance/pay/order/change-billing-functions-sum'

    async def wrapper(
            operation_token, new_sum, flow='claims', uid=None, login=None,
    ):
        if uid is None:
            uid = default_uid
        if login is None:
            login = default_login

        params = {'flow': flow, 'entity_id': claim_id}
        headers = {'X-Yandex-Uid': uid, 'X-Yandex-Login': login}
        data = {
            'operation_token': operation_token,
            'new_sum': new_sum,
            'reason': default_reason,
        }
        response = await taxi_cargo_finance.post(
            url, params=params, headers=headers, json=data,
        )
        return response

    return wrapper


@pytest.fixture(name='request_admin_retry_hold')
def _request_admin_retry_hold(
        taxi_cargo_finance, claim_id, default_uid, default_login, default_flow,
):
    url = '/admin/cargo-finance/pay/order/retry-hold'

    async def wrapper(operation_token, flow=None, uid=None, login=None):
        if flow is None:
            flow = default_flow
        if uid is None:
            uid = default_uid
        if login is None:
            login = default_login

        params = {'flow': flow, 'entity_id': claim_id}
        headers = {'X-Yandex-Uid': uid, 'X-Yandex-Login': login}
        data = {'operation_token': operation_token}
        response = await taxi_cargo_finance.post(
            url, params=params, headers=headers, json=data,
        )
        return response

    return wrapper


#  #################
#  External handlers


@pytest.fixture(name='mock_upsert')
def _mock_upsert(mockserver, upsert_response):
    url = '/cargo-finance/internal/cargo-finance/pay/order/transactions/upsert'

    @mockserver.json_handler(url)
    def handler(request):
        return upsert_response.make(request)

    return handler


@pytest.fixture(name='upsert_response')
def _upsert_response():
    class UpsertResponse:
        def __init__(self):
            self.data = {}

        def set(self, data):
            self.data = data

        def make(self, request):
            return self.data

    return UpsertResponse()


@pytest.fixture(name='mock_debt')
def _mock_debt(mockserver, debt_response):
    url = '/cargo-finance/internal/cargo-finance/pay/order/transactions/debt'

    @mockserver.json_handler(url)
    def handler(request):
        return debt_response.make(request)

    return handler


@pytest.fixture(name='debt_response')
def _debt_response():
    class DebtResponse:
        def __init__(self):
            self.data = {}

        def set(self, data):
            self.data = data

        def make(self, request):
            return self.data

    return DebtResponse()


@pytest.fixture(name='mock_retrieve')
def _mock_retrieve(mockserver, retrieve_response):
    url = (
        '/cargo-finance/internal/cargo-finance/pay/order/transactions/retrieve'
    )

    @mockserver.json_handler(url)
    def handler(request):
        return retrieve_response.make(request)

    return handler


@pytest.fixture(name='retrieve_response')
def _retrieve_response():
    class RetrieveResponse:
        def __init__(self):
            self.data = {}

        def set(self, data):
            self.data = data

        def make(self, request):
            return self.data

    return RetrieveResponse()


@pytest.fixture(name='flush_all')
def _flush_all(
        stq,
        mock_procaas_create,
        mock_procaas_events,
        mock_upsert,
        mock_debt,
        mock_retrieve,
):
    def wrapper():
        mock_procaas_create.flush()
        mock_procaas_events.flush()
        mock_upsert.flush()
        mock_debt.flush()
        mock_retrieve.flush()
        stq.cargo_finance_pay_applying.flush()

    return wrapper


@pytest.fixture(autouse=True)
def _setup_environment(
        mock_procaas_create,
        mock_procaas_events,
        mock_upsert,
        upsert_response,
        mock_debt,
        debt_response,
        mock_retrieve,
        retrieve_response,
):
    pass


#  #############################
#  constants


@pytest.fixture(name='default_flow')
def _default_flow():
    return 'claims'


@pytest.fixture(name='default_uid')
def _default_uid():
    return 'myuid'


@pytest.fixture(name='default_login')
def _default_login():
    return 'mylogin'


@pytest.fixture(name='default_reason')
def _default_reason():
    return {'st_ticket': 'CHATTERBOX-777', 'comment': 'no-comment'}


@pytest.fixture(name='new_card')
def _new_card():
    return {'cardstorage_id': 'card-456', 'owner_yandex_uid': 'yandex_uid-654'}


@pytest.fixture(name='old_card')
def _old_card(load_json):
    sum2pay = load_json('sum2pay_can_hold.json')
    return sum2pay['client']['agent']['payment_methods']['card']

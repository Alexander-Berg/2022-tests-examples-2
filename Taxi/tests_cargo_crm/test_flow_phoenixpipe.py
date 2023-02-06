import pytest

from tests_cargo_crm import const


URL_PREFIX = '/internal/cargo-crm/flow/phoenixpipe/ticket'
PROCAAS_URLPATH = '/processing/v1/cargo/crm_flow_phoenixpipe/create-event'

PHOENIX_EVENT_ID = '77777777777777777777777777777777'

PIPEDRIVE_ACCOUNT = {'deal_id': 1, 'org_id': 2, 'person_id': 3}
ACTIVITY_ID = 4

KIND_INIT = 'init'
KIND_PHOENIX_TICKET_UPDATED = 'phoenix_ticket_updated'
KIND_PIPEDRIVE_ACCOUNT_CREATED = 'pipedrive_account_created'
KIND_PIPEDRIVE_TASK_SET = 'pipedrive_task_set'

STEP_INITIAL_FORM = 'initial_form'
STEP_COMPANY_CREATED_FORM = 'company_created_form'


async def test_initial_event(call_phoenixpipe, get_procaas_request):
    await call_phoenixpipe('init', {})

    request = get_procaas_request()
    assert _token(request) == const.TICKET_ID
    assert request.json == {'kind': KIND_INIT, 'data': {}}


async def test_acc_created_event(call_phoenixpipe, get_procaas_request):
    data = {'pipedrive_account': PIPEDRIVE_ACCOUNT}
    await call_phoenixpipe('notify-pipedrive-account-created', data)

    request = get_procaas_request()
    expected_token = 'pipe-acc-created:{}'.format(PIPEDRIVE_ACCOUNT['org_id'])
    assert _token(request) == expected_token
    assert request.json == {
        'kind': KIND_PIPEDRIVE_ACCOUNT_CREATED,
        'data': data,
    }


async def test_task_is_set(call_phoenixpipe, get_procaas_request):
    data = {'pipedrive_activity_id': ACTIVITY_ID}
    await call_phoenixpipe('notify-pipedrive-task-set', data)

    request = get_procaas_request()
    expected_token = 'activity-created:{}'.format(ACTIVITY_ID)
    assert _token(request) == expected_token
    assert request.json == {'kind': KIND_PIPEDRIVE_TASK_SET, 'data': data}


@pytest.mark.parametrize(
    'phoenix_step,corp_client_id',
    [
        (STEP_INITIAL_FORM, None),
        (STEP_COMPANY_CREATED_FORM, const.CORP_CLIENT_ID),
    ],
)
async def test_phoenix_ticket_changed(
        call_phoenixpipe, get_procaas_request, phoenix_step, corp_client_id,
):
    request_data = {
        'phoenix_step_passed': phoenix_step,
        'phoenix_event_id': PHOENIX_EVENT_ID,
    }
    await call_phoenixpipe(
        'notify-phoenix-ticket-updated',
        request_data,
        corp_client_id=corp_client_id,
    )

    request = get_procaas_request()
    assert _token(request) == PHOENIX_EVENT_ID

    event_data = {
        'phoenix_step': phoenix_step,
        'phoenix_event_id': PHOENIX_EVENT_ID,
    }
    if corp_client_id is not None:
        event_data['corp_client_id'] = corp_client_id
    assert request.json == {
        'kind': KIND_PHOENIX_TICKET_UPDATED,
        'data': event_data,
    }


@pytest.fixture(name='get_procaas_request')
def _get_procaas_request(procaas_handler_create_event):
    def wrapper(expected_times_called=1):
        times_called = procaas_handler_create_event.times_called
        assert times_called == expected_times_called

        request = procaas_handler_create_event.next_call()['request']
        assert request.method == 'POST'
        assert request.path == PROCAAS_URLPATH
        assert request.query['item_id'] == const.TICKET_ID

        return request

    return wrapper


@pytest.fixture(name='call_phoenixpipe')
def _call_phoenixpipe(taxi_cargo_crm):
    async def wrapper(url_ending, data, corp_client_id=None):
        params = {'ticket_id': const.TICKET_ID}
        if corp_client_id is not None:
            params['corp_client_id'] = corp_client_id
        response = await taxi_cargo_crm.post(
            _url(url_ending), params=params, json=data,
        )
        assert response.status_code == 200
        return response

    return wrapper


@pytest.fixture(autouse=True)
def _setup_env(procaas_handler_create_event):
    pass


def _url(ending):
    return '{}/{}'.format(URL_PREFIX, ending)


def _token(request):
    return request.headers['X-Idempotency-Token']

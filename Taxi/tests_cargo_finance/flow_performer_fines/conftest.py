import dateutil.parser
import pytest

from testsuite.utils import matching


UID = '1111'
LOGIN = 'ya1111'


@pytest.fixture(name='recently')
async def _recently(mocked_time, taxi_cargo_finance):
    now = '2021-02-13T11:00:10+00:00'
    mocked_time.set(dateutil.parser.parse(now))
    await taxi_cargo_finance.invalidate_caches()
    return now


@pytest.fixture(name='admin_fines_state')
def _admin_fines_state(taxi_cargo_finance, load_json):
    async def _wrapper(
            taxi_order_id,
            yandex_uid,
            performer_index=0,
            performers_path='performers.json',
    ):
        params = {'taxi_order_id': taxi_order_id}
        if performer_index >= 0:
            performer = load_json(performers_path)[performer_index]
            params = {
                'taxi_order_id': taxi_order_id,
                'park_id': performer['park_id'],
                'driver_uuid': performer['driver_uuid'],
            }
        headers = {'X-Yandex-Uid': str(yandex_uid)}
        response = await taxi_cargo_finance.get(
            '/admin/cargo-finance/performer/fines/state',
            params=params,
            headers=headers,
        )
        return response

    return _wrapper


@pytest.fixture(name='get_admin_fines_state')
def _get_admin_fines_state(admin_fines_state, order_proc):
    async def _wrapper(
            x_uid=1111, performer_index=0, performers_path='performers.json',
    ):
        response = await admin_fines_state(
            order_proc['_id'], x_uid, performer_index, performers_path,
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='get_total_admin_fines_state')
def _get_total_admin_fines_state(admin_fines_state, order_proc):
    async def _wrapper(x_uid=1111):
        response = await admin_fines_state(order_proc['_id'], x_uid, -1)
        assert response.status_code == 200
        return response.json()

    return _wrapper


def construct_events(path, performers_path, load_json):
    performers = load_json(performers_path)
    result_events = {}
    for performer in performers:
        alias_id = performer['alias_id']
        events = load_json(path)
        for event in events:
            if event['payload']['kind'] == 'dummy_init':
                continue
            data = event['payload']['data']
            if 'operation_id' in data:
                data['operation_id'] += alias_id
            if event['payload']['kind'] == 'update_fine_request':
                data['order_info']['taxi_alias_id'] = alias_id
        result_events[alias_id] = events
    return result_events


@pytest.fixture(name='inject_events')
def _inject_events(load_json, procaas_events_response):
    def mock(path='processing_events.json', performers_path='performers.json'):
        procaas_events_response.events = construct_events(
            path, performers_path, load_json,
        )

    return mock


def operation_id_append_alias(decision, performer: dict):
    decision['operation_id'] += performer['alias_id']


@pytest.fixture(name='expected_decisions')
def _expected_decisions(load_json, procaas_events_response):
    def mock(
            path='order_fines_state.json',
            performers_path='performers.json',
            performer_index=0,
    ):
        state = load_json(path)
        performer = load_json(performers_path)[performer_index]
        if 'decisions' in state:
            for decision in state['decisions']:
                operation_id_append_alias(decision, performer)
        if 'pending_decisions' in state:
            for decision in state['pending_decisions']:
                operation_id_append_alias(decision, performer)
        return state

    return mock


@pytest.fixture(name='drop_events')
def _drop_events(procaas_events_response):
    def wrap():
        procaas_events_response.events = []

    return wrap


@pytest.fixture(name='get_disable_reason')
def _get_disable_reason(admin_fines_state, order_proc):
    async def _wrapper(order_id=None, x_uid='1111'):
        if order_id is None:
            order_id = order_proc['_id']

        response = await admin_fines_state(order_id, x_uid)
        assert response.status_code == 200
        new_decision = response.json()['new_decision']
        assert 'disable_reason' in new_decision
        return new_decision['disable_reason']

    return _wrapper


def recursive_dict_check(x, y):
    for key, value in x.items():
        if isinstance(value, dict):
            recursive_dict_check(value, y[key])
        else:
            if key == 'operation_id':
                assert value == matching.AnyString()
                continue
            assert value == y[key]


@pytest.fixture(name='check_payload')
def _check_payload():
    def wrap(payload, source):
        recursive_dict_check(payload, source)

    return wrap


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind, path='processing_events.json'):
        for event in load_json(path):
            if event['event_id'] == event_kind:
                return event
        template = 'event event_id={} not found in processing_events.json'
        raise ValueError(template.format(event_kind))

    return wrapper


@pytest.fixture(name='mock_cargo_finance_dummy_init', autouse=True)
async def _mock_cargo_finance_dummy_init(taxi_cargo_finance, mockserver):
    url = 'cargo-finance/internal/cargo-finance/events/dummy-init'

    @mockserver.json_handler(url)
    async def handler(request):
        params = {'entity_id': 'alias_id_1', 'flow': 'performer_fines'}
        response = await taxi_cargo_finance.post(
            '/internal/cargo-finance/events/dummy-init', params=params,
        )
        assert response.status_code == 200
        return {}

    return handler


@pytest.fixture(name='admin_update_fine')
def _admin_update_fine(taxi_cargo_finance):
    async def _wrapper(
            request_body, order_id, alias_id, yandex_uid, yandex_login,
    ):
        params = {'taxi_order_id': order_id, 'taxi_alias_id': alias_id}
        headers = {
            'X-Yandex-Uid': str(yandex_uid),
            'X-Yandex-Login': yandex_login,
        }
        response = await taxi_cargo_finance.post(
            '/admin/cargo-finance/performer/fines/update-fine',
            params=params,
            headers=headers,
            json=request_body,
        )
        return response

    return _wrapper


@pytest.fixture(name='admin_send_request')
def _admin_send_request(admin_update_fine, order_proc):
    async def _wrapper(request_body):
        response = await admin_update_fine(
            request_body, order_proc['_id'], 'alias_id_1', UID, LOGIN,
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='admin_send_request_409_json')
def _admin_send_request_409_json(admin_update_fine, order_proc):
    async def _wrapper(request_body, order_id=None):
        if order_id is None:
            order_id = order_proc['_id']
        response = await admin_update_fine(
            request_body, order_id, 'alias_id_1', UID, LOGIN,
        )
        assert response.status_code == 409
        return response.json()

    return _wrapper


@pytest.fixture(name='admin_send_request_400_json')
def _admin_send_request_400_json(admin_update_fine, order_proc):
    async def _wrapper(request_body, operation_token='INVALID'):
        request_body['operation_token'] = operation_token
        response = await admin_update_fine(
            request_body, order_proc['_id'], 'alias_id_1', UID, LOGIN,
        )
        assert response.status_code == 400
        return response.json()

    return _wrapper


@pytest.fixture(name='request_body_from_payload')
def _request_body_from_payload():
    def _wrapper(payload, token=None):
        request_body = {
            'decision': payload['data']['decision'],
            'reason': {'st_ticket': payload['data']['st_ticket']},
        }
        if token is not None:
            request_body['operation_token'] = token
        if 'comment' in payload['data']:
            request_body['reason']['comment'] = payload['data']['comment']
        return request_body

    return _wrapper

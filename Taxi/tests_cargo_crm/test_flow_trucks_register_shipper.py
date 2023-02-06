import pytest

EXTERNAL_REF = 'external_ref_1'

CARRIER = 'carrier'
CARRIERS = 'carriers'
SHIPPER = 'shipper'
SHIPPERS = 'shippers'


@pytest.mark.parametrize(
    ['state_response', 'expected_status'],
    (
        pytest.param('state_fail_registration.json', 'failed', id='failed'),
        pytest.param('state_successful_registration.json', 'done', id='done'),
        pytest.param(
            'state_new_attempt_started.json', 'processing', id='processing',
        ),
    ),
)
@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_states_interpretation(
        taxi_cargo_crm,
        mockserver,
        state_response,
        expected_status,
        entity,
        load_json,
):
    @mockserver.json_handler(
        f'/cargo-crm/internal/cargo-crm/flow/trucks_register_{entity}/state',
    )
    def dummy_mock(request):
        return mockserver.make_response(
            status=200, json=load_json(state_response),
        )

    response = await taxi_cargo_crm.post(
        f'/internal/cargo-crm/flow/trucks_register_{entity}/state-interpretaion'
        '?external_ref=123',
    )
    assert response.status_code == 200
    assert response.json()['status'] == expected_status


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_empty_state(
        get_state, shippers_find_response, mock_procaas_create, entity,
):
    shippers_find_response.shippers = []
    state = await get_state(entity)
    assert state == {'actions': {'start_registration': {'is_hidden': False}}}


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_after_successful_init(
        get_state,
        procaas_events_response,
        shippers_find_response,
        load_json,
        entity,
):
    shippers_find_response.shippers = []
    procaas_events_response.set('first_request')
    state = await get_state(entity)
    assert state == load_json('state_after_init.json')


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_before_resolution_sent(
        get_state, procaas_events_response, load_json, entity,
):
    procaas_events_response.set('first_request')
    state = await get_state(entity)

    expected_state = load_json('state_after_init.json')
    successful = load_json('state_successful_registration.json')
    expected_state['actions'] = successful['actions']
    expected_state['billing_data'] = successful['billing_data']

    assert state == expected_state


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_after_successful_resolution(
        get_state, procaas_events_response, load_json, entity,
):
    procaas_events_response.set('first_request', 'first_resolution')
    state = await get_state(entity)
    assert state == load_json('state_successful_registration.json')


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_resolution_failed(
        get_state,
        procaas_events_response,
        shippers_find_response,
        load_json,
        entity,
):
    shippers_find_response.shippers = []
    procaas_events_response.set('first_request', 'first_resolution_fail')
    state = await get_state(entity)
    assert state == load_json('state_fail_registration.json')


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_after_new_attempt(
        get_state,
        procaas_events_response,
        shippers_find_response,
        load_json,
        entity,
):
    shippers_find_response.shippers = []
    procaas_events_response.set(
        'first_request', 'first_resolution_fail', 'second_request',
    )
    state = await get_state(entity)
    assert state == load_json('state_new_attempt_started.json')


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_state_when_shipper_created_outside_crm(
        get_state, load_json, entity,
):
    state = await get_state(entity)
    successful = load_json('state_successful_registration.json')
    assert state == {
        'actions': successful['actions'],
        'billing_data': successful['billing_data'],
    }


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_get_state_find_shipper_request(
        get_state, mock_shippers_find, entity,
):
    await get_state(entity)

    assert mock_shippers_find.times_called == 1
    request = mock_shippers_find.next_call()['request']
    assert request.path.count(entity)
    assert request.query == {'external_ref': EXTERNAL_REF}


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_get_state_fetch_events_request(
        get_state, mock_procaas_events, entity,
):
    await get_state(entity)

    assert mock_procaas_events.times_called == 1
    request = mock_procaas_events.next_call()['request']
    assert request.path.count(entity)
    assert request.query == {'item_id': EXTERNAL_REF}


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_successful_init_calls_shipper(
        provide_successful_init, mock_shippers_find, entity,
):
    await provide_successful_init(entity)
    assert mock_shippers_find.times_called == 1


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_successful_init_fetches_events_twice(
        provide_successful_init, mock_procaas_events, entity,
):
    await provide_successful_init(entity)
    # need refetch events to ensure request is acccepted
    assert mock_procaas_events.times_called == 2


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_successful_init_sends_event(
        provide_successful_init, mock_procaas_create, entity,
):
    await provide_successful_init(entity)
    assert mock_procaas_create.times_called == 1


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_init_idempotency(
        request_init,
        procaas_events_response,
        mock_procaas_create,
        mock_procaas_events,
        entity,
):
    procaas_events_response.set('first_request')
    response = await request_init(entity, 'first_request')
    assert response.status_code == 200

    # it doesn't send request again
    assert not mock_procaas_create.has_calls
    # so no need to call /events twice to ensure that request is accepted
    assert mock_procaas_events.times_called == 1


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_init_conflict(request_init, procaas_events_response, entity):
    procaas_events_response.set('first_request')
    response = await request_init(entity, 'second_request')
    assert response.status_code == 409
    assert response.json() == {
        'code': 'conflict',
        'message': 'registration is in process',
        'details': {},
    }


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_init_another_conflict(request_init, load_json, entity):
    # do nothing if shipper exists
    response = await request_init(entity, 'first_request')
    assert response.status_code == 409
    actions = load_json('state_successful_registration.json')['actions']
    assert response.json() == actions['start_registration']['disable_reason']


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_init_checks_country_code(request_init, procaas_events, entity):
    event_data = procaas_events['first_request']['payload']['data']
    event_data['request']['country'] = 515

    response = await request_init(entity, 'first_request')
    assert response.status_code == 400
    assert response.json() == {
        'code': 'country_not_supported',
        'message': 'country not supported',
        'details': {},
    }


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
async def test_init_checks_currency(request_init, procaas_events, entity):
    event_data = procaas_events['first_request']['payload']['data']
    event_data['request']['currency'] = 'XXX'

    response = await request_init(entity, 'first_request')
    assert response.status_code == 400
    assert response.json() == {
        'code': 'currency_not_supported',
        'message': 'currency not supported',
        'details': {},
    }


@pytest.mark.parametrize('entity', [SHIPPER, CARRIER])
@pytest.mark.parametrize(
    'event_id', ['first_resolution', 'first_resolution_fail'],
)
async def test_send_resolution_as_is(
        mock_procaas_create, send_resolution, procaas_events, event_id, entity,
):
    await send_resolution(entity, event_id)
    event_payload = procaas_events.get_or_error(event_id)['payload']
    event_data = event_payload['data']
    idempotency_token = 'resolution/{}'.format(event_data['operation_id'])

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count(entity)
    assert request.query == {'item_id': EXTERNAL_REF}
    assert request.headers['X-Idempotency-Token'] == idempotency_token
    assert request.json == event_payload


@pytest.fixture(name='provide_successful_init')
def _provide_successful_init(
        request_init, shippers_find_response, set_events_after_create, entity,
):
    async def wrapper(entity):
        shippers_find_response.shippers = []
        set_events_after_create('first_request')
        response = await request_init(entity, 'first_request')
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='get_state')
def _get_state(taxi_cargo_crm):
    url_template = '/internal/cargo-crm/flow/trucks_register_{}/state'

    async def wrapper(entity):
        url = url_template.format(entity)
        params = {'external_ref': EXTERNAL_REF}
        response = await taxi_cargo_crm.post(url, params=params)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_init')
def _request_init(taxi_cargo_crm, procaas_events):
    url_template = '/internal/cargo-crm/flow/trucks_register_{}/init'

    async def wrapper(entity, event_id):
        url = url_template.format(entity)

        event = procaas_events.get_or_error(event_id)
        payload_data = event['payload']['data']

        params = {'external_ref': EXTERNAL_REF}
        headers = {'X-Idempotency-Token': payload_data['operation_id']}
        data = payload_data['request']
        response = await taxi_cargo_crm.post(
            url, params=params, headers=headers, json=data,
        )
        return response

    return wrapper


@pytest.fixture(name='send_resolution')
def _send_resolution(taxi_cargo_crm, procaas_events):
    url_template = '/internal/cargo-crm/flow/trucks_register_{}/resolution'

    async def wrapper(entity, event_id):
        url = url_template.format(entity)
        event = procaas_events.get_or_error(event_id)
        payload_data = event['payload']['data']

        params = {'external_ref': EXTERNAL_REF}
        response = await taxi_cargo_crm.post(
            url, params=params, json=payload_data,
        )
        return response

    return wrapper


@pytest.fixture(name='procaas_events')
def _procaas_events(load_json):
    class AllEventsMap(dict):
        def get_or_error(self, event_id):
            if event_id not in self:
                template = 'event_id={} not found in procaas_events.json'
                raise ValueError(template.format(event_id))
            return self[event_id]

    all_events_map = AllEventsMap()

    for event in load_json('procaas_events.json'):
        event_id = event['event_id']
        if event_id in all_events_map:
            raise ValueError(
                'duplicate event_id={} in procaas_events.json'.format(
                    event_id,
                ),
            )
        all_events_map[event_id] = event

    return all_events_map


@pytest.fixture(name='procaas_events_response')
def _procaas_events_resposne(procaas_events):
    class ProcaasEventsResponse:
        def __init__(self):
            self.events = []

        def set(self, *event_ids):
            self.events = []
            for event_id in event_ids:
                self.events.append(procaas_events.get_or_error(event_id))

        def make(self, request):
            return {'events': self.events}

    return ProcaasEventsResponse()


@pytest.fixture(name='mock_procaas_events')
def _mock_procaas_events(mockserver, procaas_events_response):
    url = r'/processing/v1/cargo/crm_trucks_register_(?P<entity>\w+)/events'

    @mockserver.json_handler(url, regex=True)
    def handler(request, entity):
        return procaas_events_response.make(request)

    return handler


@pytest.fixture(name='mock_procaas_create')
def _mock_procaas_create(mockserver):
    # pylint: disable=E1102

    url = (
        r'/processing/v1/cargo/crm_trucks_register_(?P<entity>\w+)'
        r'/create-event'
    )

    callback_container = {'callback': None}

    @mockserver.json_handler(url, regex=True)
    def handler(request, entity):
        if callback_container['callback']:
            callback_container['callback'](request)

        idempotency_token = request.headers['X-Idempotency-Token']
        return {'event_id': idempotency_token}

    def set_callback(callback):
        callback_container['callback'] = callback

    handler.set_callback = set_callback

    return handler


@pytest.fixture(name='shippers_find_response')
def _shippers_find_response(load_json):
    class ShippersFindResponse:
        def __init__(self):
            self.shippers = [load_json('shipper.json')]

        def make(self, request):
            if request.path.count(CARRIER):
                key = CARRIERS
            elif request.path.count(SHIPPER):
                key = SHIPPERS
            return {key: self.shippers}

    return ShippersFindResponse()


@pytest.fixture(name='mock_shippers_find')
def _mock_shippers_find(mockserver, shippers_find_response):
    url = r'/cargo-trucks/internal/cargo-trucks/(?P<entities>\w+)/find'

    @mockserver.json_handler(url, regex=True)
    def handler(request, entities):
        return shippers_find_response.make(request)

    return handler


@pytest.fixture(name='set_events_after_create')
def _set_events_after_create(procaas_events_response, mock_procaas_create):
    def wrapper(*event_ids):
        def callback(request):
            procaas_events_response.set(*event_ids)

        mock_procaas_create.set_callback(callback)

    return wrapper


@pytest.fixture(name='flush_all')
def _flush_all(mock_procaas_events, mock_procaas_create, mock_shippers_find):
    def wrapper():
        mock_procaas_events.flush()
        mock_procaas_create.flush()
        mock_shippers_find.flush()

    return wrapper


@pytest.fixture(autouse=True)
def _setup_environment(
        mock_procaas_events, mock_procaas_create, mock_shippers_find,
):
    pass

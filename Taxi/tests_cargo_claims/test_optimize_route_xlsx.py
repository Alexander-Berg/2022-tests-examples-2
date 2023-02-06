# pylint: disable=redefined-outer-name,redefined-builtin,invalid-name
# pylint: disable=too-many-lines
# MVRP takes 'id' parameter, which triggers the last 2 warnings
import datetime
import json
import urllib.parse

import pytest

ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
NOW = datetime.datetime(2020, 4, 20, 0, 0, 0)
NOW_STR = NOW.strftime(ISO_FORMAT)
geocoder_addr_error_message = (
    'Не удалось преобразовать адрес в координаты: '
    'проверьте корректность адреса'
)


@pytest.fixture
def get_start_headers(get_default_headers):
    def wrapped(*args, **kwargs):
        headers = get_default_headers(*args, **kwargs)
        headers[
            'Content-Type'
        ] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        headers['X-Idempotency-Token'] = '12345'
        return headers

    return wrapped


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_optimize_route_vehicle',
    consumers=['cargo-claims/optimize-route'],
    clauses=[],
    default_value={'unit_load': 10, 'routing_mode': 'truck'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_optimize_route_penalty',
    consumers=['cargo-claims/optimize-route'],
    clauses=[],
    default_value={
        'location': {'early': {'fixed': 100}},
        'depot': {'throughput': {'fixed': 1000}},
    },
)
@pytest.mark.parametrize(
    ['masking', 'expected_suffix'], ([['author_login'], '_id_pd'], [[], '']),
)
@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_200(
        taxi_cargo_claims,
        taxi_config,
        mockserver,
        load,
        load_json,
        yamaps,
        get_start_headers,
        stq_runner,
        stq,
        pgsql,
        async_xlsx_start,
        yamaps_get_geo_objects,
        mock_cargo_matcher,
        masking,
        expected_suffix,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    taxi_config.set_values(
        {'CARGO_CLAIMS_PERSONAL_DATA_MASKING': {'masking': masking}},
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'

        expected_request = load_json('b2bgeo_request.json')
        request.json['options']['incompatible_load_types'] = sorted(
            sorted(x)
            for x in request.json['options']['incompatible_load_types']
        )
        expected_request['options']['incompatible_load_types'] = sorted(
            sorted(x)
            for x in expected_request['options']['incompatible_load_types']
        )
        for vehicle, expected in zip(
                request.json['vehicles'], expected_request['vehicles'],
        ):
            assert vehicle['id'].startswith(expected['id'])
            vehicle.pop('id')
            expected.pop('id')
        assert request.json == expected_request
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
            status=202,
        )

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )
    assert response.status == 200
    assert response.headers['Content-Type'].startswith('application/json')

    # call twice - check idempotency token
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )
    assert response.status == 200

    task_id = '12345' if not async_xlsx_start else response.json()['id']
    assert task_id

    queue = (
        stq.cargo_claims_optimize_route_get_result
        if not async_xlsx_start
        else stq.cargo_claims_xlsx_start_run_geocoders
    )
    assert queue.times_called == 1
    assert queue.next_call()['id'] == task_id

    if async_xlsx_start:
        await stq_runner.cargo_claims_xlsx_start_run_geocoders.call(
            task_id=task_id, args=[task_id],
        )

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
    SELECT
    task_id, author_login, idempotency_token,
    status, corp_client_id, request_json, user_locale, api_kind, b2bgeo_task_id
    FROM cargo_claims.optimization_tasks
    WHERE task_id='{}'
        """.format(
            task_id,
        ),
    )
    result = list(cursor)[0]
    assert result[0] == task_id
    assert result[1] == 'abacaba' + expected_suffix
    assert result[2] == '12345'
    assert result[3] == 'queued'
    assert result[4] == '01234567890123456789012345678912'
    assert result[5] == load_json('parsed_ok_xlsx.json')
    assert result[6] == 'en'
    assert result[7] == 'api'
    assert result[8] == '12345'


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_no_data(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/start',
        headers=get_start_headers(),
    )
    assert response.status == 400
    response = response.json()
    assert response['code'] == 'parse_error'
    assert (
        response['message'] == 'Не удалось открыть XLSX файл: уберите из '
        'документа ссылки и проверьте корректность формата'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_claims_use_google_geocoder',
    consumers=['cargo-claims/cargo-claims-xlsx-start-run-geocoders'],
    clauses=[],
    default_value={
        'enabled': False,
        'correct_google_geo_precision': ['ROOFTOP'],
    },
)
@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_yamaps_geocoder_failed(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        async_xlsx_start,
        get_default_headers,
        load_json,
        mockserver,
        stq,
        stq_runner,
        yamaps,
        mock_cargo_matcher,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        assert request.args.get('ms') == 'pb'
        assert request.args.get('type') == 'geo'
        return []

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
            status=202,
        )

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        assert False

    @mockserver.json_handler('/google-geocoder/geocode/json')
    def _mock_google_geo(request):
        assert False

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )

    def check_response(resp):
        assert resp.status == 400
        resp_json = resp.json()
        assert resp_json['code'] == 'bad_request'
        assert resp_json['message'] == geocoder_addr_error_message

    if not async_xlsx_start:
        check_response(response)
        return

    assert response.status == 200
    assert response.headers['Content-Type'].startswith('application/json')

    task_id = '12345' if not async_xlsx_start else response.json()['id']
    assert task_id

    queue = (
        stq.cargo_claims_optimize_route_get_result
        if not async_xlsx_start
        else stq.cargo_claims_xlsx_start_run_geocoders
    )
    assert queue.times_called == 1
    assert queue.next_call()['id'] == task_id

    if async_xlsx_start:
        await stq_runner.cargo_claims_xlsx_start_run_geocoders.call(
            task_id=task_id, args=[task_id],
        )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=get_default_headers(),
        json={'id': task_id},
    )

    check_response(response)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_claims_use_google_geocoder',
    consumers=['cargo-claims/cargo-claims-xlsx-start-run-geocoders'],
    clauses=[],
    default_value={
        'enabled': True,
        'correct_google_geo_precision': ['ROOFTOP'],
    },
)
@pytest.mark.parametrize(
    'google_problem, code, status, message',
    [
        ('ZERO_RESULTS', 400, 'bad_request', geocoder_addr_error_message),
        ('OVER_QUERY_LIMIT', 200, '', ''),
        ('OK', 200, '', ''),
        ('500', 400, 'bad_request', geocoder_addr_error_message),
    ],
)
async def test_start_google_after_yamaps_failed(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        get_default_headers,
        load_json,
        mockserver,
        stq,
        stq_runner,
        yamaps,
        google_problem,
        code,
        status,
        message,
        mock_cargo_matcher,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=True)

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        assert request.args.get('ms') == 'pb'
        assert request.args.get('type') == 'geo'
        return []

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
            status=202,
        )

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        requests = request.json['requests']
        assert request.args['service'] == 'api-google-geocoder-limiter'
        assert len(requests) == 1
        assert requests[0]['resource'] == 'api-google-geocoder-unique-name'
        assert requests[0]['limit'] == 50
        assert requests[0]['interval'] == 1
        return {
            'quotas': [
                {
                    'resource': 'api-google-geocoder-unique-name',
                    'assigned-quota': 3,
                },
            ],
        }

    @mockserver.json_handler('/google-geocoder/geocode/json')
    def _mock_google_geo(request):
        assert request.query['key'] == 'google-geocoder-api-key'
        assert request.query['language'] == 'en'
        assert request.query['address'] == 'Москва, Пятницкое шоссе, 23к2'
        if google_problem == 'ZERO_RESULTS':
            assert _rps_quotas.times_called == 1
            assert _mock_google_geo.times_called == 0
            return {'status': google_problem, 'results': []}
        if google_problem == 'OVER_QUERY_LIMIT':
            if _mock_google_geo.times_called == 1:
                assert _rps_quotas.times_called == 2
                return load_json('google_response.json')
            assert _rps_quotas.times_called == 1
            assert _mock_google_geo.times_called == 0
            return {'status': google_problem, 'results': []}
        if google_problem == 'OK':
            assert _rps_quotas.times_called == 1
            assert _mock_google_geo.times_called == 0
            return load_json('google_response.json')
        assert _rps_quotas.times_called == 1
        assert _mock_google_geo.times_called == 0
        return mockserver.make_response(
            json={'status': 'FAILED', 'message': 'error'}, status=500,
        )

    # ATTENTION: xlsx input data not related to response for this test
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )

    assert response.status == 200
    assert response.headers['Content-Type'].startswith('application/json')

    task_id = response.json()['id']
    assert task_id

    queue = stq.cargo_claims_xlsx_start_run_geocoders
    assert queue.times_called == 1
    assert queue.next_call()['id'] == task_id

    await stq_runner.cargo_claims_xlsx_start_run_geocoders.call(
        task_id=task_id, args=[task_id],
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=get_default_headers(),
        json={'id': task_id},
    )

    assert response.status == code
    if code == 200:
        resp_json = response.json()['info']
        assert resp_json['status'] == 'queued'
        assert resp_json['id'] == task_id
        return

    resp_json = response.json()
    assert resp_json['code'] == status
    assert resp_json['message'] == message


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_claims_use_google_geocoder',
    consumers=['cargo-claims/cargo-claims-xlsx-start-run-geocoders'],
    clauses=[
        {
            'title': 'check',
            'value': {
                'enabled': True,
                'correct_google_geo_precision': ['ROOFTOP'],
            },
            'predicate': {
                'init': {
                    'predicate': {
                        'init': {
                            'set': ['Exact', 'Number'],
                            'arg_name': 'yamaps_geo_precision_result',
                            'set_elem_type': 'string',
                        },
                        'type': 'in_set',
                    },
                },
                'type': 'not',
            },
        },
    ],
    default_value={'enabled': False},
)
async def test_yamaps_ok_google_not_used(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        get_default_headers,
        load_json,
        mockserver,
        stq,
        stq_runner,
        yamaps,
        yamaps_get_geo_objects,
        mock_cargo_matcher,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=True)

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
            status=202,
        )

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        assert False

    @mockserver.json_handler('/google-geocoder/geocode/json')
    def _mock_google_geo(request):
        assert False

    # ATTENTION: xlsx input data not related to response for this test
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )

    assert response.status == 200
    assert response.headers['Content-Type'].startswith('application/json')

    task_id = response.json()['id']
    assert task_id

    queue = stq.cargo_claims_xlsx_start_run_geocoders
    assert queue.times_called == 1
    assert queue.next_call()['id'] == task_id

    await stq_runner.cargo_claims_xlsx_start_run_geocoders.call(
        task_id=task_id, args=[task_id],
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=get_default_headers(),
        json={'id': task_id},
    )

    assert response.status == 200
    resp_json = response.json()['info']
    assert resp_json['status'] == 'queued'
    assert resp_json['id'] == task_id


async def test_start_get_vehicles_failed(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        get_default_headers,
        load_json,
        mockserver,
        stq,
        stq_runner,
        yamaps,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=True)

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        assert request.args.get('ms') == 'pb'
        assert request.args.get('type') == 'geo'
        assert (
            urllib.parse.unquote(request.args.get('text'))
            == 'Москва, Пятницкое шоссе, 23к2'
        )
        return [load_json('yamaps_response.json')]

    @mockserver.json_handler('/cargo-matcher/v1/client-cars')
    def _mock_cargo_matcher(request):
        assert (
            request.json['corp_client_id']
            == get_start_headers()['X-B2B-Client-Id']
        )
        assert request.json['point_a'] == [37.588472, 55.733996]
        return {'cars': []}

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
            status=202,
        )

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/xlsx/start',
        data=load('ok_xlsx.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )

    assert response.status == 200
    assert response.headers['Content-Type'].startswith('application/json')

    task_id = response.json()['id']
    assert task_id

    queue = stq.cargo_claims_xlsx_start_run_geocoders
    assert queue.times_called == 1
    assert queue.next_call()['id'] == task_id

    await stq_runner.cargo_claims_xlsx_start_run_geocoders.call(
        task_id=task_id, args=[task_id],
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=get_default_headers(),
        json={'id': task_id},
    )

    assert response.status == 500


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_empty(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/start',
        data=load('empty.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )
    assert response.status == 400
    response = response.json()
    assert response['code'] == 'parse_error'
    assert response['message'] == 'В файле отсутствует лист Orders'


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_bad_header(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/start',
        data=load('bad_header.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )
    assert response.status == 400
    response = response.json()
    assert response['code'] == 'parse_error'
    assert (
        response['message']
        == 'Лист Orders: неизвестное поле заголовка в ячейке I3'
    )


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_start_missing_phone(
        taxi_cargo_claims,
        load,
        get_start_headers,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/start',
        data=load('missing_phone.xlsx', mode='rb', encoding=None),
        headers=get_start_headers(),
    )
    assert response.status == 400
    response = response.json()
    assert response['code'] == 'parse_error'
    assert (
        response['message']
        == 'Лист Orders: ячейка J4 должна содержать значение, но она пуста'
    )


def insert_task(pgsql, load_json, status='queued'):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """INSERT INTO cargo_claims.optimization_tasks (task_id,
        author_login, user_locale, idempotency_token, status,
        corp_client_id, request_json, b2bgeo_task_id)  VALUES(
        '12345', 'some_yandex_login', 'ru', 'some_idempotency_token',
        '{}', '01234567890123456789012345678912', '{}', '12345')""".format(
            status, json.dumps(load_json('parsed_ok_xlsx.json')),
        ),
    )


@pytest.mark.parametrize('status', ['queued', 'started'])
async def test_reschedule(mockserver, stq_runner, pgsql, load_json, status):
    insert_task(pgsql, load_json)

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        return mockserver.make_response(
            status=201 if status == 'started' else 202,
            json={'status': {'queued': 0, status: 0}, 'id': '12345'},
        )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    assert mock_stq_reschedule.times_called == 1

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT status FROM cargo_claims.optimization_tasks '
        'WHERE task_id=\'12345\'',
    )
    assert list(cursor)[0][0] == status


async def test_idempotency(
        mockserver, stq_runner, pgsql, load_json, state_controller,
):
    insert_task(pgsql, load_json)

    claim_info = await state_controller.apply(target_status='new')
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'UPDATE cargo_claims.claims SET '
        'idempotency_token=\'yarouting__12345__0\'',
    )

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        return load_json('b2bgeo_result.json')

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    cursor.execute('SELECT count(*) FROM cargo_claims.claims')
    assert list(cursor)[0][0] == 1
    cursor.execute(
        'SELECT status, created_claims, error_data '
        'FROM cargo_claims.optimization_tasks WHERE task_id=\'12345\'',
    )
    result = list(cursor)[0]
    assert result[0] == 'completed'
    assert result[1] == [claim_info.claim_id]
    assert result[2] == {'dropped_orders': []}


async def test_creation_success(
        taxi_cargo_claims,
        get_default_headers,
        mockserver,
        stq_runner,
        pgsql,
        load_json,
):
    insert_task(pgsql, load_json)

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        return load_json('b2bgeo_result.json')

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT count(*) FROM cargo_claims.claims')
    assert list(cursor)[0][0] == 1

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json={'offset': 0, 'limit': 2},
    )
    assert response.status == 200
    expected = load_json('created_claim.json')
    result = response.json()

    assert len(result['claims']) == len(expected)
    result_claim = result['claims'][0]
    expected_claim = expected['claims'][0]
    del result_claim['created_ts']
    del result_claim['updated_ts']
    for point in result_claim['route_points']:
        assert 'visited_at' in point
        del point['visited_at']

    created_claim_id = result_claim.pop('id')
    assert result_claim == expected_claim

    cursor.execute(
        'SELECT status, created_claims, b2bgeo_response, error_data '
        'FROM cargo_claims.optimization_tasks WHERE task_id=\'12345\'',
    )
    result = list(cursor)[0]
    assert result[0] == 'completed'
    assert result[1] == [created_claim_id]
    assert result[2] == load_json('b2bgeo_result.json')
    assert not result[3] or not result[3].get('dropped_orders')


async def test_creation_with_return(
        taxi_cargo_claims,
        get_default_headers,
        mockserver,
        stq_runner,
        pgsql,
        load_json,
):
    insert_task(pgsql, load_json)

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        result = load_json('b2bgeo_result.json')
        result['result']['routes'][0]['route'].append(
            result['result']['routes'][0]['route'][0],
        )
        return result

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT count(*) FROM cargo_claims.claims')
    assert list(cursor)[0][0] == 1

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json={'offset': 0, 'limit': 2},
    )
    assert response.status == 200
    expected = load_json('created_claim_with_return.json')
    result = response.json()

    assert len(result['claims']) == len(expected)
    result_claim = result['claims'][0]
    expected_claim = expected['claims'][0]
    del result_claim['created_ts']
    del result_claim['updated_ts']
    for point in result_claim['route_points']:
        assert 'visited_at' in point
        del point['visited_at']

    del result_claim['id']

    assert result_claim == expected_claim


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_dropped_orders(
        mockserver,
        stq_runner,
        pgsql,
        load_json,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    insert_task(pgsql, load_json)

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        return load_json('b2bgeo_partial_result.json')

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT count(*) FROM cargo_claims.claims')
    assert list(cursor)[0][0] == 0
    cursor.execute(
        'SELECT status, created_claims, error_data '
        'FROM cargo_claims.optimization_tasks WHERE task_id=\'12345\'',
    )
    result = list(cursor)[0]
    assert result[0] == 'completed'
    assert result[1] == []
    assert result[2] == {
        'dropped_orders': [
            {
                'id': 'Заказ 1224047489',
                'drop_reason': (
                    'Заказ слишком тяжелый или объемный, '
                    'или занимает слишком много слотов: '
                    'попробуйте разбить его'
                ),
            },
        ],
    }


@pytest.mark.parametrize('async_xlsx_start', [False, True])
async def test_creation_error(
        mockserver,
        stq_runner,
        pgsql,
        load_json,
        taxi_config,
        async_xlsx_start,
):
    taxi_config.set(CARGO_CLAIMS_ASYNC_XLSX_START=async_xlsx_start)
    insert_task(pgsql, load_json)

    @mockserver.json_handler(r'/b2bgeo/v1/result/mvrp/(?P<id>.+)$', regex=True)
    def mock_b2bgeo(request, id):
        assert id == '12345'
        return load_json('b2bgeo_result.json')

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_store():
        return mockserver.make_response(
            status=400, json={'code': 'validation-error', 'message': 'error'},
        )

    await stq_runner.cargo_claims_optimize_route_get_result.call(
        task_id='12345',
    )

    assert mock_b2bgeo.times_called == 1
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT count(*) FROM cargo_claims.claims')
    assert list(cursor)[0][0] == 0
    cursor.execute(
        'SELECT status, created_claims, error_data '
        'FROM cargo_claims.optimization_tasks WHERE task_id=\'12345\'',
    )
    result = list(cursor)[0]
    assert result[0] == 'completed'
    assert result[1] == []
    assert result[2] == {
        'dropped_orders': [
            {
                'id': 'Заказ 1224047489',
                'drop_reason': 'Некорректный номер телефона или email',
            },
        ],
    }


async def test_result_wrong_corp(
        taxi_cargo_claims, pgsql, load_json, get_default_headers,
):
    insert_task(pgsql, load_json)

    headers = get_default_headers(
        corp_client_id='notarealcorp34567890123456789012',
    )
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=headers,
        json={'id': '12345'},
    )

    assert response.status == 404
    assert response.json()['code'] == 'task_not_found'


@pytest.mark.parametrize(
    'created_claims,dropped_orders,status',
    [
        (None, None, 'queued'),
        ([{'id': 'claim_uuid_1'}, {'id': 'claim_uuid_2'}], None, 'completed'),
        ([], [{'id': 'order_1', 'drop_reason': 'some reason'}], 'completed'),
    ],
)
async def test_result_200(
        taxi_cargo_claims,
        pgsql,
        load_json,
        get_default_headers,
        created_claims,
        dropped_orders,
        status,
):
    insert_task(pgsql, load_json, status=status)
    cursor = pgsql['cargo_claims'].cursor()
    if dropped_orders is not None:
        cursor.execute(
            'UPDATE cargo_claims.optimization_tasks '
            'SET error_data=\'{}\''.format(
                json.dumps({'dropped_orders': dropped_orders}),
            ),
        )
    if created_claims is not None:
        cursor.execute(
            'UPDATE cargo_claims.optimization_tasks '
            'SET created_claims=\'{{{}}}\''.format(
                ','.join(f'"{x["id"]}"' for x in created_claims),
            ),
        )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/xlsx/result',
        headers=get_default_headers(),
        json={'id': '12345'},
    )

    assert response.status == 200
    response = response.json()
    assert response['info']['id'] == '12345'
    assert response['info']['status'] == status
    if status == 'completed':
        assert response['result']['created_claims'] == created_claims
        assert (
            response['result'].get('error_data', {}).get('dropped_orders')
            == dropped_orders
        )
    else:
        assert 'result' not in response

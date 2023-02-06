import datetime
import hashlib
import json
import operator
import sys

import pytest


# tvmknife unittest service -s 333 -d 2345
TVM_TICKET = (
    '3:serv:CBAQ__________9_IgYIzQIQqRI:TGmtDDKrPhzmr72y7PKTp'
    'P4HCS18oFYaPgS83z2OC3NWjNCe3fGGviJ22Qe8frjFQz9ffB0xbvVVa'
    'Z5CUqzD5HC75l2cTW_zGS1vjclfT0xmYA_ZOaic95OzICXZ1rC5kaYN3'
    '_rK1aDdplf1xLKjfn5ScyV6RMYFikASH8uJh5w'
)


async def test_exp3_matcher_empty(taxi_exp3_matcher, now):
    response = await taxi_exp3_matcher.post('/v1/experiments/', {})
    assert response.status_code == 400


async def test_exp3_matcher_empty_with_consumer(taxi_exp3_matcher, now):
    request = {'consumer': 'launch'}
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 400


async def test_exp3_matcher_empty_with_consumer_and_empty_args(
        taxi_exp3_matcher, now,
):
    request = {'consumer': 'launch', 'args': []}
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['items'] == []
    assert content['version'] == -1


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [
            {
                'name': 'android',
                'version_range': {'from': '0.0.0', 'to': '9.9.9'},
            },
        ],
    },
    clauses=[],
    default_value={'value': 9875},
)
async def test_exp3_matcher_exp_doesnt_match(
        taxi_exp3_matcher, now, experiments3,
):
    request = {
        'consumer': 'launch',
        'args': [
            {'name': 'application', 'type': 'application', 'value': 'iphone'},
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
        ],
    }

    exp3_recorder = experiments3.record_match_tries('test1')

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert content['items'] == []

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    match_tries[0].ensure_no_match()
    assert match_tries[0].kwargs['consumer'] == 'launch'
    assert match_tries[0].kwargs['application'] == 'iphone'
    assert match_tries[0].kwargs['version'] == '5.5.5'


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'value': 9875},
)
async def test_exp3_matcher_incorrect_consumer(taxi_exp3_matcher, now):
    request = {
        'consumer': 'incorrect',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'iphone'},
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 400


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'value': 9875},
)
async def test_exp3_matcher_incorrect_arg(taxi_exp3_matcher, now):
    request = {
        'consumer': 'launch',
        'args': [{'name': 'yandex_uid', 'type': 'string', 'value': None}],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 400


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'value': 9875},
)
async def test_exp3_matcher_incorrect_application_info(taxi_exp3_matcher, now):
    request = {'consumer': 'launch', 'args': []}

    response = await taxi_exp3_matcher.post(
        '/v1/experiments/',
        request,
        headers={
            'X-Request-Application': (
                'app_name=android,app_ver1=none,app_ver2=6,app_ver3=6'
            ),
        },
    )
    assert response.status_code == 400


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    trait_tags=['enable-debug'],
    clauses=[],
    default_value={'foo': 9875},
)
async def test_exp3_matcher_exp_match(taxi_exp3_matcher, now, experiments3):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    exp3_recorder = experiments3.record_match_tries('test1')

    for _ in range(3):
        response = await taxi_exp3_matcher.post('/v1/experiments/', request)
        assert response.status_code == 200
        content = response.json()
        assert len(content['items']) == 1
        assert content['items'][0]['value']['foo'] == 9875

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=3)
    for i in range(3):
        match_tries[i].ensure_matched_with_default()


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
async def test_exp3_matcher_api_key_authorize(taxi_exp3_matcher, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    response = await taxi_exp3_matcher.post(
        '/v1/experiments/',
        request,
        headers={'X-YaTaxi-API-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['foo'] == 9875


@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'experiments3'}],
)
@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
async def test_exp3_matcher_exp_match_tvm(taxi_exp3_matcher, now, load):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    response = await taxi_exp3_matcher.post(
        '/v1/experiments/',
        request,
        headers={'X-Ya-Service-Ticket': TVM_TICKET},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['foo'] == 9875


@pytest.mark.experiments3(filename='exp3_match.json')
async def test_exp3_matcher_exp_match_with_string(taxi_exp3_matcher, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {'name': 'key', 'type': 'string', 'value': 'super-key'},
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 9875


@pytest.mark.experiments3(filename='exp3_match.json')
async def test_exp3_matcher_exp_match_with_geopoint(taxi_exp3_matcher, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'point_a',
                'type': 'point',
                'value': [37.04910393749999, 55.864550814117806],
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 98754


@pytest.mark.experiments3(filename='exp3_match.json')
async def test_exp3_matcher_exp_match_with_timepoint(taxi_exp3_matcher, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'created',
                'type': 'timepoint',
                'value': '2020-02-20T20:20:20+03:00',
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 987543


@pytest.mark.experiments3(
    name='test',
    consumers=['launch'],
    match={
        'predicate': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'value': 'apple',
                            'arg_name': 'device_make',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                    {
                        'init': {
                            'value': 'iphone13.3',
                            'arg_name': 'device_model',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                ],
            },
            'type': 'all_of',
        },
        'enabled': True,
        'applications': [
            {
                'name': 'android',
                'version_range': {'from': '0.0.0', 'to': '9.9.9'},
            },
        ],
    },
    clauses=[],
    default_value={'key': 'default_value'},
)
async def test_exp3_matcher_application_header(taxi_exp3_matcher, now):
    request = {'consumer': 'launch', 'args': []}

    response = await taxi_exp3_matcher.post(
        '/v1/experiments/',
        request,
        headers={
            'X-Request-Application': (
                'app_name=android,app_ver1=6,app_ver2=6,app_ver3=6,'
                'device_make=apple,device_model=iphone13.3,'
            ),
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['key'] == 'default_value'


@pytest.mark.now('2020-07-02T08:33:44+00:00')
@pytest.mark.experiments3(filename='default_kwargs.json')
async def test_exp3_matcher_default_kwargs(taxi_exp3_matcher):
    request = {'consumer': 'launch', 'args': []}

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['name'] == 'test_default_kwargs'


def transform_decorator(country):
    return pytest.mark.experiments3(
        name='test',
        consumers=['launch'],
        match={
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'country',
                    'arg_type': 'string',
                    'value': country,
                },
            },
            'enabled': True,
        },
        clauses=[],
        default_value={'key': 'default_value'},
    )


@pytest.mark.parametrize(
    'ipaddress,preserve_src_kwargs',
    (
        pytest.param('95.59.90.0', True, marks=[transform_decorator('kz')]),
        pytest.param('185.15.98.233', True, marks=[transform_decorator('ru')]),
        pytest.param(
            '93.170.252.25', False, marks=[transform_decorator('by')],
        ),
    ),
)
async def test_exp3_matcher_transform_country_by_ip(
        taxi_exp3_matcher, ipaddress, preserve_src_kwargs, now,
):

    request = {
        'consumer': 'launch',
        'args': [{'name': 'ip', 'type': 'string', 'value': ipaddress}],
        'kwargs_transformations': [
            {
                'type': 'country_by_ip',
                'src_kwargs': ['ip'],
                'dst_kwarg': 'country',
                'preserve_src_kwargs': preserve_src_kwargs,
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['key'] == 'default_value'


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'bulk_kwarg',
                    'set': ['hit'],
                    'set_elem_type': 'string',
                },
            },
            'value': 'clause',
        },
    ],
    default_value='default',
)
async def test_exp3_matcher_experiments_bulk(taxi_exp3_matcher, now):
    request = {
        'items': [
            {
                'consumer': 'launch',
                'args': [
                    {'name': 'bulk_kwarg', 'type': 'string', 'value': 'hit'},
                ],
            },
            {
                'consumer': 'launch',
                'args': [
                    {'name': 'bulk_kwarg', 'type': 'string', 'value': 'miss'},
                ],
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/experiments/bulk/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['results']) == 2
    assert content['results'][0]['items'][0]['value'] == 'clause'
    assert content['results'][1]['items'][0]['value'] == 'default'


@pytest.mark.experiments3(
    name='disabled_clause_exp',
    consumers=['launch'],
    # match={'predicate': {'type': 'true'}, enabled=Tru},
    clauses=[
        {
            'enabled': False,
            'predicate': {'type': 'true'},
            'value': 'value_disabled_clause',
        },
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': 'value_enabled_clause',
            'alias': 'enabled_clause',
        },
    ],
)
async def test_exp3_matcher_disabled_clause(
        taxi_exp3_matcher, now, experiments3,
):
    request = {'consumer': 'launch', 'args': []}

    exp3_recorder = experiments3.record_match_tries('disabled_clause_exp')

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 'value_enabled_clause'

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    match_tries[0].ensure_matched_with_clause(1)
    match_tries[0].ensure_matched_with_clause('enabled_clause')


def exp3_hash(arg, salt):
    sha1 = hashlib.sha1()
    sha1.update(salt.encode('utf-8'))
    if isinstance(arg, str):
        sha1.update(arg.encode('utf-8'))
    elif isinstance(arg, int):
        sha1.update(arg.to_bytes(8, byteorder=sys.byteorder))
    elif isinstance(arg, datetime.datetime):
        # Cannot use `arg.timestamp()` or `arg.total_seconds()` because float
        time_since_epoch = arg - datetime.datetime.utcfromtimestamp(0)
        total_ns = (
            time_since_epoch.days * 86400 + time_since_epoch.seconds
        ) * 10 ** 9 + time_since_epoch.microseconds * 10 ** 3
        sha1.update(total_ns.to_bytes(8, byteorder=sys.byteorder))
    else:
        raise ValueError('Unknown type')
    res = sha1.hexdigest()[:16]
    return int(res, 16)


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch'],
    match={
        'predicate': {
            'type': 'segmentation',
            'init': {
                'arg_name': 'arg',
                'divisor': 100,
                'range_from': 50,
                'range_to': 100,
                'salt': 'salt',
            },
        },
        'enabled': True,
    },
    clauses=[],
    default_value={'key': 42},
)
@pytest.mark.parametrize('arg_type', ('int', 'string', 'timepoint'))
async def test_segmentation_compatible_with_python_emulation(
        arg_type, taxi_exp3_matcher, experiments3,
):
    for i in range(100):
        if arg_type == 'int':
            value = arg = i
        elif arg_type == 'string':
            value = arg = f'abacaba_{i}'
        elif arg_type == 'timepoint':
            arg = datetime.datetime(2021, 1, 19, 13, 40, 48, i)
            value = arg.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
        request = {
            'consumer': 'launch',
            'args': [{'name': 'arg', 'value': value, 'type': arg_type}],
        }
        response = await taxi_exp3_matcher.post('/v1/experiments/', request)
        assert response.status_code == 200
        content = response.json()
        if exp3_hash(arg, 'salt') % 100 >= 50:
            assert len(content['items']) == 1
            assert content['items'][0]['value']['key'] == 42
        else:
            assert not content['items'], f'Error for i={i}'


@pytest.mark.config(
    EXPERIMENTS3_COMMON_LIBRARY_SETTINGS={
        'features': {'s3_redirect_enabled': True},
        'general_settings': {
            's3_url': {'$mockserver': '/mds-s3'},
            's3_bucket': 'taxi-experiments3',
            's3_connection_timeout': 15000,
            's3_num_retries': 3,
        },
    },
)
@pytest.mark.experiments3(
    name='test',
    consumers=['launch'],
    match={
        'predicate': {
            'init': {
                'arg_name': 'some_arg',
                'file': 'file_228',
                'set_elem_type': 'string',
            },
            'type': 'in_file',
        },
        'enabled': True,
    },
    clauses=[],
    default_value={'key': 42},
)
@pytest.mark.parametrize('use_s3', ['false', 'true'])
async def test_in_file_predicate(
        taxi_exp3_matcher,
        mockserver,
        testsuite_build_dir,
        experiments3,
        use_s3,
):
    @mockserver.handler('/taxi-exp-uservices/v1/files/')
    def _mock_exp(request):
        assert request.args['id'] == 'file_228'
        if use_s3:
            assert request.args['s3_redirect_support'] == 'true'
            return mockserver.make_response('', headers={'X-Use-S3': 'true'})
        return mockserver.make_response('abacaba\nqqq\nrrr\n')

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response('abacaba\nqqq\nrrr\n')

    request = {
        'consumer': 'launch',
        'args': [{'name': 'some_arg', 'value': 'abacaba', 'type': 'string'}],
    }
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    assert response.json()['items'][0]['value']['key'] == 42

    file_dump = (
        testsuite_build_dir / 'cache' / 'exp3' / '___files' / 'file_228.string'
    )
    assert file_dump.is_file()
    with open(file_dump) as file:
        assert set(file.read().split()) == {'abacaba', 'qqq', 'rrr'}

    experiments3.add_experiment(
        name='test',
        consumers=['launch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'key': 43},
    )

    await taxi_exp3_matcher.invalidate_caches()

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    assert response.json()['items'][0]['value']['key'] == 43

    # verifies that dump is being cleared on the fly
    assert not file_dump.is_file()


@pytest.mark.now('2021-01-13T08:33:44+00:00')
@pytest.mark.config(
    EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['consumer_only_for_cache_dump_test'],
)
@pytest.mark.experiments3(
    name='test1',
    consumers=['consumer_only_for_cache_dump_test'],
    clauses=[],
    default_value={'key': 1},
)
@pytest.mark.experiments3(
    name='test2',
    consumers=['consumer_only_for_cache_dump_test'],
    clauses=[],
    default_value={'key': 2},
)
async def test_cache_dump(taxi_exp3_matcher, testsuite_build_dir):
    cache_file = (
        testsuite_build_dir
        / 'cache'
        / 'exp3'
        / 'consumer_only_for_cache_dump_test'
        / '2_2021-01-13.json'
    )
    await taxi_exp3_matcher.get('ping')

    with open(cache_file) as file:
        updates = map(json.loads, file.read().split())
        updates = sorted(updates, key=operator.itemgetter('name'))
        assert updates[0]['name'] == 'test1'
        assert updates[0]['default_value']['key'] == 1
        assert updates[1]['name'] == 'test2'
        assert updates[1]['default_value']['key'] == 2


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
async def test_exp3_matcher_match_metric(
        taxi_exp3_matcher, taxi_exp3_matcher_monitor,
):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    metrics_before = await taxi_exp3_matcher_monitor.get_metric(
        'experiments3-cache',
    )
    match_metric_before = metrics_before.get(
        'experiments3.experiment.test1.default', 0,
    )

    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200

    metrics_after = await taxi_exp3_matcher_monitor.get_metric(
        'experiments3-cache',
    )
    match_metric_after = metrics_after.get(
        'experiments3.experiment.test1.default', 0,
    )

    assert match_metric_after - match_metric_before == 1

# pylint: disable=unused-variable, redefined-outer-name
import datetime
import functools

import pytest

from eslogadminpy3.generated.service.service_schemas import (
    plugin as service_schemas,
)
from eslogadminpy3.generated.service.swagger.models import api as models
from eslogadminpy3.lib import consts
from eslogadminpy3.lib.utils import es_request


@pytest.fixture
def es_request_mock(patch):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def _search_mock(index, *args, **kwargs):
        return {'hits': {'hits': []}}

    return _search_mock


@pytest.fixture
def mock_filters(monkeypatch, load_yaml, web_app):
    schema = load_yaml('filters.yaml')
    monkeypatch.setitem(
        web_app['context'].service_schemas.schemas, 'filters', schema,
    )
    monkeypatch.setattr(
        web_app['context'].service_schemas,
        'known_filters',
        {x['name']: service_schemas.Filter(**x) for x in schema['filters']},
    )


@pytest.mark.usefixtures('es_request_mock')
async def test_filters_with_out_additions(web_app_client):
    response = await web_app_client.post(
        '/v2/logs/list/', params={'limit': 10}, json={'filters': []},
    )
    assert response.status == 200


@pytest.mark.usefixtures('es_request_mock')
@pytest.mark.parametrize(
    'filters',
    [
        [{'name': 'unknown', 'value': '10'}],
        [{'name': 'http_code', 'value': 'abc'}],
        [{'name': 'integer_array', 'value': 'a'}],
        [{'name': 'integer_array', 'value': 'a,1'}],
        [{'name': 'integer_array', 'value': '1,2,'}],
        [
            {'name': 'unknown', 'value': '10'},
            {'name': 'park_name', 'value': 'abc'},
        ],
    ],
)
async def test_bad_additional_filter(
        monkeypatch, load_yaml, web_app, web_app_client, filters,
):
    schema = load_yaml('filters.yaml')
    monkeypatch.setitem(
        web_app['context'].service_schemas.schemas, 'filters', schema,
    )
    monkeypatch.setattr(
        web_app['context'].service_schemas,
        'known_filters',
        {x['name']: service_schemas.Filter(**x) for x in schema['filters']},
    )
    response = await web_app_client.post(
        '/v2/logs/list/', params={'limit': 10}, json={'filters': filters},
    )
    assert response.status == 400


@pytest.mark.usefixtures('es_request_mock')
@pytest.mark.parametrize(
    'to_check,err_cls',
    [
        ([], None),
        ([models.FiltersRequestItem('park_name', 'some')], None),
        ([models.FiltersRequestItem('http_code', '123')], None),
        ([models.FiltersRequestItem('useragent', 'abc')], None),
        ([models.FiltersRequestItem('cgroups', 'abc')], None),
        ([models.FiltersRequestItem('cgroups', 'abc, bcd')], None),
        ([models.FiltersRequestItem('integer_array', '1,2,3')], None),
        ([models.FiltersRequestItem('park_name', 'abc')], None),
        (
            [models.FiltersRequestItem('http_code', 'abc')],
            es_request.BadFilterValue,
        ),
        (
            [models.FiltersRequestItem('some', 'more')],
            es_request.UnknownFilter,
        ),
        (
            [models.FiltersRequestItem('integer_array', 'a,2,3')],
            es_request.BadFilterValue,
        ),
        (
            [models.FiltersRequestItem('integer_array', '1,2,')],
            es_request.BadFilterValue,
        ),
        (
            [
                models.FiltersRequestItem('useragent', 'abc'),
                models.FiltersRequestItem('http_code', '123'),
            ],
            es_request.MutuallyExclusiveFilters,
        ),
    ],
)
async def test_check_filters(load_yaml, to_check, err_cls):
    filters = {
        x['name']: service_schemas.Filter(**x)
        for x in load_yaml('filters.yaml')['filters']
    }
    checker = functools.partial(
        es_request.clear_filters, to_check, filters, None,
    )

    if err_cls is None:
        checker()
    else:
        with pytest.raises(err_cls):
            checker()


@pytest.mark.now('2019-10-30T20:10:00Z')
@pytest.mark.parametrize(
    'filters, params_ext, expected_must_additions, es_request_type,status',
    [
        ([], {}, [], 'response', 200),
        (
            [
                {'name': 'useragent', 'value': 'some'},
                {'name': 'http_code', 'value': '123'},
            ],
            {},
            [],
            None,
            400,
        ),
        (
            [{'name': 'http_code', 'value': '123'}],
            {},
            [{'term': {'meta_code': 123}}],
            'response',
            200,
        ),
        (
            [{'name': 'useragent', 'value': 'some'}],
            {},
            [{'wildcard': {'useragent': {'value': '*some*'}}}],
            'request',
            200,
        ),
        (
            [{'name': 'type', 'value': 'routestats'}],
            {},
            [
                {
                    'bool': {
                        'should': [
                            {
                                'wildcard': {
                                    'meta_type': {'value': 'routestats'},
                                },
                            },
                        ],
                    },
                },
            ],
            'response',
            200,
        ),
        (
            [
                {'name': 'type', 'value': 'routestats,launch'},
                {'name': 'driver_id', 'value': '123abc'},
            ],
            {},
            [
                {
                    'bool': {
                        'should': [
                            {
                                'wildcard': {
                                    'meta_type': {'value': 'routestats'},
                                },
                            },
                            {'wildcard': {'meta_type': {'value': 'launch'}}},
                        ],
                    },
                },
                {'term': {'driver_id': '123abc'}},
            ],
            'response',
            200,
        ),
        (
            [],
            {'time_from': '2019-07-24T12:00:00Z'},
            [
                {
                    'range': {
                        '@timestamp': {
                            'gte': datetime.datetime(2019, 7, 24, 12),
                        },
                    },
                },
            ],
            'response',
            200,
        ),
        (
            [
                {'name': 'type', 'value': 'routestats,launch'},
                {'name': 'driver_id', 'value': '123abc'},
            ],
            {
                'time_from': '2019-07-24T12:00:00Z',
                'time_to': '2019-07-24T13:00:00Z',
            },
            [
                {
                    'range': {
                        '@timestamp': {
                            'gte': datetime.datetime(2019, 7, 24, 12),
                            'lt': datetime.datetime(2019, 7, 24, 13),
                        },
                    },
                },
                {
                    'bool': {
                        'should': [
                            {
                                'wildcard': {
                                    'meta_type': {'value': 'routestats'},
                                },
                            },
                            {'wildcard': {'meta_type': {'value': 'launch'}}},
                        ],
                    },
                },
                {'term': {'driver_id': '123abc'}},
            ],
            'response',
            200,
        ),
        (
            [{'name': 'park_name', 'value': 'abc'}],
            {},
            [{'term': {'park_id': 'abc'}}],
            ['response', 'stq_task_finish', 'periodic_task_finish'],
            200,
        ),
        (
            [{'name': 'stq_task', 'value': 'send_report'}],
            {},
            [{'terms': {'queue': ['send_report']}}],
            'stq_task_finish',
            200,
        ),
        (
            [
                {'name': 'stq_task', 'value': 'send_report'},
                {'name': 'type', 'value': 'routestats'},
            ],
            {},
            [
                {
                    'bool': {
                        'should': [
                            {
                                'wildcard': {
                                    'meta_type': {'value': 'routestats'},
                                },
                            },
                        ],
                    },
                },
                {'terms': {'queue': ['send_report']}},
            ],
            ['response', 'stq_task_finish'],
            200,
        ),
        (
            [],
            {'time_from': '2019-10-30T19:11:00Z'},
            [
                {
                    'range': {
                        '@timestamp': {
                            'gte': datetime.datetime(2019, 10, 30, 19, 11),
                        },
                    },
                },
            ],
            'response',
            200,
        ),
        (
            [
                {'name': 'type', 'value': 'routestats'},
                {'name': 'http_method', 'value': 'POST'},
            ],
            {},
            [
                {
                    'bool': {
                        'should': [
                            {
                                'wildcard': {
                                    'meta_type': {'value': 'routestats'},
                                },
                            },
                        ],
                    },
                },
                {'terms': {'method': ['POST']}},
            ],
            'response',
            200,
        ),
        (
            [{'name': 'user_phone', 'value': '1234'}],  # filters
            {},  # params_ext
            [
                {
                    'bool': {
                        'should': [
                            {'term': {'meta_personal_phone_id': '1234'}},
                            {'terms': {'phone_id': ['1234']}},
                            {'terms': {'personal_phone_id': ['1234']}},
                        ],
                    },
                },
            ],  # expected_must_additions
            [
                'response',
                'stq_task_finish',
                'periodic_task_finish',
            ],  # es_request_type
            200,  # status
        ),
        (
            [{'name': 'user_phone', 'value': '12345'}],  # filters
            {},  # params_ext
            [
                {
                    'bool': {
                        'should': [
                            {'term': {'meta_personal_phone_id': '12345'}},
                            {'terms': {'phone_id': ['12345']}},
                            {'terms': {'personal_phone_id': ['12345']}},
                            {'terms': {'device_id': ['11111', '22222']}},
                        ],
                    },
                },
            ],  # expected_must_additions
            [
                'response',
                'stq_task_finish',
                'periodic_task_finish',
            ],  # es_request_type
            200,  # status
        ),
    ],
)
@pytest.mark.usefixtures('es_request_mock', 'mock_filters')
@pytest.mark.config(TVM_RULES=[{'src': 'eslogsadminpy3', 'dst': 'personal'}])
async def test_create_es_request(
        monkeypatch,
        patch,
        mockserver,
        web_app_client,
        filters,
        params_ext,
        expected_must_additions,
        es_request_type,
        status,
):
    @patch('taxi.util.cleaners.clean_international_phone')
    async def _clean_international_phone(
            territories_client, phone, *args, **kwargs,
    ):
        return phone

    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_handler(request):
        return {'id': request.json['value'], 'value': request.json['value']}

    @mockserver.json_handler('/eats-notifications/v1/device-list')
    def _devices_handler(request):
        devices = (
            ['11111', '22222']
            if request.json['ids_type'] == 'personal_phone_id'
            and request.json['ids']
            and request.json['ids'][0] == '12345'
            else []
        )
        return {request.json['ids'][0]: devices}

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve_bulk')
    def _mock_retrieve_user_phones(request):
        return {'items': []}

    orig = es_request.create

    async def _mock(request, context, additional_filters, request_type):
        if isinstance(es_request_type, list):
            assert request_type in es_request_type
        else:
            assert request_type == es_request_type
        result = await orig(request, context, additional_filters, request_type)
        check_with = sorted(result['query']['bool']['must'], key=str)

        if not isinstance(es_request_type, list):
            expected_must_part = [{'term': {'type': es_request_type}}]
            expected_must_part.extend(expected_must_additions)
            assert check_with == sorted(expected_must_part, key=str)
        else:
            variants = []
            for _type in es_request_type:
                variants.append(
                    [{'term': {'type': _type}}, *expected_must_additions],
                )
            assert any(check_with == sorted(x, key=str) for x in variants)

        return result

    monkeypatch.setattr('eslogadminpy3.lib.utils.es_request.create', _mock)

    response = await web_app_client.post(
        '/v2/logs/list/',
        params={'limit': 10, **params_ext},
        json={'filters': filters},
    )
    assert response.status == status, await response.json()


@pytest.mark.usefixtures('es_request_mock', 'mock_filters')
@pytest.mark.config(
    LOGS_SEARCH_BY_PHONE_LIMITS={
        'data_api_limit': None,
        'es_request_chunk_size': 501,
    },
    TVM_RULES=[{'src': 'eslogsadminpy3', 'dst': 'personal'}],
)
async def test_create_several_request_for_limits(
        mockserver, monkeypatch, patch, web_app_client,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_handler(request):
        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'error'},
        )

    @patch('eslogadminpy3.lib.data_api.get_user_phones')
    async def _get_user_phones(*args, **kwargs):
        return [{'_id': x, 'type': 'uber'} for x in range(1000)]

    @patch('eslogadminpy3.lib.data_api.get_users_by_phones')
    async def _get_users_by_phones(*args, **kwargs):
        return [{'_id': x, 'phone_id': x, 'device_id': x} for x in range(1000)]

    @patch('taxi.util.cleaners.clean_international_phone')
    async def _clean_international_phone(
            territories_client, phone, *args, **kwargs,
    ):
        return phone

    orig = es_request.create

    async def _mock(request, context, additional_filters, request_type):
        result = await orig(request, context, additional_filters, request_type)
        check_with = sorted(result['query']['bool']['must'], key=str)
        assert len(check_with) == 2
        assert check_with[1]['term']['type'] in (
            'response',
            'stq_task_finish',
            'periodic_task_finish',
        )
        _filter = check_with[0]
        assert len(_filter['bool']['should']) == 8
        assert all(
            set(x.keys()) == {'terms'} for x in _filter['bool']['should']
        )
        for _should in _filter['bool']['should']:
            _terms = _should['terms']
            for _key in (
                    'phone_id',
                    'personal_phone_id',
                    'meta_user_id',
                    'device_id',
            ):
                if _key in _terms:
                    assert len(_terms[_key]) in (501, 499)

        return result

    monkeypatch.setattr('eslogadminpy3.lib.utils.es_request.create', _mock)

    response = await web_app_client.post(
        '/v2/logs/list/',
        params={'limit': 10},
        json={'filters': [{'name': 'user_phone', 'value': '+7123456789'}]},
    )
    assert response.status == 200


@pytest.mark.config(
    LOGS_ELASTIC_LIST_REQUEST_SETTINGS={
        'distribution': [48],
        'full_range': 48,
        'group_by_index': True,
    },
)
async def test_stq_logs(patch, load_json, web_app_client, mockserver):
    first_request_done = False

    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search_list(*args, **kwargs):
        if 'archive' in kwargs['index']:
            return {'hits': {'hits': []}}
        if consts.ELASTIC_LOG_INDEX_EDA in kwargs['index']:
            return {'hits': {'hits': []}}
        nonlocal first_request_done
        _data = load_json('es_response_stq_task_no_logs.json')
        if not first_request_done:
            first_request_done = True
            _data['hits']['hits'].pop(-1)
        else:
            _data['hits']['hits'].pop(0)
        return _data

    @mockserver.json_handler('/user_api-api/users/get')
    def _mock_get_user(request):
        if request.json['id'] == 'user-without-phone_id':
            return {'id': 'user-without-phone_id'}
        if request.json['id'] == 'user-with-phone-id':
            return {'id': 'user-with-phone-id', 'phone_id': '123'}
        return mockserver.make_response(status=404)

    response = await web_app_client.post(
        '/v2/logs/list/', params={'limit': 10}, json={'filters': []},
    )
    assert response.status == 200
    data = await response.json()
    assert data == [
        {
            'cgroups': ['taxi_test_stq'],
            'delay': '0.115',
            'level': 'error',
            'link': 'dfcf22649db64e08be7a37ec4b67647e',
            'order_id': '92c97516135a554c8db7bae1e85510a1',
            'time': '2019-10-29T20:32:38.764000+0300',
            'user_id': '86c6d4472083259ea764a38906be03b0',
            'user_uid': '4031146166',
            'type': 'stq/send_report',
        },
    ]

    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search_by_link(index, *args, **kwargs):
        return load_json('es_response_stq_task_with_logs.json')

    response = await web_app_client.get(
        '/v1/logs/by_link/',
        params={'link_id': 'dfcf22649db64e08be7a37ec4b67647e'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'host': 'taxi-stq-myt-01.taxi.tst.yandex.net',
        'lang': 'json',
        'response_body': (
            'Тело ответа не найдено, ' 'возможно, логирование отключено.'
        ),
        'request_body': (
            'Тело запроса не найдено, ' 'возможно, логирование отключено.'
        ),
        'log_extra_link': 'dfcf22649db64e08be7a37ec4b67647e',
        'span_id': 'b8f8277238cb4898a32eb53ec287bb7c',
        'exception': (
            'Traceback (most recent call last):\n  '
            'File "/usr/lib/yandex/taxi-stq/taxi_stq/utils.py", '
            'line 36, in run_and_log\n    '
            'yield\n  '
            'File "/usr/lib/yandex/taxi-stq/taxi_stq/stq_task.py", '
            'line 124, in _run_and_log\n    '
            'yield self._task_function(*args, **kwargs)\n'
            'KeyError: \'_id\'\n'
        ),
        'logs': [
            {
                'time': '2019-10-29T20:32:38.707000+03:00',
                'message': (
                    'got few emails: [(ObjectId(\'5b7e9283030553e65806b18e\'),'
                    ' u\'4021771070\'), '
                    '(ObjectId(\'5d5bd31f91272f03f61f8399\'), '
                    'u\'4027395454\')]'
                ),
                'level': 'info',
            },
            {
                'time': '2019-10-29T20:32:38.733000+03:00',
                'message': (
                    '(some_extra_tag=extra_val) '
                    'start send_report_task for order '
                    '92c97516135a554c8db7bae1e85510a1'
                ),
                'level': 'info',
            },
        ],
    }


@pytest.mark.now('2019-12-10T10:10:10Z')
@pytest.mark.parametrize(
    'index_pattern_query, index_pattern_body, expected_indices',
    [
        (
            None,
            None,
            {
                'yandex-taxi-*2019.12.10.10',
                'pilorama-core-*2019.12.10.10',
                'yandex-taxi-archive',
            },
        ),
        (
            ['yandex-taxi'],
            None,
            {'yandex-taxi-2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            None,
            ['yandex-taxi'],
            {'yandex-taxi-2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            ['yandex-taxi*'],
            None,
            {'yandex-taxi*2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            None,
            ['yandex-taxi*'],
            {'yandex-taxi*2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            ['yandex-taxi-*'],
            None,
            {'yandex-taxi-*2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            None,
            ['yandex-taxi-*'],
            {'yandex-taxi-*2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            ['yandex-taxi-api'],
            None,
            {'yandex-taxi-api-2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            None,
            ['yandex-taxi-api'],
            {'yandex-taxi-api-2019.12.10.10', 'yandex-taxi-archive'},
        ),
        (
            ['yandex-taxi-api', 'index-2'],
            None,
            {
                'yandex-taxi-api-2019.12.10.10',
                'index-2-2019.12.10.10',
                'yandex-taxi-archive',
            },
        ),
        (
            None,
            ['yandex-taxi-api', 'index-2'],
            {
                'yandex-taxi-api-2019.12.10.10',
                'index-2-2019.12.10.10',
                'yandex-taxi-archive',
            },
        ),
    ],
)
async def test_index_pattern(
        patch,
        web_app_client,
        index_pattern_query,
        index_pattern_body,
        expected_indices,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def _search_mock(index, *args, **kwargs):
        assert set(index.split(',')) & expected_indices
        return {'hits': {'hits': []}}

    params = {'limit': 10}
    if index_pattern_query is not None:
        params['indices'] = ','.join(index_pattern_query)
    body = {'filters': []}
    if index_pattern_body is not None:
        body['indices'] = index_pattern_body
    response = await web_app_client.post(
        '/v2/logs/list/', params=params, json=body,
    )
    assert response.status == 200

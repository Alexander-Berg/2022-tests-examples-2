import json

from aiohttp import web
import pytest

from example_service.generated.service.swagger.models import api
from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'views': 1},
            response={'name': 'Bad things', 'stats': {'views': 1}},
        ),
        common.Params(
            {'views': -1},
            status=500,
            response=common.make_internal_error(
                'Invalid value for views: -1 '
                'must be a value greater than or equal to 0',
            ),
        ),
    ],
)
async def test_ref_to_model(web_app_client, params):
    response = await web_app_client.get(
        '/test_inline/ref_to_model', params=params.request,
    )
    assert await response.json() == params.response
    assert response.status == params.status


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            {'durations': '1,2'}, response=[{'duration': 1}, {'duration': 2}],
        ),
        common.Params(
            {'durations': '-1,2'},
            status=500,
            response=common.make_internal_error(
                'Invalid value for duration: -1 '
                'must be a value greater than or equal to 0',
            ),
        ),
    ],
)
async def test_ref_to_list(web_app_client, params):
    response = await web_app_client.get(
        '/test_inline/ref_to_list', params=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


def make_test_cases(
        error_status,
        error_text_func,
        *,
        add_external_refs=True,
        allow_extra=True,
):
    params = [
        common.Params({'name': 'name'}),
        common.Params(
            {'name': 1},
            error_status,
            response=error_text_func(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
        common.Params({'grep': ['1', '2']}),
        common.Params({'grep': []}),
        common.Params(
            {'grep': 1},
            error_status,
            response=error_text_func(
                'Invalid value for grep: 1 is not instance of list',
            ),
        ),
        common.Params(
            {'grep': [2, 3]},
            error_status,
            response=error_text_func(
                'Invalid value for grep_item: 2 is not instance of str',
            ),
        ),
        common.Params({'jobs': [{'name': 'some'}]}),
        common.Params({'jobs': [{'name': 'here'}, {'name': 'where?'}]}),
        common.Params({'jobs': []}),
        common.Params({'jobs': [{}]}),
        common.Params(
            {'jobs': 1},
            error_status,
            response=error_text_func(
                'Invalid value for jobs: 1 is not instance of list',
            ),
        ),
        common.Params(
            {'jobs': [{'name': 2}]},
            error_status,
            response=error_text_func(
                'Invalid value for name: 2 is not instance of str',
            ),
        ),
        common.Params({'rides': [{'duration': 1}]}),
        common.Params(
            {
                'rides': [
                    {'duration': 1},
                    {'duration': 2},
                    {'duration': 3},
                    {'duration': 4},
                ],
            },
        ),
        common.Params(
            {'rides': [{'duration': '1'}]},
            error_status,
            response=error_text_func(
                'Invalid value for duration: \'1\' is not instance of int',
            ),
        ),
        common.Params(
            {
                'rides_of_rides': [
                    [{'duration': 1}, {'duration': 2}, {'duration': 3}],
                ],
            },
        ),
        common.Params(
            {
                'rides_of_rides': [
                    [{'duration': 1}, {'duration': '2'}, {'duration': 3}],
                ],
            },
            error_status,
            response=error_text_func(
                'Invalid value for duration: \'2\' is not instance of int',
            ),
        ),
        common.Params({'ages': [1005001, 1005002]}),
        common.Params(
            {'ages': 0},
            error_status,
            response=error_text_func(
                'Invalid value for ages: 0 is not instance of list',
            ),
        ),
        common.Params(
            {'ages': [0]},
            error_status,
            response=error_text_func(
                'Invalid value for ages_item: 0 must be a value greater than '
                'or equal to 100500',
            ),
        ),
        common.Params(
            {
                'movies': [
                    {'name': 'hunt'},
                    {'name': 'reap', 'stats': {'views': 100500}},
                ],
            },
        ),
        common.Params(
            {'movies': 0},
            error_status,
            response=error_text_func(
                'Invalid value for movies: 0 is not instance of list',
            ),
        ),
        common.Params(
            {'movies': [{'name': 1}]},
            error_status,
            response=error_text_func(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
        common.Params(
            {'movies': [{'stats': {'views': -1}}]},
            error_status,
            response=error_text_func(
                'Invalid value for views: -1 must be a value greater than '
                'or equal to 0',
            ),
        ),
        common.Params({'bongos': [{'name': 'a' * 10}]}),
        common.Params(
            {'bongos': [{'name': 'a'}]},
            error_status,
            response=error_text_func(
                'Invalid value for name: '
                '\'a\' length must be greater than '
                'or equal to 10',
            ),
        ),
        common.Params({'bringos': ['1212']}),
        common.Params(
            {'bringos': [123]},
            error_status,
            response=error_text_func(
                'Invalid value for bringos_item: '
                '123 is not instance of str',
            ),
        ),
        common.Params({'drugs': [{'doze_grams': 100}]}),
        common.Params(
            {'drugs': [{'doze_grams': 321}]},
            error_status,
            response=error_text_func(
                'Invalid value for doze_grams: 321 must be a value less than '
                'or equal to 200',
            ),
        ),
        common.Params(
            {'clips': [{'name': 'heello'}, {'stats': {'views': 112}}]},
        ),
        common.Params(
            {'clips': [{'name': 1}]},
            error_status,
            response=error_text_func(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
        common.Params(
            {'crops': [{'name': 'heello'}, {'stats': {'views': 112}}]},
        ),
        common.Params(
            {'crops': [{'name': 1}]},
            error_status,
            response=error_text_func(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
    ]
    if add_external_refs:
        params += [
            common.Params({'user': {'name': 'Boogieman'}}),
            common.Params(
                {'user': {}},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'users_list': [{'name': 'Boogieman'}]}),
            common.Params(
                {'users_list': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'ref_users_list': [{'name': 'Boogieman'}]}),
            common.Params(
                {'ref_users_list': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'ref_ref_users_list': [{'name': 'Boogieman'}]}),
            common.Params(
                {'ref_ref_users_list': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'ref_user': {'name': 'Boogieman'}}),
            common.Params(
                {'ref_user': {}},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'user_ref_list': [{'name': 'Boogieman'}]}),
            common.Params(
                {'user_ref_list': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'friends': [{'name': 'Boogieman'}]}),
            common.Params(
                {'friends': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params(
                {'friends_of_friends': [[{'name': 'Boogieman'}], []]},
            ),
            common.Params(
                {'friends_of_friends': [[{'name': 1}]]},
                error_status,
                response=error_text_func(
                    'Invalid value for name: 1 is not instance of str',
                ),
            ),
            common.Params({'family': [{'name': 'Boogieman'}]}),
            common.Params(
                {'family': [{}]},
                error_status,
                response=error_text_func('name is required property'),
            ),
            common.Params({'hops': [{'hip': 1}, {'hip': 20}]}),
            common.Params(
                {'hops': [{'hip': 'abba'}]},
                error_status,
                response=error_text_func(
                    'Invalid value for hip: '
                    '\'abba\' is not instance of int',
                ),
            ),
            common.Params(
                {'list_of_list_of_hops': [[[]], [[{'hip': 1}, {'hip': 20}]]]},
            ),
            common.Params(
                {'list_of_list_of_hops': [[[{'hip': 1}, {'hip': 'abba'}]]]},
                error_status,
                response=error_text_func(
                    'Invalid value for hip: '
                    '\'abba\' is not instance of int',
                ),
            ),
            common.Params(
                {'list_of_list_of_hops': [[{'hello': 1}]]},
                error_status,
                response=error_text_func(
                    'Invalid value for list_of_list_of_hops_item_item: '
                    '{\'hello\': 1} is not instance of list',
                ),
            ),
        ]
    if allow_extra:
        params.append(
            common.Params({'jobs': [{'name': 'bac', 'x': 'y'}]}, response={}),
        )
    else:
        params.append(
            common.Params(
                {'jobs': [{'name': 'bac', 'x': 'y'}]},
                status=error_status,
                response=error_text_func('Unexpected fields: [\'x\']'),
            ),
        )
    return params


@pytest.mark.parametrize(
    'params', make_test_cases(400, common.make_request_error),
)
async def test_ref_to_extra_model(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/ref_to_extra_model', json=params.request,
    )
    assert response.status == params.status
    assert await response.json() == (params.response or {})


@pytest.mark.parametrize(
    'params',
    [
        common.Params('abacaba'),
        common.Params(
            'a',
            status=400,
            response=common.make_request_error(
                'Invalid value for body: \'a\' length must be greater than or '
                'equal to 3',
            ),
        ),
    ],
)
async def test_parameter_string(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/parameters/string', data=params.request,
    )
    assert response.status == params.status
    assert await response.json() == (params.response or {})


@pytest.mark.parametrize(
    'params', make_test_cases(400, common.make_request_error),
)
async def test_parameter_model(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/parameters/model', json=params.request,
    )
    assert await response.json() == (params.response or {})
    assert response.status == params.status


@pytest.mark.parametrize(
    'params',
    make_test_cases(500, common.make_internal_error, allow_extra=False),
)
async def test_response_model(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/responses/model', data=json.dumps(params.request),
    )
    assert await response.json() == (params.response or params.request)
    assert response.status == params.status


async def test_response_inline_list(web_app_client):
    response = await web_app_client.get('/test_inline/responses/inline-list')
    assert await response.json() == [{'id': '100', 'channel': 'memes'}]
    assert response.status == 200


@pytest.mark.parametrize(
    'params',
    make_test_cases(
        500,
        common.make_internal_error,
        add_external_refs=False,
        allow_extra=False,
    ),
)
async def test_client_parameter_model(
        web_app_client, params, mock_yet_another_service,
):
    @mock_yet_another_service('/test_inline/parameters/model')
    async def handler(request):
        return web.json_response({})

    response = await web_app_client.post(
        '/test_inline/client/parameters/model',
        data=json.dumps(params.request),
    )

    assert await response.json() == (params.response or {})
    assert response.status == params.status
    assert handler.times_called == int(params.status == 200)


@pytest.mark.parametrize(
    'params',
    make_test_cases(500, common.make_internal_error, add_external_refs=False),
)
async def test_client_response_model(
        web_app_client, params, mock_yet_another_service,
):
    @mock_yet_another_service('/test_inline/responses/model')
    async def handler(request):
        return web.json_response(json.loads(request.get_data()))

    response = await web_app_client.post(
        '/test_inline/client/responses/model', data=json.dumps(params.request),
    )

    assert await response.json() == (params.response or {})
    assert response.status == params.status
    assert handler.times_called == 1


async def test_response_obj_in_obj(web_app_client):
    response = await web_app_client.get(
        '/test_inline/responses/object_in_object',
    )
    assert response.status == 200
    assert await response.json() == {
        'name': 'bacbac',
        'address': {'street': '11', 'country': {'code': 7}},
    }


@pytest.mark.parametrize(
    'params',
    [
        common.Params(None),
        common.Params([{'name': '1'}]),
        common.Params(
            [{'name': 1}],
            status=400,
            response=common.make_request_error(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
        common.Params([{'grep': ['1', '2', '3']}]),
        common.Params(
            [{'grep': 1}],
            status=400,
            response=common.make_request_error(
                'Invalid value for grep: 1 is not instance of list',
            ),
        ),
        common.Params([{'jobs': [{'name': 'oppo'}]}]),
        common.Params(
            [{'jobs': [{'name': 1}]}],
            status=400,
            response=common.make_request_error(
                'Invalid value for name: 1 is not instance of str',
            ),
        ),
    ],
)
async def test_parameter_list(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/parameters/list', json=params.request,
    )
    assert await response.json() == (params.response or {})
    assert response.status == params.status


@pytest.mark.parametrize(
    'params',
    [
        *make_test_cases(400, common.make_request_error, allow_extra=False),
        common.Params({'address': {'street': 'aaa', 'country': {'code': 1}}}),
        common.Params(
            {'address': {'street': 'aaa', 'country': {'code': 'aa'}}},
            400,
            common.make_request_error(''),
        ),
    ],
)
async def test_parameter_one_of(web_app_client, params):
    response = await web_app_client.post(
        '/test_inline/parameters/one_of', json=params.request,
    )
    resp_data = await response.json()
    if params.status == 200:
        assert resp_data == {}
    else:
        resp_data['details'].pop('reason')
        params.response['details'].pop('reason')
        assert resp_data == params.response
    assert response.status == params.status


@pytest.mark.parametrize(
    'params', [*make_test_cases(400, common.make_request_error)],
)
async def test_parameter_additional_properties(params, web_app_client):
    response = await web_app_client.post(
        '/test_inline/parameters/additional_properties',
        json={'add_prop': params.request},
    )
    assert await response.json() == (params.response or {})
    assert response.status == params.status


async def test_ref_from_response_to_list_with_inline_models_hierarchy(
        web_app_client,
):
    response = await web_app_client.get(
        '/test_inline/'
        'responses/ref-to-list-with-inline-item-with-inline-model',
    )
    assert await response.json() == [
        {'name': 'seanchaidh', 'inline-model': {'status': 'ok!'}},
    ]
    assert response.status == 200


async def test_deep_list_incorrect_inline_items_schemas_propogation():
    test_cls = api.FleetVehiclesItem.Data
    assert not hasattr(test_cls, 'DataItem')
    assert hasattr(test_cls.DriverChairsItem, 'DataItem')
    assert hasattr(test_cls.DriverConfirmedChairsItem, 'DataItem')

    obj = test_cls.deserialize(
        {
            'driver_confirmed_chairs': [{'data': [{'is_enabled': True}]}],
            'driver_chairs': [{'data': [{'brand': 'Cococo'}]}],
        },
    )

    assert isinstance(
        obj.driver_chairs[0].data[0], test_cls.DriverChairsItem.DataItem,
    )
    assert isinstance(
        obj.driver_confirmed_chairs[0].data[0],
        test_cls.DriverConfirmedChairsItem.DataItem,
    )

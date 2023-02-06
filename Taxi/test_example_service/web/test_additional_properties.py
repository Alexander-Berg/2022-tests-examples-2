import json

import pytest

from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'size': 20, 'aaa': 'a', 'bbbb': 'b'}, response=22,
        ),
        common.Params(
            request={'aaa': 'a', 'bbbb': 'b', 'cc': 'c'}, response=3,
        ),
        common.Params(
            request={'size': 'a'},
            status=400,
            response=common.make_request_error(
                'Invalid value for size: ' '\'a\' is not instance of int',
            ),
        ),
        common.Params(
            request={'aaa': 1},
            status=400,
            response=common.make_request_error(
                'Invalid value for extra_value: ' '1 is not instance of str',
            ),
        ),
    ],
)
async def test_additional_properties(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/primitive', json=params.request,
    )
    assert response.status == params.status
    if params.status == 200:
        assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert int(await response.text()) == params.response
    else:
        assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'a': {'size': 10, 'aaa': 'a', 'bbbb': 'b'}, 'size': 100},
            response=112,
        ),
        common.Params(
            request={'b': {'size': 10, 'aaa': 'a', 'bbbb': 'b', 'cc': 'c'}},
            response=13,
        ),
        common.Params(
            request={'size': 'a'},
            status=400,
            response=common.make_request_error(
                'Invalid value for size: ' '\'a\' is not instance of int',
            ),
        ),
        common.Params(
            request={'aaa': 1},
            status=400,
            response=common.make_request_error(
                'Invalid value to deserialize PrimitiveAdditionalProperties: '
                '1 is not instance of dict',
            ),
        ),
    ],
)
async def test_additional_properties_model(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/parameters_schemed', json=params.request,
    )
    assert response.status == params.status
    if params.status == 200:
        assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert int(await response.text()) == params.response
    else:
        assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'a': {'size': 10, 'aaa': 'a', 'bbbb': 'b'}, 'size': 100},
        ),
        common.Params(
            request={'b': {'size': 10, 'aaa': 'a', 'bbbb': 'b', 'cc': 'c'}},
        ),
        common.Params(
            {'size': 'a'},
            status=500,
            response=common.make_internal_error(
                'Invalid value for size: ' '\'a\' is not instance of int',
            ),
        ),
        common.Params(
            {'aaa': 1},
            status=500,
            response=common.make_internal_error(
                'Invalid value to deserialize PrimitiveAdditionalProperties: '
                '1 is not instance of dict',
            ),
        ),
    ],
)
async def test_additional_properties_model_resp(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/responses_schemed', data=json.dumps(params.request),
    )
    assert response.status == params.status
    assert await response.json() == (params.response or params.request)


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={
                'a': {'a': 1, 'b': [0, 2, 3]},
                'x': 'y',
                'y': 123,
                'z': None,
                'size': 100,
            },
            response=104,
        ),
        common.Params(request={}, response=0),
        common.Params(
            request={'size': 'a'},
            status=400,
            response=common.make_request_error(
                'Invalid value for size: ' '\'a\' is not instance of int',
            ),
        ),
        common.Params(request={'aaa': 1}, response=1),
    ],
)
async def test_additional_properties_dynamic_params(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/parameters_dynamic', json=params.request,
    )
    assert response.status == params.status
    if params.status == 200:
        assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert int(await response.text()) == params.response
    else:
        assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            {
                'a': {'a': 1, 'b': [0, 2, 3]},
                'x': 'y',
                'y': 123,
                'z': None,
                'size': 100,
            },
            200,
        ),
        common.Params({}, 200),
        common.Params(
            {'size': 'a'},
            500,
            common.make_internal_error(
                'Invalid value for size: ' '\'a\' is not instance of int',
            ),
        ),
        common.Params({'aaa': 1}, 200),
    ],
)
async def test_additional_properties_dynamic_resp(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/responses_dynamic', data=json.dumps(params.request),
    )
    assert response.status == params.status
    assert await response.json() == (params.response or params.request)


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={
                'a': {'a': 1, 'b': [0, 2, 3]},
                'x': 'y',
                'y': 123,
                'z': None,
                'size': 100,
            },
            response={'a', 'x', 'y', 'z', 'size'},
        ),
        common.Params(request={}, response=set()),
        common.Params(request={'size': 'a'}, response={'size'}),
    ],
)
async def test_additional_properties_dict_params(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/parameters_dict', json=params.request,
    )
    assert response.status == params.status
    assert set(await response.json()) == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={
                'a': {'a': 1, 'b': [0, 2, 3]},
                'x': 'y',
                'y': 123,
                'z': None,
                'size': [100],
            },
        ),
        common.Params(request={}),
        common.Params(request={'size': 'a', 'x': {'a': []}, 'z': [1, 2]}),
    ],
)
async def test_additional_properties_dict_resp(web_app_client, params):
    response = await web_app_client.post(
        'test_ap/responses_dict', data=json.dumps(params.request),
    )
    assert response.status == params.status
    assert await response.json() == (params.response or params.request)


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'named-size': 0, 'hack-size': 0},
            status=500,
            response=common.make_internal_error(
                'Additional properties keys intersects '
                'with named properties: {\'size\'}',
            ),
        ),
        common.Params(
            request={'named-size': 0, 'hack-size': 1},
            status=500,
            response=common.make_response_error(
                'Additional properties keys intersects '
                'with named properties: {\'size\'}',
            ),
        ),
        common.Params(
            request={'named-size': 1, 'hack-size': 0},
            status=500,
            response=common.make_internal_error(
                'Additional properties keys intersects '
                'with named properties: {\'size\'}',
            ),
        ),
        common.Params(
            request={'named-size': 1, 'hack-size': 1},
            status=500,
            response=common.make_response_error(
                'Additional properties keys intersects '
                'with named properties: {\'size\'}',
            ),
        ),
    ],
)
async def test_keys_intersection(web_app_client, params):
    response = await web_app_client.get(
        'test_ap/keys_intersection', params=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response

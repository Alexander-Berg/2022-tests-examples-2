import json

import pytest

from example_service.generated.service.swagger.models import api as models
from . import common


CASES = [
    common.Params(
        request={'name': 'name', 'age': 1}, response='name1', status=200,
    ),
    common.Params(
        request={'age': 10},
        response=common.make_request_error('name is required property'),
        status=400,
    ),
    common.Params(
        request={'name': 'name', 'age': 'aaa'},
        response=common.make_request_error(
            'Invalid value for age: \'aaa\' is not instance of int',
        ),
        status=400,
    ),
]


@pytest.mark.parametrize('params', CASES)
@pytest.mark.parametrize(
    'url',
    [
        '/all_of_test/inline_inline',
        '/all_of_test/ref_to_ref',
        '/all_of_test/mixed',
        '/all_of_test/ref_to_inline',
        '/all_of_test/ref_to_mixed',
        '/all_of_test/with_common_ref',
        '/all_of_test/with_plugin_ref',
    ],
)
async def test_all_of(web_app_client, params, url):
    response = await web_app_client.post(url, json=params.request)
    assert response.status == params.status
    if response.status == 200:
        assert await response.text() == params.response
    else:
        assert await response.json() == params.response


async def test_all_of_all_of(web_app_client):
    response = await web_app_client.post(
        '/all_of_test/all_of_all_of',
        json={'name': 'Quentin', 'age': 56, 'suffix': 'aaa'},
    )
    assert response.status == 200
    assert await response.text() == 'Quentin56aaa'


async def test_all_of_external_definitions(web_app_client):
    response = await web_app_client.post(
        '/all_of_test/link-to-external-definitions',
        json={'name': 'Quentin', 'age': 56},
    )
    assert response.status == 200
    assert await response.text() == 'Quentin: 56'


async def test_complex_inline_parameter(web_app_client):
    response = await web_app_client.post(
        '/all_of_test/complex_inline',
        json={
            'inline': {
                'name': 'Peter',
                'day': {'number': 101, 'week': 'Second'},
                'age': 56,
            },
        },
    )
    assert response.status == 200
    assert await response.text() == 'Peter101Second56'


async def test_complex_inline_response(web_app_client):
    data = {
        'inline': {
            'name': 'Peter',
            'day': {'number': 101, 'week': 'Second'},
            'age': 56,
        },
    }
    response = await web_app_client.post(
        '/all_of_test/complex_inline_response', data=json.dumps(data),
    )
    assert response.status == 200
    assert await response.json() == data


async def test_object_property_ref(web_app_client):
    response = await web_app_client.post(
        '/all_of_test/object-properties',
        json={'mix': {'name': 'name', 'age': 1}},
    )
    assert response.status == 200
    assert await response.text() == ''


@pytest.mark.parametrize(
    'params',
    [
        common.Params({'inner': {'name': 'abc'}}, 200, 'abc'),
        common.Params({'inner': {'name': 'abc'}, 'outer': 1}, 200, 'abc'),
    ],
)
async def test_additional_properties_leak(web_app_client, params):
    response = await web_app_client.post(
        '/all_of_test/additional-properties-leak', json=params.request,
    )
    assert response.status == params.status
    if params.status != 200:
        assert await response.json() == params.response
    else:
        assert await response.text() == params.response


def test_object_with_dict():
    obj = models.WithDict.deserialize(
        {'name': 'seanchaidh', 'not_name': 'not_seanchaidh'},
    )
    assert obj.name == 'seanchaidh'
    assert not hasattr(obj, 'not_name')
    assert repr(obj) == 'WithDict(name=\'seanchaidh\')'


def test_bad_inline_naming():
    # checks TAXITOOLS-1997
    obj = models.Test1997.deserialize(
        {
            'property': {
                'name': 'seanchaidh',
                'stats': {'views': 1},
                'property': 'bacbac',
            },
        },
    )
    prop = obj.property
    assert prop.name == 'seanchaidh'
    assert prop.property == 'bacbac'
    assert prop.stats.views == 1

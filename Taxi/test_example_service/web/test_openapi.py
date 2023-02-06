import pytest

from taxi.codegen import swaggen_serialization as utils

from example_service.generated.service.swagger.models import api as api_models
from . import common


@pytest.mark.parametrize(
    'params',
    (
        common.Params(
            request={'name': 'Petra'},
            response={
                'name': 'Petra',
                'age': 33,
                'favorite_movies': [],
                'tobaccos': [],
            },
        ),
        common.Params(
            request={'name': 'Petra', 'movies': 'Bang!', 'tobaccos': 'cherry'},
            response={
                'name': 'Petra',
                'age': 33,
                'favorite_movies': ['Bang!'],
                'tobaccos': ['cherry'],
            },
        ),
        common.Params(
            request={
                'movies': 'Bang!,BoogieMan',
                'tobaccos': 'cherry|double-apple',
            },
            response={
                'name': 'Vasya',
                'age': 33,
                'favorite_movies': ['Bang!', 'BoogieMan'],
                'tobaccos': ['cherry', 'double-apple'],
            },
        ),
    ),
)
async def test_simple_get(web_app_client, params):
    response = await web_app_client.get(
        '/openapi/simple', params=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response
    assert response.headers['X-YaTaxi-BacBac'] == '3'
    assert response.headers['X-YaTaxi-IDS'] == '1,2,3'


@pytest.mark.parametrize(
    'params',
    (
        common.Params(request=None, response='<empty>'),
        common.Params(
            request={'name': 'Vasya', 'age': 21}, response='Vasya-21',
        ),
        common.Params(request={'name': 'Vasya'}, response='Vasya-None'),
        common.Params(
            request={'name': 'Vasya', 'age': 'sto'},
            status=400,
            response=common.make_request_error(
                'Invalid value for age: \'sto\' is not instance of int',
            ),
        ),
    ),
)
async def test_simple_post(web_app_client, params):
    response = await web_app_client.post(
        '/openapi/simple', json=params.request,
    )
    assert response.status == params.status
    if response.status == 200:
        assert await response.text() == params.response
    else:
        assert await response.json() == params.response


async def test_get_ref_model(web_app_client):
    response = await web_app_client.get('/openapi/user')
    assert response.status == 200
    assert await response.json() == {
        'name': 'Vasya',
        'age': 33,
        'likes': [{'from': 'Peter'}, {'from': 'Antoine'}],
    }


def test_nullable_model():
    first = api_models.OpenNullable.deserialize(
        {
            'nullable_required_string': None,
            'nullable_not_required_string': None,
            'required_string': 'aa',
            'extra 1': None,
            'extra 11': None,
            'extra 2': '',
            'nullable_ref': None,
            'nullable_one_of': None,
            'one_of_with_nullable_ref': None,
            'nullable_array': None,
            'nullable_inline_object': None,
            'nullable_items': ['1', '2', None, 'bacbac'],
            'array_in_one_of': ['1, 2', None],
        },
    )
    assert first.nullable_required_string is None
    assert first.nullable_not_required_string is None
    assert first.required_string == 'aa'
    assert first.not_required_string is None
    assert first.nullable_ref is None
    assert first.ref is None
    assert first.one_of_with_nullable_ref is None
    assert first.nullable_one_of is None
    assert first.not_nullable_one_of is None
    assert first.nullable_array is None
    assert first.not_nullable_array is None
    assert first.nullable_inline_object is None
    assert first.not_nullable_inline_object is None
    assert first.nullable_items == ['1', '2', None, 'bacbac']
    assert first.array_in_one_of == ['1, 2', None]
    assert first.extra == {'extra 1': None, 'extra 11': None, 'extra 2': ''}

    first.array_in_one_of = [None, None, None, 'hello']
    first.nullable_items = [None, 'bacbac', None]

    assert first.serialize() == {
        'array_in_one_of': [None, None, None, 'hello'],
        'nullable_required_string': None,
        'required_string': 'aa',
        'extra 1': None,
        'extra 11': None,
        'extra 2': '',
        'nullable_items': [None, 'bacbac', None],
    }

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize({'required_string': 'aaa'})
    assert exc_info.value.args == (
        'nullable_required_string is required property',
    )

    required_obj = {'required_string': 'aaa', 'nullable_required_string': None}

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize(
            {**required_obj, 'not_required_string': None},
        )
    assert exc_info.value.args == (
        'Invalid value for not_required_string: null',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize({**required_obj, 'ref': None})
    assert exc_info.value.args == ('Invalid value for ref: null',)

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize(
            {**required_obj, 'not_nullable_one_of': None},
        )
    assert exc_info.value.args == (
        'Invalid value for not_nullable_one_of: null',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize(
            {**required_obj, 'not_nullable_array': None},
        )
    assert exc_info.value.args == (
        'Invalid value for not_nullable_array: null',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize(
            {**required_obj, 'not_nullable_inline_object': None},
        )
    assert exc_info.value.args == (
        'Invalid value for not_nullable_inline_object: null',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        api_models.OpenNullable.deserialize(
            {**required_obj, 'not_nullable_items': ['a', None]},
        )
    assert exc_info.value.args == (
        'Invalid value for not_nullable_items_item: '
        'None is not instance of str',
    )


def test_nullable_additional_properties():
    happy_path = api_models.NullableDictsCollector.deserialize(
        {
            'typed-ref': None,
            'untyped-ref': None,
            'typed-inline': None,
            'untyped-inline': None,
        },
    )
    assert happy_path.typed_ref is None
    assert happy_path.untyped_ref is None
    assert happy_path.typed_inline is None
    assert happy_path.untyped_inline is None


@pytest.mark.parametrize(
    'params, content_type',
    (
        (
            common.Params(
                request=b'abc', response={'name': 'Vasya', 'data': 'abc'},
            ),
            'application/octet-stream',
        ),
        (
            common.Params(
                request=b'abc',
                status=400,
                response=common.make_request_error(
                    'Invalid Content-Type: image/png; '
                    'expected one of [\'application/octet-stream\']',
                ),
            ),
            'image/png',
        ),
    ),
)
async def test_binary(web_app_client, params, content_type):
    response = await web_app_client.post(
        '/openapi/binary',
        params={'name': 'Vasya'},
        data=params.request,
        headers={'Content-Type': content_type},
    )
    assert response.status == params.status
    assert await response.json() == params.response


async def test_no_content_response(web_app_client):
    response = await web_app_client.get('/openapi/ping')
    # this is default content-type
    assert response.headers['content-type'] == 'application/octet-stream'
    assert await response.read() == b''


async def test_multiple_content_types(web_app_client):
    response = await web_app_client.get(
        '/openapi/multiple-responses', params={'name': 'bacbac'},
    )
    assert response.status == 200
    assert response.headers['content-type'] == 'text/plain; charset=utf-8'
    assert await response.text() == 'bacbac'

    response = await web_app_client.get(
        '/openapi/multiple-responses', params={'name': 'matrix'},
    )
    assert response.status == 200
    assert response.headers['content-type'] == 'application/octet-stream'
    assert await response.read() == b'\xDE\xAD\xBE\xEF'


async def test_homogeneous_multiple_content_types(web_app_client):
    response = await web_app_client.get(
        '/openapi/homogeneous-multiple-responses', params={'ext': 'png'},
    )
    assert response.status == 200
    assert response.headers['content-type'] == 'image/png'
    assert await response.read() == b'\xFFpng'
    response = await web_app_client.get(
        '/openapi/homogeneous-multiple-responses', params={'ext': 'jpeg'},
    )
    assert response.status == 200
    assert response.headers['content-type'] == 'image/jpeg'
    assert await response.read() == b'\xAAjpeg'

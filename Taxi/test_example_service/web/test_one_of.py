import pytest

from taxi.codegen import swaggen_serialization

from example_service.generated.service.swagger.models import api
from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params(1),
        common.Params('a' * 10),
        common.Params(
            20,
            400,
            common.make_request_error(
                'Invalid value for body: \'20\' does not match any schemes; '
                'Invalid value for body: '
                '20 must be a value less than or equal to 10; '
                'Invalid value for body: '
                '\'20\' length must be greater than or equal to 10',
            ),
        ),
        common.Params(
            'aaa',
            400,
            common.make_request_error(
                'Invalid value for body: \'aaa\' does not match any schemes; '
                'Invalid value for body: \'aaa\' is not instance of int; '
                'Invalid value for body: '
                '\'aaa\' length must be greater than or equal to 10',
            ),
        ),
    ],
)
async def test_different_types(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/different_types', data=str(params.request),
    )
    assert response.status == params.status
    if params.response:
        assert await response.json() == params.response
    else:
        assert await response.text() == ''


@pytest.mark.parametrize(
    'params',
    [
        common.Params('a', response={'score': 'a'}),
        common.Params('aaaa', response={'score': 'aaaa', 'weight': 4}),
        common.Params(
            1,
            400,
            common.make_request_error(
                'Invalid value for body: 1 does not match any schemes; '
                'Invalid value for body: 1 is not instance of str; '
                'Invalid value to deserialize ComplexOneUser: 1 is not '
                'instance of dict',
            ),
        ),
        common.Params({'int_score': 1}, response={'score': 2}),
        common.Params(
            {'int_score': -2},
            500,
            common.make_internal_error(
                'Invalid value for score: -1 does not match any schemes; '
                'Invalid value for score: -1 must be a value greater than or '
                'equal to 0; '
                'Invalid value for score: -1 is not instance of str',
            ),
        ),
        common.Params(
            {'int_score': 1, 'int_weight': 20},
            response={'score': 2, 'weight': 20},
        ),
        common.Params(
            {'int_score': 1, 'int_weight': 200},
            500,
            common.make_internal_error(
                'Invalid value for weight: 200 does not match any schemes; '
                'Invalid value for weight: 200 must be a value less than or '
                'equal to 100; '
                'Invalid value for weight: 200 is not instance of list',
            ),
        ),
        common.Params({'string_score': 'tor'}, response={'score': 'bactor'}),
        common.Params(
            {'string_score': 1},
            400,
            common.make_request_error(
                'Invalid value for body: '
                '{\'string_score\': 1} does not match any schemes; '
                'Invalid value for body: '
                '{\'string_score\': 1} is not instance of str; '
                'Invalid value for string_score: 1 is not instance of str',
            ),
        ),
        common.Params(
            {'string_score': 'xyz', 'list_weight': 10},
            response={'score': 'bacxyz', 'weight': [10, 100]},
        ),
        common.Params(
            {'string_score': 'xyz', 'list_weight': 10},
            response={'score': 'bacxyz', 'weight': [10, 100]},
        ),
    ],
)
async def test_models(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/model_param', json=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params({'integer_score': 1}, response={'external': 1}),
        common.Params({'integer_score': -20}, response={'external': -20}),
        common.Params({'string_score': 12}, response={'external': '12'}),
        common.Params(
            {'integer_score': -1},
            500,
            common.make_internal_error(
                'Invalid value for external: '
                '-1 does not match any schemes; '
                'Invalid value for external: '
                '-1 must be a value less than or equal to -10; '
                'Invalid value for external: '
                '-1 does not match any schemes; '
                'Invalid value for external: '
                '-1 must be a value greater than or equal to 0; '
                'Invalid value for external:'
                ' -1 is not instance of str',
            ),
        ),
    ],
)
async def test_nested(web_app_client, params):
    response = await web_app_client.get(
        '/test_one_of/nested', params=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params('aaa', response=3),
        common.Params('a' * 10, response=10),
        common.Params(
            'a' * 9,
            400,
            common.make_request_error(
                'Invalid value for body: '
                '\'aaaaaaaaa\' does not match any schemes; '
                'Invalid value for body: '
                '\'aaaaaaaaa\' length must be greater than or equal to 10; '
                'Invalid value for body: '
                '\'aaaaaaaaa\' length must be less than or equal to 8',
            ),
        ),
    ],
)
async def test_same_type(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/same_type', data=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params([['a']], response=1),
        common.Params([['a'], ['b']], response=2),
        common.Params([['a', 'b', 'c'], ['b']], response=2),
        common.Params(
            [['a', 'b', 'c'], ['b' * 9]],
            400,
            common.make_request_error(
                'Invalid value for body_item_item: '
                '\'bbbbbbbbb\' does not match any schemes; '
                'Invalid value for body_item_item: '
                '\'bbbbbbbbb\' length must be greater than or equal to 10; '
                'Invalid value for body_item_item: '
                '\'bbbbbbbbb\' length must be less than or equal to 8',
            ),
        ),
    ],
)
async def test_list_in_list(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/list_in_list', json=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(-1, response=-1),
        common.Params(100, response=100),
        common.Params(
            5,
            500,
            common.make_response_error(
                'Invalid value for body: '
                'matching more than one schema: num. 0, 1',
            ),
        ),
    ],
)
async def test_ambiguous_int(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/ambiguous_int', data=str(params.request),
    )
    assert response.status == params.status
    assert await response.json() == params.response


async def test_bool_or_int(web_app_client):
    response = await web_app_client.post(
        '/test_one_of/bool_or_int', json={'field': True},
    )
    assert response.status == 200
    assert await response.text() == 'bool'

    response = await web_app_client.post(
        '/test_one_of/bool_or_int', json={'field': 1},
    )
    assert response.status == 200
    assert await response.text() == 'int'


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'name': 'abacaba', 'object_type': 'OneDiscriminator'},
            response={
                'name': 'abacaba',
                'age': 0,
                'object_type': 'TwoDiscriminator',
            },
        ),
        common.Params(
            request={
                'name': 'abacaba',
                'age': 1212,
                'object_type': 'TwoDiscriminator',
            },
            response={'name': '1212', 'object_type': 'OneDiscriminator'},
        ),
        common.Params(
            request={'name': 'xxx'},
            status=400,
            response=common.make_request_error(
                'Invalid value for body: '
                'discriminator property `object_type` is missing',
            ),
        ),
        common.Params(
            request={'name': 'xxx', 'object_type': '111'},
            status=400,
            response=common.make_request_error(
                'Invalid value for body: '
                'invalid discriminator `object_type` value: \'111\'',
            ),
        ),
        common.Params(
            request={
                'name': 'evil',
                'age': 1212,
                'object_type': 'TwoDiscriminator',
            },
            status=500,
            response=common.make_response_error(
                'Invalid value for body: '
                'invalid discriminator `object_type` value: \'boogie\'',
            ),
        ),
    ],
)
async def test_discriminator_only_property_name(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/discriminator-only-with-property', json=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'name': 'abacaba', 'object_type': 'first'},
            response={'name': 'abacaba', 'object_type': 'premier'},
        ),
        common.Params(
            request={'name': 'abacaba', 'object_type': 'eins'},
            response={'name': 'abacaba', 'object_type': 'premier'},
        ),
        common.Params(
            request={'name': '111', 'age': 100, 'object_type': 'second'},
            response={'name': '111', 'age': 100, 'object_type': 'deuxieme'},
        ),
        common.Params(
            request={'name': 'xxx'},
            status=400,
            response=common.make_request_error(
                'Invalid value for body: '
                'discriminator property `object_type` is missing',
            ),
        ),
        common.Params(
            request={'name': 'xxx', 'object_type': 'premier'},
            status=400,
            response=common.make_request_error(
                'Invalid value for body: '
                'invalid discriminator `object_type` value: \'premier\'',
            ),
        ),
        common.Params(
            request={'name': 'xxx', 'object_type': 'OneDiscriminator'},
            status=400,
            response=common.make_request_error(
                'Invalid value for body: '
                'invalid discriminator `object_type` '
                'value: \'OneDiscriminator\'',
            ),
        ),
        common.Params(
            request={'name': 'evil', 'age': 1212, 'object_type': 'second'},
            status=500,
            response=common.make_response_error(
                'Invalid value for body: '
                'invalid discriminator `object_type` value: \'boogie\'',
            ),
        ),
    ],
)
async def test_discriminator_mapping(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/discriminator-with-mapping', json=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'name': 'abacaba', 'object_type': 'OneDiscriminator'},
            response='OneDiscriminator',
        ),
        common.Params(
            request={
                'name': 'abacaba',
                'age': 100,
                'object_type': 'TwoDiscriminator',
            },
            response='TwoDiscriminator',
        ),
        common.Params(
            request={
                'name': 'abacaba',
                'object_type': 'OneOfInsideDiscriminator',
            },
            response='OneOfInsideDiscriminator',
        ),
        common.Params(
            request={
                'lame': 'lalala',
                'object_type': 'OneOfInsideDiscriminator',
            },
            response='OneOfInsideDiscriminator',
        ),
    ],
)
async def test_discriminator_one_of_inside(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/discriminator-internal-one-of', json=params.request,
    )
    assert response.status == params.status
    assert await response.text() == params.response


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'name': 'abacaba', 'object_type': 'OneDiscriminator'},
            response='OneDiscriminator',
        ),
        common.Params(
            request={
                'name': 'abacaba',
                'age': 100,
                'object_type': 'TwoDiscriminator',
            },
            response='TwoDiscriminator',
        ),
        common.Params(
            request={
                'lame': 'lalala',
                'name': 'bacbac',
                'object_type': 'AllOfInsideDiscriminator',
            },
            response='AllOfInsideDiscriminator',
        ),
    ],
)
async def test_discriminator_all_of_inside(web_app_client, params):
    response = await web_app_client.post(
        '/test_one_of/discriminator-internal-all-of', json=params.request,
    )
    assert response.status == params.status
    assert await response.text() == params.response


async def test_recursive_one_of():
    obj = api.RecursiveOneOf.deserialize(
        {'field': [{'field': [{'field': ['aa']}]}, 'aaa']},
    )
    assert obj.field[0].field[0].field[0] == 'aa'
    assert obj.field[1] == 'aaa'


async def test_inline_propogation():
    # checks TAXITOOLS-1831
    obj = api.Test1831.deserialize(
        {'first': ['1', '2'], 'second': {'count': 100}},
    )
    assert obj.first == ['1', '2']


async def test_discriminator_short_form():
    first = api.ShortDiscriminator.deserialize(
        {'one-of': {'object_type': 'premier', 'name': 'Vasya'}},
    )
    assert first.one_of.name == 'Vasya'
    second = api.ShortDiscriminator.deserialize(
        {'one-of': {'object_type': 'deuxieme', 'name': 'Assa', 'age': 11}},
    )
    assert second.one_of.name == 'Assa'

    with pytest.raises(swaggen_serialization.ValidationError) as exc_info:
        api.ShortDiscriminator.deserialize(
            {'one-of': {'object_type': 'troisieme', 'name': 'Assa!'}},
        )

    assert exc_info.value.args == (
        'Invalid value for one-of: invalid discriminator '
        '`object_type` value: \'troisieme\'',
    )


def test_mutable_one_of_variant_validation():
    obj = api.WeightedScore(weight=[99])
    assert isinstance(obj.weight, list)
    obj.weight.append(10000)
    with pytest.raises(swaggen_serialization.ValidationError) as exc_info:
        obj.validate_mutable_fields()

    assert exc_info.value.args == (
        'Invalid value for weight: [99, 10000] does not match any schemes; '
        'Invalid value for weight: [99, 10000] is not instance of int; '
        'Invalid value for weight_item: 10000 must be a value less than '
        'or equal to 100',
    )

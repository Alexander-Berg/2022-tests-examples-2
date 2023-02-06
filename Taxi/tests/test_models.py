# pylint: disable=redefined-outer-name,
import pytest

from taxi.codegen import swaggen_serialization as utils


def test_petstore_models(petstore):
    models = petstore.api_models()
    pet = models.Pet.deserialize(
        {
            'photoUrls': ['a', 'b', 'c'],
            'name': 'Kitty',
            'status': 'available',
            'category': {'name': 'cats', 'id': 1},
            'id': 1,
            'schema': {'a': 1},
        },
    )
    assert pet.name == 'Kitty'
    assert pet.photo_urls == ['a', 'b', 'c']
    assert pet.status == 'available'
    assert pet.category.name == 'cats'
    assert pet.category.id == 1
    assert pet.id == 1
    assert pet.schema == {'a': 1}

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.status = 'blablabla'
    assert exc_info.value.args == (
        'Invalid value for status: \'blablabla\' '
        'must be one of [\'available\', \'pending\', \'sold\']',
    )

    pet.status = 'sold'
    assert pet.status == 'sold'

    pet_data = pet.serialize()
    assert pet_data['status'] == 'sold'
    assert pet_data['name'] == 'Kitty'
    assert pet_data['photoUrls'] == ['a', 'b', 'c']
    assert pet_data['category']['name'] == 'cats'
    assert pet_data['category']['id'] == 1
    assert pet_data['id'] == 1


# pylint: disable=invalid-name, too-many-statements
def test_primitive_fields_validation(make_schema, generator):
    schema = make_schema(
        {
            'Pet': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'a': {
                        'type': 'number',
                        'maximum': 100,
                        'exclusiveMaximum': True,
                        'minimum': 1.0,
                        'exclusiveMinimum': False,
                    },
                    'b': {
                        'type': 'integer',
                        'maximum': 100,
                        'exclusiveMaximum': False,
                        'minimum': 1,
                        'exclusiveMinimum': True,
                    },
                    'c': {
                        'type': 'string',
                        'minLength': 2,
                        'maxLength': 10,
                        'pattern': r'x+',
                    },
                    'd': {
                        'type': 'array',
                        'items': {
                            'type': 'integer',
                            'maximum': 100,
                            'exclusiveMaximum': True,
                            'minimum': 1.0,
                            'exclusiveMinimum': False,
                        },
                        'maxItems': 4,
                        'minItems': 2,
                    },
                    'def': {'type': 'integer', 'format': 'int64'},
                },
            },
        },
    )
    pet_project = generator('pet', schema)
    models = pet_project.api_models()
    pet_dict = {'a': 1.0, 'b': 100, 'c': 'x' * 10, 'd': [5, 10], 'def': 1}
    pet = models.Pet.deserialize(pet_dict)
    assert pet.a == 1.0
    assert pet.b == 100
    assert pet.c == 'x' * 10
    assert pet.d == [5, 10]
    assert pet.def_ == 1

    assert pet.serialize() == pet_dict

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.a = 10000.0
    assert exc_info.value.args == (
        'Invalid value for a: 10000.0 must be a value less than 100',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.a = 0.0
    assert exc_info.value.args == (
        'Invalid value for a: '
        '0.0 must be a value greater than or equal to 1.0',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.a = 100.0
    assert exc_info.value.args == (
        'Invalid value for a: 100.0 must be a value less than 100',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.a = 'a'
    assert exc_info.value.args == (
        'Invalid value for a: \'a\' is not instance of (float, int)',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.b = 10.0
    assert exc_info.value.args == (
        'Invalid value for b: 10.0 is not instance of int',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.b = 1000
    assert exc_info.value.args == (
        'Invalid value for b: '
        '1000 must be a value less than or equal to 100',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.b = 0
    assert exc_info.value.args == (
        'Invalid value for b: 0 must be a value greater than 1',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.b = 1
    assert exc_info.value.args == (
        'Invalid value for b: 1 must be a value greater than 1',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.b = 'b'
    assert exc_info.value.args == (
        'Invalid value for b: \'b\' is not instance of int',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.c = 'x'
    assert exc_info.value.args == (
        'Invalid value for c: '
        '\'x\' length must be greater than or equal to 2',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.c = 'x' * 11
    assert exc_info.value.args == (
        'Invalid value for c: '
        '\'xxxxxxxxxxx\' length must be less than or equal to 10',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.c = 'a' * 5
    assert exc_info.value.args == (
        'Invalid value for c: \'aaaaa\' must match r\'x+\'',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = [1]
    assert exc_info.value.args == (
        'Invalid value for d: '
        '[1] number of items must be greater than or equal to 2',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = [1] * 5
    assert exc_info.value.args == (
        'Invalid value for d: '
        '[1, 1, 1, 1, 1] number of items must be less than or equal to 4',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = [100, 100]
    assert exc_info.value.args == (
        'Invalid value for d_item: 100 must be a value less than 100',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = [1000, 1000]
    assert exc_info.value.args == (
        'Invalid value for d_item: 1000 must be a value less than 100',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = [0, 0]
    assert exc_info.value.args == (
        'Invalid value for d_item: '
        '0 must be a value greater than or equal to 1.0',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = list('abc')
    assert exc_info.value.args == (
        'Invalid value for d_item: \'a\' is not instance of int',
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.d = 1
    assert exc_info.value.args == (
        'Invalid value for d: 1 is not instance of list',
    )

    pet.d.extend([10] * 5)
    with pytest.raises(utils.ValidationError) as exc_info:
        pet.serialize()
    assert exc_info.value.args == (
        'Invalid value for d: '
        '[5, 10, 10, 10, 10, 10, 10] '
        'number of items must be less than or equal to 4',
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.def_ = 2 ** 100
    assert exc_info.value.args == (
        f'Invalid value for def: {2 ** 100} too big for int64',
    )


def test_default(make_schema, generator):
    schema = make_schema(
        {
            'Pet': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'c': {'type': 'string', 'default': 'aaaa'},
                    'd': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'default': [0, 1],
                    },
                },
            },
        },
    )
    bet_project = generator('bet', schema)
    models = bet_project.api_models()
    pet = models.Pet.deserialize({})

    assert pet.c == 'aaaa'
    assert pet.d == [0, 1]

    pet.d.append(1)
    assert pet.d == [0, 1, 1]

    assert models.Pet.deserialize({}).d == [0, 1]


def test_user(petstore):
    models = petstore.api_models()
    user = models.User.deserialize(
        {'username': 'a', 'friends': [{'username': 'b'}]},
    )
    assert user.username == 'a'
    assert user.friends[0].username == 'b'


def test_currency(petstore):
    models = petstore.api_models()
    amount = models.Amount.deserialize({'value': 1.0, 'currency': 'AAA'})

    assert amount.value == 1.0
    assert amount.currency == 'AAA'

    with pytest.raises(utils.ValidationError) as exc_info:
        models.Amount.deserialize({'value': 1.0, 'currency': 'AAAA'})
    assert exc_info.value.args == (
        'Invalid value for currency: \'AAAA\' must match r\'^[A-Z]{3,3}$\'',
    )


def test_digit_word_with_slashed_regexp(petstore):
    models = petstore.api_models()

    with pytest.raises(utils.ValidationError) as exc_info:
        models.Amount.deserialize(
            {'value': 1.0, 'currency': 'AAA', 'digitWord': 'nonono'},
        )
    assert exc_info.value.args == (
        'Invalid value for digitWord: \'nonono\' must match r\'^\\d\\w$\'',
    )


def test_single_quote_regexp(petstore):
    models = petstore.api_models()

    with pytest.raises(utils.ValidationError) as exc_info:
        models.Amount.deserialize(
            {
                'value': 1.0,
                'currency': 'AAA',
                'insidiousSingleQuotes': 'nonono',
            },
        )

    assert exc_info.value.args == (
        'Invalid value for insidiousSingleQuotes: '
        '\'nonono\' must match r\'^\'$\'',
    )


def test_empty_model(petstore):
    models = petstore.api_models()
    obj = models.Emptiness.deserialize({})

    assert obj.__slots__ == ()
    assert obj.serialize() == {}


def test_int_in_number_type_field(petstore):
    models = petstore.api_models()
    amount = models.Amount.deserialize({'value': 1, 'currency': 'RUB'})
    assert amount.value == 1
    assert amount.currency == 'RUB'

    amount.value = 2
    assert amount.value == 2


def test_null_field_serialization(petstore):
    models = petstore.api_models()
    user = models.User.deserialize({'username': 'a'})

    assert user.email is None
    assert user.serialize() == {'username': 'a'}


def test_not_dict_model_deserialization(petstore):
    models = petstore.api_models()
    with pytest.raises(utils.ValidationError) as exc_info:
        models.User.deserialize('aaa')

    assert exc_info.value.args == (
        'Invalid value to deserialize User: \'aaa\' is not instance of dict',
    )


def test_one_of_ambiguity(petstore):
    models = petstore.api_models()

    assert (
        models.ShinyThing.deserialize(
            {'stone': {'shining': 'good'}},
        ).stone.shining
        == 'good'
    )
    assert (
        models.ShinyThing.deserialize(
            {'stone': {'shining': 'very-very-good'}},
        ).stone.shining
        == 'very-very-good'
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        models.ShinyThing.deserialize({'stone': {'shining': 'not-good'}})
    assert exc_info.value.args == (
        'Invalid value for stone: '
        '{\'shining\': \'not-good\'} match more than one scheme: '
        'num. 0, 1',
    )

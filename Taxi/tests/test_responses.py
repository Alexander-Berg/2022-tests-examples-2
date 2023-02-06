import datetime
import json

from aiohttp import web
import pytest
import pytz

from taxi.codegen import swaggen_serialization as utils


def test_response_with_model(petstore):
    responses = petstore.responses()
    pet_cls = petstore.api_models().Pet

    response_to_check = responses.FindPetsByStatus200(
        data=[pet_cls('Kitty', []), pet_cls('Snoopy', ['a/b'])],
    )
    for pet in response_to_check.data:
        assert isinstance(pet, pet_cls)
    serialized = response_to_check.serialize()
    assert isinstance(serialized, web.Response)
    assert serialized.content_type == 'application/json'
    data = json.loads(serialized.text)
    assert data == [
        {'photoUrls': [], 'name': 'Kitty'},
        {'photoUrls': ['a/b'], 'name': 'Snoopy'},
    ]


def test_headers(petstore):
    responses = petstore.responses()

    expires = '2018-10-22T18:43:39+03:00'
    expires_ts = 1540223019
    response_to_check = responses.LoginUser200(
        data='aaa',
        headers=responses.LoginUser200.Headers(
            x_expires_after=datetime.datetime.fromtimestamp(
                expires_ts, tz=pytz.utc,
            ),
            x_rate_limit=1,
        ),
        content_type='application/json',
    )

    serialized = response_to_check.serialize()
    assert isinstance(serialized, web.Response)
    assert serialized.text == '"aaa"'
    assert serialized.headers['x-rate-limit'] == '1'
    assert serialized.headers['X-EXPIRES-AFTER'] == expires


def test_response_validation(petstore):
    responses = petstore.responses()
    pet = petstore.api_models().Pet('name', ['url'])
    pet.photo_urls.append(1)
    response_to_check = responses.FindPetsByStatus200(data=[pet])
    with pytest.raises(utils.ValidationError) as exc_info:
        response_to_check.serialize()

    assert exc_info.value.args == (
        'Invalid value for photoUrls_item: 1 is not instance of str',
    )

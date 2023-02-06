# pylint: disable=redefined-outer-name,
import collections
import json

import multidict
import pytest

from taxi.codegen import swaggen_serialization as utils


class Request(collections.UserDict):
    def __init__(self, text=None, headers=None, match_info=None, query=None):
        super().__init__()
        self['log_extra'] = None
        self.text = text
        self.headers = headers
        self.match_info = match_info
        self.query = query


async def test_add_pet(petstore):
    async def get_text():
        return json.dumps(
            {
                'photoUrls': ['a', 'b', 'c'],
                'name': 'Kitty',
                'status': 'available',
                'category': {'name': 'cats', 'id': 1},
                'id': 1,
            },
        )

    request = Request(text=get_text)

    data = await petstore.request('add_pet').AddPet.create(request)
    pet = data.body
    assert pet.name == 'Kitty'
    assert pet.photo_urls == ['a', 'b', 'c']
    assert pet.status == 'available'
    assert pet.category.name == 'cats'
    assert pet.category.id == 1
    assert pet.id == 1

    with pytest.raises(utils.ValidationError) as exc_info:
        pet.status = 'blablabla'

    assert exc_info.value.args == (
        'Invalid value for status: \'blablabla\' '
        'must be one of [\'available\', \'pending\', \'sold\']',
    )


# pylint: disable=invalid-name
async def test_create_users_with_array_input(petstore):
    async def get_text():
        return json.dumps(
            [
                {
                    'userStatus': 1,
                    'phone': 'bacbac',
                    'password': 'admin11',
                    'email': 'admin@yandex-team.ru',
                    'lastName': 'Snow',
                    'firstName': 'John',
                    'username': 'king',
                    'id': 1,
                },
                {
                    'userStatus': 2,
                    'phone': 'x+x',
                    'password': 'xxx',
                    'email': 'x@yandex-team.ru',
                    'lastName': 'Whatever',
                    'firstName': 'Lola',
                    'username': 'queen',
                    'id': 2,
                },
            ],
        )

    request = Request(text=get_text)
    module = petstore.request('create_users_with_array_input')
    data = await module.CreateUsersWithArrayInput.create(request)

    king = data.body[0]
    queen = data.body[1]

    assert king.username == 'king'
    assert king.user_status == 1
    assert king.phone == 'bacbac'
    assert king.password == 'admin11'
    assert king.email == 'admin@yandex-team.ru'
    assert king.last_name == 'Snow'
    assert king.first_name == 'John'
    assert king.id == 1

    assert queen.username == 'queen'


async def test_delete_pet(petstore):
    request = Request(
        headers=multidict.CIMultiDict({'Api_KeY': '1234567890'}),
        match_info={'petId': '666'},
    )

    data = await petstore.request('delete_pet').DeletePet.create(request)

    assert data.api_key == '1234567890'
    assert data.pet_id == 666


async def test_find_pets_by_status(petstore):
    request = Request(
        query=multidict.MultiDict([('status', 'sold,available')]),
    )

    module = petstore.request('find_pets_by_status').FindPetsByStatus
    data = await module.create(request)

    assert set(data.status) == {'sold', 'available'}

    bad_request = Request(
        query=multidict.MultiDict([('status', 'sold,enslaved')]),
    )

    with pytest.raises(utils.ValidationError) as exc_info:
        await module.create(bad_request)
    assert exc_info.value.args == (
        'Invalid value for status_item: \'enslaved\' '
        'must be one of [\'available\', \'pending\', \'sold\']',
    )


async def test_get_pet(petstore):
    request = Request(match_info={'petId': '11'})
    module = petstore.request('get_pet_by_id').GetPetById
    data = await module.create(request)
    assert data.pet_id == 11

    request = Request(match_info={'petId': 'abc'})
    module = petstore.request('get_pet_by_id').GetPetById
    with pytest.raises(utils.ValidationError) as exc_info:
        await module.create(request)
    assert exc_info.value.args == (
        'Invalid value for petId: \'abc\' is not instance of int',
    )


async def test_user_login(petstore):
    request = Request(
        query=multidict.MultiDict(
            [('username', '1111'), ('password', 'password')],
        ),
    )

    module = petstore.request('login_user').LoginUser
    data = await module.create(request)

    assert data.username == 1111
    assert data.password == 'password'

    request = Request(
        query=multidict.MultiDict(
            [('username', 'alberist'), ('password', 'password')],
        ),
    )
    with pytest.raises(utils.ValidationError) as exc_info:
        await module.create(request)
    assert exc_info.value.args == (
        'Invalid value for username: \'alberist\' is not instance of int',
    )

    request = Request(query=multidict.MultiDict([('username', '1111')]))

    data = await module.create(request)

    assert data.username == 1111
    assert data.password == 'password'


async def test_find_by_tags(petstore):
    request = Request(query=multidict.MultiDict([('tags', 'a,b,c')]))

    module = petstore.request('find_pets_by_tags').FindPetsByTags
    data = await module.create(request)

    assert data.tags == ['a', 'b', 'c']


async def test_send_extra_field(petstore):
    async def get_text():
        return json.dumps({'photoUrls': ['a'], 'name': 'Bim', 'ear': 'black'})

    request = Request(text=get_text)

    data = await petstore.request('add_pet').AddPet.create(request)
    pet = data.body
    assert pet.name == 'Bim'
    assert pet.photo_urls == ['a']

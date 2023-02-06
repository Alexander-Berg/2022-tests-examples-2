import pytest


async def test_happy_path(web_app_client, load_json):
    response = await web_app_client.post(
        '/v1/form', json=load_json('valid_full_features_form.json'),
    )
    response_body = await response.text()
    print(response_body)
    assert response.status == 200


async def test_idempotent_dont_fall(upsert_form, load_json):
    yield upsert_form(load_json('valid_full_features_form.json'))
    yield upsert_form(load_json('valid_full_features_form.json'))


async def test_description_changed(_insert_forms_with_descriptions):
    first, second = await _insert_forms_with_descriptions('first', 'second')
    assert first['description'] != second['description']


@pytest.fixture
def _insert_forms_with_descriptions(upsert_form, get_form, load_json):
    async def _wrapper(first_description, second_description):
        data = load_json('valid_full_features_form.json')

        data['description'] = first_description
        await upsert_form(data)
        first = await get_form(data['form_name'])

        data['description'] = second_description
        await upsert_form(data)
        second = await get_form(data['form_name'])

        return first, second

    return _wrapper

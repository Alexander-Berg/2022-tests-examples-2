import pytest


@pytest.mark.parametrize(
    'data, expected_tags',
    [
        ({'entities': [{'type': 'udid', 'id': 'some_udid'}]}, ['three']),
        ({'entities': [{'type': 'udid', 'id': 'other_udid'}]}, []),
        (
            {
                'entities': [
                    {'type': 'user_phone_id', 'id': 'some_user_phone_id'},
                ],
            },
            ['one', 'two'],
        ),
        (
            {
                'entities': [
                    {'type': 'user_phone_id', 'id': 'other_user_phone_id'},
                ],
            },
            [],
        ),
        (
            {
                'entities': [
                    {'type': 'udid', 'id': 'some_udid'},
                    {'type': 'user_phone_id', 'id': 'some_user_phone_id'},
                ],
            },
            ['one', 'three', 'two'],
        ),
    ],
)
async def test_tags(web_app_client, data, expected_tags):
    response = await web_app_client.post('/v1/tags', json=data)
    assert response.status == 200
    content = await response.json()
    assert content == {'tags': expected_tags}

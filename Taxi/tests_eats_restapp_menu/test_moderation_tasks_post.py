# pylint: disable=redefined-outer-name,unused-variable
PARTNER_ID = 777
PLACE_ID = 109151


async def test_moderation_tasks_happy_path(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/list')
    def mock_moderation(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {
                        'task_id': '456',
                        'status': 'process',
                        'queue': 'restapp_moderation_menu',
                        'payload': (
                            '{"id":"qwertyuiop","photo_url":"http://url"}'
                        ),
                        'reasons': [],
                        'moderator_context': 'Ivanov',
                        'context': '{"place_id":1234567}',
                    },
                    {
                        'task_id': '123',
                        'status': 'process',
                        'queue': 'restapp_moderation_item',
                        'payload': (
                            '{"id":"qwertyuiop","value":'
                            '"{\\"name\\":\\"name\\",\\"'
                            'description\\":\\"new_descr\\"}"}'
                        ),
                        'reasons': [],
                        'moderator_context': 'Petrov',
                        'context': '{"place_id":1234567}',
                    },
                    {
                        'task_id': '246',
                        'status': 'process',
                        'queue': 'restapp_moderation_item',
                        'payload': (
                            '{"id":"qwerty","value":"'
                            '{\\"name\\":\\"name\\",\\'
                            '"description\\":\\"new_de'
                            'scr\\"}","modified_value"'
                            ':"{\\"description\\":\\"new_descr\\"}"}'
                        ),
                        'reasons': [],
                        'moderator_context': 'Petrov',
                        'context': '{"place_id":1234567}',
                    },
                ],
            },
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/moderation/tasks?place_id='
        + str(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        json={},
    )

    assert response.status_code == 200
    assert response.json() == {
        'isSuccess': True,
        'payload': [
            {
                'id': '456',
                'status': 'process',
                'reasons': [],
                'place_id': 1234567,
                'target_type': 'menu',
                'target_id': 'qwertyuiop',
                'data': [{'field': 'picture', 'value': 'http://url'}],
            },
            {
                'id': '123',
                'status': 'process',
                'reasons': [],
                'place_id': 1234567,
                'target_type': 'item',
                'target_id': 'qwertyuiop',
                'data': [
                    {'field': 'name', 'value': 'name'},
                    {'field': 'description', 'value': 'new_descr'},
                ],
            },
            {
                'id': '246',
                'status': 'process',
                'reasons': [],
                'place_id': 1234567,
                'target_type': 'item',
                'target_id': 'qwerty',
                'data': [{'field': 'description', 'value': 'new_descr'}],
            },
        ],
    }

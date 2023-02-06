# pylint: disable=unused-variable
ACTIONS_RESPONSE = [
    {
        'action_id': 'just_action_id',
        'title': 'просто тестовый тайтл',
        'comment': 'просто тестовый коммент',
    },
    {
        'action_id': 'get_user_pd',
        'title': 'Просмотр персональных данных пользователей',
        'comment': 'открыл(а) персональные данные пользователя',
        'object_id_name': 'Test_object_name',
    },
    {
        'action_id': 'get_driver_geotrack',
        'title': 'Просмотр геотрека водителя',
        'comment': 'открыл(а) геотрек водителя',
    },
    {
        'action_id': 'search_by_pd',
        'title': 'Поиск по персональным данным',
        'comment': 'искал(а) по пресональным данным',
    },
    {
        'action_id': 'create_something',
        'title': 'Создание чего-то прекрасного',
        'comment': 'создал(а) что-то прекрасное',
    },
    {
        'action_id': 'upload_file',
        'title': 'Загрузка важного файла',
        'comment': 'загрузил(а) важный файл',
    },
    {
        'action_id': 'approve_something',
        'title': 'Создание подтверждения чего-то прекрасного',
        'comment': 'создал(а) подтверждение на что-то прекрасное',
    },
    {
        'action_id': 'some_action_id',
        'title': 'some_title',
        'comment': 'some_comment',
    },
    {
        'action_id': 'create_log',
        'title': 'Создание записи лога',
        'comment': 'Записала логи',
    },
]


async def test_audit_actions(taxi_api_admin_client):
    # get all audit actions from service
    response = await taxi_api_admin_client.get('/audit_actions')
    assert response.status == 200
    data = await response.json()
    assert sorted(data, key=lambda x: x['action_id']) == sorted(
        ACTIONS_RESPONSE, key=lambda x: x['action_id'],
    )

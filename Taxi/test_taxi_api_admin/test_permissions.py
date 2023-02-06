# pylint: disable=unused-variable
PERMISSION_RESPONSE = {
    'permissions': {
        'send_sms_new': {
            'category_id': 'send_sms_category_id',
            'action': 'редактирование',
            'comment': 'отправка смс новое',
            'sections': ['Заказы'],
        },
        'view_drafts': {
            'category_id': 'drafts',
            'action': 'просмотр',
            'comment': 'списка черновиков',
            'category_name': 'Сервис аппрувов',
            'sections': [
                'Запуск скриптов',
                'Скрипты SURGE 3.0',
                'Новый сурдж',
                'Комиссии',
            ],
        },
    },
}


async def test_permission(taxi_api_admin_client):
    # get all permissions from service
    response = await taxi_api_admin_client.get('/permissions')
    assert response.status == 200
    assert await response.json() == PERMISSION_RESPONSE

async def test_partner_types(web_app_client):
    response = await web_app_client.get('/admin/v1/partner/')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'categories': [
            {
                'name': 'Новые',
                'id': 'new',
                'url': '/v1/partner/in-category/new/',
            },
            {
                'name': 'Обработанные',
                'id': 'resolved',
                'url': '/v1/partner/in-category/resolved/',
            },
            {
                'name': 'Отклоненные',
                'id': 'denied',
                'url': '/v1/partner/in-category/denied/',
            },
        ],
    }

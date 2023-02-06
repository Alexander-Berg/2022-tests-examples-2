async def test_service_ticket_enabled(web_app_client):

    response = await web_app_client.post('/fleet_common/tvm-service-enabled')

    assert response.status == 200


async def test_user_ticket_enabled(web_app_client):

    response = await web_app_client.post(
        '/fleet_common/tvm-user-enabled',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status == 200

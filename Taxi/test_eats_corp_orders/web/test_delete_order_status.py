async def test_200(
        web_app_client, proper_headers_code_get, notify_about_order,
):
    await notify_about_order()
    response = await web_app_client.post(
        '/v1/user/delete-order-status', headers=proper_headers_code_get,
    )
    assert response.status == 200


async def test_update_status(
        web_app_client, proper_headers_code_get, notify_about_order,
):
    await notify_about_order()
    response = await web_app_client.post(
        '/v1/user/delete-order-status', headers=proper_headers_code_get,
    )
    assert response.status == 200
    response2 = await web_app_client.post(
        '/v1/user/delete-order-status', headers=proper_headers_code_get,
    )
    assert response2.status == 404


async def test_404(web_app_client, proper_headers_code_get):
    response = await web_app_client.post(
        '/v1/user/delete-order-status', headers=proper_headers_code_get,
    )
    assert response.status == 404

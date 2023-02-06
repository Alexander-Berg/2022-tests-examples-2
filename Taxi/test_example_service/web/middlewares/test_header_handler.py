import pytest


async def test_handler(web_app_client):
    response = await web_app_client.get(
        '/middlewares/check_header', headers={'X-YaTaxi-Awesome': 'ABACABA'},
    )
    assert response.status == 200
    content = await response.text()
    assert content == 'abacaba'


@pytest.mark.parametrize('headers', [{}, {'X-YaTaxi-Awesome': 'ABACABA'}])
async def test_404(web_app_client, headers):
    response = await web_app_client.get(
        '/middlewares/checkheader', headers=headers,
    )
    assert response.status == 404

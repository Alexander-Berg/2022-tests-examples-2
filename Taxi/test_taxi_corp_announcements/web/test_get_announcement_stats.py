from aiohttp import web
import pytest

X_YATAXI_API_KEY = 'test_api_key'
X_REAL_IP = 'test_user_ip'


@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_get_announcement_stat(
        web_app_client, web_context, mockserver, patch,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _request(*args, **kwargs):
        return web.json_response(
            {'users': [{'uid': {'value': '3000062912'}, 'login': 'test'}]},
        )

    announcement_id = '12345'

    response = await web_app_client.get(
        '/v1/admin/announcement/stats',
        params={'announcement_id': announcement_id},
        headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY, 'X-Real-Ip': X_REAL_IP},
    )

    assert response.status == 200

    stats = await response.json()
    expected = {
        'clients_received': 3,
        'clients_read': 2,
        'clients_clicked': 2,
        'roles_received': 7,
        'roles_read': 3,
        'roles_clicked': 3,
    }

    assert stats == expected

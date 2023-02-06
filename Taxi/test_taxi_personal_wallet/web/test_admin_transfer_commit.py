from aiohttp import test_utils
import pytest


@pytest.mark.now('2021-03-08T12:00:00')
async def test_happy_path(
        web_app_client: test_utils.TestClient, stq, mockserver,
):
    @mockserver.handler('/zalogin/v1/internal/uid-info')
    async def _uid_info_handler(request):
        return mockserver.make_response(
            json={'type': 'phonish', 'yandex_uid': 'tmp'}, status=200,
        )

    response = await web_app_client.post(
        '/v1/admin/transfer/commit', json=dict(src_uid='uid1', dst_uid='uid2'),
    )
    json = await response.json()

    assert response.status == 200
    assert json == {'status': 'completed'}

    assert stq.personal_wallet_uid_notify_handler.times_called == 1
    data = stq.personal_wallet_uid_notify_handler.next_call()
    assert data['kwargs'] == {
        'event_type': 'admintransfer',
        'event_at': '2021-03-08T15:00:00+03:00',
        'phonish_uid': 'uid1',
        'portal_uid': 'uid2',
    }

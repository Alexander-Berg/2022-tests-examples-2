import pytest

from taxi_corp_announcements.api.common import announcements_helper as helper
from taxi_corp_announcements.internal import base_context

ANNOUNCEMENT_ID = '12345'
X_YATAXI_API_KEY = 'test_api_key'
X_YANDEX_UID = '12345'


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_approve_announcement(web_app_client, web_context):
    response = await web_app_client.post(
        '/v1/admin/announcement/approve/',
        params={'announcement_id': ANNOUNCEMENT_ID},
        headers={
            'X-Yandex-Uid': X_YANDEX_UID,
            'X-YaTaxi-Api-Key': X_YATAXI_API_KEY,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')
    announcement = await helper.fetch_announcement_by_id(ctx, ANNOUNCEMENT_ID)
    assert announcement['status'] == 'processing'


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
@pytest.mark.parametrize(
    'announcement_id, code, expected_content',
    [
        pytest.param(
            '98765',
            404,
            {
                'code': 'invalid-input',
                'details': {},
                'message': 'announcement not found',
                'status': 'error',
            },
            id='not_found',
        ),
        pytest.param(
            '23456',
            400,
            {
                'code': 'invalid-input',
                'details': {},
                'message': 'announcement is already approved',
                'status': 'error',
            },
            id='already_approved',
        ),
    ],
)
async def test_approve_announcement_fail(
        web_app_client, announcement_id, code, expected_content,
):
    response = await web_app_client.post(
        '/v1/admin/announcement/approve/',
        params={'announcement_id': announcement_id},
        headers={
            'X-Yandex-Uid': X_YANDEX_UID,
            'X-YaTaxi-Api-Key': X_YATAXI_API_KEY,
        },
    )
    assert response.status == code
    content = await response.json()
    assert content == expected_content

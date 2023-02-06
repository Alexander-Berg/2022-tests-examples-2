from typing import List

import pytest

from test_chatterbox import plugins as conftest


# pylint: disable=invalid-name
pytestmark = pytest.mark.usefixtures('mock_uuid_fixture')


@pytest.mark.now('2019-01-01T01:00:00')
async def test_incoming_sip_url(cbox: conftest.CboxWrap):
    await cbox.post('/v1/user/incoming_sip', data={})
    assert cbox.status == 200
    assert cbox.body_data['url'] == (
        'https://chatterbox.orivet.ru/widget/incoming?'
        'timestamp=1546304400&'
        'create_ticket_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net'
        '%2Fsupport_info%2Fwebhooks%2Fincoming_call&'
        'user_id=superuser%40test.test&'
        'webhook_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net%2F'
        'v1%2Fwebhooks%2F%7Btask_id%7D%2Fcall&token='
        'e48ffbba9a6af9ad3d5db6b431cd8916616bfbd842c0d23d0d2953a19adb8fc8'
    )


@pytest.mark.parametrize(
    ('groups', 'is_superuser', 'expected_status'),
    (
        # superuser don't need permission
        ([], True, 200),
        # user with permission
        (['chatterbox_incoming_sip'], False, 200),
        # user without permission
        ([], False, 403),
    ),
)
async def test_incoming_sip_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        groups: List[str],
        is_superuser: bool,
        expected_status: int,
):
    patch_auth(superuser=is_superuser, groups=groups)

    await cbox.post('/v1/user/incoming_sip', data={})

    assert cbox.status == expected_status

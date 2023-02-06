from typing import List

import pytest

from test_chatterbox import plugins as conftest


# pylint: disable=invalid-name
pytestmark = pytest.mark.usefixtures('mock_uuid_fixture')


@pytest.mark.config(
    CHATTERBOX_SIP_SOURCE_PHONE={
        '__default__': '+79666660435',
        'sources': [
            {
                'phone': '+79999999999',
                'conditions': {'line': 'second'},
                'tenant': 'ats1',
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('task_id', 'phone', 'sip_url'),
    (
        (
            # default source_phone
            '5b2cae5cb2682a976914c2a1',
            '+79099998877',
            'https://chatterbox.orivet.ru/default/widget?'
            'id=2104653b-dac3-43e3-9ac5-7869d0bd738d&'
            'local_num=%2B79666660435&'
            'num=%2B79099998877&'
            'timestamp=1546304400&'
            'user_id=superuser%40test.test&'
            'webhook_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net'
            '%2Fv1%2Fwebhooks%2F5b2cae5cb2682a976914c2a1%2Fcall&token='
            '83c0623ff5238b6fac780ac3c3e7d14148276b4d5bc8dec7756c08cc41e0e126',
        ),
        (
            # line source_phone
            '5b2cae5cb2682a976914c2a2',
            '+79099998877',
            'https://chatterbox.orivet.ru/ats1/widget?'
            'id=2104653b-dac3-43e3-9ac5-7869d0bd738d&'
            'local_num=%2B79999999999&'
            'num=%2B79099998877&'
            'timestamp=1546304400&'
            'user_id=superuser%40test.test&'
            'webhook_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net'
            '%2Fv1%2Fwebhooks%2F5b2cae5cb2682a976914c2a2%2Fcall&token='
            '8d6e7633c12efd71f2e0cb7ccd60ac5a600cc3051663029cf75ca8c96f19d3d6',
        ),
    ),
)
@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_url(
        cbox: conftest.CboxWrap, task_id: str, phone: str, sip_url: str,
):
    await cbox.query(
        '/v1/tasks/{}/sip_url'.format(task_id), params={'phone': phone},
    )
    assert cbox.status == 200
    assert cbox.body_data['url'] == sip_url


@pytest.mark.parametrize(
    ('groups', 'is_superuser', 'expected_status'),
    (
        # superuser don't need permission
        ([], True, 200),
        # user with permission
        (['chatterbox_outgoing_sip'], False, 200),
        # user without permission
        ([], False, 403),
    ),
)
async def test_outgoing_sip_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        groups: List[str],
        is_superuser: bool,
        expected_status: int,
):
    patch_auth(superuser=is_superuser, groups=groups)

    await cbox.query(
        '/v1/tasks/{}/sip_url'.format('5b2cae5cb2682a976914c2a1'),
        params={'phone': '+79099998877'},
    )

    assert cbox.status == expected_status


@pytest.mark.parametrize(
    ('task_id', 'is_superuser', 'expected_status', 'expected_response'),
    (
        (
            'invalid_id',
            True,
            400,
            {
                'code': 'bad_request',
                'message': 'Invalid task_id',
                'status': 'error',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            False,
            403,
            {
                'code': 'permission_forbidden',
                'message': 'User has no required permissions',
                'status': 'error',
            },
        ),
    ),
)
@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_errors(
        cbox: conftest.CboxWrap,
        patch_auth,
        task_id: str,
        is_superuser: bool,
        expected_status: int,
        expected_response: dict,
):
    patch_auth(superuser=is_superuser)

    await cbox.query(
        '/v1/tasks/{}/sip_url'.format(task_id),
        params={'phone': '+79099998877'},
    )
    assert cbox.status == expected_status
    assert cbox.body_data == expected_response

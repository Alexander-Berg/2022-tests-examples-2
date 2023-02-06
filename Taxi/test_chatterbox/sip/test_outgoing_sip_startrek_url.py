import pytest

from test_chatterbox import plugins as conftest

# pylint: disable=invalid-name
pytestmark = pytest.mark.usefixtures('mock_uuid_fixture')


@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_url_startrek(
        cbox: conftest.CboxWrap, mock_st_get_ticket_with_status,
):
    mocked_get_ticket = mock_st_get_ticket_with_status(
        status='open', data_constructor=conftest.construct_ticket_with_cc,
    )

    await cbox.query(
        '/v1/startrek/TEST-1/sip_url',
        params={
            'phone': '+79099998877',
            'mail': 'user_with_sip_permissions@yandex-taxi.yaconnect.com',
        },
    )
    assert cbox.status == 200
    assert cbox.body_data['url'] == (
        'https://chatterbox.orivet.ru/default/widget?'
        'id=2104653b-dac3-43e3-9ac5-7869d0bd738d&'
        'local_num=%2B79666660435&'
        'num=%2B79099998877&'
        'timestamp=1546304400&'
        'user_id=user_with_sip_permissions%40test.test&'
        'webhook_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net'
        '%2Fv1%2Fwebhooks%2FTEST-1%2Ftracker_call&token='
        'ec42d9cda47fb3e0c1e906651c9056649be2108f45e64cdd1f20c78cfa7e17f9'
    )
    assert mocked_get_ticket.calls[0] == {'ticket': 'TEST-1', 'profile': None}


@pytest.mark.parametrize(
    ('login', 'expected_status'),
    (
        ('user_with_sip_permissions@yandex-taxi.yaconnect.com', 200),
        ('superuser@yandex-taxi.yaconnect.com', 200),
        ('user_without_sip_permissions@yandex-taxi.yaconnect.com', 403),
    ),
)
@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_startrek_permissions(
        cbox: conftest.CboxWrap,
        mock_st_get_ticket_with_status,
        login: str,
        expected_status: int,
):
    mock_st_get_ticket_with_status(
        status='open', data_constructor=conftest.construct_ticket_with_cc,
    )
    await cbox.query(
        '/v1/startrek/TEST-1/sip_url',
        params={'phone': '+79099998877', 'mail': login},
    )
    assert cbox.status == expected_status


@pytest.mark.parametrize(
    ('login', 'expected_status', 'expected_response'),
    (
        # without postfix
        (
            'user_with_sip_permissions',
            400,
            {
                'status': 'error',
                'code': 'request_error',
                'message': 'Invalid mail',
            },
        ),
        # with invalid postfix
        (
            'user_with_sip_permissions@yandex.ru',
            400,
            {
                'status': 'error',
                'code': 'request_error',
                'message': 'Invalid mail',
            },
        ),
        (
            'user_without_sip_permissions@yandex-taxi.yaconnect.com',
            403,
            {
                'status': 'error',
                'code': 'permission_error',
                'message': 'User has no required permissions',
            },
        ),
    ),
)
@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_startrek_errors(
        cbox: conftest.CboxWrap,
        login: str,
        expected_status: int,
        expected_response: dict,
):
    await cbox.query(
        '/v1/startrek/{}/sip_url'.format('5b2cae5cb2682a976914c2a1'),
        params={'phone': '+79099998877', 'mail': login},
    )
    assert cbox.status == expected_status
    assert cbox.body_data == expected_response


@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={'support-taxi': {'country': 'country'}},
    STARTRACK_SIP_SOURCE_PHONE={
        '__default__': '+79666660435',
        'sources': [
            {
                'phone': '+79666666666',
                'conditions': {'country': 'rus'},
                'tenant': 'ats1',
            },
        ],
    },
)
@pytest.mark.now('2019-01-01T01:00:00')
async def test_outgoing_sip_url_startrek_conditions(
        cbox: conftest.CboxWrap, mock_st_get_ticket_with_status,
):
    mocked_get_ticket = mock_st_get_ticket_with_status(
        status='open',
        custom_fields={'country': 'rus'},
        data_constructor=conftest.construct_ticket_with_cc,
    )

    await cbox.query(
        '/v1/startrek/TEST-1/sip_url',
        params={
            'phone': '+79099998877',
            'mail': 'user_with_sip_permissions@yandex-taxi.yaconnect.com',
        },
    )
    assert cbox.status == 200
    assert cbox.body_data['url'] == (
        'https://chatterbox.orivet.ru/ats1/widget?'
        'id=2104653b-dac3-43e3-9ac5-7869d0bd738d&'
        'local_num=%2B79666666666&'
        'num=%2B79099998877&'
        'timestamp=1546304400&'
        'user_id=user_with_sip_permissions%40test.test&'
        'webhook_url=https%3A%2F%2Fsm-monitor-ext.tst.mobile.yandex.net'
        '%2Fv1%2Fwebhooks%2FTEST-1%2Ftracker_call&token='
        'bf67b0892087fc33b1173b74f5e3dfe0c8c0c98d20d2aee7291ad937c269c408'
    )
    assert mocked_get_ticket.calls

import pytest

AGENT_REGISTRATION_URL = '/external/v1/agent/registration'
BEFORE = '2021-12-09 11:00:00+03'
NOW = '2021-12-09 12:00:00+03'


def make_body(
        sip_username='user3_drvrc.com',
        reg_node='taxi-myt-phonereg-v6',
        reg_status='Registered',
        user_socket='127.0.0.1:1234',
):
    return {
        'sip_username': sip_username,
        'reg_node': reg_node,
        'reg_status': reg_status,
        'user_socket': user_socket,
    }


@pytest.mark.now('2021-12-09T12:00:00+0300')
@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
@pytest.mark.parametrize(
    [
        'body',
        'sip_username',
        'expected_code',
        'expected_status',
        'expected_reg_node',
        'expected_user_socket',
        'expected_reg_status_updated_at',
    ],
    (
        pytest.param(
            make_body(sip_username='1000010001', reg_status='Registered'),
            '1000010001',
            200,
            'Registered',
            'taxi-myt-phonereg-v6',
            '127.0.0.1:1234',
            NOW,
            id='agent by SIP user name, registered',
        ),
        pytest.param(
            make_body(sip_username='you', reg_status='Unregistered'),
            '1000010001',
            200,
            'BadStatus1',
            'node01',
            'IP1:PORT1',
            BEFORE,
            id='agent by SIP user name, unregistered (wrong node)',
        ),
        pytest.param(
            make_body(
                sip_username='you',
                reg_status='Unregistered',
                reg_node='node01',
                user_socket='IP1:PORT1',
            ),
            '1000010001',
            200,
            'Unregistered',
            'node01',
            'IP1:PORT1',
            NOW,
            id='agent by SIP user name, unregistered',
        ),
    ),
)
async def test_user_registration(
        taxi_callcenter_reg,
        body,
        sip_username,
        expected_code,
        expected_status,
        expected_reg_node,
        expected_user_socket,
        expected_reg_status_updated_at,
        pgsql,
):
    response = await taxi_callcenter_reg.post(AGENT_REGISTRATION_URL, body)
    assert response.status_code == expected_code

    if response.status_code != 200:
        return

    cursor = pgsql['callcenter_reg'].cursor()

    query = (
        f'SELECT reg_node, user_socket, reg_status'
        f', reg_status_updated_at::varchar '
        f'FROM callcenter_reg.agent '
        f'WHERE sip_username = \'{sip_username}\''
    )

    cursor.execute(query)

    res = cursor.fetchall()

    assert res == [
        (
            expected_reg_node,
            expected_user_socket,
            expected_status,
            expected_reg_status_updated_at,
        ),
    ]

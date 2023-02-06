import pytest

AGENT_INFO_URL = '/external/v1/agent/info?sip_username={}'


@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
@pytest.mark.parametrize(
    ['sip_username', 'expected_code', 'expected_data'],
    (
        pytest.param(
            '1000010000',
            200,
            (
                {
                    'reg_node': '',
                    'reg_status': 'Unregistered',
                    'sip_username': '1000010000',
                    'user_socket': '',
                }
            ),
            id='agent not exists',
        ),
        pytest.param(
            '1000010001',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Unregistered',
                    'sip_username': '1000010001',
                    'user_socket': 'IP1:PORT1',
                }
            ),
            id='agent bad status',
        ),
        pytest.param(
            '1000010002',
            200,
            (
                {
                    'reg_node': '',
                    'reg_status': 'Unregistered',
                    'sip_username': '1000010002',
                    'user_socket': '',
                }
            ),
            id='agent status unknown',
        ),
        pytest.param(
            '1000010003',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010003',
                    'user_socket': 'IP1:PORT2',
                }
            ),
            id='agent status registered',
        ),
        pytest.param(
            '1000010004',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010004',
                    'user_socket': 'IP1:PORT3',
                    'supervisor_info': {
                        'reg_node': '',
                        'reg_status': 'Unregistered',
                        'sip_username': '1000020000',
                    },
                }
            ),
            id='supervisor not exists',
        ),
        pytest.param(
            '1000010005',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010005',
                    'user_socket': 'IP1:PORT4',
                    'supervisor_info': {
                        'reg_node': 'node02',
                        'reg_status': 'Unregistered',
                        'sip_username': '1000020001',
                    },
                }
            ),
            id='supervisor bad status',
        ),
        pytest.param(
            '1000010006',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010006',
                    'user_socket': 'IP1:PORT5',
                    'supervisor_info': {
                        'reg_node': '',
                        'reg_status': 'Unregistered',
                        'sip_username': '1000020002',
                    },
                }
            ),
            id='supervisor status unknown',
        ),
        pytest.param(
            '1000010007',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010007',
                    'user_socket': 'IP1:PORT6',
                    'supervisor_info': {
                        'reg_node': 'node02',
                        'reg_status': 'Registered',
                        'sip_username': '1000020003',
                    },
                }
            ),
            id='supervisor status registered',
        ),
        pytest.param(
            'user_not_exists_drvrc.com',
            200,
            (
                {
                    'reg_node': '',
                    'reg_status': 'Unregistered',
                    'sip_username': 'user_not_exists_drvrc.com',
                    'user_socket': '',
                }
            ),
            id='agent not exists (iptel db)',
        ),
        pytest.param(
            '1000010008',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Unregistered',
                    'sip_username': '1000010008',
                    'user_socket': 'IP1:PORT1',
                }
            ),
            id='agent bad status',
        ),
        pytest.param(
            '1000010009',
            200,
            (
                {
                    'reg_node': '',
                    'reg_status': 'Unregistered',
                    'sip_username': '1000010009',
                    'user_socket': '',
                }
            ),
            id='agent status unknown',
        ),
        pytest.param(
            '1000010010',
            200,
            (
                {
                    'reg_node': 'node01',
                    'reg_status': 'Registered',
                    'sip_username': '1000010010',
                    'user_socket': 'IP1:PORT2',
                }
            ),
            id='agent status registered',
        ),
    ),
)
async def test_user_registration(
        taxi_callcenter_reg, sip_username, expected_code, expected_data,
):
    response = await taxi_callcenter_reg.post(
        AGENT_INFO_URL.format(sip_username),
    )
    assert response.status_code == expected_code
    assert response.json() == expected_data

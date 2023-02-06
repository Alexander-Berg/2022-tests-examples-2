import pytest


@pytest.mark.parametrize(
    'viewer,user_ticket,body,status,expected_data',
    [
        (
            'calltaxi_user',
            'calltaxi_user_ticket',
            {
                'from': '2022-01-01',
                'to': '2022-01-07',
                'login': 'calltaxi_user',
            },
            200,
            [
                {'date': '2022-01-01', 'marks': ['shift']},
                {'date': '2022-01-02', 'marks': ['break']},
                {
                    'date': '2022-01-03',
                    'marks': [
                        'shift',
                        'break',
                        'break',
                        'truancy',
                        'unspecified',
                    ],
                },
            ],
        ),
        (
            'taxisupport_user',
            'taxisupport_user_ticket',
            {
                'from': '2022-01-01',
                'to': '2022-01-07',
                'login': 'taxisupport_user',
            },
            200,
            [],
        ),
        (
            'taxisupport_user',
            'taxisupport_user_ticket',
            {
                'from': '2022-01-01',
                'to': '2022-01-07',
                'login': 'calltaxi_user',
            },
            200,
            [],
        ),
    ],
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {},
        'calltaxi': {
            'events_source': 'hrms',
            'main_permission': 'user_calltaxi',
        },
        'taxisupport': {
            'events_source': 'wfm',
            'main_permission': 'user_taxisupport',
        },
    },
)
async def test_marks(
        web_app_client,
        viewer,
        user_ticket,
        body,
        status,
        expected_data,
        mock_hrms_categories,
):
    response = await web_app_client.get(
        '/marks',
        headers={
            'X-Yandex-Login': viewer,
            'Accept-Language': 'ru-ru',
            'X-Ya-User-Ticket': user_ticket,
        },
        params=body,
    )
    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content == expected_data

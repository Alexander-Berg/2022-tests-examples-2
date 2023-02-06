import pytest


@pytest.mark.parametrize(
    'status, expected',
    [
        (
            200,
            {
                'entries': [
                    {
                        'name': 'some_config_name',
                        'value': {
                            'actions': [],
                            'entries': [],
                            'examples': [
                                {
                                    'context': {},
                                    'expected_actions': [],
                                    'expected_entries': [],
                                },
                            ],
                        },
                        'ns': 'entry_templates',
                        'project': 'taxi',
                        'version': 1,
                        'start_date': '2021-01-01T00:00:00+00:00',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2022-01-01T00:00:00Z')
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings', files=['defaults.sql'])
async def test_select(taxi_billing_settings, status, expected):
    response = await taxi_billing_settings.get('v1/entry_templates', params={})
    assert response.status_code == status
    assert response.json() == expected


@pytest.mark.parametrize(
    'status, expected',
    [(500, {'code': '500', 'message': 'Internal Server Error'})],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings', files=['broken_template.sql'])
async def test_failed_select(taxi_billing_settings, status, expected):
    response = await taxi_billing_settings.get('v1/entry_templates', params={})
    assert response.status_code == status
    assert response.json() == expected

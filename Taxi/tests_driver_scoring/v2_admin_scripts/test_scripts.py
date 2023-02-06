import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_v2_admin_scripts_scripts(taxi_driver_scoring):
    response = await taxi_driver_scoring.get(
        'v2/admin/scripts/scripts',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )

    assert response.status_code == 200

    data = response.json()

    def bonus_key(data):
        return data['script_name']

    def script_key(data):
        return '_'.join(sorted([str(i) for i in data.values()]))

    # Soring
    data['scripts'] = sorted(data['scripts'], key=bonus_key)
    for bonus in data['scripts']:
        bonus['scripts'] = sorted(bonus['scripts'], key=script_key)

    # Checking
    assert data['scripts'] == sorted(
        [
            {
                'script_name': 'bonus-1',
                'scripts': sorted(
                    [
                        {
                            'revision': 0,
                            'type': 'calculate',
                            'id': 10,
                            'active': False,
                            'maintainers': [],
                        },
                        {
                            'revision': 1,
                            'type': 'calculate',
                            'id': 11,
                            'active': True,
                            'maintainers': [],
                        },
                        {
                            'revision': 2,
                            'type': 'calculate',
                            'id': 12,
                            'active': False,
                            'maintainers': [],
                        },
                        {
                            'revision': 0,
                            'type': 'filter',
                            'id': 13,
                            'active': True,
                            'maintainers': [],
                        },
                    ],
                    key=script_key,
                ),
            },
            {
                'script_name': 'bonus-2',
                'scripts': sorted(
                    [
                        {
                            'revision': 0,
                            'type': 'filter',
                            'id': 14,
                            'active': True,
                            'maintainers': [],
                        },
                    ],
                    key=script_key,
                ),
            },
        ],
        key=bonus_key,
    )

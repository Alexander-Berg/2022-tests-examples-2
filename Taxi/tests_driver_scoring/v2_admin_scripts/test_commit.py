import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_simple(taxi_driver_scoring, pgsql):
    def execute_query(query):
        pg_cursor = pgsql['driver_scoring'].cursor()
        pg_cursor.execute(query)
        return list(pg_cursor)

    async def commit_script(
            script_name,
            script_type,
            content,
            maintainers=None,
            config_name=None,
    ):
        # TODO EFFICIENCYDEV-15847:
        # Switch back to passing json directly to the function call
        json = {
            'script_name': script_name,
            'type': script_type,
            'content': content,
            'tests': [],
        }
        if maintainers:
            json['maintainers'] = maintainers
        if config_name:
            json['config_name'] = config_name
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/commit',
            headers={
                'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
                'X-YaTaxi-Draft-Id': '0',
            },
            json=json,
        )
        assert response.status_code == 200

    # Adding several scripts
    await commit_script(
        script_name='bonus_1',
        script_type='filter',
        content='return 1',
        maintainers=['alex-tsarkov', 'dulumzhiev'],
    )
    await commit_script(
        script_name='bonus_1',
        script_type='filter',
        content='return 2',
        maintainers=['fourthrome'],
    )
    await commit_script(
        script_name='bonus_2',
        script_type='filter',
        content='return 1',
        config_name='bonus_2_config',
    )
    await commit_script(
        script_name='bonus_3', script_type='calculate', content='return 1',
    )
    # Check that tests were added
    items = execute_query(
        'select '
        '    bonus_name, '
        '    revision, '
        '    updated, '
        '    type, '
        '    content, '
        '    id, '
        '    maintainers, '
        '    config_name '
        'from scripts.js_scripts',
    )
    now = datetime.datetime(2020, 2, 2, 2, 2, 2)
    assert items == [
        (
            'bonus_1',
            0,
            now,
            'filter',
            'return 1',
            1,
            ['alex-tsarkov', 'dulumzhiev'],
            None,
        ),
        ('bonus_1', 1, now, 'filter', 'return 2', 2, ['fourthrome'], None),
        ('bonus_2', 0, now, 'filter', 'return 1', 3, [], 'bonus_2_config'),
        ('bonus_3', 0, now, 'calculate', 'return 1', 4, [], None),
    ]
    # Check that scripts were activated properly
    items = execute_query('select * from scripts.active_scripts')
    assert items == [
        (1, now, 'bonus_1', 'filter', 2),
        (3, now, 'bonus_2', 'filter', 3),
        (4, now, 'bonus_3', 'calculate', 4),
    ]


async def test_v2_admin_scripts_commit_empty_maintainers(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'failure',
            'type': 'filter',
            'content': 'return 1',
            'tests': [],
            'maintainers': [],
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_v2_admin_scripts_commit_overwrite_maintainers(
        taxi_driver_scoring, pgsql,
):
    async def post_script(request):
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/commit',
            headers={
                'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
                'X-YaTaxi-Draft-Id': '0',
            },
            json=request,
        )
        assert response.status_code == 200
        return response

    async def get_scripts():
        response = await taxi_driver_scoring.get(
            'v2/admin/scripts/scripts',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        )
        assert response.status_code == 200
        return response

    request = {
        'script_name': 'some_name',
        'type': 'filter',
        'content': 'return 1',
        'tests': [],
        'maintainers': ['fourthrome'],
        'config_name': 'some_name_config',
    }

    await post_script(request)
    response = await get_scripts()
    assert response.json()['scripts'][0]['scripts'][0]['maintainers'] == [
        'fourthrome',
    ]
    assert (
        response.json()['scripts'][0]['scripts'][0]['config_name']
        == 'some_name_config'
    )

    # Now make a new revision of the same script,
    # but change maintainers
    request['maintainers'] = ['alex-tsarkov', 'dulumzhiev']

    response = await post_script(request)
    response = await get_scripts()
    assert response.json()['scripts'][0]['scripts'][0]['maintainers'] == [
        'alex-tsarkov',
        'dulumzhiev',
    ]


async def test_v2_admin_scripts_commit_empty_config_name_fail(
        taxi_driver_scoring,
):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'failure',
            'type': 'filter',
            'content': 'return 1',
            'tests': [],
            'config_name': '',
        },
    )

    assert response.status_code == 400

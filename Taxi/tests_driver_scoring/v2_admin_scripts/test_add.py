import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.parametrize(
    'data, expected_status',
    [
        (
            {
                'script_name': 'bonus_1',
                'type': 'wrong_type',
                'content': 'return 1',
            },
            400,
        ),
    ],
)
@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_v2_admin_scripts_add_errors(
        taxi_driver_scoring, data, expected_status,
):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=data,
    )

    assert response.status_code == expected_status


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_v2_admin_scripts_add(taxi_driver_scoring, pgsql):
    def execute_query(query):
        pg_cursor = pgsql['driver_scoring'].cursor()
        pg_cursor.execute(query)
        return list(pg_cursor)

    async def add_script(
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
        }
        if maintainers:
            json['maintainers'] = maintainers
        if config_name:
            json['config_name'] = config_name
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/add',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=json,
        )

        assert response.status_code == 200

    # Validate that database is empty
    items = execute_query('select * from scripts.js_scripts')

    assert not items

    # Adding several scripts
    await add_script(
        script_name='bonus_1',
        script_type='filter',
        content='return 1',
        maintainers=['alex-tsarkov', 'dulumzhiev'],
    )
    await add_script(
        script_name='bonus_1',
        script_type='postprocess_results',
        content='postprocess_results.field = 3;',
        maintainers=['fourthrome'],
    )
    await add_script(
        script_name='bonus_1',
        script_type='filter',
        content='return 2',
        config_name='bonus_1_config',
    )
    await add_script(
        script_name='bonus_3', script_type='calculate', content='return 1',
    )

    # Validate database
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
        (
            'bonus_1',
            0,
            now,
            'postprocess_results',
            'postprocess_results.field = 3;',
            2,
            ['fourthrome'],
            None,
        ),
        ('bonus_1', 1, now, 'filter', 'return 2', 3, [], 'bonus_1_config'),
        ('bonus_3', 0, now, 'calculate', 'return 1', 4, [], None),
    ]


async def test_v2_admin_scripts_add_validation_fail(
        taxi_driver_scoring, pgsql,
):
    body = {
        'script_name': 'bonus_1',
        'type': 'calculate',
        'content': 'will not compile',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 400

    resp_body = response.json()
    assert resp_body['message'].startswith(
        'Script validation failed: JS compile error',
    )
    assert resp_body['code_point'] == {
        'column_begin': 5,
        'column_end': 9,
        'line': 1,
    }
    assert resp_body['status'] == 400


async def test_v2_admin_scripts_add_empty_maintainers(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'failure',
            'type': 'filter',
            'content': 'return 1',
            'maintainers': [],
        },
    )

    assert response.status_code == 400


async def test_v2_admin_scripts_add_empty_config_name(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'failure',
            'type': 'filter',
            'content': 'return 1',
            'config_name': '',
        },
    )
    assert response.status_code == 400

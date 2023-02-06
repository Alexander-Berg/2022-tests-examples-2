import tests_driver_scoring.tvm_tickets as tvm_tickets


def _execute_query(pgsql, query):
    pg_cursor = pgsql['driver_scoring'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


def _pgsql_format(*values):
    return [(value,) for value in values]


async def _prepare_scripts(taxi_driver_scoring, pgsql):
    # Validate that database is empty
    items = _execute_query(pgsql, 'SELECT * FROM scripts.js_scripts')
    assert not items
    items = _execute_query(pgsql, 'SELECT * FROM scripts.active_scripts')
    assert not items
    items = _execute_query(pgsql, 'SELECT * FROM scripts.tests')
    assert not items

    # Add two revisions of two scripts
    for script_id in [1, 2]:
        for _ in range(2):
            response = await taxi_driver_scoring.post(
                'v2/admin/scripts/commit',
                headers={
                    'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
                    'X-YaTaxi-Draft-Id': 'fake id',
                },
                json={
                    'script_name': f'dummy_script_{script_id}',
                    'type': 'calculate',
                    'content': 'return 0;',
                    'maintainers': ['fourthrome'],
                    'config_name': f'dummy_script_config_{script_id}',
                    'tests': [
                        {
                            'name': 'some_test',
                            'test_input': {},
                            'test_output': {'return_value': 0},
                        },
                    ],
                },
            )
            assert response.status_code == 200


async def test_successful_delete_bulk(taxi_driver_scoring, pgsql):
    # Fill the db
    await _prepare_scripts(taxi_driver_scoring, pgsql)

    # Delete one active and one inactive script
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': [1, 4]},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Check that db has changed
    items = _execute_query(pgsql, 'SELECT id from scripts.js_scripts')
    assert sorted(items) == _pgsql_format(2, 3)
    items = _execute_query(
        pgsql, 'SELECT script_id from scripts.active_scripts',
    )
    assert sorted(items) == _pgsql_format(2)
    items = _execute_query(pgsql, 'SELECT script_id from scripts.tests')
    assert sorted(items) == _pgsql_format(2, 3)


async def test_failed_delete_bulk(taxi_driver_scoring, pgsql):
    # Fill the db
    await _prepare_scripts(taxi_driver_scoring, pgsql)

    # Delete one active, one inactive and some non-existing scripts
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': [1, 5, 4, 42]},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'script_ids_not_found',
        'details': '[5, 42]',
    }

    # Validate db integrity
    items = _execute_query(pgsql, 'SELECT id from scripts.js_scripts')
    assert sorted(items) == _pgsql_format(1, 2, 3, 4)
    items = _execute_query(
        pgsql, 'SELECT script_id from scripts.active_scripts',
    )
    assert sorted(items) == _pgsql_format(2, 4)
    items = _execute_query(pgsql, 'SELECT script_id from scripts.tests')
    assert sorted(items) == _pgsql_format(1, 2, 3, 4)


async def test_delete_bulk_incorrect_request(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': []},
    )
    assert response.status_code == 400

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': None},
    )
    assert response.status_code == 400

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={},
    )
    assert response.status_code == 400

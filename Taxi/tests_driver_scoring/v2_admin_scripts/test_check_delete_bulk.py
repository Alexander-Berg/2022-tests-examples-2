import tests_driver_scoring.tvm_tickets as tvm_tickets


def _execute_query(pgsql, query):
    pg_cursor = pgsql['driver_scoring'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


async def _prepare_scripts(taxi_driver_scoring, pgsql):
    # Validate that database is empty
    items = _execute_query(pgsql, 'SELECT * FROM scripts.js_scripts')
    assert not items

    # Add several scripts
    for _ in range(3):
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/add',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json={
                'script_name': 'dummy_script',
                'type': 'calculate',
                'content': 'return 0;',
                'maintainers': ['fourthrome'],
                'config_name': 'dummy_script_config',
            },
        )
        assert response.status_code == 200


async def test_successful_check_delete_bulk(taxi_driver_scoring, pgsql):
    # Fill the db
    await _prepare_scripts(taxi_driver_scoring, pgsql)

    # Check
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': [1, 2]},
    )
    assert response.status_code == 200
    assert response.json()['data'] == {'script_ids': [1, 2]}


async def test_failed_check_delete_bulk(taxi_driver_scoring, pgsql):
    # Fill the db
    await _prepare_scripts(taxi_driver_scoring, pgsql)

    # Check missing ids
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-delete-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'script_ids': [2, 3, 4, 5]},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'script_ids_not_found',
        'details': '[4, 5]',
    }


async def test_check_delete_bulk_incorrect_request(taxi_driver_scoring):
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

import tests_driver_scoring.tvm_tickets as tvm_tickets


def _execute_query(pgsql, query):
    pg_cursor = pgsql['driver_scoring'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


async def test_basic_delete_plugin(taxi_driver_scoring, pgsql):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # Delete it
    response = await taxi_driver_scoring.delete(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Check db
    items = _execute_query(
        pgsql, 'SELECT name, type, module, tags_in_use FROM scripts.plugins',
    )
    assert not items


async def test_failed_delete_plugin(taxi_driver_scoring):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # Delete a plugin with the same name, but a different module
    response = await taxi_driver_scoring.delete(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'cpp'},
    )
    assert response.status_code == 404


async def test_missing_params_delete_plugin(taxi_driver_scoring):
    # Delete a plugin without a name
    response = await taxi_driver_scoring.delete(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'type': 'calculate', 'module': 'cpp'},
    )
    assert response.status_code == 400

    # Delete a plugin without a type
    response = await taxi_driver_scoring.delete(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'module': 'cpp'},
    )
    assert response.status_code == 400

    # Delete a plugin without a module
    response = await taxi_driver_scoring.delete(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate'},
    )
    assert response.status_code == 400

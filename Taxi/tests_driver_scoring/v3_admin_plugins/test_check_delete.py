import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_basic_check_delete_plugin(taxi_driver_scoring, pgsql):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # (check-)Delete it
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['data'] == {}
    assert response.json()['lock_ids'] == [
        {'custom': True, 'id': 'driver_scoring_some_plugin_calculate_js'},
    ]


async def test_failed_check_delete_plugin(taxi_driver_scoring):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # (check-)Delete a plugin with the same name and type, but different module
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'cpp'},
    )
    assert response.status_code == 404

    # (check-)Delete a plugin with the same type and module, but different name
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'another_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 404

    # (check-)Delete a plugin with the same name and module, but different type
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'filter', 'module': 'js'},
    )
    assert response.status_code == 404


async def test_missing_params_check_delete_plugin(taxi_driver_scoring):
    # (check-)Delete a plugin without a name
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'type': 'calculate', 'module': 'cpp'},
    )
    assert response.status_code == 400

    # (check-)Delete a plugin without a type
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'module': 'js'},
    )
    assert response.status_code == 400

    # (check-)Delete a plugin without a module
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-delete',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate'},
    )
    assert response.status_code == 400

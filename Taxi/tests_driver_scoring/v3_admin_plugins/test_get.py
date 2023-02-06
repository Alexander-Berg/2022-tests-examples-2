import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_basic_get_plugin(taxi_driver_scoring):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # Get it back
    response = await taxi_driver_scoring.get(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['tags_in_use'] = sorted(response_json['tags_in_use'])
    assert response_json == {
        'name': 'some_plugin',
        'type': 'calculate',
        'module': 'js',
        'tags_in_use': ['tag1', 'tag2'],
    }


async def test_failed_get_plugin(taxi_driver_scoring):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # Get a plugin with the same name and type, but a different module
    response = await taxi_driver_scoring.get(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'cpp'},
    )
    assert response.status_code == 404


async def test_missing_params_get_plugin(taxi_driver_scoring):
    # Get a plugin without a module
    response = await taxi_driver_scoring.get(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate'},
    )
    assert response.status_code == 400

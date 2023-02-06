import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_basic_check_put_plugin(taxi_driver_scoring, pgsql):
    # (check-)Put a plugin
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert sorted(resp_body['data']['tags_in_use']) == ['tag1', 'tag2']
    assert response.json()['lock_ids'] == [
        {'custom': True, 'id': 'driver_scoring_some_plugin_calculate_js'},
    ]


async def test_missing_params_check_put_plugin(taxi_driver_scoring):
    # (check-)Put a plugin without a name
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'type': 'calculate', 'module': 'cpp'},
        json={'tags_in_use': ['tag3', 'tag4']},
    )
    assert response.status_code == 400

    # (check-)Put a plugin without a type
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'module': 'js'},
        json={'tags_in_use': ['tag3', 'tag4']},
    )
    assert response.status_code == 400

    # (check-)Put a plugin without a module
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate'},
        json={'tags_in_use': ['tag3', 'tag4']},
    )
    assert response.status_code == 400

    # (check-)Put a plugin without tags_in_use
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 400


async def test_incorrect_query_params(taxi_driver_scoring):
    # (check-)Put a plugin with incorrect type
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': '', 'module': 'js'},
    )
    assert response.status_code == 400

    # (check-)Put a plugin with incorrect module
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': ''},
    )
    assert response.status_code == 400


async def test_tags_service_status_4xx(
        taxi_driver_scoring, mock_tags_v1_topics_items,
):
    mock_tags_v1_topics_items.set_mode('status_4xx')

    # Will fail, as we get 4xx response from tags' service
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1']},
    )
    assert response.status_code == 500


async def test_tags_service_status_5xx(
        taxi_driver_scoring, mock_tags_v1_topics_items,
):
    mock_tags_v1_topics_items.set_mode('status_5xx')

    # Will fail, as we get 5xx response from tags' service
    response = await taxi_driver_scoring.post(
        f'v3/admin/plugins/check-put',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1']},
    )
    assert response.status_code == 502
    assert (
        response.json()['message']
        == 'Got 5xx status code from tags/v1/topics/items'
    )

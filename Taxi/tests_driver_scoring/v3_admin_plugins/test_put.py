import tests_driver_scoring.tvm_tickets as tvm_tickets


def _execute_query(pgsql, query):
    pg_cursor = pgsql['driver_scoring'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


async def test_basic_put_plugin(taxi_driver_scoring, pgsql):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Make sure it arrived into db
    items = _execute_query(
        pgsql, 'SELECT name, type, module, tags_in_use FROM scripts.plugins',
    )
    assert items[0][0] == 'some_plugin'
    assert items[0][1] == 'calculate'
    assert items[0][2] == 'js'
    assert sorted(items[0][3]) == ['tag1', 'tag2']


async def test_colliding_put_plugin(taxi_driver_scoring, pgsql):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag2']},
    )
    assert response.status_code == 200

    # Put a plugin with the same secondary key
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag3', 'tag4']},
    )
    assert response.status_code == 200

    # Make sure the plugin was overwritten
    items = _execute_query(
        pgsql, 'SELECT name, type, module, tags_in_use FROM scripts.plugins',
    )
    assert sorted(items[0][3]) == ['tag3', 'tag4']


async def test_missing_params_put_plugin(taxi_driver_scoring):
    # Put a plugin without a module
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate'},
        json={'tags_in_use': ['tag3', 'tag4']},
    )
    assert response.status_code == 400

    # Put a plugin without tags_in_use
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
    )
    assert response.status_code == 400


async def test_incorrect_tags_in_use(taxi_driver_scoring):
    # Put a plugin
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={
            'tags_in_use': [
                'tag_not_from_topic',
                'tag1',
                'another_missing_tag',
            ],
        },
    )
    assert response.status_code == 400
    assert (
        response.json()['message'] == 'Some tags are not in topic: '
        '["another_missing_tag", "tag_not_from_topic"]'
    )


async def test_tags_service_status_4xx(
        taxi_driver_scoring, mock_tags_v1_topics_items,
):
    mock_tags_v1_topics_items.set_mode('status_4xx')

    # Will fail, as we get 4xx response from tags' service
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
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
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1']},
    )
    assert response.status_code == 502
    assert (
        response.json()['message']
        == 'Got 5xx status code from tags/v1/topics/items'
    )

import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_validate_tags_topic_append(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        f'v1/validate-tags-topic',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'action': 'append', 'tags': ['tag_5']},
    )
    assert response.status_code == 200
    assert response.json() == {'permission': 'allowed', 'details': {}}


async def test_validate_tags_topic_remove_success(taxi_driver_scoring):
    # Put a few plugins
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag3']},
    )
    assert response.status_code == 200

    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'another_plugin', 'type': 'filter', 'module': 'js'},
        json={'tags_in_use': ['tag3']},
    )
    assert response.status_code == 200

    # Request removing tags that are not being used by plugins
    response = await taxi_driver_scoring.post(
        f'v1/validate-tags-topic',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'action': 'remove', 'tags': ['tag2', 'tag4']},
    )
    assert response.status_code == 200
    assert response.json() == {'permission': 'allowed', 'details': {}}


async def test_validate_tags_topic_remove_fail(taxi_driver_scoring):
    # Put a few plugins
    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'some_plugin', 'type': 'calculate', 'module': 'js'},
        json={'tags_in_use': ['tag1', 'tag3']},
    )
    assert response.status_code == 200

    response = await taxi_driver_scoring.put(
        f'v3/admin/plugins',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        params={'name': 'another_plugin', 'type': 'filter', 'module': 'js'},
        json={'tags_in_use': ['tag3']},
    )
    assert response.status_code == 200

    # Request removing some tags that are in use (and some that aren't)
    response = await taxi_driver_scoring.post(
        f'v1/validate-tags-topic',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'action': 'remove', 'tags': ['tag1', 'tag2', 'tag3', 'tag4']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['permission'] == 'prohibited'
    assert (
        response_json['message']
        == 'Some of the tags are still in use in driver-scoring'
    )
    assert sorted(response_json['details']['errors']) == [
        'Plugin {\'name\': \'another_plugin\', \'type\': \'filter\', \'module\': \'js\'} '
        'still uses tags: [\'tag3\']',
        'Plugin {\'name\': \'some_plugin\', \'type\': \'calculate\', \'module\': \'js\'} '
        'still uses tags: [\'tag1\', \'tag3\']',
    ]


async def test_validate_tags_topic_empty_tags(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        f'v1/validate-tags-topic',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'action': 'append', 'tags': []},
    )
    assert response.status_code == 200
    assert response.json() == {'permission': 'allowed', 'details': {}}

    response = await taxi_driver_scoring.post(
        f'v1/validate-tags-topic',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={'action': 'remove', 'tags': []},
    )
    assert response.status_code == 200
    assert response.json() == {'permission': 'allowed', 'details': {}}

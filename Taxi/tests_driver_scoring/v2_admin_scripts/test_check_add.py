import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_check_add(taxi_driver_scoring):
    body = {
        'script_name': 'script_1',
        'content': 'postprocess_results.field = 3;',
        'type': 'postprocess_results',
        'maintainers': ['fourthrome'],
        'config_name': 'script_1_config',
    }
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['data'] == body


async def test_v2_admin_scripts_add_validation_fail(
        taxi_driver_scoring, pgsql,
):
    body = {
        'script_name': 'bonus_1',
        'type': 'calculate',
        'content': 'will not compile',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-add',
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


async def test_v2_admin_scripts_add_empty_maintainers_fail(
        taxi_driver_scoring,
):
    body = {
        'script_name': 'some_name',
        'content': 'return 0;',
        'type': 'calculate',
        'maintainers': [],
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 400


async def test_v2_admin_scripts_add_empty_config_name_fail(
        taxi_driver_scoring,
):
    body = {
        'script_name': 'some_name',
        'content': 'return 0;',
        'type': 'calculate',
        'config_name': '',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 400

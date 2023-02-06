import pytest


@pytest.mark.parametrize(
    'params, expected_response_json',
    [
        pytest.param(
            {'service_id': 1}, 'service-by-id.json', id='get service by id',
        ),
        pytest.param(
            {'service_id': 2},
            'deleted-service-by-id.json',
            id='get deleted service by id',
        ),
        pytest.param(
            {'project_id': 1},
            'get-by-project_id.json',
            id='get by project id',
        ),
    ],
)
async def test_get_services(
        load_json,
        web_app_client,
        staff_mockserver,
        login_mockserver,
        add_service,
        add_nanny_branch,
        make_empty_config,
        set_service_general_params,
        set_service_params,
        params,
        expected_response_json,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'existing-service')
    branch_id = await add_nanny_branch(
        service['id'], 'branch-1', 'stable', 'taxi_branch-1_stable',
    )

    cfg = make_empty_config()

    cfg.service_info.general.fill(
        {'service_type': 'backendpy3', 'description': 'some description'},
    )
    cfg.abc.stable.set('maintainers', ['kus', 'karachevda'])
    await set_service_general_params(service['id'], cfg)
    await set_service_params(service['id'], branch_id, cfg)

    await add_service('taxi', 'deleted-service', is_deleted=True)

    response = await web_app_client.get('/v1/services/', params=params)
    assert response.status == 200, await response.text()
    result = await response.json()
    assert result == load_json(expected_response_json)

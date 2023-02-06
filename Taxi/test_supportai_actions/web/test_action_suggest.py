async def test_suggest_action_id(web_app_client):
    project_id = 'echo'
    action_id = 'echo'
    wrong_action_id = 'not_echo'
    not_full_action_id = 'ec'
    version = '0'
    wrong_version = '2'

    response = await web_app_client.get(
        f'/v1/action/suggest?project_id={project_id}&search={wrong_action_id}',
    )

    response_json = await response.json()
    assert response_json['action_types'] == []

    response = await web_app_client.get(
        f'/v1/action/suggest?project_id={project_id}'
        f'&search={not_full_action_id}',
    )

    response_json = await response.json()
    assert response_json['action_types'] == [
        'echo',
        'ech',
        'get_objects_nearby',
    ]

    response = await web_app_client.get(
        f'/v1/action/suggest?project_id={project_id}&search={action_id}',
    )

    response_json = await response.json()
    assert response_json['action_types'] == ['echo']

    response = await web_app_client.get(
        f'/v1/action/suggest/versions?project_id={project_id}'
        f'&action_id={action_id}&search={wrong_version}',
    )

    response_json = await response.json()
    assert response_json['versions'] == []

    response = await web_app_client.get(
        f'/v1/action/suggest/versions?project_id={project_id}'
        f'&action_id={action_id}&search=',
    )

    response_json = await response.json()
    assert response_json['versions'] == ['0']

    response = await web_app_client.get(
        f'/v1/action/suggest/versions?project_id={project_id}'
        f'&action_id={action_id}&search={version}',
    )

    response_json = await response.json()
    assert response_json['versions'] == ['0']

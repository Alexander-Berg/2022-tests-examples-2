import pytest


@pytest.mark.parametrize('cube_name', ['AwacsGetNamespaceForService'])
async def test_post_awacs_cubes_handles(
        web_app_client,
        cube_name,
        load_json,
        login_mockserver,
        awacs_mockserver,
        nanny_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        abc_mockserver,
        patch,
):
    login_mockserver()
    awacs_mockserver()
    staff_mockserver()
    abc_mockserver(services=True)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    # pylint: disable=unused-variable
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert text == (
            'Namespace admin-data.taxi.yandex.net is created: '
            'https://nanny.yandex-team.ru/ui/#/awacs/namespaces/list/'
            'admin-data.taxi.yandex.net/show/'
        )

    service_id = await add_service('taxi', 'admin-data')
    await add_nanny_branch(
        service_id['id'],
        'stable',
        env='stable',
        direct_link='taxi_admin-data_stable',
    )

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']

async def test_exists(taxi_authproxy_manager, mockserver):
    @mockserver.json_handler('staff-production/v3/persons')
    async def _mock(request):
        assert request.query == {
            'login': 'segoon',
            '_fields': 'department_group',
        }
        url = 'yandex_distproducts_browserdev_mobile_taxi_9720_9558'
        return {
            'page': 1,
            'result': [
                {
                    'department_group': {
                        'name': 'Группа разработки общих компонент',
                        'responsibles': [],
                        'role_scope': None,
                        'department': {
                            'description': {
                                'en': '',
                                'ru': 'менеджер: karmanovats@',
                            },
                            'url': url,
                        },
                    },
                },
            ],
        }

    response = await taxi_authproxy_manager.post(
        '/v1/dev-teams-hint',
        json={'yandex_team_login': 'segoon'},
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json() == {'dev_team_name': 'common_components'}
    assert _mock.times_called == 1


async def test_missing(taxi_authproxy_manager, mockserver):
    @mockserver.json_handler('staff-production/v3/persons')
    async def _mock(request):
        assert request.query == {
            'login': 'segoon',
            '_fields': 'department_group',
        }
        return {'page': 1, 'result': []}

    response = await taxi_authproxy_manager.post(
        '/v1/dev-teams-hint',
        json={'yandex_team_login': 'segoon'},
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json() == {}
    assert _mock.times_called == 1


async def test_unknown_group(taxi_authproxy_manager, mockserver):
    @mockserver.json_handler('staff-production/v3/persons')
    async def _mock(request):
        assert request.query == {
            'login': 'segoon',
            '_fields': 'department_group',
        }
        return {
            'page': 1,
            'result': [
                {
                    'department_group': {
                        'name': 'Группа разработки общих компонент',
                        'responsibles': [],
                        'role_scope': None,
                        'department': {
                            'description': {
                                'en': '',
                                'ru': 'менеджер: karmanovats@',
                            },
                            'url': 'unknown_group_name',
                        },
                    },
                },
            ],
        }

    response = await taxi_authproxy_manager.post(
        '/v1/dev-teams-hint',
        json={'yandex_team_login': 'segoon'},
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json() == {}
    assert _mock.times_called == 1

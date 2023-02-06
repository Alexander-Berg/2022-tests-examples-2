# pylint: disable=redefined-outer-name,unused-variable
PARTNER_ID = 777
PLACE_ID = 109151


async def test_moderation_tasks_happy_path(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=200,
            json={'payload': {'deleted_tasks': [], 'not_deleted_tasks': []}},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 201


async def test_moderation_tasks_no_access(
        mock_place_access_400, taxi_eats_restapp_menu,
):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 403


async def test_moderation_tasks_v2_404(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        if request.json == {
                'context': '{"place_id":"109151","partner_id":"777"}',
                'task_id': '213125',
        }:
            return mockserver.make_response(status=404)
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=200,
            json={'payload': {'deleted_tasks': [], 'not_deleted_tasks': []}},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'task_id:213125, version:v2, not found',
    }


async def test_moderation_tasks_v2_400(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        if request.json == {
                'context': '{"place_id":"109151","partner_id":"777"}',
                'task_id': '213126',
        }:
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'error'},
            )
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=200,
            json={'payload': {'deleted_tasks': [], 'not_deleted_tasks': []}},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'task_id:213126, version:v2, bad request:error',
    }


async def test_moderation_tasks_v1_not_del(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'deleted_tasks': [],
                    'not_deleted_tasks': [213123],
                },
            },
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'task_id:213123, version:v1, not deleted',
    }


async def test_moderation_tasks_v1_400(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=400, json={'payload': {'error': 'error'}},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'task_ids:213123, 213124, version: v1, not deleted:error',
    }


async def test_moderation_tasks_all_err(
        mockserver, mock_place_access_200, taxi_eats_restapp_menu,
):
    @mockserver.json_handler('/eats-moderation/moderation/v1/task/remove')
    def mock_moderation(request):
        if request.json == {
                'context': '{"place_id":"109151","partner_id":"777"}',
                'task_id': '213125',
        }:
            return mockserver.make_response(status=404)
        if request.json == {
                'context': '{"place_id":"109151","partner_id":"777"}',
                'task_id': '213126',
        }:
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'error'},
            )

        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places/menu/moderation/remove',
    )
    def mock_core(request):
        return mockserver.make_response(
            status=400, json={'payload': {'error': 'error'}},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/moderation/tasks/delete?'
        'place_id=' + str(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'delete': [
                {'version': 'v1', 'id': '213123'},
                {'version': 'v1', 'id': '213124'},
                {'version': 'v2', 'id': '213125'},
                {'version': 'v2', 'id': '213126'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'task_id:213125, version:v2, not found; task_id:213126, ver'
            'sion:v2, bad request:error; task_ids:213123, 213124, versi'
            'on: v1, not deleted:error'
        ),
    }

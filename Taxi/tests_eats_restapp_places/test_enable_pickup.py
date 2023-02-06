async def test_set_pickup_status_empty(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        stq,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': []},
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 200
    assert response.json() == {'places': []}
    assert stq.eats_restapp_places_pickup.times_called == 0


async def test_set_pickup_status_happy_path(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        stq,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222, 333]},
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'places': [
            {
                'commission': {'percent': 15.2},
                'place_id': 111,
                'status': 'in_process',
            },
            {
                'commission': {'percent': 15.2},
                'place_id': 222,
                'status': 'in_process',
            },
            {
                'commission': {'percent': 15.2},
                'place_id': 333,
                'status': 'in_process',
            },
        ],
    }
    assert stq.eats_restapp_places_pickup.times_called == 1
    arg = stq.eats_restapp_places_pickup.next_call()
    assert arg['queue'] == 'eats_restapp_places_pickup'
    assert arg['args'] == []
    assert arg['kwargs']['places_ids'] == [111, 222, 333]
    assert arg['kwargs']['operation'] == 'enable'


async def test_set_pickup_status_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        stq,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222, 333]},
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 403
    assert stq.eats_restapp_places_pickup.times_called == 0


async def test_set_pickup_status_stq(stq_runner, mock_eats_core_pickup_enable):
    await stq_runner.eats_restapp_places_pickup.call(
        task_id='fake_task',
        kwargs={'places_ids': [111, 222, 333], 'operation': 'enable'},
    )


async def test_set_pickup_status_stq_400(
        stq_runner, mock_eats_core_pickup_enable_f,
):
    await stq_runner.eats_restapp_places_pickup.call(
        task_id='fake_task',
        kwargs={'places_ids': [111, 222, 333], 'operation': 'enable'},
        expect_fail=True,
    )


async def test_enable_pickup_status_400_by_role(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        stq,
        mock_restapp_authorizer_400,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222, 333]},
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Enable pickup operation is inaccessible for this role',
    }

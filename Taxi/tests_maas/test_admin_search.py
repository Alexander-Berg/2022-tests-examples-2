import pytest


@pytest.mark.pgsql('maas', files=['admin.sql'])
async def test_no_results(taxi_maas, mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _mock_user_api(request):
        assert request.json == {
            'phone': '+79998887766',
            'type': 'yandex',
            'primary_replica': False,
        }
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'no such phone'}, status=404,
        )

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'limit': 0, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': []}
    assert _mock_user_api.times_called == 0

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'maas_subscription_status': 'reserved', 'limit': 0, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': []}
    assert _mock_user_api.times_called == 0

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'user_maas_id': 'no_such_user', 'limit': 0, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': []}
    assert _mock_user_api.times_called == 0

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'user_phone': '+79998887766', 'limit': 0, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': []}
    assert _mock_user_api.times_called == 1


@pytest.mark.pgsql('maas', files=['admin.sql'])
async def test_simple(taxi_maas, mockserver, load_json):
    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _mock_user_api(request):
        if request.json['phone'] == '+79998887766':
            return load_json('user_api_response.json')
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'no such phone'}, status=404,
        )

    user_1_subs = load_json('user_1_subscriptions.json')
    user_2_subs = load_json('user_2_subscriptions.json')

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'user_phone': '+79998887766', 'limit': 10, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': user_1_subs}

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={
            'user_phone': '+79998887766',
            'maas_subscription_status': 'active',
            'limit': 10,
            'skip': 0,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'results': [user_1_subs[0]]}

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'user_maas_id': 'user_2', 'limit': 10, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': user_2_subs}

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={
            'user_maas_id': 'user_2',
            'maas_subscription_status': 'expired',
            'limit': 10,
            'skip': 0,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'results': [user_2_subs[1]]}

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscriptions/search',
        headers={},
        json={'maas_subscription_status': 'active', 'limit': 10, 'skip': 0},
    )
    assert response.status_code == 200
    assert response.json() == {'results': [user_1_subs[0], user_2_subs[0]]}

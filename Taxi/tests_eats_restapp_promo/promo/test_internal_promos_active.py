# pylint: disable=too-many-lines

import pytest


PROMOS = {
    307: {
        'id': 307,
        'name': 'Блюдо в подарок',
        'type': {
            'id': 25,
            'name': 'Блюдо в подарок',
            'picture': 'gift.icon',
            'detailed_picture': None,
        },
        'places': [
            {'id': 1, 'disabled_by_surge': False},
            {'id': 2, 'disabled_by_surge': False},
        ],
    },
    306: {
        'id': 306,
        'name': 'Скидка 20%',
        'type': {
            'id': 7,
            'name': 'Скидка на меню или некоторые позиции',
            'picture': 'discount.icon',
            'detailed_picture': None,
        },
        'places': [
            {'id': 1, 'disabled_by_surge': False},
            {'id': 2, 'disabled_by_surge': False},
        ],
    },
    305: {
        'id': 305,
        'name': 'Два по цене одного',
        'type': {
            'id': 2,
            'name': 'Два по цене одного',
            'picture': 'one_plus_one.icon',
            'detailed_picture': None,
        },
        'places': [
            {'id': 1, 'disabled_by_surge': False},
            {'id': 2, 'disabled_by_surge': False},
        ],
    },
    301: {
        'id': 301,
        'name': 'Блюдо в подарок',
        'type': {
            'id': 25,
            'name': 'Блюдо в подарок',
            'picture': 'gift.icon',
            'detailed_picture': None,
        },
        'places': [
            {'id': 1, 'disabled_by_surge': False},
            {'id': 2, 'disabled_by_surge': False},
        ],
    },
}


CORE_PROMOS = {
    200: {
        'id': 200,
        'name': 'Блюдо в подарок',
        'type': {
            'id': 25,
            'name': 'Блюдо в подарок',
            'picture': 'gift.icon',
            'detailed_picture': None,
        },
        'places': [
            {'id': 3, 'disabled_by_surge': False},
            {'id': 4, 'disabled_by_surge': True},
        ],
    },
}


def promos_response(*promo_ids):
    result = []
    for promo_id in promo_ids:
        if promo_id in PROMOS:
            result.append(PROMOS[promo_id])
        if promo_id in CORE_PROMOS:
            result.append(CORE_PROMOS[promo_id])
    return result


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_ignores_new_promos(
        taxi_eats_restapp_promo,
):
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos/active', json={'limit': 1},
    )

    assert response.status_code == 200
    response = response.json()
    assert sorted(
        response['promos'], key=lambda x: x['id'], reverse=True,
    ) == promos_response(307)
    assert response['cursor'] == 'service-307'


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_ignores_inactive(
        taxi_eats_restapp_promo,
):
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos/active', json={'limit': 4},
    )

    assert response.status_code == 200
    response = response.json()
    assert sorted(
        response['promos'], key=lambda x: x['id'], reverse=True,
    ) == promos_response(307, 306, 305, 301)
    assert response['cursor'] == 'service-301'


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_request_core(
        taxi_eats_restapp_promo, mockserver,
):
    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _mock_core(request):
        assert request.json['limit'] == 1
        response_body = {'promos': promos_response(200), 'cursor': '200'}
        return mockserver.make_response(status=200, json=response_body)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos/active', json={'limit': 5},
    )

    assert _mock_core.times_called == 1
    assert response.status_code == 200
    response = response.json()
    assert sorted(
        response['promos'], key=lambda x: x['id'], reverse=True,
    ) == promos_response(307, 306, 305, 301, 200)
    assert response['cursor'] == '200'


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_start_from_cursor(
        taxi_eats_restapp_promo,
):
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos/active',
        json={'limit': 1, 'cursor': 'service-306'},
    )

    assert response.status_code == 200
    response = response.json()
    assert sorted(
        response['promos'], key=lambda x: x['id'], reverse=True,
    ) == promos_response(305)
    assert response['cursor'] == 'service-305'


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_start_from_core_cursor(
        taxi_eats_restapp_promo, mockserver,
):
    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _mock_core(request):
        assert request.json['limit'] == 5
        assert request.json['cursor'] == '201'
        response_body = {'promos': promos_response(200), 'cursor': '200'}
        return mockserver.make_response(status=200, json=response_body)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promos/active',
        json={'limit': 5, 'cursor': '201'},
    )

    assert _mock_core.times_called == 1
    assert response.status_code == 200
    response = response.json()
    assert sorted(
        response['promos'], key=lambda x: x['id'], reverse=True,
    ) == promos_response(200)
    assert response['cursor'] == '200'


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_internal_promos_active_bulk(
        taxi_eats_restapp_promo, mockserver,
):
    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _mock_core(request):
        assert request.json['limit'] == 1
        response_body = {'promos': promos_response(200)}
        return mockserver.make_response(status=200, json=response_body)

    cursor = None
    promos = [307, 306, 305, 301, 200]
    promo_idx = 0
    while True:
        data = {'limit': 1}
        if cursor:
            data['cursor'] = cursor
        response = await taxi_eats_restapp_promo.post(
            '/internal/eats-restapp-promo/v1/promos/active', json=data,
        )

        assert _mock_core.times_called == int(promo_idx > 3)
        assert response.status_code == 200
        response = response.json()
        assert sorted(
            response['promos'], key=lambda x: x['id'], reverse=True,
        ) == promos_response(promos[promo_idx])
        if not response.get('cursor'):
            break
        assert response['cursor'] == f'service-{promos[promo_idx]}'
        cursor = response['cursor']
        promo_idx += 1

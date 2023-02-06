# pylint: disable = redefined-outer-name
import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
PLACE_ID2 = '109152'


@pytest.fixture()
def mock_moderation_count(mockserver):
    @mockserver.json_handler('/eats-moderation/moderation/v1/tasks/count')
    def _mock_func(request):
        req_json = request.json
        assert req_json == {
            'requests': [
                {
                    'context': [{'field': 'place_id', 'value': '109151'}],
                    'queue': ['restapp_moderation_menu'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
                {
                    'context': [{'field': 'place_id', 'value': '109151'}],
                    'queue': ['restapp_moderation_item'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
                {
                    'context': [{'field': 'place_id', 'value': '109151'}],
                    'queue': ['restapp_moderation_category'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
                {
                    'context': [{'field': 'place_id', 'value': '109152'}],
                    'queue': ['restapp_moderation_menu'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
                {
                    'context': [{'field': 'place_id', 'value': '109152'}],
                    'queue': ['restapp_moderation_item'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
                {
                    'context': [{'field': 'place_id', 'value': '109152'}],
                    'queue': ['restapp_moderation_category'],
                    'scope': ['eda'],
                    'statuses': ['rejected'],
                },
            ],
        }

        return {'counts': [1, 2, 3, 0, 0, 0]}

    return _mock_func


@pytest.fixture()
def mock_core_moderation_status(mockserver):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-moderation/moderation/status',
    )
    def _mock_func(request):
        assert request.query == {'place_id': '109151,109152'}

        return {
            'moderation_status': [
                {
                    'place_id': 109151,
                    'reject': {
                        'menu_category': 3,
                        'menu_item': 2,
                        'menu_item_photo': 1,
                        'total': 6,
                    },
                    'total': 6,
                },
                {
                    'place_id': 109152,
                    'reject': {
                        'menu_category': 3,
                        'menu_item': 2,
                        'menu_item_photo': 1,
                        'total': 6,
                    },
                    'total': 6,
                },
            ],
            'total': 12,
        }

    return _mock_func


async def test_moderation_status_get_no_access(
        taxi_eats_restapp_menu, mock_place_access_400,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/moderation/status',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert 'X-Polling-Period-Ms' not in response.headers

    assert mock_place_access_400.times_called == 1


async def test_moderation_status_get_basic(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mock_moderation_count,
        mock_core_moderation_status,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/moderation/status',
        params={'place_id': '109151,109152'},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'moderation_status': [
            {
                'place_id': 109152,
                'reject': {
                    'menu_category': 3,
                    'menu_item': 2,
                    'menu_item_photo': 1,
                    'total': 6,
                },
                'total': 6,
            },
            {
                'place_id': 109151,
                'reject': {
                    'menu_category': 6,
                    'menu_item': 4,
                    'menu_item_photo': 2,
                    'total': 12,
                },
                'total': 12,
            },
        ],
        'total': 18,
    }
    assert response.headers['X-Polling-Period-Ms'] == '60000'

    assert mock_place_access_200.times_called == 2

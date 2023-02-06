import pytest


PARTNER_ID = 1


PLACE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def mock_sender_success(mockserver, email, name):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/WC78FQ64-6IN/send',
    )
    def _mock_sender_success(req):
        assert req.json.get('to')[0].get('email') == email
        assert req.json.get('to')[0].get('name') == name
        return mockserver.make_response(
            status=200,
            json={
                'result': {
                    'status': 'OK',
                    'task_id': '2258a15b-6209-44f9-841b-53ac1f47fa52',
                    'message_id': (
                        '<20200507080804@api-10.production.ysendercloud>'
                    ),
                },
            },
        )

    return _mock_sender_success


@pytest.fixture(name='mock_configs')
def _mock_configs(load_json):
    return pytest.mark.config(
        EATS_RESTAPP_PLACES_RESTAURANT_DISABLE_LISTS=load_json(
            'disable_reasons_lists.json',
        ),
        EATS_RESTAPP_PLACES_RESTAURANT_DISABLE_DETAILS=load_json(
            'disable_reasons_details.json',
        ),
    )


@pytest.fixture(name='mock_sender_email_partners')
def _mock_sender_email_partners(mockserver):
    return mock_sender_success(
        mockserver, 'eda-partners@yandex-team.ru', 'Партнеры',
    )


@pytest.fixture(name='mock_sender_email_callcenter')
def _mock_sender_email_callcenter(mockserver):
    return mock_sender_success(
        mockserver, 'eda-content@yandex-team.ru', 'Колл Центр',
    )


@pytest.fixture(name='mock_sender_email_content')
def _mock_sender_email_content(mockserver):
    return mock_sender_success(
        mockserver, 'eda-content@yandex-team.ru', 'Контент',
    )


@pytest.fixture(name='mock_authorizer_places_enable')
def _mock_authorizer_places_enable(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_authorizer(request):
        assert request.json == {'partner_id': PARTNER_ID}
        return mockserver.make_response(
            status=200, json={'is_success': True, 'place_ids': PLACE_IDS},
        )


@pytest.fixture(name='mock_eats_core_enabled')
def _mock_eats_core_enabled(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/enable')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'enabled_places': request.json['place_ids'],
                    'errors': [],
                },
            },
        )


@pytest.fixture(name='mock_eats_core_places')
def _mock_eats_core_places(mockserver, load_json, request):
    places = load_json('places_info.json')

    def find_place(place_id):
        for item in places.get('places'):
            if item.get('id') == place_id:
                return item
        raise ValueError('Place id not found')

    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_core(request):
        try:
            return mockserver.make_response(
                status=200,
                json={
                    'payload': [
                        find_place(place_id)
                        for place_id in request.json['place_ids']
                    ],
                },
            )
        except ValueError as error:
            return mockserver.make_response(
                status=404, json={'code': '40', 'message': error.args[0]},
            )


async def test_enable_places_empty(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': []},
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 204


async def test_enable_places_already_enable(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [1, 2]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_unknown_reason_ignore(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [5]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_send_in_core(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
        mock_eats_core_enabled,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [3, 4]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_request_enable_send_partners(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
        mock_sender_email_partners,
        mock_configs,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [6, 7]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_request_enable_send_content(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
        mock_sender_email_content,
        mock_configs,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [8, 9]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_request_enable_send_callcenter(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
        mock_sender_email_callcenter,
        mock_configs,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [10]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_enable_places_request_enable_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
        mock_authorizer_places_enable,
        mock_eats_core_places,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [11, 12, 13]},
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 404


async def test_enable_places_request_enable_403(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer_403,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [11, 12, 13]},
        headers={'X-YaEda-PartnerId': str(123)},
    )

    assert response.status_code == 403


async def test_enable_places_request_enable_400(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer_400,
):
    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/enable',
        json={'place_ids': [11, 12, 13]},
        headers={'X-YaEda-PartnerId': str(123)},
    )

    assert response.status_code == 400

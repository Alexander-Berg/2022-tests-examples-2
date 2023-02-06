import pytest

from tests_eats_smart_prices import utils


AUTH_HEADER = {'X-YaEda-PartnerId': '123'}


def place_status(place_id, status='can_be_activated'):
    return {'history': [], 'place_id': place_id, 'status': status}


@pytest.fixture(name='partner_auth')
def mock_partner_authorizer(mockserver, partner_auth_resp_code: int):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_eats_restapp_authorizer(request):
        if partner_auth_resp_code != 200:
            return mockserver.make_response(
                json={
                    'permissions': ['permission'],
                    'place_ids': request.json['place_ids'],
                    'code': 'error_code',
                    'message': 'error_message',
                },
                status=partner_auth_resp_code,
            )

        return {}

    return _mock_eats_restapp_authorizer


@pytest.mark.parametrize(
    'partner_auth_resp_code, expected_code, expected_resp',
    [
        pytest.param(
            403,
            403,
            {'code': 'forbidden', 'message': 'Недостаточно прав'},
            id='forbidden',
        ),
        pytest.param(
            200,
            200,
            {'places': [place_status(1), place_status(2), place_status(3)]},
            id='auth_ok',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_partner_status_auth(
        taxi_eats_smart_prices, partner_auth, expected_code, expected_resp,
):
    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/status',
        json={'place_ids': [1, 2, 3]},
        headers=AUTH_HEADER,
    )

    assert resp.status_code == expected_code

    assert partner_auth.times_called == 1
    assert resp.json() == expected_resp


@pytest.mark.parametrize(
    'status_code, body, headers',
    [
        pytest.param(400, {}, AUTH_HEADER, id='wrong_body'),
        pytest.param(
            400,
            {'place_ids': [1, 2, 3]},
            {'wrong': 'header'},
            id='wrong_headers',
        ),
        pytest.param(
            500,
            {'place_ids': [1, 2, 3]},
            {'X-YaEda-PartnerId': 'str'},
            id='wrong_headers_2',
        ),
    ],
)
@pytest.mark.parametrize('partner_auth_resp_code', [200])
async def test_partner_status_bad_request(
        taxi_eats_smart_prices, partner_auth, status_code, body, headers,
):
    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/status',
        json=body,
        headers=headers,
    )

    assert resp.status_code == status_code
    assert partner_auth.times_called == 0


@pytest.mark.now('2022-03-31T19:00:00+03:00')
@pytest.mark.parametrize('partner_auth_resp_code', [200])
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    'id_disabled_smart_prices',
    [
        pytest.param(
            True,
            marks=utils.smart_prices_disabled_places(True),
            id='disabled_smart_price',
        ),
        pytest.param(
            False,
            marks=utils.smart_prices_disabled_places(False),
            id='available_smart_price',
        ),
    ],
)
async def test_partner_status_simple(
        taxi_eats_smart_prices,
        partner_auth,
        eats_smart_prices_cursor,
        id_disabled_smart_prices,
):
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='20',
        start_time='2022-03-30T00:00:00+03:00',
        end_time=None,
        deleted_at=None,
    )
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='40',
        start_time='2022-03-29T00:00:00+03:00',
        end_time='2022-03-30T00:00:00+03:00',
        deleted_at=None,
    )
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='30',
        start_time='2022-03-29T00:00:00+03:00',
        end_time=None,
        deleted_at='2022-03-28T00:00:00+03:00',
    )
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='2',
        partner_id='12',
        max_modification_percent='50',
        start_time='2022-04-01T00:00:00+03:00',
        end_time=None,
        deleted_at=None,
    )
    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/status',
        json={'place_ids': [1, 2, 3]},
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 200

    assert partner_auth.times_called == 1
    data = resp.json()
    assert len(data['places']) == 3
    assert data['places'][0] == {
        'place_id': 1,
        'status': 'active',
        'history': [
            {'max_percent': '20', 'starts': '2022-03-30T00:00:00+03:00'},
            {
                'max_percent': '40',
                'starts': '2022-03-29T00:00:00+03:00',
                'ends': '2022-03-30T00:00:00+03:00',
            },
        ],
        'current_value': '20',
    }
    assert data['places'][1] == {
        'place_id': 2,
        'status': 'active',
        'history': [
            {'max_percent': '50', 'starts': '2022-04-01T01:00:00+04:00'},
        ],
    }
    place_status_result = (
        'can_not_be_activated'
        if id_disabled_smart_prices
        else 'can_be_activated'
    )
    assert data['places'][2] == {
        'place_id': 3,
        'status': place_status_result,
        'history': [],
    }


@pytest.mark.parametrize(
    'partner_auth_resp_code, expected_code, expected_resp',
    [
        pytest.param(
            403,
            403,
            {'code': 'forbidden', 'message': 'Недостаточно прав'},
            id='forbidden',
        ),
        pytest.param(
            200,
            200,
            {'places': [place_status(1), place_status(2), place_status(3)]},
            id='auth_ok',
        ),
    ],
)
@pytest.mark.parametrize(
    'id_disabled_smart_prices',
    [
        pytest.param(
            False,
            marks=utils.smart_prices_disabled_places(False),
            id='available_smart_price',
        ),
        pytest.param(
            True,
            marks=utils.smart_prices_disabled_places(True),
            id='disabled_smart_price',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_partner_update_auth(
        taxi_eats_smart_prices,
        partner_auth,
        expected_code,
        expected_resp,
        id_disabled_smart_prices,
):
    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/update',
        json={
            'smart_prices_settings': [
                {'place_id': 1, 'enabled': False},
                {'place_id': 2, 'enabled': False},
                {'place_id': 3, 'enabled': False},
            ],
        },
        headers=AUTH_HEADER,
    )
    if id_disabled_smart_prices and expected_code == 200:
        expected_code = 400
        expected_resp = {
            'code': 'prices_turn_off_for_place',
            'message': 'Невозможно выполнить запрос, умные цены выключены',
        }

    assert resp.status_code == expected_code

    assert partner_auth.times_called == 1
    assert resp.json() == expected_resp


@pytest.mark.parametrize(
    'status_code, body, headers',
    [
        pytest.param(400, {}, AUTH_HEADER, id='wrong_body'),
        pytest.param(
            400,
            {'smart_prices_settings': [{'place_id': 1, 'enabled': False}]},
            {'wrong': 'header'},
            id='wrong_headers',
        ),
        pytest.param(
            500,
            {'smart_prices_settings': [{'place_id': 1, 'enabled': False}]},
            {'X-YaEda-PartnerId': 'str'},
            id='wrong_headers_2',
        ),
    ],
)
@pytest.mark.parametrize('partner_auth_resp_code', [200])
async def test_partner_update_bad_request(
        taxi_eats_smart_prices, partner_auth, status_code, body, headers,
):
    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/update',
        json=body,
        headers=headers,
    )

    assert resp.status_code == status_code
    assert partner_auth.times_called == 0


@pytest.mark.now('2022-03-31T19:00:00+03:00')
@pytest.mark.parametrize('partner_auth_resp_code', [200])
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_partner_update_simple(
        taxi_eats_smart_prices, partner_auth, eats_smart_prices_cursor,
):
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='20',
        start_time='2022-03-30T00:00:00+03:00',
        end_time=None,
        deleted_at=None,
    )  # active
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='40',
        start_time='2022-03-29T00:00:00+03:00',
        end_time='2022-03-30T00:00:00+03:00',
        deleted_at=None,
    )  # finished
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='30',
        start_time='2022-03-29T00:00:00+03:00',
        end_time=None,
        deleted_at='2022-03-28T00:00:00+03:00',
    )  # deleted
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='2',
        partner_id='12',
        max_modification_percent='50',
        start_time='2022-04-01T03:00:00+04:00',
        end_time=None,
        deleted_at=None,
    )  # future
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='3',
        partner_id='12',
        max_modification_percent='23',
        start_time='2022-03-30T00:00:00+03:00',
        end_time=None,
        deleted_at=None,
    )  # active
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='4',
        partner_id='12',
        max_modification_percent='23',
        start_time='2022-04-02T00:00:00+03:00',
        end_time=None,
        deleted_at=None,
    )  # future

    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='1',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-25T19:00:00+00:00',
    )  # will be changed

    resp = await taxi_eats_smart_prices.post(
        '/4.0/restapp-front/smart-prices/v1/update',
        json={
            'smart_prices_settings': [
                {'place_id': 1, 'enabled': True, 'max_percent': '33'},
                {'place_id': 2, 'enabled': True, 'max_percent': '44'},
                {'place_id': 3, 'enabled': False},
                {'place_id': 4, 'enabled': False},
            ],
        },
        headers=AUTH_HEADER,
    )

    assert resp.status_code == 200

    assert partner_auth.times_called == 1
    data = resp.json()
    assert len(data['places']) == 4
    assert data['places'][0] == {
        'place_id': 1,
        'status': 'active',
        'history': [
            {'max_percent': '33', 'starts': '2022-04-01T03:00:00+03:00'},
            {
                'max_percent': '20',
                'starts': '2022-03-30T00:00:00+03:00',
                'ends': '2022-04-01T03:00:00+03:00',
            },
            {
                'max_percent': '40',
                'starts': '2022-03-29T00:00:00+03:00',
                'ends': '2022-03-30T00:00:00+03:00',
            },
        ],
        'current_value': '20',
    }
    assert data['places'][1] == {
        'place_id': 2,
        'status': 'active',
        'history': [
            {'max_percent': '44', 'starts': '2022-04-01T03:00:00+04:00'},
        ],
    }
    assert data['places'][2] == {
        'place_id': 3,
        'status': 'can_be_activated',
        'history': [
            {
                'max_percent': '23',
                'starts': '2022-03-30T01:00:00+04:00',
                'ends': '2022-04-01T03:00:00+04:00',
            },
        ],
        'current_value': '23',
    }
    assert data['places'][3] == {
        'place_id': 4,
        'status': 'can_be_activated',
        'history': [],
    }

    eats_smart_prices_cursor.execute(
        'SELECT place_id, update_status, status_time '
        'FROM eats_smart_prices.place_recalculation '
        'ORDER BY place_id',
    )
    places = eats_smart_prices_cursor.fetchall()
    assert len(places) == 4

    # updated
    assert places[0]['place_id'] == '1'
    assert (
        places[0]['update_status']
        == utils.PlaceRecalcStatus.need_recalculation.name
    )
    assert str(places[0]['status_time']) == '2022-03-31 19:00:00+03:00'

    assert places[1]['place_id'] == '2'
    assert (
        places[1]['update_status']
        == utils.PlaceRecalcStatus.need_recalculation.name
    )
    assert str(places[1]['status_time']) == '2022-03-31 19:00:00+03:00'

    assert places[2]['place_id'] == '3'
    assert (
        places[2]['update_status']
        == utils.PlaceRecalcStatus.need_recalculation.name
    )
    assert str(places[2]['status_time']) == '2022-03-31 19:00:00+03:00'

    assert places[3]['place_id'] == '4'
    assert (
        places[3]['update_status']
        == utils.PlaceRecalcStatus.need_recalculation.name
    )
    assert str(places[3]['status_time']) == '2022-03-31 19:00:00+03:00'

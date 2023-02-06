import pytest


ORDER_NR = '123456-123456'
CLAIM_ID = 'some_claim_id'
CLAIM_ALIAS = 'some_claim_alias'

CARGO_POINTS_ETA_URL = '/cargo-claims/api/integration/v1/claims/points-eta'
CARGO_CLAIMS_INFO_URL = '/cargo-claims/api/integration/v2/claims/info'
EATS_ETA_PLACE_ETA_URL = '/eats-eta/v1/eta/order/courier-arrival-at'
EATS_ETA_EATER_ETA_URL = '/eats-eta/v1/eta/order/delivery-at'
TRACKING_URL = (
    '/eats-orders-tracking/internal/eats-orders-tracking'
    '/v1/get-claim-by-order-nr'
)

CARGO_POINTS_ETA_RESPONSE = {
    'id': CLAIM_ID,
    'route_points': [
        {
            'id': 1,
            'address': {
                'fullname': '3',
                'coordinates': [40.8, 50.4],
                'country': '3',
                'city': '3',
                'street': '3',
                'building': '3',
            },
            'type': 'source',
            'visit_order': 2,
            'visit_status': 'pending',
            'visited_at': {'expected': '2020-04-28T12:20:00.100000+03:00'},
        },
        {
            'id': 2,
            'address': {
                'fullname': '3',
                'coordinates': [40.8, 50.4],
                'country': '3',
                'city': '3',
                'street': '3',
                'building': '3',
            },
            'type': 'destination',
            'visit_order': 2,
            'visit_status': 'pending',
            # check for another timezone
            'visited_at': {'expected': '2020-04-28T10:35:00.100000+01:00'},
        },
    ],
}

CARGO_POINTS_ETA_ERROR_404 = {'code': 'db_error', 'message': 'DB error'}

CARGO_POINTS_ETA_ERROR_409 = {
    'code': 'no_performer_info',
    'message': 'Performer not found',
}

CLAIMS_INFO_RESPONSE = {
    'created_ts': '2020-04-28T12:35:00+03:00',
    'id': 'some_claim_id',
    'items': [
        {
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Title',
            'cost_value': '1.00',
            'cost_currency': 'RUB',
            'quantity': 1,
        },
    ],
    'revision': 1,
    'route_points': [
        {
            'address': {'fullname': 'Some name', 'coordinates': [50.0, 50.0]},
            'contact': {'phone': '+79099999998', 'name': 'Name'},
            'id': 1,
            'type': 'source',
            'visit_order': 1,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'address': {'fullname': 'Some name', 'coordinates': [50.0, 50.0]},
            'contact': {'phone': '+79099999998', 'name': 'Name'},
            'id': 2,
            'type': 'destination',
            'visit_order': 2,
            'visit_status': 'pending',
            'visited_at': {},
        },
    ],
    'status': 'pickuped',
    'updated_ts': '2020-04-28T12:35:00+03:00',
    'user_request_revision': '1',
    'version': 1,
    'performer_info': {
        'courier_name': 'Some name',
        'legal_name': 'Some name',
        'transport_type': 'car',
    },
}

CLAIMS_INFO_ERROR_403 = {'code': 'invalid_cursor', 'message': 'Invalid cursor'}

CLAIMS_INFO_ERROR_404 = {'code': 'not_found', 'message': 'Claim not found'}

EATS_ETA_PLACE_ETA_RESPONSE = {
    'expected_at': '2020-04-28T12:20:00.100000+03:00',
    'calculated_at': '2020-04-28T10:35:00.100000+01:00',
    'status': 'skipped',
}

EATS_ETA_PLACE_ETA_ERROR_404 = {
    'code': 'claim_not_found',
    'message': 'Claim is not found for order',
}

EATS_ETA_PLACE_ETA_ERROR_500 = {
    'code': 'server_error',
    'message': 'Internal server error',
}

EATS_ETA_EATER_ETA_RESPONSE = {
    'expected_at': '2020-04-28T10:35:00.100000+01:00',
    'calculated_at': '2020-04-28T10:35:00.100000+01:00',
    'status': 'skipped',
}

EATS_ETA_EATER_ETA_ERROR_404 = {
    'code': 'claim_not_found',
    'message': 'Claim is not found for order',
}

EATS_ETA_EATER_ETA_ERROR_500 = {
    'code': 'server_error',
    'message': 'Internal server error',
}

TRACKING_RESPONSE = {
    'order_nr': ORDER_NR,
    'claim_id': CLAIM_ID,
    'claim_alias': CLAIM_ALIAS,
}

TRACKING_ERROR_400 = {
    'code': 'NOT_FOUND_COURIER_DATA',
    'message': 'Courier data is not found',
}

EXPECTED_RESPONSE_RU = {
    'eater_text': 'Время до точки назначения "Клиент" - 26',
    'place_text': 'Время до точки назначения "Ресторан/Магазин" - 11',
    'courier_text': 'Тип курьера - Машина',
}

EXPECTED_RESPONSE_EN = {
    'eater_text': 'Estimated time to point "Client" - 26',
    'place_text': 'Estimated time to point "Restoraunt/Shop" - 11',
    'courier_text': 'Courier type - Car',
}

TRANSLATIONS = {
    'eater.text': {
        'ru': [
            'Время до точки назначения "Клиент" - %(eater_eta_minutes)s',
        ] * 4,
        'en': ['Estimated time to point "Client" - %(eater_eta_minutes)s'] * 4,
    },
    'place.text': {
        'ru': [
            'Время до точки назначения "Ресторан/Магазин" - '
            '%(place_eta_minutes)s',
        ] * 4,
        'en': [
            'Estimated time to point "Restoraunt/Shop" - '
            '%(place_eta_minutes)s',
        ] * 4,
    },
    'courier.text': {
        'ru': 'Тип курьера - %(courier_type)s',
        'en': 'Courier type - %(courier_type)s',
    },
    'courier.type.car': {'ru': 'Машина', 'en': 'Car'},
}


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    (
        'eats_eta_place_eta_response',
        'eats_eta_eater_eta_response',
        'cargo_points_eta_response',
        'expected_response',
    ),
    [
        pytest.param(
            EATS_ETA_PLACE_ETA_RESPONSE,
            EATS_ETA_EATER_ETA_RESPONSE,
            None,
            EXPECTED_RESPONSE_RU,
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=True,
            ),
        ),
        pytest.param(
            None,
            None,
            CARGO_POINTS_ETA_RESPONSE,
            EXPECTED_RESPONSE_RU,
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
            ),
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_eta_place_eta_response,
        eats_eta_eater_eta_response,
        cargo_points_eta_response,
        expected_response,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def _mock_cargo_points_eta(request):
        return mockserver.make_response(
            status=200, json=cargo_points_eta_response,
        )

    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(status=200, json=CLAIMS_INFO_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(EATS_ETA_PLACE_ETA_URL)
    def _mock_eats_eta_courier_arrival_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_PLACE_ETA_RESPONSE,
        )

    @mockserver.json_handler(EATS_ETA_EATER_ETA_URL)
    def _mock_eats_eta_delivery_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_EATER_ETA_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """points_eta_code,points_eta_response,claims_info_code,
    claims_info_response,expected_code""",
    [
        (404, CARGO_POINTS_ETA_ERROR_404, 404, CLAIMS_INFO_ERROR_404, 404),
        (409, CARGO_POINTS_ETA_ERROR_409, 403, CLAIMS_INFO_ERROR_403, 404),
        (500, None, 500, None, 404),
    ],
)
async def test_error_cargo(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        points_eta_code,
        points_eta_response,
        claims_info_code,
        claims_info_response,
        expected_code,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def _mock_cargo_points_eta(request):
        return mockserver.make_response(
            status=points_eta_code, json=points_eta_response,
        )

    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(
            status=claims_info_code, json=claims_info_response,
        )

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta', params={'order_nr': ORDER_NR},
    )

    assert response.status == expected_code


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=True,
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    (
        'eats_eta_place_eta_code',
        'eats_eta_place_eta_response',
        'eats_eta_eater_eta_code',
        'eats_eta_eater_eta_response',
        'claims_info_code',
        'claims_info_response',
        'expected_code',
    ),
    [
        (
            404,
            EATS_ETA_PLACE_ETA_ERROR_404,
            404,
            EATS_ETA_EATER_ETA_ERROR_404,
            404,
            CLAIMS_INFO_ERROR_404,
            404,
        ),
        (
            500,
            EATS_ETA_PLACE_ETA_ERROR_500,
            404,
            EATS_ETA_EATER_ETA_ERROR_404,
            403,
            CLAIMS_INFO_ERROR_403,
            404,
        ),
        (502, None, 502, EATS_ETA_EATER_ETA_ERROR_500, 500, None, 404),
    ],
)
async def test_error_eats_eta(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_eta_place_eta_code,
        eats_eta_place_eta_response,
        eats_eta_eater_eta_code,
        eats_eta_eater_eta_response,
        claims_info_code,
        claims_info_response,
        expected_code,
):
    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(
            status=claims_info_code, json=claims_info_response,
        )

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(EATS_ETA_PLACE_ETA_URL)
    def _mock_eats_eta_courier_arrival_at(request):
        return mockserver.make_response(
            status=eats_eta_place_eta_code, json=eats_eta_place_eta_response,
        )

    @mockserver.json_handler(EATS_ETA_EATER_ETA_URL)
    def _mock_eats_eta_delivery_at(request):
        return mockserver.make_response(
            status=eats_eta_eater_eta_code, json=eats_eta_eater_eta_response,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta', params={'order_nr': ORDER_NR},
    )

    assert response.status == expected_code


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=True,
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """language,expected_response""",
    [('ru', EXPECTED_RESPONSE_RU), ('en', EXPECTED_RESPONSE_EN)],
)
async def test_translations(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        language,
        expected_response,
):
    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(status=200, json=CLAIMS_INFO_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(EATS_ETA_PLACE_ETA_URL)
    def _mock_eats_eta_courier_arrival_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_PLACE_ETA_RESPONSE,
        )

    @mockserver.json_handler(EATS_ETA_EATER_ETA_URL)
    def _mock_eats_eta_delivery_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_EATER_ETA_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta',
        params={'order_nr': ORDER_NR},
        headers={'Accept-Language': language},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response


EXPECTED_DB_COURIER_META = {
    'claim_id': CLAIM_ID,
    'eater_eta': '2020-04-28T12:35:00.100000+03:00',
    'place_eta': '2020-04-28T12:20:00.100000+03:00',
    'courier_type': 'car',
}

EXPECTED_EXISTING_DB_COURIER_META = {
    'claim_id': CLAIM_ID,
    'eater_eta': '2020-04-28T12:25:00+03',
    'place_eta': '2020-04-28T12:15:00+03',
    'courier_type': 'car',
}

EXPECTED_RESPONSE_FROM_DB = {
    'eater_text': 'Время до точки назначения "Клиент" - 15',
    'place_text': 'Время до точки назначения "Ресторан/Магазин" - 5',
    'courier_text': 'Тип курьера - Машина',
}


async def get_support_meta(pgsql, order_nr):
    cursor = pgsql['eats_support_misc'].cursor()
    cursor.execute(
        f"""SELECT order_nr, courier_support_meta
            FROM eats_support_misc.support_meta
            WHERE order_nr = '{order_nr}';""",
    )
    res = cursor.fetchone()
    return res[0], res[1]


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_response,expected_db_courier_meta""",
    [
        (ORDER_NR, EXPECTED_RESPONSE_RU, EXPECTED_DB_COURIER_META),
        ('123456-123457', EXPECTED_RESPONSE_RU, EXPECTED_DB_COURIER_META),
        ('123456-123458', EXPECTED_RESPONSE_RU, EXPECTED_DB_COURIER_META),
        ('123456-123459', EXPECTED_RESPONSE_RU, EXPECTED_DB_COURIER_META),
        ('123456-123460', {}, {'claim_id': CLAIM_ID}),
        (
            '123456-123461',
            EXPECTED_RESPONSE_FROM_DB,
            EXPECTED_EXISTING_DB_COURIER_META,
        ),
        ('123456-123462', EXPECTED_RESPONSE_RU, EXPECTED_DB_COURIER_META),
    ],
)
async def test_update_db(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        pgsql,
        # ---- parameters ----
        order_nr,
        expected_response,
        expected_db_courier_meta,
):
    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(status=200, json=CLAIMS_INFO_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(EATS_ETA_PLACE_ETA_URL)
    def _mock_eats_eta_courier_arrival_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_PLACE_ETA_RESPONSE,
        )

    @mockserver.json_handler(EATS_ETA_EATER_ETA_URL)
    def _mock_eats_eta_delivery_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_EATER_ETA_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta', params={'order_nr': order_nr},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response

    db_support_meta = await get_support_meta(pgsql, order_nr)
    assert db_support_meta[0] == order_nr
    assert db_support_meta[1] == expected_db_courier_meta


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': 'some_corp_client_id1234567890123'},
    },
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """tracking_code,tracking_response,expected_code""",
    [(400, TRACKING_ERROR_400, 404), (500, None, 404)],
)
async def test_error_tracking(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        tracking_code,
        tracking_response,
        expected_code,
):
    @mockserver.json_handler(CARGO_CLAIMS_INFO_URL)
    def _mock_claims_info(request):
        return mockserver.make_response(status=200, json=CLAIMS_INFO_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(
            status=tracking_code, json=tracking_response,
        )

    @mockserver.json_handler(EATS_ETA_PLACE_ETA_URL)
    def _mock_eats_eta_courier_arrival_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_PLACE_ETA_RESPONSE,
        )

    @mockserver.json_handler(EATS_ETA_EATER_ETA_URL)
    def _mock_eats_eta_delivery_at(request):
        return mockserver.make_response(
            status=200, json=EATS_ETA_EATER_ETA_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-points-eta', params={'order_nr': ORDER_NR},
    )

    assert response.status == expected_code

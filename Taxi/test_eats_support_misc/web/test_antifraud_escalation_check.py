# pylint: disable=too-many-lines
import pytest

EATER_ID = '1234'
MAX_ATTEMPTS = 3

REFUND_SETTINGS = {
    'fresh_eater_registration_days': 30,
    'refund_limits': [
        {'currency': 'RUB', 'amount': '500'},
        {'currency': 'BYN', 'amount': '17'},
        {'currency': 'KZT', 'amount': '2805'},
    ],
    'complaint_limit': 3,
    'complaint_limit_days': 30,
    'huge_refund_limits': [
        {'currency': 'RUB', 'amount': '5000'},
        {'currency': 'BYN', 'amount': '170'},
        {'currency': 'KZT', 'amount': '25000'},
    ],
    'huge_refund_orders_number': 100,
    'one_region_orders_min': 5,
}

EATS_EATERS_URL = '/eats-eaters/v1/eaters/find-by-id'
CORE_COMPLAINT_URL = '/eats-core-complaint/find-by-eater-id'
ORDERSHISTORY_URL = '/eats-ordershistory/v2/get-orders'
CATALOG_URL = (
    '/eats-catalog-storage/internal'
    '/eats-catalog-storage/v1/places/retrieve-by-ids'
)
RT_XARON_URL = '/rt-xaron/lavka/support-abuse-scoring/user'


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
@pytest.mark.parametrize(
    """eater_created_at, complaints, refund_amount, check_result""",
    [
        ('2020-04-20T12:10:00+03:00', [], '499', 'not_need_escalation'),
        ('2020-04-20T12:10:00+03:00', [], '501', 'need_escalation'),
        (
            '2020-03-20T12:10:00+03:00',
            [
                {
                    'id': '1',
                    'order_nr': '123-123',
                    'situation_title': 'Отсутствует блюдо',
                    'created_at': '2020-02-28T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
                {
                    'id': '2',
                    'order_nr': '124-124',
                    'situation_title': 'Привезли весь заказ поврежденным',
                    'created_at': '2020-04-25T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
            ],
            '1000',
            'not_need_escalation',
        ),
        (
            '2020-03-20T12:10:00+03:00',
            [
                {
                    'id': '1',
                    'order_nr': '123-123',
                    'situation_title': 'Отсутствует блюдо',
                    'created_at': '2020-04-20T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
                {
                    'id': '2',
                    'order_nr': '124-124',
                    'situation_title': 'Привезли весь заказ поврежденным',
                    'created_at': '2020-03-20T12:10:00+03:00',
                    'compensations': [
                        {
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                        },
                    ],
                },
            ],
            '499',
            'not_need_escalation',
        ),
        (
            '2020-03-20T12:10:00+03:00',
            [
                {
                    'id': '1',
                    'order_nr': '123-123',
                    'situation_title': 'Отсутствует блюдо',
                    'created_at': '2020-04-20T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
                {
                    'id': '2',
                    'order_nr': '124-124',
                    'situation_title': 'Привезли весь заказ поврежденным',
                    'created_at': '2020-04-20T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
                {
                    'id': '3',
                    'order_nr': '125-125',
                    'situation_title': 'Отсутствует блюдо',
                    'created_at': '2020-04-20T12:10:00+03:00',
                    'compensations': [
                        {
                            'amount': '100',
                            'currency_code': 'RUB',
                            'type': 'refund',
                            'id': '1',
                            'created_at': '2020-03-20T12:10:00+03:00',
                        },
                    ],
                },
            ],
            '501',
            'need_escalation',
        ),
    ],
    ids=[
        'fresh_eater_with_small_refund',
        'fresh_eater_with_big_refund',
        'old_eater_with_few_complaints',
        'old_eater_with_small_refund',
        'old_eater_with_big_refund',
    ],
)
async def test_green_flow_normal_refund(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eater_created_at,
        complaints,
        refund_amount,
        check_result,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'eater': {
                    'id': EATER_ID,
                    'uuid': 'uuid1234',
                    'created_at': eater_created_at,
                    'updated_at': eater_created_at,
                },
            },
        )

    @mockserver.json_handler(CORE_COMPLAINT_URL)
    async def _core_complaint_handler(request):
        assert 'eater_id' in request.json
        return mockserver.make_response(
            status=200, json={'complaints': complaints},
        )

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': refund_amount,
            'situation_id': '123',
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == {'escalation_check_result': check_result}


@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1={
        'fresh_eater_registration_days': 30,
        'refund_limits': [{'currency': 'RUB', 'amount': '500'}],
        'complaint_limit': 3,
        'complaint_limit_days': 30,
    },
)
async def test_currency_not_found(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
):
    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'BYN',
            'amount': '1',
            'situation_id': '123',
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == {'escalation_check_result': 'not_enough_data'}


@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
async def test_eaters_not_found(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        return mockserver.make_response(
            status=404,
            json={
                'message': 'Eater with id 1234 not found in eaters',
                'code': 'eater_not_found',
            },
            headers={'X-YaTaxi-Error-Code': '404'},
        )

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': '501',
            'situation_id': '123',
        },
    )

    assert _eats_eaters_handler.times_called == 1
    assert response.status == 500


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
async def test_complaints_not_found(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'eater': {
                    'id': EATER_ID,
                    'uuid': 'uuid1234',
                    'created_at': '2020-03-20T12:10:00+03:00',
                    'updated_at': '2020-04-20T12:10:00+03:00',
                },
            },
        )

    @mockserver.json_handler(CORE_COMPLAINT_URL)
    async def _core_complaint_handler(request):
        assert 'eater_id' in request.json
        return mockserver.make_response(
            status=400,
            json={
                'message': 'Eater with id 1234 not found in Core',
                'code': 'eater_complaint_not_found',
            },
            headers={'X-YaTaxi-Error-Code': '404'},
        )

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': '501',
            'situation_id': '123',
        },
    )

    assert _eats_eaters_handler.times_called == 1
    assert _core_complaint_handler.times_called == 1
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'eater_complaint_not_found',
        'message': 'Eater with id 1234 not found in Core',
    }


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
@pytest.mark.parametrize(
    """ordershistory_response, catalog_response, rt_xaron_response,
    complaints_response, refund_amount""",
    [
        pytest.param({'orders': []}, None, None, None, '5000', id='no_orders'),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 127,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            {'places': [], 'not_found_place_ids': []},
            None,
            None,
            '5000',
            id='not_enough_regions',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            None,
            {'result': [{'name': 'eats_red', 'value': True}]},
            None,
            '5000',
            id='have_enough_places_orders_red_eater',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 124,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 125,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 126,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 127,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            {
                'places': [
                    {
                        'id': 123,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 124,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 125,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 126,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 127,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                ],
                'not_found_place_ids': [],
            },
            {'result': [{'name': 'eats_red', 'value': True}]},
            None,
            '5000',
            id='have_enough_regions_orders_red_eater',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 124,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 125,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 126,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 127,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            {
                'places': [
                    {
                        'id': 123,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 124,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 125,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 126,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 63,
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                    {
                        'id': 127,
                        'revision_id': 15,
                        'updated_at': '2020-01-14T12:00:00+03:00',
                        'region': {
                            'id': 67,  # not 63
                            'geobase_ids': [12412],
                            'time_zone': 'Europe/Saratov',
                        },
                    },
                ],
                'not_found_place_ids': [],
            },
            None,
            None,
            '5000',
            id='have_not_enough_regions_orders',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            None,
            {'result': [{'name': 'eats_green', 'value': True}]},
            None,
            '5000',
            id='green_eater_only_small_cost_orders',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '5000',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
            None,
            {'result': [{'name': 'eats_green', 'value': True}]},
            {
                'complaints': [
                    {
                        'id': '1',
                        'order_nr': '123-123',
                        'situation_title': 'Отсутствует блюдо',
                        'created_at': '2020-02-28T12:10:00+03:00',
                        'compensations': [
                            {
                                'amount': '100',
                                'currency_code': 'RUB',
                                'type': 'refund',
                                'id': '1',
                                'created_at': '2020-03-20T12:10:00+03:00',
                            },
                        ],
                    },
                ],
            },
            '5000',
            id='big_cost_order_with_complaint',
        ),
    ],
)
async def test_need_escalation_huge_refund(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        ordershistory_response,
        catalog_response,
        rt_xaron_response,
        complaints_response,
        refund_amount,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        eaters_response = {
            'eater': {
                'id': EATER_ID,
                'uuid': 'uuid1234',
                'created_at': '2020-04-20T12:10:00+03:00',
                'updated_at': '2020-04-20T12:10:00+03:00',
                'personal_phone_id': 'phone_id_12345',
            },
        }
        return mockserver.make_response(status=200, json=eaters_response)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    async def _ordershistory_handler(request):
        assert str(request.json['eats_user_id']) == EATER_ID
        assert request.json['orders'] == 100
        return mockserver.make_response(
            status=200, json=ordershistory_response,
        )

    @mockserver.json_handler(CATALOG_URL)
    async def _catalog_handler(request):
        assert request.json['projection'] == ['region']
        assert 'place_ids' in request.json
        print(request.json['place_ids'])
        return mockserver.make_response(status=200, json=catalog_response)

    @mockserver.json_handler(RT_XARON_URL)
    async def _rt_xaron_handler(request):
        assert request.json == {'user_personal_phone_id': 'phone_id_12345'}
        return mockserver.make_response(status=200, json=rt_xaron_response)

    @mockserver.json_handler(CORE_COMPLAINT_URL)
    async def _core_complaint_handler(request):
        assert 'eater_id' in request.json
        return mockserver.make_response(status=200, json=complaints_response)

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': refund_amount,
            'situation_id': '123',
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == {'escalation_check_result': 'need_escalation'}


@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
async def test_exceptional_eater(
        # ---- fixtures ----
        mockserver,
        testpoint,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        eaters_response = {
            'eater': {
                'id': EATER_ID,
                'uuid': 'uuid1234',
                'created_at': '2020-04-20T12:10:00+03:00',
                'updated_at': '2020-04-20T12:10:00+03:00',
                'personal_phone_id': 'phone_id_12345',
            },
        }
        return mockserver.make_response(status=200, json=eaters_response)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    async def _ordershistory_handler(request):
        assert str(request.json['eats_user_id']) == EATER_ID
        assert request.json['orders'] == 100
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '5000',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
        )

    @mockserver.json_handler(RT_XARON_URL)
    async def _rt_xaron_handler(request):
        assert request.json == {'user_personal_phone_id': 'phone_id_12345'}
        return mockserver.make_response(
            status=200,
            json={'result': [{'name': 'eats_green', 'value': True}]},
        )

    @mockserver.json_handler(CORE_COMPLAINT_URL)
    async def _core_complaint_handler(request):
        assert 'eater_id' in request.json
        return mockserver.make_response(
            status=200,
            json={
                'complaints': [
                    {
                        'id': '1',
                        'order_nr': '124-124',
                        'situation_title': 'Отсутствует блюдо',
                        'created_at': '2020-02-28T12:10:00+03:00',
                        'compensations': [
                            {
                                'amount': '100',
                                'currency_code': 'RUB',
                                'type': 'refund',
                                'id': '1',
                                'created_at': '2020-03-20T12:10:00+03:00',
                            },
                        ],
                    },
                ],
            },
        )

    @testpoint('exceptional_eater_testpoint')
    def exceptional_eater_point(data):
        pass

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': '5000',
            'situation_id': '123',
        },
    )

    # means that was one check
    assert exceptional_eater_point.times_called == 1
    assert response.status == 200
    data = await response.json()
    assert data == {'escalation_check_result': 'not_need_escalation'}


@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
async def test_ordershistory_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        eaters_response = {
            'eater': {
                'id': EATER_ID,
                'uuid': 'uuid1234',
                'created_at': '2020-04-20T12:10:00+03:00',
                'updated_at': '2020-04-20T12:10:00+03:00',
                'personal_phone_id': 'phone_id_12345',
            },
        }
        return mockserver.make_response(status=200, json=eaters_response)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    async def _ordershistory_handler(request):
        assert str(request.json['eats_user_id']) == EATER_ID
        assert request.json['orders'] == 100
        return mockserver.make_response(
            status=400,
            json={
                'code': 'ordershistory_bad_request',
                'message': 'Bad request to eats-ordershistory',
            },
        )

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': '5000',
            'situation_id': '123',
        },
    )

    assert _eats_eaters_handler.times_called == 1
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'ordershistory_bad_request',
        'message': 'Bad request to eats-ordershistory',
    }


@pytest.mark.config(
    EATS_SUPPORT_MISC_ANTIFRAUD_ESCALATION_CHECK_SETTINGS_1=REFUND_SETTINGS,
)
async def test_rt_complaints_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_EATERS_URL)
    async def _eats_eaters_handler(request):
        eaters_response = {
            'eater': {
                'id': EATER_ID,
                'uuid': 'uuid1234',
                'created_at': '2020-04-20T12:10:00+03:00',
                'updated_at': '2020-04-20T12:10:00+03:00',
                'personal_phone_id': 'phone_id_12345',
            },
        }
        return mockserver.make_response(status=200, json=eaters_response)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    async def _ordershistory_handler(request):
        assert str(request.json['eats_user_id']) == EATER_ID
        assert request.json['orders'] == 100
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'order_id': '123-123',
                        'place_id': 123,
                        'total_amount': '5000',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '124-124',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '125-125',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '126-126',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        'total_amount': '123',
                        'status': 'finished',
                        'created_at': '2020-04-20T12:10:00+03:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'is_asap': True,
                        'currency': 'RUB',
                    },
                ],
            },
        )

    @mockserver.json_handler(RT_XARON_URL)
    async def _rt_xaron_handler(request):
        assert request.json == {'user_personal_phone_id': 'phone_id_12345'}
        return mockserver.make_response(
            status=200,
            json={'result': [{'name': 'eats_green', 'value': True}]},
        )

    @mockserver.json_handler(CORE_COMPLAINT_URL)
    async def _core_complaint_handler(request):
        assert 'eater_id' in request.json
        return mockserver.make_response(
            status=400,
            json={'code': 'eater_not_found', 'message': 'eater not found'},
            headers={'X-YaTaxi-Error-Code': '400'},
        )

    response = await taxi_eats_support_misc_web.post(
        '/v1/antifraud-escalation-check',
        json={
            'eater_id': EATER_ID,
            'currency': 'RUB',
            'amount': '5000',
            'situation_id': '123',
        },
    )

    assert _eats_eaters_handler.times_called == 1
    assert _ordershistory_handler.times_called == 1
    assert _rt_xaron_handler.times_called == 1
    assert _core_complaint_handler.times_called == 1
    assert response.status == 400
    data = await response.json()
    assert data == {'code': 'eater_not_found', 'message': 'eater not found'}

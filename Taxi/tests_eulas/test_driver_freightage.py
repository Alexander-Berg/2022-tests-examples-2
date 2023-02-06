import datetime

import pytest

from tests_eulas.mocks import order_core
from tests_eulas.mocks import parks_replica
from tests_eulas.mocks import personal

OrderProcGetFieldsContext = order_core.OrderProcGetFieldsContext
ParksReplicaRetrieveContext = parks_replica.ParksReplicaRetrieveContext
PersonalPhoneRetrieveContext = personal.PersonalPhoneRetrieveContext

URLS = [
    'driver/v1/eulas/v1/freightage',
    'internal/driver/v1/eulas/v1/freightage',
]
ORDER_CORE_FIELDS = [
    'candidates.car_number',
    'candidates.tags',
    'candidates.tariff_class',
    'candidates.tariff_currency',
    'order.created',
    'order.current_prices.current_cost.driver.total',
    'order.current_prices.kind',
    'order.current_prices.user_ride_display_price',
    'order.fixed_price.driver_price',
    'order.nz',
    'order.performer.uuid',
    'order.performer.db_id',
    'order.personal_phone_id',
    'order.request.destinations.geopoint',
    'order.request.destinations.fullname',
    'order.request.destinations.oid',
    'order.request.destinations.type',
    'order.request.destinations.uris',
    'order.request.source.geopoint',
    'order.request.source.fullname',
    'order.request.source.oid',
    'order.request.source.type',
    'order.request.source.uris',
    'order.user_id',
    'order.user_locale',
    'performer.candidate_index',
    'performer.park_id',
]
ORDER_CORE_OPTIONAL_FIELDS = {
    'candidates.tags',
    'order.current_prices.current_cost.driver.total',
    'order.fixed_price.driver_price',
    'order.request.destinations.oid',
    'order.request.destinations.type',
    'order.request.destinations.uris',
    'order.request.source.oid',
    'order.request.source.type',
    'order.request.source.uris',
}
ORDER_CORE_MANDATORY_FIELDS = [
    field
    for field in ORDER_CORE_FIELDS
    if field not in ORDER_CORE_OPTIONAL_FIELDS
]
PARKS_FIELDS = ['data.inn', 'data.long_name']
FREIGHTAGE_DRIVER_TAGS = ['show_freightage']
DEFAULT_COST = 'From 789 руб.'


def make_order():
    return {
        '_id': 'test_order_id',
        'candidates': [
            {
                'car_number': 'f000ff',
                'tariff_class': 'ultimate',
                'tariff_currency': 'RUB',
            },
        ],
        'order': {
            'created': datetime.datetime(2021, 1, 1),
            'current_prices': {
                'current_cost': {'driver': {'total': 123}},
                'kind': 'fixed',
                'user_ride_display_price': 654,
            },
            'fixed_price': {'driver_price': 789},
            'nz': 'test_zone',
            'performer': {'uuid': 'performer_uuid', 'db_id': 'performer_dbid'},
            'personal_phone_id': 'test_personal_phone_id',
            'request': {
                'destinations': [
                    {
                        'fullname': (
                            'Россия, Москва, Есенинский бульвар, 3, подъезд 1'
                        ),
                        'geopoint': [37.565306, 55.745537],
                        'uris': [
                            'ymapsbm1://geo?'
                            'll=37.555%2C55.750&spn=0.001%2C0.001',
                        ],
                    },
                    {
                        'fullname': (
                            'Россия, Москва, ТРЦ Европейский, Выход №1'
                        ),
                        'geopoint': [37.56530594673405, 55.74553754198694],
                        'uris': [
                            'ymapsbm1://geo?'
                            'll=37.565%2C55.750&spn=0.001%2C0.001',
                        ],
                    },
                ],
                'source': {
                    'fullname': (
                        'Россия, Москва, 1-й Красногвардейский проезд, 21с1'
                    ),
                    'geopoint': [37.5334785, 55.75000699999999],
                    'type': 'address',
                    'uris': [
                        'ymapsbm1://geo?ll=37.534%2C55.750&spn=0.001%2C0.001',
                    ],
                },
            },
            'user_id': 'test_user_id',
            'user_locale': 'ru',
        },
        'performer': {'candidate_index': 0, 'park_id': 'test_park_id'},
    }


def make_get_order_fields_call():
    call = OrderProcGetFieldsContext.Call()
    call.expected.order_id = 'test_order_id'
    call.expected.fields = ORDER_CORE_FIELDS
    call.response.order = make_order()
    return call


def make_retrieve_park_call():
    call = ParksReplicaRetrieveContext.Call()
    call.expected.park_id = 'test_park_id'
    call.expected.fields = PARKS_FIELDS
    call.response.park_data = {
        'inn': 'test_inn',
        'long_name': 'Park long legal name',
    }
    return call


def make_retrieve_phone_call():
    call = PersonalPhoneRetrieveContext.Call()
    call.expected.personal_phone_id = 'test_personal_phone_id'
    call.response.phone = 'test_phone_value'
    return call


class HandlerContext:
    get_order_fields: OrderProcGetFieldsContext
    retrieve_park: ParksReplicaRetrieveContext
    retrieve_phone: PersonalPhoneRetrieveContext


@pytest.fixture(name='freightage_handler_context')
def _freightage_handler_context(
        mock_order_core_get_fields: OrderProcGetFieldsContext,
        mock_parks_replica_retrieve: ParksReplicaRetrieveContext,
        mock_personal_phones_retrieve: PersonalPhoneRetrieveContext,
):
    context = HandlerContext()
    context.get_order_fields = mock_order_core_get_fields
    context.retrieve_park = mock_parks_replica_retrieve
    context.retrieve_phone = mock_personal_phones_retrieve

    context.get_order_fields.call = make_get_order_fields_call()
    context.retrieve_park.call = make_retrieve_park_call()
    context.retrieve_phone.call = make_retrieve_phone_call()
    return context


def get_items(cost=DEFAULT_COST):
    return [
        {
            'id': 'freightage_contract_freighter',
            'reverse': True,
            'subtitle': 'Park long legal name TIN: test_inn',
            'title': 'Freighter',
            'type': 'default',
        },
        {
            'checked': True,
            'enabled': False,
            'id': 'freightage_contract_freighter_signature',
            'title': 'Freighter signature',
            'type': 'default_check',
        },
        {
            'id': 'freightage_contract_charterer',
            'reverse': True,
            'subtitle': 'test_user_id test**********ue',
            'title': 'Charterer',
            'type': 'default',
        },
        {
            'checked': True,
            'enabled': False,
            'id': 'freightage_contract_charterer_signature',
            'title': 'Charterer signature',
            'type': 'default_check',
        },
        {
            'id': 'freightage_contract_plates',
            'reverse': True,
            'subtitle': 'M1 f000ff',
            'title': 'Car type and number',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_source_address',
            'reverse': True,
            'subtitle': 'Россия, Москва, 1-й Красногвардейский проезд, 21с1',
            'title': 'Source address',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_route',
            'reverse': True,
            'subtitle': (
                'Россия, Москва, 1-й Красногвардейский проезд, 21с1; '
                'Россия, Москва, Есенинский бульвар, 3, подъезд 1; '
                'Россия, Москва, ТРЦ Европейский, Выход №1'
            ),
            'title': 'Route',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_passenger_names',
            'reverse': True,
            'subtitle': 'Unknown',
            'title': 'Passengers list',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_date',
            'reverse': True,
            'subtitle': '01.01.2021',
            'title': 'Date',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_cost',
            'reverse': True,
            'subtitle': cost,
            'title': 'Cost',
            'type': 'default',
        },
        {
            'id': 'freightage_contract_passenger_access',
            'reverse': True,
            'subtitle': 'Via code',
            'title': 'Passenger access',
            'type': 'default',
        },
    ]


DEFAULT_REQUEST = {'order_id': 'test_order_id'}
DEFAULT_HEADERS = {
    'X-YaTaxi-Park-Id': 'performer_dbid',
    'X-YaTaxi-Driver-Profile-Id': 'performer_uuid',
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '10.08 (2345)',
}


def make_headers(url):
    return None if 'internal' in url else DEFAULT_HEADERS


@pytest.mark.parametrize('url', URLS)
async def test_ok(taxi_eulas, freightage_handler_context: HandlerContext, url):
    ctx = freightage_handler_context
    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 200
    assert response.json() == {'items': get_items()}

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 1
    assert ctx.retrieve_phone.times_called == 1


@pytest.mark.parametrize('url', URLS)
@pytest.mark.parametrize('missing_field', ORDER_CORE_MANDATORY_FIELDS)
async def test_order_core_mandatory_fields_missing(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        url,
        missing_field,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.delete_order_field(missing_field)

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'order_proc_field_missing'

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


@pytest.mark.parametrize('url', URLS)
async def test_order_core_fixed_price_missing(
        taxi_eulas, freightage_handler_context: HandlerContext, url,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.delete_order_field('order.fixed_price')

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 200
    assert response.json() == {'items': get_items(cost='')}

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 1
    assert ctx.retrieve_phone.times_called == 1


@pytest.mark.parametrize('url', URLS)
async def test_class_not_found(
        taxi_eulas, freightage_handler_context: HandlerContext, url,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('no_category_zone')

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 500

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


@pytest.mark.parametrize('url', URLS)
async def test_charter_not_required(
        taxi_eulas, freightage_handler_context: HandlerContext, url,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('contract_not_required_zone')

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


@pytest.mark.parametrize('url', URLS)
@pytest.mark.parametrize(
    'park_data',
    [
        pytest.param({}, id='no data'),
        pytest.param({'long_name': 'test_long_name'}, id='no inn'),
        pytest.param({'inn': 'test_inn'}, id='no long_name'),
    ],
)
async def test_park_missing_data(
        taxi_eulas, freightage_handler_context: HandlerContext, url, park_data,
):
    ctx = freightage_handler_context
    ctx.retrieve_park.call.response.park_data = park_data

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 1
    assert ctx.retrieve_phone.times_called == 1


@pytest.mark.parametrize('url', URLS)
@pytest.mark.parametrize(
    'failing_mock_name', ['retrieve_park', 'retrieve_phone'],
)
async def test_extra_data_errors(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        url,
        failing_mock_name,
):
    ctx = freightage_handler_context
    failing_mock = getattr(ctx, failing_mock_name)
    failing_mock.call.response.error_code = 500

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=make_headers(url),
    )

    assert response.status_code == 500

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called > 0
    assert ctx.retrieve_phone.times_called > 0


@pytest.mark.parametrize(
    'headers_override',
    [
        pytest.param(
            {'X-YaTaxi-Driver-Profile-Id': ''}, id='empty driver_profile_id',
        ),
        pytest.param({'X-YaTaxi-Park-id': ''}, id='empty park_id'),
        pytest.param(
            {'X-YaTaxi-Driver-Profile-Id': 'unauthorized'},
            id='unauthorized driver_profile_id',
        ),
        pytest.param(
            {'X-YaTaxi-Park-id': 'unauthorized'}, id='unauthorized park_id',
        ),
    ],
)
async def test_unauthorized(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        headers_override,
):
    ctx = freightage_handler_context

    headers = {**DEFAULT_HEADERS, **headers_override}
    response = await taxi_eulas.post(
        'driver/v1/eulas/v1/freightage', json=DEFAULT_REQUEST, headers=headers,
    )
    expected_status_code = (
        401 if headers.get('X-YaTaxi-Driver-Profile-Id') == '' else 403
    )

    assert response.status_code == expected_status_code
    assert ctx.get_order_fields.times_called == int(
        expected_status_code == 403,
    )
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


@pytest.mark.config(EULAS_FREIGHTAGE_DRIVER_TAGS=FREIGHTAGE_DRIVER_TAGS)
@pytest.mark.parametrize('url', URLS)
@pytest.mark.parametrize(
    'tags, is_ok',
    [
        pytest.param(
            FREIGHTAGE_DRIVER_TAGS, True, id='driver tags match config',
        ),
        pytest.param(
            ['another_tag'], False, id='driver tags do not match config',
        ),
    ],
)
async def test_contract_by_driver_tag(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        url,
        tags,
        is_ok,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('contract_not_required_zone')
    ctx.get_order_fields.call.response.set_candidate_tags(tags)

    response = await taxi_eulas.post(
        url, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == ({'items': get_items()} if is_ok else {})

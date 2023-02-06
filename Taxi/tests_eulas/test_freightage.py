import datetime

import pytest

from tests_eulas.mocks import order_core
from tests_eulas.mocks import parks_replica
from tests_eulas.mocks import personal

OrderProcGetFieldsContext = order_core.OrderProcGetFieldsContext
ParksReplicaRetrieveContext = parks_replica.ParksReplicaRetrieveContext
PersonalPhoneRetrieveContext = personal.PersonalPhoneRetrieveContext

URL = 'internal/eulas/v1/freightage'
ORDER_CORE_FIELDS = [
    'candidates.car_number',
    'candidates.tags',
    'candidates.tariff_class',
    'candidates.tariff_currency',
    'order.created',
    'order.current_prices.kind',
    'order.current_prices.user_ride_display_price',
    'order.application',
    'order.nz',
    'order.personal_phone_id',
    'order.request.destinations.fullname',
    'order.request.source.fullname',
    'order.user_id',
    'order.user_locale',
    'performer.candidate_index',
    'performer.park_id',
]
ORDER_CORE_OPTIONAL_FIELDS = ['candidates.tags', 'order.application']
ORDER_CORE_MANDATORY_FIELDS = [
    field
    for field in ORDER_CORE_FIELDS
    if field not in ORDER_CORE_OPTIONAL_FIELDS
]
PARKS_FIELDS = ['data.inn', 'data.long_name']
FREIGHTAGE_DRIVER_TAGS = ['show_freightage']

CACHE_CONTROL = 'Cache-Control'


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
                'kind': 'fixed',
                'user_ride_display_price': 654,
            },
            'nz': 'test_zone',
            'personal_phone_id': 'test_personal_phone_id',
            'request': {
                'destinations': [
                    {'fullname': 'Test destination address 1'},
                    {'fullname': 'Test destination address 2'},
                ],
                'source': {'fullname': 'Test source address'},
            },
            'application': 'iphone',
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


def get_ride_info():
    return {
        'title': 'Ride info title',
        'description': 'Ride info description',
        'image_tag': '7_g',
    }


def get_contract():
    return {
        'title': 'Freightage contract for order',
        'contract_data': [
            {
                'item_type': 'string',
                'name': 'Title',
                'value': 'Freightage contract',
            },
            {
                'item_type': 'string',
                'name': 'Freighter',
                'value': 'Park long legal name TIN: test_inn',
            },
            {'item_type': 'check', 'name': 'Freighter signature'},
            {
                'item_type': 'string',
                'name': 'Charterer',
                'value': 'test_user_id test**********ue',
            },
            {'item_type': 'check', 'name': 'Charterer signature'},
            {
                'item_type': 'string',
                'name': 'Car type and number',
                'value': 'M1 f000ff',
            },
            {
                'item_type': 'string',
                'name': 'Source address',
                'value': 'Test source address',
            },
            {
                'item_type': 'string',
                'name': 'Route',
                'value': (
                    'Test source address; Test destination address 1; '
                    'Test destination address 2'
                ),
            },
            {
                'item_type': 'string',
                'name': 'Passengers list',
                'value': 'Unknown',
            },
            {'item_type': 'string', 'name': 'Date', 'value': '01.01.2021'},
            {
                'item_type': 'cost_string',
                'name': 'Cost',
                'value': '654\u2006$SIGN$$CURRENCY$',
            },
            {
                'item_type': 'string',
                'name': 'Passenger access',
                'value': 'Via code',
            },
        ],
    }


DEFAULT_REQUEST = {'order_id': 'test_order_id', 'format_currency': True}


@pytest.mark.parametrize('search_archive', [True, False])
@pytest.mark.experiments3(filename='exp3_freightage_ride_additional_info.json')
async def test_ok(
        taxi_eulas, search_archive, freightage_handler_context: HandlerContext,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.expected.search_archive = search_archive
    request = {**DEFAULT_REQUEST, 'search_archive': search_archive}
    response = await taxi_eulas.post(URL, json=request)

    assert response.status_code == 200
    assert response.json() == {
        'ride_info': get_ride_info(),
        'contract': get_contract(),
    }
    assert response.headers[CACHE_CONTROL] == 'max-age=300'

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 1
    assert ctx.retrieve_phone.times_called == 1


@pytest.mark.parametrize('missing_field', ORDER_CORE_MANDATORY_FIELDS)
async def test_order_core_fields_missing(
        taxi_eulas, freightage_handler_context: HandlerContext, missing_field,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.delete_order_field(missing_field)

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 400
    assert response.json()['code'] == 'order_proc_field_missing'

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


async def test_class_not_found(
        taxi_eulas, freightage_handler_context: HandlerContext,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('no_category_zone')

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 500

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


async def test_charter_not_required(
        taxi_eulas, freightage_handler_context: HandlerContext,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('contract_not_required_zone')

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 200
    assert response.json() == {}
    assert response.headers[CACHE_CONTROL] == 'max-age=300'

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 0
    assert ctx.retrieve_phone.times_called == 0


@pytest.mark.parametrize(
    'park_data',
    [
        pytest.param({}, id='no data'),
        pytest.param({'long_name': 'test_long_name'}, id='no inn'),
        pytest.param({'inn': 'test_inn'}, id='no long_name'),
    ],
)
async def test_park_missing_data(
        taxi_eulas, freightage_handler_context: HandlerContext, park_data,
):
    ctx = freightage_handler_context
    ctx.retrieve_park.call.response.park_data = park_data

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 200
    assert response.json() == {}

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called == 1
    assert ctx.retrieve_phone.times_called == 1


@pytest.mark.parametrize(
    'failing_mock_name', ['retrieve_park', 'retrieve_phone'],
)
async def test_extra_data_errors(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        failing_mock_name,
):
    ctx = freightage_handler_context
    failing_mock = getattr(ctx, failing_mock_name)
    failing_mock.call.response.error_code = 500

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 500

    assert ctx.get_order_fields.times_called == 1
    assert ctx.retrieve_park.times_called > 0
    assert ctx.retrieve_phone.times_called > 0


def get_cache_control_config_mark(max_age):
    return pytest.mark.config(
        EULAS_FREIGHTAGE_CACHE_CONTROL_SETTINGS={
            'no_cache': max_age is None,
            'max_age_seconds': max_age or 300,
        },
    )


@pytest.mark.parametrize(
    'expected_header_value',
    [
        pytest.param('max-age=300'),
        pytest.param('no-cache', marks=get_cache_control_config_mark(None)),
        pytest.param('max-age=123', marks=get_cache_control_config_mark(123)),
    ],
)
async def test_cache_control(
        taxi_eulas,
        freightage_handler_context: HandlerContext,
        expected_header_value,
):
    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 200
    assert response.headers[CACHE_CONTROL] == expected_header_value


@pytest.mark.config(EULAS_FREIGHTAGE_DRIVER_TAGS=FREIGHTAGE_DRIVER_TAGS)
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
@pytest.mark.experiments3(filename='exp3_freightage_ride_additional_info.json')
async def test_contract_by_driver_tag(
        taxi_eulas, freightage_handler_context: HandlerContext, tags, is_ok,
):
    ctx = freightage_handler_context
    ctx.get_order_fields.call.response.set_zone('contract_not_required_zone')
    ctx.get_order_fields.call.response.set_candidate_tags(tags)

    response = await taxi_eulas.post(URL, json=DEFAULT_REQUEST)

    assert response.status_code == 200
    if is_ok:
        assert response.json() == {
            'ride_info': get_ride_info(),
            'contract': get_contract(),
        }
    else:
        assert response.json() == {}

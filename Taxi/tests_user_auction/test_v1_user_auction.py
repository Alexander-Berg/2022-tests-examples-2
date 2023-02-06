import dataclasses
import datetime
import math
import typing as tp

import bson
import pytest

ORDER_ID = 'order_id1'
DISALLOWED_PRICE_CHANGE_ORDER_ID = 'order_id2'
ITERATIONS_LIMIT_EXCEEDED_ORDER_ID = 'order_id3'
AUCTION_NOT_PREPARED_ORDER_ID = 'order_id4'

SOME_DATETIME = datetime.datetime(
    2021, 6, 4, 13, 37, 2, 85130, tzinfo=datetime.timezone.utc,
)
SOME_DATETIME_STR = SOME_DATETIME.isoformat()

IDEMPOTENCY_TOKEN = '123'
HEADERS = {
    'X-Yandex-UID': '4003514353',
    'X-Request-Language': 'ru',
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
}
URL = '/4.0/user-auction/v1/user-price'


@dataclasses.dataclass()
class FixedSteps:
    step: float
    max_steps: int


@dataclasses.dataclass()
class PassengerPrice:
    base: float
    current: float


@dataclasses.dataclass()
class DriverBidInfo:
    min_price: float
    max_price: float
    price_options: tp.List[float]
    passenger_price: PassengerPrice


@dataclasses.dataclass()
class ChangePriceEvent:
    order_id: str

    current_iteration: int
    new_iteration: int
    new_price: float
    total_price_change: float

    new_fixed_steps: tp.Optional[FixedSteps] = None

    driver_bid_info: tp.Optional[DriverBidInfo] = None


def user_auction_change_price(
        mockserver, request, expected_event: ChangePriceEvent,
):
    assert request.query['order_id'] == expected_event.order_id
    assert request.headers['X-Idempotency-Token'] == IDEMPOTENCY_TOKEN
    body = bson.BSON(request.get_data()).decode()
    event_arg = body['event_arg']
    expected_args_len = 6
    if expected_event.new_fixed_steps is None:
        expected_args_len -= 1
    if expected_event.driver_bid_info is None:
        expected_args_len -= 1
    assert len(event_arg) == expected_args_len
    assert event_arg['current_iteration'] == expected_event.current_iteration
    assert event_arg['new_iteration'] == expected_event.new_iteration
    assert math.isclose(
        event_arg['total_price_change'], expected_event.total_price_change,
    )
    assert math.isclose(event_arg['new_price'], expected_event.new_price)
    if expected_event.new_fixed_steps:
        assert event_arg['new_fixed_steps'] == vars(
            expected_event.new_fixed_steps,
        )
    else:
        assert 'new_fixed_steps' not in event_arg
    if expected_event.driver_bid_info:
        real, expected = (
            event_arg['driver_bid_info'],
            expected_event.driver_bid_info,
        )
        assert real['price_options'] == expected.price_options
        assert math.isclose(real['min_price'], expected.min_price)
        assert math.isclose(real['max_price'], expected.max_price)
        assert math.isclose(
            real['passenger_price']['base'], expected.passenger_price.base,
        )
        assert math.isclose(
            real['passenger_price']['current'],
            expected.passenger_price.current,
        )
    else:
        assert 'driver_bid_info' not in event_arg
    return mockserver.make_response(
        status=200, content_type='application/bson',
    )


def full_auction_exp(enabled, round_rule):
    return [
        pytest.mark.experiments3(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='full_auction',
            consumers=['user_auction/full_auction'],
            clauses=[
                {
                    'title': 'Test',
                    'value': {
                        'enabled': enabled,
                        'percent_steps': {
                            'min_ratio': 0.6,
                            'max_ratio': 1.4,
                            'step_percent': 0.1,
                            'decrease_steps': 3,
                            'increase_steps': 3,
                        },
                    },
                    'predicate': {'type': 'true'},
                },
            ],
        ),
        pytest.mark.config(
            CURRENCY_ROUNDING_RULES={
                '__default__': {'__default__': 1},
                'RUB': {'__default__': 1, 'full_auction': round_rule},
            },
        ),
    ]


@pytest.fixture(autouse=True)
def order_core_mock(mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        args = request.args
        body = bson.BSON.decode(request.get_data())
        if args['order_id'] not in {
                ORDER_ID,
                DISALLOWED_PRICE_CHANGE_ORDER_ID,
                ITERATIONS_LIMIT_EXCEEDED_ORDER_ID,
                AUCTION_NOT_PREPARED_ORDER_ID,
        }:
            return mockserver.make_response(
                status=404,
                content_type='application/json',
                json={'code': 'no_such_order', 'message': 'No such order'},
            )
        assert args['require_latest'] == 'true'
        assert body == {
            'fields': [
                'auction',
                'driver_bid_info',
                'order.nz',
                'order.pricing_data.currency.name',
                'order.request.class',
                'order.status',
                'order.user_phone_id',
            ],
        }

        response_fields = {
            'document': {
                '_id': args['order_id'],
                'auction': {
                    'iteration': 0,
                    'change_ts': SOME_DATETIME,
                    'price': {'base': 100.5, 'current': 100.9},
                    'allowed_price_change': {
                        'fixed_steps': {'step': 5.4, 'max_steps': 3},
                    },
                },
                'order': {
                    'user_phone_id': bson.ObjectId('123412341234123412341234'),
                    'nz': 'tariff_zone_with_max_2_iterations',
                    'status': 'pending',
                    'pricing_data': {'currency': {'name': 'RUB'}},
                    'request': {'class': ['econom']},
                },
                'driver_bid_info': {
                    'min_price': 70.0,
                    'max_price': 140.0,
                    'price_options': [70, 80, 90, 110, 120, 130],
                    'passenger_price': {'base': 100.5, 'current': 100.9},
                },
            },
        }
        if args['order_id'] == DISALLOWED_PRICE_CHANGE_ORDER_ID:
            del response_fields['document']['auction']['allowed_price_change']
        if args['order_id'] == ITERATIONS_LIMIT_EXCEEDED_ORDER_ID:
            response_fields['document']['auction']['iteration'] = 1
        if args['order_id'] == AUCTION_NOT_PREPARED_ORDER_ID:
            response_fields['document']['auction'] = {
                'iteration': 0,
                'change_ts': SOME_DATETIME,
            }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )


@pytest.mark.experiments3(filename='allowed_price_change_config.json')
@pytest.mark.parametrize(
    'full_auction_etalon',
    [
        pytest.param(None, marks=full_auction_exp(False, 10)),
        pytest.param(
            DriverBidInfo(
                80.0,
                160.0,
                [90.0, 100.0, 110.0, 130.0, 150.0, 160.0],
                PassengerPrice(100.5, 117.1),
            ),
            marks=full_auction_exp(True, 10),
        ),
        pytest.param(
            DriverBidInfo(100.0, 117.1, [100.0], PassengerPrice(100.5, 117.1)),
            marks=full_auction_exp(True, 100),
        ),
        pytest.param(
            DriverBidInfo(117.1, 117.1, [], PassengerPrice(100.5, 117.1)),
            marks=full_auction_exp(True, 1000),
        ),
    ],
)
async def test_200_happy_price_change(
        taxi_user_auction, mockserver, full_auction_etalon,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-change-price',
    )
    async def mock_processing(request, *args, **kwargs):
        return user_auction_change_price(
            mockserver,
            request,
            ChangePriceEvent(
                ORDER_ID,
                current_iteration=0,
                new_iteration=1,
                new_price=117.1,
                total_price_change=16.6,
                new_fixed_steps=FixedSteps(step=5.4, max_steps=3),
                driver_bid_info=full_auction_etalon,
            ),
        )

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 200

    assert mock_processing.times_called == 1


@pytest.mark.experiments3(filename='allowed_price_change_config.json')
async def test_200_iterations_limit_exceeded(taxi_user_auction, mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-change-price',
    )
    async def mock_processing(request, *args, **kwargs):
        return user_auction_change_price(
            mockserver,
            request,
            ChangePriceEvent(
                ITERATIONS_LIMIT_EXCEEDED_ORDER_ID,
                current_iteration=1,
                new_iteration=2,
                new_price=117.1,
                total_price_change=16.6,
            ),
        )

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ITERATIONS_LIMIT_EXCEEDED_ORDER_ID},
        json={'iteration': 1, 'price_change': 16.2},
    )
    assert res.status == 200

    assert mock_processing.times_called == 1


async def test_200_not_found_allowed_price_change_config(
        taxi_user_auction, mockserver,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-change-price',
    )
    async def mock_processing(request, *args, **kwargs):
        return user_auction_change_price(
            mockserver,
            request,
            ChangePriceEvent(
                ORDER_ID,
                current_iteration=0,
                new_iteration=1,
                new_price=117.1,
                total_price_change=16.6,
            ),
        )

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 200

    assert mock_processing.times_called == 1


async def test_404_order_core_404(taxi_user_auction):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': 'non_exist_order_id'},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 404
    assert res.json()['code'] == 'ORDER_NOT_FOUND'


async def test_400_disallowed_price_change(taxi_user_auction):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': DISALLOWED_PRICE_CHANGE_ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 400
    assert res.json()['code'] == 'PRICE_CHANGE_DISALLOWED'


async def test_400_too_big_price_change(taxi_user_auction):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.3},
    )
    assert res.status == 400
    assert res.json()['code'] == 'TOO_BIG_PRICE_CHANGE'


@pytest.mark.parametrize(
    'price_change', [-100.0, -5.4, -16.2, -0.01, 0.0, 0.4, 2.7, 10.7],
)
async def test_400_invalid_price_change(taxi_user_auction, price_change):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': price_change},
    )
    assert res.status == 400
    assert res.json()['code'] == 'INVALID_PRICE_CHANGE'


async def test_409_iteration_mismatch(taxi_user_auction):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 1, 'price_change': 16.2},
    )
    assert res.status == 409
    assert res.json()['code'] == 'ITERATION_MISMATCH'


async def test_409_auction_not_prepared(taxi_user_auction):
    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': AUCTION_NOT_PREPARED_ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 409
    assert res.json()['code'] == 'AUCTION_NOT_PREPARED'


@pytest.mark.parametrize('status', ['finished', 'cancelled', 'assigned'])
async def test_409_order_search_not_active(
        taxi_user_auction, mockserver, status,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        response_fields = {
            'document': {
                '_id': ORDER_ID,
                'auction': {
                    'iteration': 0,
                    'change_ts': SOME_DATETIME,
                    'price': {'base': 100.5, 'current': 100.9},
                    'allowed_price_change': {
                        'fixed_steps': {'step': 5.4, 'max_steps': 3},
                    },
                },
                'order': {
                    'user_phone_id': bson.ObjectId('123412341234123412341234'),
                    'nz': 'tariff_zone_with_max_2_iterations',
                    'status': status,
                    'pricing_data': {'currency': {'name': 'RUB'}},
                    'request': {'class': ['econom']},
                },
            },
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 409
    assert res.json()['code'] == 'NOT_PENDING_ORDER'


async def test_500_order_core_get_fields_500(taxi_user_auction, mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        return mockserver.make_response(status=500)

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 500


async def test_500_order_core_send_event_500(taxi_user_auction, mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-change-price',
    )
    async def _mock_processing(request, *args, **kwargs):
        return mockserver.make_response(status=500)

    res = await taxi_user_auction.put(
        URL,
        headers=HEADERS,
        params={'order_id': ORDER_ID},
        json={'iteration': 0, 'price_change': 16.2},
    )
    assert res.status == 500

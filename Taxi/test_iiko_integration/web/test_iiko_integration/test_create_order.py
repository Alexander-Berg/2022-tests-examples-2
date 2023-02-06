import dataclasses
import enum
from typing import Any
from typing import Dict
from typing import Optional
import uuid

import pytest

from test_iiko_integration import stubs


class Language(enum.Enum):
    RU = 'ru'  # pylint: disable=invalid-name
    EN = 'en'  # pylint: disable=invalid-name
    UNKNOWN = 'kek'
    NOT_TRANSLATED = 'kk'


@dataclasses.dataclass
class OrderSubmission:
    api_key: str
    json: Dict[str, Any]
    language: Optional[Language] = None
    idempotency_token: str = dataclasses.field(
        default_factory=lambda: uuid.uuid4().hex,
    )


@dataclasses.dataclass
class ExpectedResponse:
    status: int
    json: Optional[Dict[str, Any]] = None


TRANSLATIONS = {
    'qr_payment': {
        'default_upper': {
            'ru': 'trans_ru_default_upper',
            'en': 'trans_en_default_upper',
        },
        'default_lower': {
            'ru': 'trans_ru_default_lower',
            'en': 'trans_en_default_lower',
        },
        'restaurant_01_upper': {
            'ru': 'trans_ru_restaurant_01_upper',
            'en': 'trans_en_restaurant_01_upper',
        },
    },
}


FOOD_ITEM = {
    'product_id': '1',
    'name': 'afood',
    'price_per_unit': '1400.00',
    'quantity': '1.00',
    'price_without_discount': '1400.00',
    'price_for_customer': '1400.00',
    'discount_amount': '0.00',
    'discount_percent': '0.00',
    'vat_amount': '213.56',
    'vat_percent': '18',
}
FOOD_ITEM_WITH_DISCOUNT = {
    **FOOD_ITEM,
    **{
        'price_for_customer': '980.00',
        'discount_amount': '420.00',
        'discount_percent': '30.00',
        'vat_amount': '149.49',
    },
}
FOOD_ITEM_WITH_INVALID_DECIMAL = {**FOOD_ITEM, **{'quantity': '1.00kek'}}
FOOD_ITEM_WITH_NEGATIVE_DECIMAL = {**FOOD_ITEM, **{'quantity': '-0.3'}}
FOOD_ITEM_WITH_100_PERCENT_DISCOUNT = {
    **FOOD_ITEM,
    **{
        'price_for_customer': '0.00',
        'discount_amount': '1400.00',
        'discount_percent': '100.00',
        'vat_amount': '0.00',
    },
}
FOOD_ITEM_WITH_101_PERCENT_DISCOUNT = {
    **FOOD_ITEM,
    **{'discount_percent': '101.00'},
}
FOOD_ITEM_WITH_MINOR_DISCOUNT_ERROR = {
    **FOOD_ITEM,
    'price_per_unit': '325',
    'price_without_discount': '325',
    'price_for_customer': '292.25',
    'discount_amount': '32.75',
    'discount_percent': '10.08',
    'vat_amount': '48.71',
    'vat_percent': '20',
}
FOOD_ITEM_WITH_ZERO_PRICE = {
    **FOOD_ITEM,
    'price_per_unit': '0',
    'price_without_discount': '0',
    'price_for_customer': '0',
    'discount_amount': '0',
    'discount_percent': '0',
    'vat_amount': '0',
}


@pytest.fixture(name='test_request')
def test_request_fixture(web_app_client, get_db_order):
    async def _test_request_fixture(
            order_submission: OrderSubmission,
            expected_response: ExpectedResponse,
    ):
        target_url = '/external/v1/orders'
        headers = {
            'X-YaTaxi-Api-Key': order_submission.api_key,
            'X-Idempotency-Token': order_submission.idempotency_token,
        }
        if order_submission.language is not None:
            headers['Accept-Language'] = order_submission.language.value
        response = await web_app_client.post(
            target_url, headers=headers, json=order_submission.json,
        )
        assert response.status == expected_response.status
        if expected_response.json is not None:
            response_json = await response.json()
            assert response_json == expected_response.json
            order_id = response_json['order_id']
            order = await get_db_order('*', id=order_id)
            assert order['status']['invoice_status'] == 'INIT'
            assert order['status']['restaurant_status'] == 'PENDING'
            status_history = order['status_history']
            assert len(status_history) == 1
            assert status_history[0] == order['status']
            assert order['version'] == 0
            changelog = order['changelog']
            assert not changelog
            assert (
                order['created_at']
                == order['updated_at']
                == order['status']['invoice_updated_at']
                == order['status']['restaurant_updated_at']
                == status_history[0]['invoice_updated_at']
                == status_history[0]['restaurant_updated_at']
            )

    return _test_request_fixture


@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS, IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize(
    ['order_submission', 'expected_response'],
    [
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '0',
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_id': '2104653bdac343e39ac57869d0bd738d',
                    'upper_text': 'trans_ru_restaurant_01_upper',
                    'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
                    'lower_text': 'trans_ru_default_lower',
                },
            ),
            id='Normal order with implicit RU locale',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                language=Language.EN,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '0',
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_id': '2104653bdac343e39ac57869d0bd738d',
                    'upper_text': 'trans_en_restaurant_01_upper',
                    'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
                    'lower_text': 'trans_en_default_lower',
                },
            ),
            id='Normal order with explicit EN locale',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                language=Language.UNKNOWN,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '0',
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_id': '2104653bdac343e39ac57869d0bd738d',
                    'upper_text': 'trans_en_restaurant_01_upper',
                    'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
                    'lower_text': 'trans_en_default_lower',
                },
            ),
            id='Normal order with unknown locale',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                language=Language.NOT_TRANSLATED,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '0',
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_id': '2104653bdac343e39ac57869d0bd738d',
                    'upper_text': 'trans_ru_restaurant_01_upper',
                    'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
                    'lower_text': 'trans_ru_default_lower',
                },
            ),
            id='Normal order with unsupported (not translated) locale',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.INVALID,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '0.00',
                    'currency': 'RUB',
                    'items': [],
                },
            ),
            ExpectedResponse(status=403),
            id='Invalid Api-Key',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '0.00',
                    'currency': 'RUB',
                    'items': [],
                },
            ),
            ExpectedResponse(status=400),
            id='Order with empty items',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '0.00',
                    'currency': 'ru',
                    'items': [FOOD_ITEM],
                },
            ),
            ExpectedResponse(status=400),
            id='Invalid currency',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM_WITH_DISCOUNT],
                    'discount': '420.00',
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_id': '2104653bdac343e39ac57869d0bd738d',
                    'upper_text': 'trans_ru_restaurant_01_upper',
                    'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
                    'lower_text': 'trans_ru_default_lower',
                },
            ),
            id='Order with discount',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '420.00',
                },
            ),
            ExpectedResponse(status=400),
            id='Different total price and item price sum',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM_WITH_INVALID_DECIMAL],
                    'discount': '420.00',
                },
            ),
            ExpectedResponse(status=400),
            id='Order with invalid decimal',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM_WITH_NEGATIVE_DECIMAL],
                    'discount': '420.00',
                },
            ),
            ExpectedResponse(status=400),
            id='Order with negative decimal in ">0" field',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM_WITH_101_PERCENT_DISCOUNT],
                    'discount': '420.00',
                },
            ),
            ExpectedResponse(status=400),
            id='Order with item discount at in 101 percent',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '980.00',
                    'currency': 'RUB',
                    'items': [
                        FOOD_ITEM_WITH_DISCOUNT,
                        FOOD_ITEM_WITH_100_PERCENT_DISCOUNT,
                    ],
                    'discount': '1820.00',
                },
            ),
            ExpectedResponse(status=200),
            id='Order with item discount at in 100 percent',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '0.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                },
            ),
            ExpectedResponse(status=400),
            id='missing discount value',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'total_price': '0.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '337.00',
                },
            ),
            ExpectedResponse(status=400),
            id='missing restaurant_order_id',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_DISABLED,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM],
                    'discount': '0',
                },
            ),
            ExpectedResponse(status=400),
            id='try create order in disabled restaurant',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '292.25',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM_WITH_MINOR_DISCOUNT_ERROR],
                    'discount': '32.75',
                },
            ),
            ExpectedResponse(status=200),
            id='Order with minor discount error',
        ),
        pytest.param(
            OrderSubmission(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'restaurant_order_id': '123',
                    'total_price': '1400.00',
                    'currency': 'RUB',
                    'items': [FOOD_ITEM, FOOD_ITEM_WITH_ZERO_PRICE],
                    'discount': '0',
                },
            ),
            ExpectedResponse(status=200),
            id='Order with zero-price item',
        ),
    ],
)
async def test_create_order(
        test_request,
        monkeypatch,
        mock_stats,
        mockserver,
        order_submission: OrderSubmission,
        expected_response: ExpectedResponse,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        assert queue_name == 'restaurant_order_expired'

    if expected_response.json is not None:
        monkeypatch.setattr(
            'uuid.UUID.hex', expected_response.json['order_id'],
        )

    stats_counter = mock_stats(
        'order.events.created', 'restaurant01', 'restaurant_group_01',
    )
    await test_request(order_submission, expected_response)

    if expected_response.status == 200:
        assert stats_counter.count == 1
        assert _queue.times_called == 1


@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS, IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.translations(**TRANSLATIONS)
async def test_idempotency(test_request, monkeypatch, mock_stats):
    order_submission = OrderSubmission(
        api_key=stubs.ApiKey.RESTAURANT_01,
        json={
            'restaurant_order_id': '123',
            'total_price': '1400.00',
            'currency': 'RUB',
            'items': [FOOD_ITEM],
            'discount': '0',
        },
    )
    expected_json = {
        'order_id': '2104653bdac343e39ac57869d0bd738d',
        'upper_text': 'trans_ru_restaurant_01_upper',
        'deeplink': 'default_2104653bdac343e39ac57869d0bd738d_1',
        'lower_text': 'trans_ru_default_lower',
    }
    expected_response = ExpectedResponse(status=200, json=expected_json)
    monkeypatch.setattr('uuid.UUID.hex', expected_json['order_id'])
    stats_counter = mock_stats(
        'order.events.created', 'restaurant01', 'restaurant_group_01',
    )
    await test_request(order_submission, expected_response)
    assert stats_counter.count == 1
    await test_request(order_submission, expected_response)
    assert stats_counter.count == 1

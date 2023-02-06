import decimal
import json
from typing import List
from typing import NamedTuple

import pytest

from cashback import const


class CashbackBySource(NamedTuple):
    value: str
    source: str


class MyTestCase(NamedTuple):
    body: dict
    expected_cashback: str
    expected_event_values: List[CashbackBySource]


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                body=dict(
                    clear_sum='20',
                    cashback_by_source=[
                        {'value': '7', 'source': 'user'},
                        {'value': '3', 'source': 'service'},
                    ],
                ),
                expected_cashback='10',
                expected_event_values=[
                    CashbackBySource('7', 'user'),
                    CashbackBySource('3', 'service'),
                ],
            ),
            id='split-simple',
        ),
        pytest.param(
            MyTestCase(
                body=dict(
                    clear_sum='30',
                    cashback_by_source=[
                        {'value': '7', 'source': 'user'},
                        {'value': '3', 'source': 'service'},
                        {'value': '4', 'source': 'possible-cashback-service'},
                    ],
                ),
                expected_cashback='14',
                expected_event_values=[
                    CashbackBySource('7', 'user'),
                    CashbackBySource('3', 'service'),
                    CashbackBySource('4', 'possible-cashback-service'),
                ],
            ),
            id='split-simple-possible-cashback',
        ),
        pytest.param(
            MyTestCase(
                body=dict(
                    clear_sum='500',
                    cashback_by_source=[
                        {'value': '100', 'source': 'user'},
                        {'value': '50.70', 'source': 'service'},
                    ],
                ),
                expected_cashback='150',
                expected_event_values=[
                    CashbackBySource('100', 'user'),
                    CashbackBySource('50', 'service'),
                ],
            ),
            id='split-rounding',
        ),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_register_cashback(web_cashback, pg_cashback, case):
    order_id = 'order_id_11'

    clears = await pg_cashback.order_clears.by_ids([order_id])

    response = await web_cashback.register_cashback.make_request(
        override_params={'order_id': order_id}, override_data=case.body,
    )
    assert response.status == 200
    assert await response.json() == {
        'status': const.REGISTER_STATUS_NEED_PROCESSING,
    }

    new_clears = await pg_cashback.order_clears.by_ids([order_id])
    assert len(new_clears) == len(clears) == 1

    new_clear = new_clears[0]
    assert new_clear['version'] == clears[0]['version'] + 1
    assert new_clear['value'] == decimal.Decimal(case.body['clear_sum'])
    assert new_clear['cashback_sum'] == decimal.Decimal(case.expected_cashback)

    events = await pg_cashback.events.by_external_ref(external_ref=order_id)
    assert len(events) == len(case.expected_event_values)

    for event in events:
        assert event['type'] == 'invoice'
        assert event['status'] == 'new'
        for expected in case.expected_event_values:
            if event['source'] == expected.source:
                assert event['value'] == decimal.Decimal(expected.value)


@pytest.mark.parametrize(
    'body',
    [
        dict(
            clear_sum='100',
            cashback_by_source=[
                {'value': '20', 'source': 'user'},
                {'value': '0', 'source': 'service'},
            ],
        ),
        dict(
            clear_sum='110',
            cashback_by_source=[
                {'value': '20.9', 'source': 'user'},
                {'value': '0', 'source': 'service'},
            ],
        ),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_register_no_cashback(web_cashback, pg_cashback, body):
    order_id = 'order_id_11'

    clears = await pg_cashback.order_clears.by_ids([order_id])

    response = await web_cashback.register_cashback.make_request(
        override_params={'order_id': order_id}, override_data=body,
    )
    assert response.status == 200
    assert await response.json() == {
        'status': const.REGISTER_STATUS_NOT_NEED_PROCESSING,
    }

    new_clears = await pg_cashback.order_clears.by_ids([order_id])
    assert len(clears) == len(new_clears) == 1
    assert new_clears[0] == clears[0]

    events = await pg_cashback.events.by_external_ref(external_ref=order_id)
    assert not events


@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_race_condition(web_cashback, pg_cashback):
    order_id = 'order_id_12'

    clears = await pg_cashback.order_clears.by_ids([order_id])

    response = await web_cashback.register_cashback.make_request(
        override_params={'order_id': order_id},
    )
    assert response.status == 409

    new_clears = await pg_cashback.order_clears.by_ids([order_id])

    assert len(new_clears) == len(clears) == 1
    assert new_clears[0] == clears[0]

    events = await pg_cashback.events.by_external_ref(order_id)
    assert not events


@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_create_event(web_cashback, pg_cashback):
    order_id = 'order_id_13'
    service = 'lavka'
    currency = 'EUR'
    payload = {'order_id': order_id}
    yandex_uid = 'yandex_uid_13'
    cashback_by_source = [
        {'value': '95', 'source': 'user'},
        {'value': '40', 'source': 'service'},
    ]

    response = await web_cashback.register_cashback.make_request(
        override_params={'order_id': order_id, 'service': service},
        override_data={
            'currency': currency,
            'payload': payload,
            'yandex_uid': yandex_uid,
            'cashback_by_source': cashback_by_source,
        },
    )
    assert response.status == 200

    events = await pg_cashback.events.by_external_ref(order_id)
    assert len(events) == 2

    for event in events:
        assert event['type'] == 'invoice'
        assert event['status'] == 'new'
        assert event['currency'] == currency
        assert event['service'] == service
        assert event['payload'] == json.dumps(payload)
        assert event['yandex_uid'] == yandex_uid
        if event['source'] == 'user':
            assert event['value'] == decimal.Decimal('95')
        if event['source'] == 'service':
            assert event['value'] == decimal.Decimal('40')


async def test_extra_payload(web_cashback, pg_cashback):
    order_id = 'order_id_13'
    payload = {'common_field': 'common_field_value'}
    cashback_by_source = [
        {'value': '95', 'source': 'user'},
        {
            'value': '40',
            'source': 'service',
            'extra_payload': {'extra_field': 'extra_field_value'},
        },
    ]

    response = await web_cashback.register_cashback.make_request(
        override_params={'order_id': order_id},
        override_data={
            'payload': payload,
            'cashback_by_source': cashback_by_source,
        },
    )
    assert response.status == 200

    events = await pg_cashback.events.by_external_ref(order_id)
    assert len(events) == 2

    for event in events:
        if event['source'] == 'user':
            assert event['value'] == decimal.Decimal('95')
            assert json.loads(event['payload']) == {
                'common_field': 'common_field_value',
            }
        if event['source'] == 'service':
            assert event['value'] == decimal.Decimal('40')
            assert json.loads(event['payload']) == {
                'common_field': 'common_field_value',
                'extra_field': 'extra_field_value',
            }

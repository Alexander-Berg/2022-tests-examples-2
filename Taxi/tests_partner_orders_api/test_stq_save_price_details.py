import datetime

import psycopg2

KWARGS = {
    'details': {
        'requirements': [
            {
                'count': 4,
                'included': 0,
                'name': 'something_important',
                'price': {'per_unit': 25.0, 'total': 100.0},
                'text': {
                    'keyset': 'requirements_keyset',
                    'tanker_key': 'prefix.something_important',
                },
            },
        ],
        'services': [
            {
                'name': 'anything_unusual',
                'price': 34.21,
                'text': {
                    'keyset': 'services_keyset',
                    'tanker_key': 'anything_unusual.suffix',
                },
            },
            {
                'name': 'something_unusual',
                'price': 12.34,
                'text': {
                    'keyset': 'services_keyset',
                    'tanker_key': 'something_unusual.suffix',
                },
            },
        ],
    },
    'order_id': 'agent_order_id',
    'calculated_at': '2017-03-13T11:30:40.123456+0300',
}


def execute_query(query, pgsql):
    pg_cursor = pgsql['partner_orders_api'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


async def test_forwarding_in_api_errors(
        taxi_partner_orders_api, stq_runner, pgsql,
):
    await stq_runner.agent_orders_save_price_details.call(
        task_id='task_id', kwargs=KWARGS,
    )

    order_price_details = execute_query(
        'SELECT * FROM partner_orders_api.order_price_details', pgsql,
    )

    assert order_price_details == [
        (
            'agent_order_id',
            'task_id',
            datetime.datetime(
                2017,
                3,
                13,
                8,
                30,
                40,
                123456,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]

    service_details = execute_query(
        'SELECT * FROM partner_orders_api.price_details_items', pgsql,
    )
    assert service_details == [
        (1, 'task_id', 34.21, 'anything_unusual'),
        (2, 'task_id', 12.34, 'something_unusual'),
        (3, 'task_id', 100.0, 'something_important'),
    ]

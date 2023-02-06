import json

from taxi.billing.util import dates as billing_dates


def _cmp_data(actual, expected):
    keys_actual = actual[0].keys() if actual else []
    keys_expected = expected[0].keys() if expected else []
    keys = keys_actual if keys_actual else keys_expected

    def _key(doc):
        return tuple(doc[key] for key in keys)

    def _sorted(docs):
        return sorted(docs, key=_key)

    # print('**** keys_actual=',sorted(keys_actual))
    # print('**** keys_expected=',sorted(keys_expected))

    assert _sorted(actual) == _sorted(expected)


async def _read_data_from_pg(pool, query, jsonb_fields):
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    data = [dict(row) for row in rows]
    data_created = json.loads(
        json.dumps(data, ensure_ascii=False, default=str),
    )
    if jsonb_fields is None:
        jsonb_fields = ['payload']
    for doc in data_created:
        for jsonb_field in jsonb_fields:
            if jsonb_field in doc:
                doc[jsonb_field] = json.loads(doc[jsonb_field])

    return data_created


async def check_pg_expected_results(
        pool, query, data_expected, jsonb_fields=None,
):
    data_created = await _read_data_from_pg(
        pool=pool, query=query, jsonb_fields=jsonb_fields,
    )
    # print('**** data_created')
    # print(data_created)
    # print('**** data_expected')
    # print(data_expected)
    _cmp_data(data_created, data_expected)


def check_stq_calls(queue, expected_calls):
    queue_calls = []
    while queue.has_calls:
        call = queue.next_call()
        queue_calls.append(
            {
                'task_id': call['id'],
                'kwargs': call['kwargs'],
                'args': call['args'],
                'eta': billing_dates.format_datetime(
                    billing_dates.ensure_aware(call['eta']),
                ),
            },
        )

    def _sorted_calls(calls):
        return sorted(calls, key=lambda x: x['task_id'])

    # print('**** queue_calls=', _sorted_calls(queue_calls))
    # print('**** expected_calls=', _sorted_calls(expected_calls))

    assert _sorted_calls(queue_calls) == _sorted_calls(expected_calls)


def check_stqs_calls(queues, expected_calls):
    queue_calls = []
    for queue in queues:
        while queue.has_calls:
            call = queue.next_call()
            queue_calls.append(
                {
                    'queue_name': call['queue'],
                    'task_id': call['id'],
                    'kwargs': call['kwargs'],
                    'args': call['args'],
                    'eta': billing_dates.format_datetime(
                        billing_dates.ensure_aware(call['eta']),
                    ),
                },
            )

    def _sorted_calls(calls):
        return sorted(calls, key=lambda x: x['task_id'])

    # print('**** queue_calls=', _sorted_calls(queue_calls))
    # print('**** expected_calls=', _sorted_calls(expected_calls))

    assert _sorted_calls(queue_calls) == _sorted_calls(expected_calls)

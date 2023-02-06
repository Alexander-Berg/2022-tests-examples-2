import pytest


@pytest.mark.parametrize(
    'args, expected_key, expected_value',
    [
        (
            {
                'subscription_doc_id': 123,
                'subscription_end': '2020-10-01T01:02:03+00:00',
            },
            'sub:123',
            b'2020-10-01T01:02:03.000000+00:00',
        ),
        (
            {'subscription_doc_id': 123},
            'sub:123',
            b'2200-01-01T00:00:00.000000+00:00',
        ),
    ],
)
async def test(stq_runner, redis_store, *, args, expected_key, expected_value):
    await stq_runner.billing_time_events_process_subs.call(
        task_id='sample_task', kwargs=args,
    )
    assert redis_store.exists(expected_key)
    assert redis_store.get(expected_key) == expected_value

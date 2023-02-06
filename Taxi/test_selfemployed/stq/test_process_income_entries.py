import pytest

from testsuite.utils import http

from selfemployed.stq import process_income_entries

_ENTRIES_SELECT_QUERY = """
SELECT id, park_id, contractor_id, agreement_id, sub_account,
    doc_ref, event_at::TEXT, inn_pd_id, is_own_park, do_send_receipt,
    status, amount::TEXT, order_id, reverse_entry_id,
    receipt_id, receipt_url
FROM se_income.entries
ORDER BY id
"""


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
        (phone_pd_id, inn_pd_id, status)
        VALUES ('PHONE_PD_ID_1', 'INN_PD_ID_1', 'COMPLETED')
        ON CONFLICT DO NOTHING;

        INSERT INTO se.finished_profiles
        (park_id, contractor_profile_id, phone_pd_id,
         inn_pd_id, do_send_receipts, is_own_park)
        VALUES ('p1', 'd1', 'PHONE_PD_ID_1',
                'INN_PD_ID_1', TRUE, TRUE)
        ON CONFLICT DO NOTHING;
        """,
    ],
)
@pytest.mark.client_experiments3(
    consumer='selfemployed/fns-se/billing-events',
    experiment_name='pro_fns_selfemployment_use_billing_events',
    args=[{'name': 'park_id', 'type': 'string', 'value': 'p1'}],
    value={'use_new_style': True},
)
async def test_task_new_style_profile(stq3_context, load_json, stq):
    await process_income_entries.task(
        stq3_context,
        park_id='p1',
        contractor_profile_id='d1',
        entries=load_json('mock_received.json'),
    )

    result = []
    for shard in stq3_context.pg.orders_masters:
        shard_records = await shard.fetch(_ENTRIES_SELECT_QUERY)
        result.extend(dict(record) for record in shard_records)

    assert result == load_json('expected_entries.json')
    assert stq.selfemployed_fns_report_income.times_called == 2
    assert stq.selfemployed_fns_correct_income.times_called == 1


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
        (id, from_park_id, from_driver_id, park_id, driver_id,
        inn, created_at, modified_at)
        VALUES
        ('aaa17', 'fp1', 'fd1', 'p1', 'd1',
        '012345678901', NOW(), NOW())
        ON CONFLICT DO NOTHING;
        """,
    ],
)
@pytest.mark.client_experiments3(
    consumer='selfemployed/fns-se/billing-events',
    experiment_name='pro_fns_selfemployment_use_billing_events',
    args=[{'name': 'park_id', 'type': 'string', 'value': 'p1'}],
    value={'use_new_style': True},
)
async def test_task_old_style_profile(
        stq3_context, load_json, stq, mock_personal,
):
    inn = '012345678901'

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        assert request.json == {'value': inn, 'validate': True}
        return {'value': inn, 'id': 'INN_PD_ID_1'}

    await process_income_entries.task(
        stq3_context,
        park_id='p1',
        contractor_profile_id='d1',
        entries=load_json('mock_received.json'),
    )

    result = []
    for shard in stq3_context.pg.orders_masters:
        shard_records = await shard.fetch(_ENTRIES_SELECT_QUERY)
        result.extend(dict(record) for record in shard_records)

    assert result == load_json('expected_entries.json')
    assert stq.selfemployed_fns_report_income.times_called == 2
    assert stq.selfemployed_fns_correct_income.times_called == 1


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
        (phone_pd_id, inn_pd_id, status)
        VALUES ('PHONE_PD_ID_1', 'INN_PD_ID_1', 'COMPLETED')
        ON CONFLICT DO NOTHING;

        INSERT INTO se.finished_profiles
        (park_id, contractor_profile_id, phone_pd_id,
         inn_pd_id, do_send_receipts, is_own_park)
        VALUES ('p1', 'd1', 'PHONE_PD_ID_1',
                'INN_PD_ID_1', TRUE, TRUE)
        ON CONFLICT DO NOTHING;
        """,
    ],
)
@pytest.mark.client_experiments3(
    consumer='selfemployed/fns-se/billing-events',
    experiment_name='pro_fns_selfemployment_use_billing_events',
    args=[{'name': 'park_id', 'type': 'string', 'value': 'p1'}],
    value={'use_new_style': False},
)
async def test_task_new_style_profile_disabled(stq3_context, load_json, stq):
    await process_income_entries.task(
        stq3_context,
        park_id='p1',
        contractor_profile_id='d1',
        entries=load_json('mock_received.json'),
    )

    result = []
    for shard in stq3_context.pg.orders_masters:
        shard_records = await shard.fetch(_ENTRIES_SELECT_QUERY)
        result.extend(dict(record) for record in shard_records)

    assert result == []
    assert stq.selfemployed_fns_report_income.times_called == 0
    assert stq.selfemployed_fns_correct_income.times_called == 0

import pytest


CARGO_CLAIMS_CORP_BILLING_JOB = {
    'dryrun_on': False,
    'corrections_log_on': True,
    'batches_count': 10,
    'process_corrections_count': -1,
}
CLAIMS_COUNT = 100


def _make_test_corrections(pgsql):
    cursor = pgsql['cargo_claims'].conn.cursor()
    claim_uuid = 'c' * 32
    claim_uuids = [
        str(x) + claim_uuid[len(str(x)) :] for x in range(CLAIMS_COUNT)
    ] * 2
    sum_to_pays = [100] * CLAIMS_COUNT * 2
    claim_statuses = ['accepted', 'delivered_finish'] * int(
        CLAIMS_COUNT / 2,
    ) + ['delivered_finish', 'accepted'] * int(CLAIMS_COUNT / 2)
    corrections_count = [1] * CLAIMS_COUNT * 2
    corp_clients = ['c' * 32] * CLAIMS_COUNT * 2
    values = ''
    for value in (
            claim_uuids,
            sum_to_pays,
            claim_statuses,
            corrections_count,
            corp_clients,
    ):
        values = values + 'UNNEST(array{}), '.format(value)
    query = (
        'INSERT INTO cargo_claims.price_corrections '
        '(claim_uuid, sum_to_pay, claim_status,'
        ' corrections_count, corp_client_id) '
        'VALUES ({});'
    ).format(values[:-2])
    cursor.execute(query)


@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_batches_distribution(mockserver, run_corp_billing, pgsql):
    _make_test_corrections(pgsql)

    @mockserver.json_handler('/corp-billing/v1/pay-order/cargo')
    async def _v1_pay_order_cargo(request):
        return mockserver.make_response(
            headers={'X-YaRequestId': 'request_id'},
            json={'status': {'code': 'SUCCESS', 'message': 'OK'}},
            status=200,
        )

    result = await run_corp_billing()
    assert len(result) == CLAIMS_COUNT
    for key in result.keys():
        assert result[key] == {'accepted': 1, 'delivered_finish': 1}


async def test_external_billing_clients(
        mockserver,
        run_corp_billing,
        create_segment_with_performer,
        pgsql,
        taxi_cargo_claims,
        taxi_config,
        get_default_corp_client_id,
):
    creator = await create_segment_with_performer(taxi_class='eda')

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.price_corrections (
            claim_uuid, sum_to_pay, claim_status,
            corrections_count, corp_client_id
        )
        VALUES (
            '{creator.claim_id}', 10, 'accepted',
            3, '{get_default_corp_client_id}'
        )
        """,
    )

    taxi_config.set_values(
        dict(
            CARGO_EXTERNAL_BILLING_CORP_CLIENTS=[get_default_corp_client_id],
            CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
        ),
    )
    await taxi_cargo_claims.invalidate_caches()

    @mockserver.json_handler('/corp-billing/v1/pay-order/cargo')
    async def _v1_pay_order_cargo(request):
        return mockserver.make_response(
            headers={'X-YaRequestId': 'request_id'},
            json={'status': {'code': 'SUCCESS', 'message': 'OK'}},
            status=200,
        )

    result = await run_corp_billing()
    assert result is None
    assert not _v1_pay_order_cargo.times_called

    cursor.execute(
        f"""
        SELECT claim_uuid, is_sent
        FROM cargo_claims.price_corrections
        """,
    )
    assert cursor.fetchall() == [(creator.claim_id, True)]

MOCK_URL = (
    '/fleet-transactions-api/v1/parks/driver-profiles/transactions/by-platform'
)

PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
BAD_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'


async def test_stq_ok(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(MOCK_URL)
    def fta_handler(request):
        return {
            'event_at': '2020-01-01T00:00:00.000000000+00:00',
            'park_id': 'park_1',
            'driver_profile_id': 'driver_profile_1',
            'category_id': 'category_1',
            'amount': '-500.0000',
            'currency_code': 'RUB',
            'description': 'description',
            'created_by': {'identity': 'platform'},
        }

    await stq_runner.contractor_instant_payouts_rollback.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert fta_handler.times_called == 2
    assert fta_handler.next_call()['request'].json == {
        'amount': '100.0101',
        'category_id': 'partner_service_transfer',
        'description': PAYOUT_ID,
        'driver_profile_id': '48b7b5d81559460fb176693800000001',
        'park_id': '48b7b5d81559460fb1766938f94009c1',
    }
    assert fta_handler.next_call()['request'].json == {
        'amount': '1.0101',
        'category_id': 'partner_service_transfer_commission',
        'description': PAYOUT_ID,
        'driver_profile_id': '48b7b5d81559460fb176693800000001',
        'park_id': '48b7b5d81559460fb1766938f94009c1',
    }

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    new_status = cursor.fetchall()[0][0]
    assert new_status == 'failed'


async def test_stq_no_payout(stq_runner, mockserver, pgsql):
    await stq_runner.contractor_instant_payouts_rollback.call(
        task_id='1', kwargs={'id': BAD_PAYOUT_ID},
    )

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT count(*)
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{BAD_PAYOUT_ID}'
        """,
    )
    count = cursor.fetchall()[0][0]
    assert count == 0

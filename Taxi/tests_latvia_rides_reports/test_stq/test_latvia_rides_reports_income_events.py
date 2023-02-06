async def test_stq(stq_runner, pgsql):
    await stq_runner.latvia_rides_reports_income_events.call(
        task_id='task_id1',
        kwargs={
            'park_id': 'park_id',
            'contractor_profile_id': 'contractor_profile_id',
            'entries': [
                {
                    'entry_id': 4106794910238,
                    'account': {
                        'entity_external_id': (
                            'taximeter_driver_id/'
                            '5a21425a940d437aa8b81ce676960f75/'
                            '66595d5fd4184db69898b9e9c3f92014'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                        'sub_account': 'payment/card',
                    },
                    'amount': '535.0000',
                    'doc_ref': 4380653760139,
                    'event_at': '2021-06-04T10:23:09+03:00',
                    'details': {
                        'alias_id': '060f118387ae36289f4826657e63a0d1',
                    },
                },
                {
                    'entry_id': 51431342141,
                    'account': {
                        'entity_external_id': (
                            'taximeter_driver_id/'
                            '5a21425a940d437aa8b81ce676960f75/'
                            '66595d5fd4184db69898b9e9c3f92014'
                        ),
                        'agreement_id': 'agreement',
                        'currency': 'RUB',
                        'sub_account': 'some_sub_account',
                    },
                    'amount': '100.0000',
                    'doc_ref': 23412513212543,
                    'event_at': '2021-06-04T10:23:09+03:00',
                },
                {
                    'entry_id': 4106794910239,
                    'account': {
                        'entity_external_id': (
                            'taximeter_driver_id/'
                            '5a21425a940d437aa8b81ce676960f75/'
                            '66595d5fd4184db69898b9e9c3f92014'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                        'sub_account': 'payment/card',
                    },
                    'amount': '535.0000',
                    'doc_ref': 4380653760139,
                    'event_at': '2021-06-04T10:23:09+03:00',
                    'details': {
                        'alias_id': 'noorder/060f118387ae36289f4826657e63a0d1',
                    },
                },
            ],
        },
    )
    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        'SELECT entry_id FROM latvia_rides_reports.order_income_events',
    )
    result = list(cursor)
    assert result == [(4106794910238,)]

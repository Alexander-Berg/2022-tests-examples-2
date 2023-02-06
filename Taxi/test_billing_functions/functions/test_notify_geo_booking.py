import datetime as dt

import pytest

from billing_functions.functions import notify_geo_booking


@pytest.mark.parametrize(
    'query, expected_sc_requests',
    [
        (
            notify_geo_booking.Query(
                notify_geo_booking.Driver('park_id', 'profile_id'),
                af_decision='pay',
                support_info_doc_id=1,
                date=dt.date(2022, 1, 2),
                rule_id='rule_id',
            ),
            [
                {
                    'date': '2022-01-02',
                    'doc_id': 1,
                    'drivers': [
                        {
                            'driver_profile_id': 'profile_id',
                            'park_id': 'park_id',
                        },
                    ],
                    'idempotency_key': '1',
                    'rule_id': 'rule_id',
                    'rule_type': 'geobooking',
                },
            ],
        ),
        (
            notify_geo_booking.Query(
                notify_geo_booking.Driver('park_id', 'profile_id'),
                af_decision='block',
                support_info_doc_id=1,
                date=dt.date(2022, 1, 2),
                rule_id='rule_id',
            ),
            [],
        ),
    ],
)
async def test_notify_geo_booking(
        stq3_context,
        mock_subvention_communications,
        *,
        query,
        expected_sc_requests,
):
    subv_comms = mock_subvention_communications()
    await notify_geo_booking.execute(
        stq3_context.clients.subvention_communications, query,
    )
    assert subv_comms.requests == expected_sc_requests

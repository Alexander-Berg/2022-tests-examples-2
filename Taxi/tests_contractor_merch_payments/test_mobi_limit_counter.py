import pytest


def get_billing_request(timestamp_from: str, timestamp_to: str):
    return {
        'accounts': [
            {
                'entity_external_id': (
                    'taximeter_park_id/19d6e2963154442e902db09aeb35dd6c'
                ),
                'agreement_id': 'taxi/yandex_marketing',
                'currency': 'RUB',
                'sub_account': 'merchant/remittance_payment_inc_vat',
            },
        ],
        'accrued_at': [timestamp_to, timestamp_from],
    }


@pytest.mark.parametrize(
    'response_data,status,successful,billing_request',
    [
        pytest.param(
            {
                'entries': [
                    {
                        'account': {
                            'account_id': 18170233,
                            'entity_external_id': 'corp/b2b_client_employee/5d99dcc91f0f705417117000',  # noqa: E501 (line too long)
                            'agreement_id': 'eats/rus/orders',
                            'currency': 'RUB',
                            'sub_account': 'payment/vat',
                        },
                        'balances': [
                            {
                                'accrued_at': '2019-09-01T00:00:00+03:00',
                                'balance': '250.12',
                                'last_created': '2019-09-01T00:00:00+03:00',
                                'last_entry_id': 100,
                            },
                            {
                                'accrued_at': '2019-09-01T00:00:00+03:00',
                                'balance': '0',
                                'last_created': '2019-09-01T00:00:00+03:00',
                                'last_entry_id': 100,
                            },
                        ],
                    },
                ],
            },
            200,
            True,
            get_billing_request(
                '2019-08-31T21:00:00+00:00', '2019-09-01T12:23:34+00:00',
            ),
            marks=pytest.mark.now('2019-09-01T12:23:34+00:00'),
        ),
        pytest.param(
            {
                'entries': [
                    {
                        'account': {
                            'account_id': 18170233,
                            'entity_external_id': 'corp/b2b_client_employee/5d99dcc91f0f705417117000',  # noqa: E501 (line too long)
                            'agreement_id': 'eats/rus/orders',
                            'currency': 'RUB',
                            'sub_account': 'payment/vat',
                        },
                        'balances': [
                            {
                                'accrued_at': '2019-09-01T00:00:00+03:00',
                                'balance': '250.12',
                                'last_created': '2019-09-01T00:00:00+03:00',
                                'last_entry_id': 100,
                            },
                            {
                                'accrued_at': '2019-09-01T00:00:00+03:00',
                                'balance': '0',
                                'last_created': '2019-09-01T00:00:00+03:00',
                                'last_entry_id': 100,
                            },
                        ],
                    },
                ],
            },
            200,
            True,
            get_billing_request(
                '2019-09-01T21:00:00+00:00', '2019-09-01T23:00:00+00:00',
            ),
            marks=pytest.mark.now('2019-09-02T02:00:00+03:00'),
        ),
        pytest.param(
            'Too many requests',
            429,
            False,
            get_billing_request(
                '2019-08-31T21:00:00+00:00', '2019-09-01T12:23:34+00:00',
            ),
            marks=pytest.mark.now('2019-09-01T12:23:34+00:00'),
        ),
        pytest.param(
            None,
            500,
            False,
            get_billing_request(
                '2019-08-31T21:00:00+00:00', '2019-09-01T12:23:34+00:00',
            ),
            marks=pytest.mark.now('2019-09-01T12:23:34+00:00'),
        ),
        pytest.param(
            {'entries': []},
            200,
            True,
            get_billing_request(
                '2019-08-31T21:00:00+00:00', '2019-09-01T12:23:34+00:00',
            ),
            marks=pytest.mark.now('2019-09-01T12:23:34+00:00'),
        ),
    ],
)
async def test_limit_counter(
        mockserver,
        testpoint,
        taxi_contractor_merch_payments,
        taxi_contractor_merch_payments_monitor,
        mocked_time,
        response_data,
        status,
        successful,
        billing_request,
):
    @testpoint('mobi-limit-counter-testpoint')
    def mobi_limit_counter_testpoint(arg):
        pass

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_billing_reports(request):
        assert request.json == billing_request
        if status == 200:
            return mockserver.make_response(status=status, json=response_data)
        return mockserver.make_response(status=status)

    async with taxi_contractor_merch_payments.spawn_task(
            'workers/mobi-limit-counter',
    ):
        if successful:
            result = await mobi_limit_counter_testpoint.wait_call()
            assert (
                await taxi_contractor_merch_payments_monitor.get_metric(
                    'mobi-limit-counter',
                )
            )['current_mobi_sum'] == 250.12
            assert result['arg'] == '250.120000'
            assert _mock_billing_reports.times_called == 1

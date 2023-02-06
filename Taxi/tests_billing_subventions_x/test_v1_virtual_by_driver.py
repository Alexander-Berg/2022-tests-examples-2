import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'test_data_json',
    [
        'driver_fix.json',
        'driver_fix_if_there_is_no_driver_fix_shift_ended.json',
        'driver_fix_if_two_modes.json',
        'driver_fix_if_two_rules.json',
        pytest.param(
            'driver_fix_with_increment.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_only_increment.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_if_now_older_shift_end.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_earlier_shift_start.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-17T00:01:00+03:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_honor_guarantee_on_order.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            'driver_fix_with_increment_if_two_shifts.json',
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_VBD_FETCH_INCREMENT=True,
                ),
                pytest.mark.now('2019-09-18T00:01:00+00:00'),
            ],
        ),
    ],
)
async def test(
        taxi_billing_subventions_x, mockserver, load_json, *, test_data_json,
):
    test_data = load_json(test_data_json)
    expected_balances_request = test_data['expected_balances_request']
    shift_ended_docs = test_data['shift_ended_docs']
    request = test_data['request']

    @mockserver.json_handler('/billing-docs/v3/docs/by_tag')
    def _v3_docs_by_tag(_):
        return mockserver.make_response(json={'docs': shift_ended_docs})

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _v2_balances_select(request):
        return mockserver.make_response(json=test_data['accounts'])

    @mockserver.json_handler('/billing-time-events/v1/balances')
    def _v1_balances(_):
        return mockserver.make_response(
            json={'balances': test_data['balances_increment']},
        )

    response = await taxi_billing_subventions_x.post(
        'v1/virtual_by_driver', request,
    )
    actual_balances_request = _v2_balances_select.next_call()['request'].json
    ordered_object.assert_eq(
        expected_balances_request,
        actual_balances_request,
        ['accrued_at', 'accounts'],
    )
    ordered_object.assert_eq(
        response.json(), test_data['expected_response'], ['subventions'],
    )

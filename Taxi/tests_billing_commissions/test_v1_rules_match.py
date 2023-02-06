# pylint: disable=too-many-lines
import pytest

from testsuite.utils import ordered_object


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_match.sql'],
)
@pytest.mark.parametrize(
    'test_name',
    [
        'has_absolute',
        # request has software_subscription
        'has_software_subscription',
        # request has software_subscription
        'has_software_subscription_with_tags',
        # request is too old for software_subscription
        'has_not_software_subscription',
        'expired_order',
        'cancel_order',
        # rule with many agreements (agent, hiring, etc)
        'order_normal_many_agreements',
        # cancel order: rule with many agreements
        'order_cancel_many_agreements',
        # expired order: rule with many agreements
        'order_expired_many_agreements',
        # commercial hiring with rent
        'normal_order_hiring_with_rent',
        # rule with many agreements, cancel billing_type
        'cancel_order_hiring_with_rent',
        # rule without hiring
        'normal_order_without_hiring',
        # rule spb (hiring+one core field)
        'normal_order_hiring_not_exists_tags_spb',
        # rule spb (hiring+one core field)
        'normal_order_hiring_exists_tags_spb',
        'normal_order_hiring_commercial_returned',
        'normal_order_hiring_commercial_returned_to_old',
        # check most specific algo
        'order_check_most_specific_new_algo_no_tag',
        'order_check_most_specific_algo_no_tag',
        'order_check_most_specific_algo_tag',
        'order_check_most_specific_new_algo_tag',
        # fine rules only for a new mode
        'normal_order_hiring_commercial_returned_with_fine',
        # zero-commission
        'order_commission_is_zero',
    ],
)
async def test_rules_match_simple(
        taxi_billing_commissions, test_name, load_json,
):
    response = await taxi_billing_commissions.post(
        'v1/rules/match/', json=load_json(f'request/{test_name}.json'),
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        load_json(f'expected/{test_name}.json'),
        ['agreements', 'group'],
    )


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_match.sql'],
)
async def test_rules_match_fails_horribly_for_duplicated_rules(
        taxi_billing_commissions, load_json,
):
    query = load_json('order_fail_with_same_rules.json')
    response = await taxi_billing_commissions.post(
        'v1/rules/match/', json=query,
    )
    assert response.status_code == 500


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_match.sql'],
)
@pytest.mark.parametrize(
    'reference_time,is_applicable',
    (
        ('2022-01-14T13:00:14+03:00', True),
        ('2022-01-14T13:00:14.000001+03:00', False),
    ),
)
async def test_rules_match_hiring_is_applicable(
        make_query,
        make_logged_request,
        load_json,
        reference_time,
        is_applicable,
):
    query = make_query(zone='magadan', reference_time=reference_time)
    response, _ = await make_logged_request(query)
    expected = load_json('hiring.json')
    expected['support_info']['hiring_applied_by_age'] = is_applicable
    assert _extract_agreements_by(response, group='hiring') == [expected]


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_match.sql'],
)
@pytest.mark.parametrize(
    'query_args,kind',
    (
        ({'zone': 'ukhta', 'tariff_class': 'uberx'}, 'acquiring'),
        ({'zone': 'igarka', 'tariff_class': 'econom'}, 'taximeter'),
    ),
)
async def test_rules_match_returns_agreements_for_non_zero_rules(
        make_query, make_logged_request, load_json, query_args, kind,
):
    query = make_query(**query_args)
    response, _ = await make_logged_request(query)
    actual = _extract_agreements_by(response, group=kind)
    assert actual == [load_json(f'{kind}.json')]


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_match.sql'],
)
@pytest.mark.parametrize(
    'query_args,kind',
    (
        ({'zone': 'ukhta', 'tariff_class': 'suv'}, 'acquiring'),
        ({'zone': 'igarka', 'tariff_class': 'suv'}, 'taximeter'),
    ),
)
async def test_rules_match_omits_agreements_for_zero_rules(
        make_query, make_logged_request, query_args, kind,
):
    query = make_query(**query_args)
    response, _ = await make_logged_request(query)
    actual = _extract_agreements_by(response, group=kind)
    assert actual == []


def _extract_agreements_by(response, **attrs):
    return [
        agreement
        for agreement in response['agreements']
        if all(agreement[key] == value for key, value in attrs.items())
    ]


@pytest.fixture(name='make_logged_request')
async def with_request(taxi_billing_commissions):
    async def _make_logged_request(query):
        async with taxi_billing_commissions.capture_logs() as logs:
            response = await taxi_billing_commissions.post(
                'v1/rules/match', json=query,
            )
        assert response.status_code == 200, response.json()
        return response.json(), logs

    return _make_logged_request


@pytest.fixture(name='make_query')
def _make_query():
    def _builder(
            *,
            reference_time='2022-01-14T13:00:14+03:00',
            tariff_class='business',
            zone='moscow',
    ):
        return {
            'billing_type': 'normal',
            'hiring': {
                'hired_at': '2021-07-18T13:00:14+03:00',
                'type': 'commercial',
            },
            'payment_type': 'card',
            'reference_time': reference_time,
            'tags': [],
            'tariff_class': tariff_class,
            'zone': zone,
        }

    return _builder

import datetime
import decimal

import pytest

from testsuite.utils import http

from fleet_rent.entities import rent
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import billing_reports


async def test_driver_total_no_affiliation(
        web_context: context_module.Context,
):
    br_service = web_context.external_access.billing_reports
    total = await br_service.get_total_driver_balance('RUB', [])
    assert total == 0


@pytest.mark.now('2020-08-01T00:00:00')
async def test_driver_total(
        web_context: context_module.Context,
        mock_billing_reports,
        aff_stub_factory,
        load_json,
):
    stub_data = load_json('test_driver_total.json')

    @mock_billing_reports('/v1/balances/select')
    async def _select(request: http.Request):
        assert request.json == stub_data['request']
        return stub_data['response']

    affiliations = [aff_stub_factory()]

    br_service = web_context.external_access.billing_reports
    total = await br_service.get_total_driver_balance('RUB', affiliations)

    assert total == decimal.Decimal(1400)


@pytest.mark.now('2020-08-01T00:00:00')
async def test_rent_and_total_by_park(
        web_context: context_module.Context,
        mock_billing_reports,
        aff_stub_factory,
        load_json,
):
    stub_data = load_json('test_rent_and_total_by_park.json')

    @mock_billing_reports('/v1/balances/select')
    async def _select(request: http.Request):
        assert request.json == stub_data['request']
        return stub_data['response']

    affiliations = [aff_stub_factory()]

    br_service = web_context.external_access.billing_reports
    by_park = await br_service.rent_and_internal_balance_by_park(
        'RUB', affiliations,
    )

    assert by_park == {'park_id': (decimal.Decimal(3000), decimal.Decimal(-1))}


@pytest.mark.now('2020-08-01T00:00:00')
async def test_driver_internal_park_balance(
        web_context: context_module.Context,
        mock_billing_reports,
        aff_stub_factory,
        load_json,
):
    stub_data = load_json('test_driver_internal_park_balance.json')

    @mock_billing_reports('/v1/balances/select')
    async def _select(request: http.Request):
        assert request.json == stub_data['request']
        return stub_data['response']

    affiliation = aff_stub_factory()

    br_service = web_context.external_access.billing_reports
    total = await br_service.driver_internal_park_balance('RUB', affiliation)

    assert total == decimal.Decimal(300)


@pytest.mark.parametrize(
    'use_billing_order_id_fix, json_file',
    [
        [False, 'test_driver_balance_by_rent.json'],
        [True, 'test_driver_balance_by_rent_fixed_order_id.json'],
    ],
)
@pytest.mark.now('2020-08-01T00:00:00')
async def test_driver_balance_by_rent(
        web_context: context_module.Context,
        mock_billing_reports,
        rent_stub_factory,
        aff_stub_factory,
        load_json,
        use_billing_order_id_fix,
        json_file,
):
    stub_data = load_json(json_file)

    @mock_billing_reports('/v1/balances/select')
    async def _select(request: http.Request):
        assert request.json == stub_data['request']
        return stub_data['response']

    affiliation = aff_stub_factory()
    rents = [
        rent_stub_factory(
            record_id='rent1',
            owner_serial_id=1,
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='rent2',
            owner_serial_id=2,
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
    ]

    br_service = web_context.external_access.billing_reports
    by_rent = await br_service.driver_balance_by_rent(
        'RUB', affiliation, rents,
    )

    assert [(b.rent.record_id, b.balance) for b in by_rent] == [
        ('rent1', decimal.Decimal(-100)),
        ('rent2', decimal.Decimal(-200)),
    ]


@pytest.mark.parametrize(
    'use_billing_order_id_fix, json_files',
    [
        [
            False,
            (
                'withdraw_balances_sums_req1.json',
                'withdraw_balances_sums_req2.json',
                'withdraw_balances_sums_resp1.json',
                'withdraw_balances_sums_resp2.json',
            ),
        ],
        [
            True,
            (
                'withdraw_balances_sums_req1_fixed_order_id.json',
                'withdraw_balances_sums_req2_fixed_order_id.json',
                'withdraw_balances_sums_resp1_fixed_order_id.json',
                'withdraw_balances_sums_resp2_fixed_order_id.json',
            ),
        ],
    ],
)
async def test_get_withdraw_balances_sums(
        web_context: context_module.Context,
        mock_billing_reports,
        rent_stub_factory,
        load_json,
        use_billing_order_id_fix,
        json_files,
):
    parse_time = datetime.datetime.fromisoformat
    times = (
        parse_time('2020-01-01T18:00+00:00'),
        parse_time('2020-01-02T18:00+00:00'),
        parse_time('2020-02-02T18:00+00:00'),
    )
    rents = (
        rent_stub_factory(
            record_id='r1_1',
            owner_park_id='pid1',
            owner_serial_id=11,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r1_2',
            owner_park_id='pid1',
            owner_serial_id=12,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r1_3',
            owner_park_id='pid1',
            owner_serial_id=13,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r1_4',
            owner_park_id='pid1',
            owner_serial_id=14,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r2_5',
            owner_park_id='pid2',
            owner_serial_id=25,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r2_6',
            owner_park_id='pid2',
            owner_serial_id=26,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r2_7',
            owner_park_id='pid2',
            owner_serial_id=27,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r2_8',
            owner_park_id='pid2',
            owner_serial_id=28,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r3_9',
            owner_park_id='pid3',
            owner_serial_id=30,
            driver_id='did3',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r3_10',
            owner_park_id='pid3',
            owner_serial_id=31,
            driver_id='did3',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r3_11',
            owner_park_id='pid3',
            owner_serial_id=32,
            driver_id='did3',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
    )

    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request: http.Request):
        first = load_json(json_files[0])
        second = load_json(json_files[1])
        assert (first == request.json) or (second == request.json)
        if request.json == first:
            return load_json(json_files[2])
        return load_json(json_files[3])

    result = (
        await web_context.external_access.billing_reports.get_withdraw_balances_sums(  # noqa: E501
            'RUB', rents, times,
        )
    )
    assert result == {
        ('pid1', parse_time('2020-01-01T18:00+00:00')): decimal.Decimal('0'),
        ('pid1', parse_time('2020-01-02T18:00+00:00')): decimal.Decimal('0'),
        ('pid1', parse_time('2020-02-02T18:00+00:00')): decimal.Decimal('200'),
        ('pid2', parse_time('2020-01-01T18:00+00:00')): decimal.Decimal('0'),
        ('pid2', parse_time('2020-01-02T18:00+00:00')): decimal.Decimal('100'),
        ('pid2', parse_time('2020-02-02T18:00+00:00')): decimal.Decimal('200'),
        ('pid3', parse_time('2020-01-01T18:00+00:00')): decimal.Decimal('0'),
        ('pid3', parse_time('2020-01-02T18:00+00:00')): decimal.Decimal('100'),
        ('pid3', parse_time('2020-02-02T18:00+00:00')): decimal.Decimal('200'),
    }


@pytest.mark.parametrize(
    'use_billing_order_id_fix, json_file_req, json_file_resp',
    [
        [False, 'all_balances_sums_req.json', 'all_balances_sums_resp.json'],
        [
            True,
            'all_balances_sums_req_fixed_order_id.json',
            'all_balances_sums_resp_fixed_order_id.json',
        ],
    ],
)
async def test_get_balances_by_rent(
        web_context: context_module.Context,
        mock_billing_reports,
        rent_stub_factory,
        load_json,
        use_billing_order_id_fix,
        json_file_req,
        json_file_resp,
):
    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request: http.Request):
        req = load_json(json_file_req)
        resp = load_json(json_file_resp)
        assert req == request.json
        return resp

    rents = [
        rent_stub_factory(
            record_id='r1_1',
            owner_park_id='pid1',
            owner_serial_id=11,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
            use_arbitrary_entries=False,
            affiliation_id='aff',
        ),
        rent_stub_factory(
            record_id='r1_2',
            owner_park_id='pid1',
            owner_serial_id=12,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
            affiliation_id='aff',
        ),
        rent_stub_factory(
            record_id='r1_3',
            owner_park_id='pid1',
            owner_serial_id=13,
            driver_id='did3',
            use_billing_order_id_fix=use_billing_order_id_fix,
            affiliation_id=None,
            use_arbitrary_entries=True,
        ),
    ]
    result = (
        await web_context.external_access.billing_reports.get_balances_by_rent(  # noqa: E501
            'RUB',
            rents,
            datetime.datetime.fromisoformat('2020-01-01T21:00:00+03:00'),
        )
    )
    expected = {
        'r1_1': billing_reports.BalancesBySubaccount(
            withhold=decimal.Decimal(400),
            withdraw=decimal.Decimal(200),
            cancel=decimal.Decimal(12),
        ),
        'r1_2': billing_reports.BalancesBySubaccount(
            withhold=decimal.Decimal(250),
            withdraw=decimal.Decimal(150),
            cancel=decimal.Decimal(0),
        ),
        'r1_3': billing_reports.BalancesBySubaccount(
            withhold=decimal.Decimal(700),
            withdraw=decimal.Decimal(0),
            cancel=decimal.Decimal(0),
        ),
    }
    assert result == expected


@pytest.mark.parametrize(
    'use_billing_order_id_fix, json_file',
    [
        [False, 'test_driver_expenses_in_park.json'],
        [True, 'test_driver_expenses_in_park_fixed_order_id.json'],
    ],
)
@pytest.mark.config(
    FLEET_RENT_BILLING_REPORTS_REQUESTS={'request_account_batch_size': 1},
)
async def test_driver_expenses_by_rent(
        web_context: context_module.Context,
        mock_billing_reports,
        rent_stub_factory,
        load_json,
        use_billing_order_id_fix,
        json_file,
):
    rents = (
        rent_stub_factory(
            record_id='rent1',
            owner_serial_id=1,
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='rent2',
            owner_serial_id=2,
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
    )

    select_stub_data = load_json(json_file)
    select_requests = select_stub_data['requests']
    select_responses = select_stub_data['responses']

    @mock_billing_reports('/v1/journal/select')
    async def _select(request: http.Request):
        stub_data_key = request.json['accounts'][0]['agreement_id']
        assert request.json == select_requests.pop(stub_data_key)
        return select_responses.pop(stub_data_key)

    service = web_context.external_access.billing_reports
    result = await service.driver_expenses_by_rent(
        currency='RUB',
        rents=rents,
        begin_time=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(2020, 1, 10, tzinfo=datetime.timezone.utc),
    )
    assert result == {
        rent.OwnerKey('park_id', 1): [
            billing_reports.Expense(
                decimal.Decimal(10),
                datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
            ),
        ],
        rent.OwnerKey('park_id', 2): [
            billing_reports.Expense(
                decimal.Decimal(20),
                datetime.datetime(2020, 1, 4, tzinfo=datetime.timezone.utc),
            ),
        ],
    }


@pytest.mark.parametrize(
    'use_billing_order_id_fix, req_json, resp_json, expected_result',
    [
        [
            False,
            'withhold_balances_req.json',
            'withhold_balances_resp.json',
            {
                'taxi/periodic_payments/11': decimal.Decimal(400),
                'taxi/periodic_payments/12': decimal.Decimal(250),
            },
        ],
        [
            True,
            'withhold_balances_req_fixed_order_id.json',
            'withhold_balances_resp_fixed_order_id.json',
            {
                'taxi/periodic_payments/pid1_11': decimal.Decimal(400),
                'taxi/periodic_payments/pid1_12': decimal.Decimal(250),
            },
        ],
    ],
)
async def test_get_balances_by_agreements(
        web_context: context_module.Context,
        mock_billing_reports,
        rent_stub_factory,
        load_json,
        use_billing_order_id_fix,
        req_json,
        resp_json,
        expected_result,
):
    req_loaded = load_json(req_json)
    resp_loaded = load_json(resp_json)

    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request: http.Request):
        assert request.json == req_loaded
        return resp_loaded

    rents = [
        rent_stub_factory(
            record_id='r1_1',
            owner_park_id='pid1',
            owner_serial_id=11,
            driver_id='did1',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
        rent_stub_factory(
            record_id='r1_2',
            owner_park_id='pid1',
            owner_serial_id=12,
            driver_id='did2',
            use_billing_order_id_fix=use_billing_order_id_fix,
        ),
    ]
    result = (
        # pylint: disable=W0212
        await web_context.external_access.billing_reports._get_balances_by_agreements(  # noqa: E501
            'RUB',
            rents,
            'withhold',
            datetime.datetime.fromisoformat('2020-01-01T21:00:00+03:00'),
        )
        # pylint: enable=W0212
    )
    assert result == expected_result


async def test_get_debt_lower_bound(
        web_context: context_module.Context, patch, rent_stub_factory,
):
    withholds = {'1': decimal.Decimal(100), '2': decimal.Decimal(100)}
    withdraws = {'1': decimal.Decimal(150)}
    cancels = {'1': decimal.Decimal(50), '2': decimal.Decimal(30)}

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService._get_balances_by_agreements',
    )
    async def _get_balances_by_agreements(currency, rents, sub_account, now):
        if sub_account == 'withhold':
            return withholds
        if sub_account == 'withdraw':
            return withdraws
        if sub_account == 'cancel':
            return cancels
        assert False

    rents = [
        rent_stub_factory(
            record_id='r1_1',
            owner_park_id='pid1',
            owner_serial_id=11,
            driver_id='did1',
            use_billing_order_id_fix=True,
        ),
        rent_stub_factory(
            record_id='r1_2',
            owner_park_id='pid1',
            owner_serial_id=12,
            driver_id='did2',
            use_billing_order_id_fix=True,
        ),
    ]
    result = (
        await web_context.external_access.billing_reports.get_debt_lower_bound(  # noqa: E501
            'RUB',
            rents,
            datetime.datetime.fromisoformat('2020-01-10T00:00:00+00:00'),
        )
    )
    assert (
        sorted(
            _get_balances_by_agreements.calls, key=lambda x: x['sub_account'],
        )
        == [
            {
                'currency': 'RUB',
                'rents': rents,
                'sub_account': 'cancel',
                'now': datetime.datetime.fromisoformat(
                    '2020-01-10T00:00:00+00:00',
                ),
            },
            {
                'currency': 'RUB',
                'rents': rents,
                'sub_account': 'withdraw',
                'now': datetime.datetime.fromisoformat(
                    '2020-01-10T00:00:00+00:00',
                ),
            },
            {
                'currency': 'RUB',
                'rents': rents,
                'sub_account': 'withhold',
                'now': datetime.datetime.fromisoformat(
                    '2020-01-09T00:00:00+00:00',
                ),
            },
        ]
    )
    assert result == decimal.Decimal(70)

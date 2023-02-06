import pytest

TEST_DOC_ID = 1234567890
TEST_DOC_ID_V2 = 1234567891
TEST_DOC_ID_AF = 1234567892


@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS={
        'orders': [
            {
                'start': '2021-04-20T00:00:00+03:00',
                'value': {'additional_profile_tags': ['some_tag']},
            },
        ],
    },
    BILLING_TLOG_SERVICE_IDS={
        'coupon/paid': 137,
        'commission/card': 128,
        'cash': 111,
    },
    DRIVER_PROMOCODES_MIN_COMMISSION={'__default__': 1},
    BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
        'by_zone': {
            '__default__': {
                'enabled': [{'since': '1991-06-18T07:15:00+03:00'}],
            },
        },
    },
    BILLING_FUNCTIONS_CREATE_COMMISSION_SUPPORT_INFO_DOC=True,
    PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00',
    BILLING_FUNCTIONS_NETTING_CONFIG={
        'rus': [
            {
                'since': '2022-04-30T21:00:00+03:00',
                'zones': ['*'],
                'kinds': [],
                'netting': 'none',
            },
        ],
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='old',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='both',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new',
            ),
        ),
    ],
)
@pytest.mark.now('2020-12-30T00:00:00.0Z')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='from_orfb',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE=dict(
                    mode='from_cost',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='fallback',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE=dict(
                    mode='fallback',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='from_calc',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE=dict(
                    mode='from_status',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
            ),
        ),
    ],
)
async def test_process_document(
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_replication,
        mock_billing_commissions,
        mock_billing_subventions_x,
        mock_driver_work_modes,
        reschedulable_stq_runner,
        mock_tlog,
        mock_limits,
        load_json,
):
    docs = do_mock_billing_docs(
        [
            load_json('taxi_order.json'),
            load_json('af_order_decision.json'),
            load_json('taxi_order_v2.json'),
        ],
    )
    do_mock_billing_accounts(
        existing_entities=load_json('entities.json'),
        existing_accounts=load_json('accounts.json'),
    )
    do_mock_billing_reports()
    mock_billing_commissions(
        agreements=load_json('commission_agreements.json'),
    )
    mock_driver_work_modes('dwm_responses.json')
    mock_replication(load_json('contracts.json'))
    mock_billing_subventions_x(**load_json('subvention_rules.json'))
    task = stq_runner.billing_functions_taxi_order
    await reschedulable_stq_runner(task, TEST_DOC_ID)
    await reschedulable_stq_runner(task, TEST_DOC_ID_AF)
    await reschedulable_stq_runner(task, TEST_DOC_ID_V2)

    assert docs.update_requests == load_json('updates.json')

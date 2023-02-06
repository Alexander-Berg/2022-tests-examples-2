import itertools

import pytest

from billing_fin_payouts.generated.cron import run_cron


def _cmp_upload_data(actual, expected):
    for actual_key, expected_key in itertools.zip_longest(
            sorted(actual), sorted(expected),
    ):
        assert actual_key == expected_key
        assert sorted(
            actual[actual_key], key=lambda x: x['export_id'],
        ) == sorted(expected[expected_key], key=lambda x: x['export_id'])


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_UPLOAD_ENABLED=True,
    BILLING_FIN_PAYOUTS_YT_UPLOAD_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'pg_read_size': 1000,
            'pg_overlap_offset': 0,
            'iterations': 1,
            'sleep_between_iterations': 0,
            'yt_upload_path': 'features/billing-fin-payouts/',
            'yt_upload_chunk_size': 1000,
            'yt_transaction_timeout_ms': 1000,
            'yt_auto_merge_output_action': 'merge',
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            ('billing_fin_payouts.crontasks.' 'upload_accruals_to_hahn'),
            'accruals_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['accruals.psql'],
                ),
            ],
        ),
        pytest.param(
            ('billing_fin_payouts.crontasks.' 'upload_accruals_to_arnold'),
            'accruals_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['accruals.psql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_payout_ready_batches_to_hahn'
            ),
            'payout_ready_batches_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['payout_ready_batches.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_payout_ready_batches_to_arnold'
            ),
            'payout_ready_batches_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['payout_ready_batches.sql'],
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.upload_export_batches_to_hahn',
            'export_batches_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['export_batches.sql'],
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.upload_export_batches_to_arnold',
            'export_batches_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['export_batches.sql'],
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.upload_export_batches_data_to_hahn',
            'export_batches_data_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['export_batches_data.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_export_batches_data_to_arnold'
            ),
            'export_batches_data_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['export_batches_data.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_expenses_to_arnold'
            ),
            'interface_expenses_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_expenses.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_expenses_to_hahn'
            ),
            'interface_expenses_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_expenses.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_payments_to_arnold'
            ),
            'interface_payments_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_payments.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_payments_to_hahn'
            ),
            'interface_payments_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_payments.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_revenues_to_hahn'
            ),
            'interface_revenues_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_revenues.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                'billing_fin_payouts.crontasks.'
                'upload_interface_revenues_to_hahn'
            ),
            'interface_revenues_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts', files=['interface_revenues.sql'],
                ),
            ],
        ),
    ],
)
async def test_upload_data_to_yt(
        cron_name, expected_data_json, load_json, patch, mock_yt_client,
):
    expected_data = load_json(expected_data_json)
    created_yt_clients = []

    # pylint: disable=unused-variable
    @patch('billing_fin_payouts.utils.yt.get_custom_yt_client')
    def get_custom_yt_client(context, cluster, config_overrides):
        result = mock_yt_client(cluster)
        nonlocal created_yt_clients
        created_yt_clients.append(result)
        return result

    await run_cron.main([cron_name, '-t', '0'])

    assert len(created_yt_clients) == 1

    yt_client = created_yt_clients[0]

    created_tables = [
        {'path': path, 'schema': schema}
        for path, schema in zip(
            yt_client.create_calls, yt_client.create_schemas,
        )
    ]

    assert created_tables == expected_data['expected_created_yt_tables']
    _cmp_upload_data(
        yt_client.write_table_calls, expected_data['expected_uploaded_data'],
    )
    assert yt_client.set_calls == expected_data['expected_set_calls']
    assert yt_client.get_calls == expected_data['expected_get_calls']
    assert yt_client.lock_calls == expected_data['expected_lock_calls']

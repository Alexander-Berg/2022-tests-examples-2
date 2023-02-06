import pytest

from replication.common.pytest import replication_rules
from . import conftest


@conftest.any_rules
@pytest.mark.nofilldb
def test_schemas(monkeypatch, replication_ctx):
    replication_rules.run_test_schemas(
        monkeypatch, replication_ctx, 'testsuite',
    )


@conftest.any_rules
@pytest.mark.nofilldb
def test_rules(replication_ctx):
    replication_rules.run_test_rules(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_deprecated_aiopg_rules(replication_ctx):
    replication_rules.run_test_deprecated_aiopg_rules(
        replication_ctx,
        aiopg_rules={
            'taximeter_orders',
            'taximeter_orders_raw',
            'taximeter_payments',
            'taximeter_feedbacks',
            'drive_analytics_drive_user_data_history',
            'drive_analytics_user_devices_history',
            'drive_analytics_drive_car_info_history',
            'drive_analytics_billing_account_history',
            'drive_analytics_billing_accnt_dscrptn_hstr',
            'market_delivery_tracker_checkpoint',
        },
    )


@conftest.dmp_rules_only
@pytest.mark.nofilldb
def test_check_source_aliases(replication_ctx):
    replication_rules.run_test_check_source_aliases(
        replication_ctx,
        exclude_rule_names={  # TODO: fix sources and remove it
            'dm_storage_udids',
            'market_mbo_mdm_reference_item',  # MARKETDWH-120
            'market_mbo_mdm_ssku_silver_param_value',  # MARKETDWH-120
        },
    )


@conftest.dmp_rules_only
@pytest.mark.nofilldb
def test_no_secdist_in_rules(replication_ctx):
    replication_rules.run_test_no_secdist_in_rules(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_yt_mappers_and_schemas(replication_ctx):
    replication_rules.run_test_yt_mappers_and_schemas(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_yt_columns(replication_ctx):
    replication_rules.run_test_yt_columns(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_yt_target_aliases(replication_ctx):
    replication_rules.run_test_yt_target_aliases(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_pd_only_for_api_source(replication_ctx):
    replication_rules.run_test_pd_only_for_api_source(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_last_replicated_ignore_shards(replication_ctx):
    replication_rules.run_test_last_replicated_ignore_shards(replication_ctx)


@conftest.any_rules
@pytest.mark.nofilldb
def test_validate_plugin_parameters(replication_ctx):
    replication_rules.run_test_validate_plugin_parameters(replication_ctx)


@conftest.dmp_rules_only
@pytest.mark.nofilldb
def test_no_tables_in_pg(replication_ctx, static_dir):
    replication_rules.run_test_no_tables_in_pg(replication_ctx)

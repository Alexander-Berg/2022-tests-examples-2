# flake8: noqa
import os
import subprocess

import pytest

ROOT = os.path.dirname(__file__)

# List of files with ClientSession() ctr
# DO NOT ADD ANYTHING TO THIS LIST!
WHITELIST_FILES = [
    'taxi/clients/yt.py',
    'taxi/maintenance/helpers.py',
    'taxi/maintenance/run.py',
    'taxi/opentracing/ext/web_app.py',
    'taxi/opentracing/ext/http_client.py',
    'taxi/pytest_plugins/blacksuite/testpoint.py',
    'taxi/util/client_session.py',
    'taxi/util/monrun/cron_check.py',
    'taxi/web_app.py',
    'libraries/http-proxy/http_proxy/pytest_plugin.py',
    'libraries/taxi-ml/taxi_ml/ml/projects/projects/supportai/datasets_translations/translate.py',
    'libraries/tracemalloc-api/tracemalloc_api/client.py',
    'services/abt/abt/logic/validation.py',
    'services/atlas-etl/atlas_etl/processes/weather/weather_loader.py',
    'services/chatterbox-admin/chatterbox_admin/stq/generate_preview.py',
    'services/contractor-permits/contractor_permits/integration/atd_client.py',
    'services/contractor-permits/contractor_permits/integration/csdd_client.py',
    'services/crm-admin/crm_admin/utils/spark_submit.py',
    'services/crm-efficiency/crm_efficiency/utils/spark_submit.py',
    'services/driver-event-detector/driver_event_detector/crontasks/detect_driver_events.py',
    'services/driver-event-detector/driver_event_detector/crontasks/predict_offer_prices.py',
    'services/driver-event-detector/driver_event_detector/internal/gorky/fetcher.py',
    'services/eda-region-points/eda_region_points/proactive_support/notifications.py',
    'services/eda-region-points/eda_region_points/common/telegram.py',
    'services/eda-region-points/eda_region_points/floor_delivery/notifications.py',
    'services/eventus-orchestrator/eventus_orchestrator/crontasks/remove_deleted_host_infos.py',
    'services/example-service/example_service/api/use_aiohttp.py',
    'services/example-service/example_service/generated/service/experiments3/plugin.py',
    'services/abt/abt/generated/service/session/plugin.py',
    'services/example-service/test_example_service/web/test_validation_errors.py',
    'services/grocery-tasks/grocery_tasks/autoorder/client/clickhouse.py',
    'services/grocery-tasks/grocery_tasks/autoorder/client/http.py',
    'services/grocery-tasks/grocery_tasks/crontasks/autoprolong.py',
    'services/hiring-st/scripts/client.py',
    'services/parks-certifications-worker/parks_certifications_worker/crontasks/certified_parks_upload.py',
    'services/payments-eda/scripts/run_payment_flow.py',
    'services/promotions/promotions/logic/admin/autoresizers/base_autoresizer.py',
    'services/grocery-tasks/grocery_tasks/crontasks/google_docs_replication.py',
    'services/quality-control/quality_control/cron_run.py',
    'services/quality-control/quality_control/web_app.py',
    'services/quality-control/test_quality_control/stress/init.py',
    'services/replication/replication/common/client_infra.py',
    'services/replication/replication/common/lock_util.py',
    'services/replication/replication/dependencies/shared_deps.py',
    'services/rida/rida/api/v1_launch_post.py',
    'services/rida/rida/logic/notifications/firebase/client.py',
    'services/scripts/scripts/app.py',
    'services/scripts/test_scripts/conftest.py',
    'services/selfemployed/test_selfemployed/test_parks.py',
    'services/stq-agent-py3/stq_agent_py3/tools/stq_config.py',
    'services/taxi-antifraud/taxi_antifraud/clients/fssp.py',
    'services/taxi-antifraud/taxi_antifraud/scripts/ml.py',
    'services/taxi-api-admin/taxi_api_admin/cron_run.py',
    'services/taxi-api-admin/taxi_api_admin/app.py',
    'services/taxi-approvals/taxi_approvals/cron_run.py',
    'services/taxi-approvals/taxi_approvals/app.py',
    'services/taxi-billing-accounts/local/stress-testing/load.py',
    'services/taxi-billing-accounts/local/external_test.py',
    'services/taxi-billing-accounts/taxi_billing_accounts/audit/app.py',
    'services/taxi-billing-accounts/taxi_billing_accounts/monrun/app.py',
    'services/taxi-billing-accounts/taxi_billing_accounts/replication/app.py',
    'services/taxi-billing-accounts/taxi_billing_accounts/stq/_context.py',
    'services/taxi-billing-accounts/taxi_billing_accounts/app.py',
    'services/taxi-billing-audit/taxi_billing_audit/internal/cron_frequency.py',
    'services/taxi-billing-buffer-proxy/taxi_billing_buffer_proxy/app.py',
    'services/taxi-billing-buffer-proxy/taxi_billing_buffer_proxy/stq_context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/driver_mode_subscription/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/limits/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/main/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/manual_transactions/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/payment_requests/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/taximeter/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/stq/tlog/context.py',
    'services/taxi-billing-calculators/taxi_billing_calculators/app.py',
    'services/taxi-billing-docs/taxi_billing_docs/cron/app.py',
    'services/taxi-billing-docs/taxi_billing_docs/monrun/app.py',
    'services/taxi-billing-docs/taxi_billing_docs/stq/context.py',
    'services/taxi-billing-docs/taxi_billing_docs/app.py',
    'services/taxi-billing-orders/taxi_billing_orders/stq/internal/context_data.py',
    'services/taxi-billing-orders/taxi_billing_orders/app.py',
    'services/taxi-billing-replication/taxi_billing_replication/__init__.py',
    'services/taxi-billing-reports/taxi_billing_reports/app.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/cron/app.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/main.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/personal_uploads/stq_task.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/process_doc/_context.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/rule_notifier/context.py',
    'services/taxi-billing-subventions/taxi_billing_subventions/subvention_notifier/context.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_payouts_driver_fix_b2b.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_rule_notifier/test_stq_task.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_subvention_notifier.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_services_antifraud.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_single_ontop_subventions.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_single_ride_subventions.py',
    'services/taxi-billing-subventions/test_taxi_billing_subventions/test_process_doc.py',
    'services/taxi-plotva-ml/taxi_plotva_ml/api/dkvu_v1.py',
    'services/taxi-strongbox/test_taxi_strongbox/components/test_clownductor_session.py',
    'services/taxi-strongbox/test_taxi_strongbox/components/test_conductor_session.py',
    'services/taxi-strongbox/test_taxi_strongbox/components/test_vault_session.py',
    'services/discounts-operation-calculations/discounts_operation_calculations/utils/spark_submit.py',
    'services/grocery-tasks/grocery_tasks/utils/jns_client.py',
    'services/grocery-salaries/grocery_salaries/utils/jns_helpers.py',
    'services/grocery-salaries/grocery_salaries/monitor_crons.py',
    'services/taxi-tracing/taxi_tracing/api/test.py',
    'services/vgw-api-tasks/vgw_api_tasks/vgw_task.py',
]


@pytest.mark.skip
def test_no_new_client_sessions():
    cmdline = (
        'grep --include \'*.py\' -r \'\\bClientSession(\\|\\bget_client_session(\' -l '
        'taxi services libraries'
    )
    paths = []
    output = subprocess.check_output([cmdline], shell=True)
    for line in output.decode('utf-8').split('\n'):
        if not line:
            continue

        if '/generated/' in line:
            continue
        if '/debian/' in line:
            continue

        if line in WHITELIST_FILES:
            continue

        paths.append(line)

    assert not paths, (
        'A new file with ClientSession creation is forbidden. '
        f'Use HTTPClient component instead. The files: {paths}'
    )

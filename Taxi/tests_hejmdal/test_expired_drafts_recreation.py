import pytest


@pytest.mark.now('2021-11-30T01:00:00Z')
@pytest.mark.config(
    HEJMDAL_DIGESTS_PREPARER_SETTINGS={
        'enabled': True,
        'period_min': 3,
        'get_digests_command_control': {
            'network_timeout_ms': 300,
            'statement_timeout_ms': 300,
        },
        'get_incidents_command_control': {
            'network_timeout_ms': 120000,
            'statement_timeout_ms': 120000,
        },
        'personalized_digest': {
            'cutres_drafts': {
                'is_email_notification_enabled': True,
                'is_enabled': True,
                'is_juggler_notification_enabled': True,
                'services_blacklist': [],
                'services_whitelist': [],
            },
            'overload_ok_bound': 10,
            'underload_ok_bound': 90,
        },
        'update_last_broadcast_command_control': {
            'network_timeout_ms': 300,
            'statement_timeout_ms': 300,
        },
    },
)
async def test_expired_drafts_recreation(taxi_hejmdal, pgsql, mockserver):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    @mockserver.json_handler('/mailing-lists/apiv3/lists/subscribers')
    def _mock_mailing_lists(request, *args, **kwargs):
        return {
            'result': {
                'hejmdal-personalized-digest-subscription@yandex-team.ru': {
                    'is_open': True,
                    'is_internal': True,
                    'subscribers': [
                        {
                            'email': 'atsinin@yandex-team.ru',
                            'imap': False,
                            'inbox': False,
                            'login': 'atsinin',
                        },
                    ],
                },
            },
        }

    @mockserver.json_handler('/taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts(request, *args, **kwargs):
        if request.query['id'] == '123456':
            return {'id': 123456, 'version': 1, 'status': 'expired'}
        return {}

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    def _mock_clown_service_values(request, *args, **kwargs):
        return {
            'subsystems': [
                {
                    'subsystem_name': 'nanny',
                    'parameters': [{'name': 'cpu', 'value': 10}],
                },
            ],
        }

    @mockserver.json_handler('/clownductor/v1/parameters/remote_values/')
    def _mock_clown_remote_values(request, *args, **kwargs):
        return {
            'subsystems': [
                {
                    'subsystem_name': 'nanny',
                    'parameters': [{'name': 'cpu', 'value': 10}],
                },
            ],
        }

    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _mock_approvals_drafts_create(request, *args, **kwargs):
        return {'id': 123457, 'version': 0, 'status': 'need_approval'}

    await taxi_hejmdal.run_task('distlock/digest_preparer')

    cursor = pgsql['hejmdal'].cursor()
    query = """
    SELECT id, branch_id, approve_status, apply_status, approve_status_age,
        apply_status_age
     FROM change_resource_drafts;
    """
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0] == (123457, 1, 'no_decision', 'not_started', 0, 0)

import pytest

from archiving import loaders

_TEST_RULE_NAME = 'test_postgres'

_RULE_PERIOD = 3600  # presuming test yaml won't change
_RULE_SLEEP_DELAY = None
_RULE_TTL_DURATION = 3600


@pytest.mark.parametrize(
    'admin_period, admin_sleep_delay, ' 'admin_ttl_duration',
    [(123, 4, 12), (2, 3, 4), (34, 2, None), (3, 1, 3)],
)
async def test_admin_settings(
        cron_context,
        monkeypatch,
        mock_archiving_admin,
        mockserver,
        admin_period,
        admin_sleep_delay,
        admin_ttl_duration,
        patch_test_env,
):
    @mock_archiving_admin('/admin/v1/rules/retrieve')
    async def rules_retrieve(request):  # pylint: disable=unused-variable
        mocked_result = {
            'rules': [
                {
                    'group_name': 'test_postgres',
                    'rule_name': 'test_postgres',
                    'source_type': 'postgres',
                    'period': admin_period,
                    'sleep_delay': admin_sleep_delay,
                    'enabled': True,
                    'last_run': [],
                    'ttl_duration': admin_ttl_duration,
                },
            ],
        }
        return mockserver.make_response(json=mocked_result)

    rule = await loaders.load_rule(
        cron_context.clients.archiving_admin,
        _TEST_RULE_NAME,
        cron_context.config,
    )
    assert rule.period == (admin_period or _RULE_PERIOD)
    # pylint: disable=protected-access
    assert rule.sleep_delay == admin_sleep_delay
    if admin_ttl_duration is not None:
        assert rule.ttl_info.duration == admin_ttl_duration
    else:
        assert rule.ttl_info.duration == _RULE_TTL_DURATION

import json

import pytest

_NOW = '2019-01-01T09:00:00+00:00'


@pytest.fixture
def cached_json_tests(request, load_json):
    json_cache = request.config.cache.get('archiving-admin/sync_status', None)
    if json_cache is None:
        json_cache = load_json('sync_statuses_values.json')
        request.config.cache.set('archiving-admin/sync_status', json_cache)
    return json_cache


@pytest.mark.parametrize(
    'test_id, expected_status',
    [
        ('non-existent-rule', 410),
        ('test-empty-last-run', 200),
        ('test-non-empty-last-run', 200),
        ('test-full-last-run', 200),
    ],
)
@pytest.mark.pgsql('archiving_admin', files=['pg_test_archiving_rules.sql'])
@pytest.mark.now(_NOW)
async def test_sync_status_handle(
        web_app,
        web_app_client,
        test_id,
        expected_status,
        load_json,
        cached_json_tests,  # pylint: disable=redefined-outer-name
        monkeypatch,
):
    test_data = cached_json_tests[test_id]
    test_input = test_data['input']
    rule_name = test_input.pop('rule_name')

    if expected_status == 200:
        await web_app_client.post(
            '/admin/v1/rules/change',
            json={'rules': [{'rule_name': rule_name, 'action': 'enable'}]},
        )

    result = await web_app_client.post(
        f'/archiving/v1/rule/sync_status/{rule_name}', json=test_input,
    )
    assert expected_status == result.status
    expected_rule_last_run = test_data['expected_rule_last_run']
    rule_last_run_query = (
        'SELECT last_run FROM archiving.last_run as rules  WHERE rule_name=$1'
    )
    archiving_db = web_app['context'].pg.archiving_rules
    result = await archiving_db.fetchrow(rule_last_run_query, rule_name)
    if expected_rule_last_run is None:
        assert result is None
        return
    last_run_db = json.loads(result['last_run'])
    assert last_run_db == expected_rule_last_run

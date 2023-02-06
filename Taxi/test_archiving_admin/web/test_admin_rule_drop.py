import pytest


@pytest.mark.pgsql('archiving_admin', files=['pg_test_archiving_rules.sql'])
@pytest.mark.parametrize(
    'rule_name,expected_status',
    [('test_foo_1', 200), ('not_found', 404), ('test_foo_2', 200)],
)
async def test_drop(web_app, web_app_client, rule_name, expected_status):
    response = await web_app_client.post(f'/admin/v1/rules/drop/{rule_name}')
    assert response.status == expected_status

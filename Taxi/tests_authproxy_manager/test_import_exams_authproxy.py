import pytest


@pytest.mark.config(
    AUTHPROXY_MANAGER_IMPORT_PROXY_LIST=['exams-authproxy'],
    AUTHPROXY_MANAGER_DEFAULT_DEV_TEAM_BY_PROXY={
        'exams-authproxy': 'dev_team',
    },
)
async def test_import_is_not_implemented(authproxy_manager):
    proxy = 'exams-authproxy'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 400
    assert response.json()['code'] == 'IMPORT_IS_NOT_IMPLEMENTED'
    assert (
        response.json()['message']
        == f'Rule importing is not implemented for "{proxy}"'
    )

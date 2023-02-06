# pylint: disable=redefined-outer-name
import pytest

from taxi import config
from taxi.billing import auth

SERVICE_GROUPS = {
    'full_access_service': ['full_access_group'],
    'restricted_access_service': [
        'restricted_access_group',
        'second_restricted_access_group',
    ],
}
GROUPS_RULES = {
    'full_access_group': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': '%'}],
    },
    'restricted_access_group': {
        'accounts': [{'kind': 'test%', 'agreement': 'test%'}],
        'documents': [{'external_obj_id': 'test%'}],
        'tags': [{'tag': 'test%'}],
    },
    'second_restricted_access_group': {
        'accounts': [{'kind': 'b%', 'agreement': 'b%'}],
        'documents': [{'external_obj_id': 'b%'}],
        'tags': [{'tag': 'b%'}],
    },
}


@pytest.fixture
def config_mock():
    class Config(config.Config):
        BILLING_AUTH_SERVICE_GROUPS = SERVICE_GROUPS
        BILLING_AUTH_GROUPS_RULES = GROUPS_RULES

    return Config()


@pytest.mark.parametrize(
    'tvm_service, kind, agreement, predicted_result',
    [
        ('full_access_service', 'test_case', 'test_case', True),
        ('full_access_service', '', '', True),
        ('restricted_access_service', 'test_case', 'test_case', True),
        ('restricted_access_service', 'test', 'test', True),
        ('restricted_access_service', 'b', 'b', True),
        ('restricted_access_service', 'a', 'a', False),
        ('restricted_access_service', '', '', False),
    ],
)
async def test_auth_accounts_check(
        tvm_service,
        kind,
        agreement,
        predicted_result,
        collected_logs_with_link,
        config_mock,
):
    result = auth.check_account_rules(
        config_mock, tvm_service, kind, agreement, collected_logs_with_link,
    )
    assert result == predicted_result


@pytest.mark.parametrize(
    'tvm_service, external_obj_id, predicted_result',
    [
        ('full_access_service', 'test_case', True),
        ('full_access_service', '', True),
        ('restricted_access_service', 'test_case', True),
        ('restricted_access_service', 'test', True),
        ('restricted_access_service', 'b', True),
        ('restricted_access_service', 'a', False),
        ('restricted_access_service', '', False),
    ],
)
async def test_auth_document_check(
        tvm_service,
        external_obj_id,
        predicted_result,
        collected_logs_with_link,
        config_mock,
):
    result = auth.check_document_rules(
        config_mock, tvm_service, external_obj_id, collected_logs_with_link,
    )
    assert result == predicted_result


@pytest.mark.parametrize(
    'tvm_service, tag, predicted_result',
    [
        ('full_access_service', 'test_case', True),
        ('full_access_service', '', True),
        ('restricted_access_service', 'test_case', True),
        ('restricted_access_service', 'test', True),
        ('restricted_access_service', 'b', True),
        ('restricted_access_service', 'a', False),
        ('restricted_access_service', '', False),
    ],
)
async def test_auth_tags_check(
        tvm_service,
        tag,
        predicted_result,
        collected_logs_with_link,
        config_mock,
):
    result = auth.check_tag_rules(
        config_mock, tvm_service, tag, collected_logs_with_link,
    )
    assert result == predicted_result


@pytest.mark.parametrize(
    'data, rule, predicted_result',
    [
        ('', '', True),
        ('', '%', True),
        ('abc', 'abc', True),
        ('abcdef', 'abc%', True),
        ('abcdef', '%bc%', True),
        ('abcdefgh', 'a%d%f%', True),
        ('test', 'abc', False),
        ('', 'abc', False),
        ('test', 'abc%', False),
        ('', 'abc%', False),
        ('', '%bc%', False),
        ('', 'a%d%f%', False),
        ('testab', '%bc%', False),
        ('adtest', 'a%d%f%', False),
    ],
)
async def test_main_validator(data, rule, predicted_result):
    result = auth.rule_validator(data, rule)
    assert result == predicted_result

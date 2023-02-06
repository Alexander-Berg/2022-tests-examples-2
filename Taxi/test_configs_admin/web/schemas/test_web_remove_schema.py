import dataclasses
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from test_configs_admin.db_operations import common


@dataclasses.dataclass
class Exists:
    main: bool = False
    service: bool = False
    stage: bool = False
    schema: bool = True


class Params(NamedTuple):
    name: str
    expected_check: Dict
    expected_apply: Optional[Dict] = None
    params: Optional[Dict[str, Any]] = None
    before_exists: Optional[Exists] = None
    after_exists: Optional[Exists] = None
    is_failed: bool = False


@pytest.mark.parametrize(
    common.get_args(Params),
    [
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                before_exists=Exists(),
                after_exists=Exists(schema=False),
                expected_check={
                    'change_doc_id': 'configs_admin_remove_schema_TEST_CONFIG',
                    'data': {'name': 'TEST_CONFIG', 'version': 1},
                },
                expected_apply={},
            ),
            id='success_web_remove_schema',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                before_exists=Exists(),
                after_exists=Exists(),
                params={'version': 2},
                expected_check={
                    'change_doc_id': 'configs_admin_remove_schema_TEST_CONFIG',
                    'data': {'name': 'TEST_CONFIG', 'version': 2},
                },
                expected_apply={
                    'code': 'INCORRECT_VERSION',
                    'message': (
                        'Incorrect version `2` for change schema `TEST_CONFIG`'
                    ),
                },
                is_failed=True,
            ),
            id='fail_web_remove_schema_if_version_is_incorrect',
        ),
        pytest.param(
            *Params(
                name='NON_EXISTED_SCHEMA',
                before_exists=Exists(schema=False),
                after_exists=Exists(schema=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_schema_NON_EXISTED_SCHEMA'
                    ),
                    'data': {'name': 'NON_EXISTED_SCHEMA', 'version': 1},
                },
                expected_apply={
                    'code': 'SCHEMA_NOT_FOUND',
                    'message': 'Schema `NON_EXISTED_SCHEMA` not found',
                },
                is_failed=True,
            ),
            id='fail_web_remove_if_schema_not_found',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_MAIN',
                before_exists=Exists(main=True),
                after_exists=Exists(main=True),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_schema_TEST_CONFIG_WITH_MAIN'
                    ),
                    'data': {'name': 'TEST_CONFIG_WITH_MAIN', 'version': 1},
                },
                expected_apply={
                    'code': 'SCHEMA_CANNOT_BE_DELETED',
                    'message': (
                        'Schema `TEST_CONFIG_WITH_MAIN` cannot be deleted. '
                        'Reason `In [\'main\'] scopes values exists`'
                    ),
                },
                is_failed=True,
            ),
            id='fail_web_remove_schema_if_main_value_exists',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_SERVICE',
                before_exists=Exists(service=True),
                after_exists=Exists(service=True),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_schema_TEST_CONFIG_WITH_SERVICE'
                    ),
                    'data': {'name': 'TEST_CONFIG_WITH_SERVICE', 'version': 1},
                },
                expected_apply={
                    'code': 'SCHEMA_CANNOT_BE_DELETED',
                    'message': (
                        'Schema `TEST_CONFIG_WITH_SERVICE` cannot be deleted. '
                        'Reason `In [\'services\'] scopes values exists`'
                    ),
                },
                is_failed=True,
            ),
            id='fail_web_remove_schema_if_service_value_exists',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_VALUES',
                params={'clean_all': True, 'version': 10},
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(schema=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_schema_TEST_CONFIG_WITH_VALUES'
                    ),
                    'data': {
                        'name': 'TEST_CONFIG_WITH_VALUES',
                        'clean_all': True,
                        'version': 10,
                    },
                },
                expected_apply={},
            ),
            id='successfull_web_remove_schema_with_all_values',
        ),
    ],
)
async def test_case(
        web_context,
        web_app_client,
        name,
        expected_check,
        expected_apply,
        params,
        before_exists,
        after_exists,
        is_failed,
):
    # check values before
    values_before = await common.get_values(
        web_context,
        name,
        service_name=common.ANY_VALUE,
        stage_name=common.ANY_VALUE,
    )
    for key, value_exists in dataclasses.asdict(before_exists).items():
        if value_exists:
            assert (
                values_before[key] is not None
            ), f'must be not None {key}:{values_before[key]}'
        else:
            assert (
                values_before[key] is None
            ), f'must be None {key}:{values_before[key]}'

    # run
    arguments: Dict[str, Any] = {'name': name, 'version': 1}
    if params:
        arguments.update(params)
    result = await web_app_client.post(
        '/v1/schemas/remove/drafts/check/', json=arguments,
    )
    check_body = await result.json()
    assert check_body == expected_check
    if 'change_doc_id' not in check_body:
        return
    result = await web_app_client.delete(
        '/v1/schemas/remove/drafts/apply/', json=check_body['data'],
    )
    apply_body = await result.json()
    assert apply_body == expected_apply
    if is_failed and result.status == 200:
        pytest.fail('Apply status is 200, wait other status')

    # check values after
    values_after = await common.get_values(
        web_context,
        name,
        service_name=common.ANY_VALUE,
        stage_name=common.ANY_VALUE,
    )
    for key, value_exists in dataclasses.asdict(after_exists).items():
        if value_exists:
            assert values_after[key] is not None, key
        else:
            assert values_after[key] is None, key

import dataclasses
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from test_configs_admin.db_operations import common


@dataclasses.dataclass
class Exists:
    main: bool = True
    service: bool = False
    stage: bool = False


class Params(NamedTuple):
    name: str
    service_name: Optional[str] = None
    stage_name: Optional[str] = None
    version: Optional[int] = None
    params: Optional[Dict] = None
    before_exists: Optional[Exists] = None
    after_exists: Optional[Exists] = None
    expected_check: Optional[Dict] = None
    expected_apply: Optional[Dict] = None
    is_failed: bool = False


@pytest.mark.parametrize(
    common.get_args(Params),
    [
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                before_exists=Exists(),
                after_exists=Exists(main=False),
                expected_check={
                    'change_doc_id': 'configs_admin_remove_value_TEST_CONFIG',
                    'data': {'name': 'TEST_CONFIG'},
                },
                expected_apply={},
            ),
            id='success_web_remove_main_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                version=5,
                before_exists=Exists(),
                after_exists=Exists(main=False),
                expected_check={
                    'change_doc_id': 'configs_admin_remove_value_TEST_CONFIG',
                    'data': {'name': 'TEST_CONFIG', 'version': 5},
                },
                expected_apply={},
            ),
            id='success_web_remove_main_value_with_version',
        ),
        pytest.param(
            *Params(
                name='UNKNOUN_CONFIG',
                before_exists=Exists(main=False),
                after_exists=Exists(main=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_UNKNOUN_CONFIG'
                    ),
                    'data': {'name': 'UNKNOUN_CONFIG'},
                },
                expected_apply={
                    'code': 'CONFIG_NOT_FOUND',
                    'message': 'Config `UNKNOUN_CONFIG` not found',
                    'details': {'errors': ['Main value not found']},
                },
            ),
            id='fail_web_remove_non_existed_main_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                service_name='abt',
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(main=True, service=False),
                expected_check={
                    'change_doc_id': 'configs_admin_remove_value_TEST_CONFIG',
                    'data': {'name': 'TEST_CONFIG', 'service_name': 'abt'},
                },
                expected_apply={},
            ),
            id='success_web_remove_service_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                service_name='unknown_service',
                expected_check={
                    'change_doc_id': 'configs_admin_remove_value_TEST_CONFIG',
                    'data': {
                        'name': 'TEST_CONFIG',
                        'service_name': 'unknown_service',
                    },
                },
                expected_apply={
                    'code': 'CONFIG_NOT_FOUND',
                    'message': 'Config `TEST_CONFIG` not found',
                    'details': {
                        'errors': [
                            'Service value for '
                            '`unknown_service` service not found',
                        ],
                    },
                },
                before_exists=Exists(main=True, service=False),
                after_exists=Exists(main=True, service=False),
            ),
            id='fail_web_remove_non_existed_service_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_STAGE',
                stage_name='unstable',
                before_exists=Exists(main=False, stage=True),
                after_exists=Exists(main=False, stage=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_TEST_CONFIG_STAGE'
                    ),
                    'data': {
                        'name': 'TEST_CONFIG_STAGE',
                        'stage_name': 'unstable',
                    },
                },
                expected_apply={},
            ),
            id='success_web_remove_stage_value',
        ),
        pytest.param(
            *Params(
                name='UNKNOUN_CONFIG',
                stage_name='unknown_stage',
                before_exists=Exists(main=False, stage=False),
                after_exists=Exists(main=False, stage=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_UNKNOUN_CONFIG'
                    ),
                    'data': {
                        'name': 'UNKNOUN_CONFIG',
                        'stage_name': 'unknown_stage',
                    },
                },
                expected_apply={
                    'code': 'CONFIG_NOT_FOUND',
                    'message': 'Config `UNKNOUN_CONFIG` not found',
                    'details': {
                        'errors': [
                            'Stage value for `unknown_stage` stage not found',
                        ],
                    },
                },
            ),
            id='fail_web_remove_non_existed_stage_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_ALL',
                params={'remove_mode': 'all'},
                service_name=common.ANY_VALUE,
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(main=False, service=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_TEST_CONFIG_WITH_ALL'
                    ),
                    'data': {
                        'name': 'TEST_CONFIG_WITH_ALL',
                        'remove_mode': 'all',
                    },
                },
                expected_apply={},
            ),
            id='success_web_remove_all_values',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_ALL',
                params={'remove_mode': 'all_services'},
                service_name=common.ANY_VALUE,
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(main=True, service=False),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_TEST_CONFIG_WITH_ALL'
                    ),
                    'data': {
                        'name': 'TEST_CONFIG_WITH_ALL',
                        'remove_mode': 'all_services',
                    },
                },
                expected_apply={},
            ),
            id='success_web_remove_all_services_values',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_ALL',
                params={'remove_mode': 'one'},
                service_name=common.ANY_VALUE,
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(main=False, service=True),
                expected_check={
                    'change_doc_id': (
                        'configs_admin_remove_value_TEST_CONFIG_WITH_ALL'
                    ),
                    'data': {
                        'name': 'TEST_CONFIG_WITH_ALL',
                        'remove_mode': 'one',
                    },
                },
                expected_apply={},
            ),
            id='success_web_remove_main_value_with_mode',
        ),
    ],
)
async def test_case(
        web_context,
        web_app_client,
        name,
        service_name,
        stage_name,
        version,
        params,
        before_exists,
        after_exists,
        expected_check,
        expected_apply,
        is_failed,
):
    # check values before
    values_before = await common.get_values(
        web_context, name, service_name, stage_name,
    )
    # print(values_before, before_exists)
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
    arguments: Dict[str, Any] = {
        'name': name,
        'version': version,
        'service_name': service_name,
        'stage_name': stage_name,
    }
    if params:
        arguments.update(params)
    arguments = {
        key: value
        for key, value in arguments.items()
        if (value is not None and value != common.ANY_VALUE)
    }
    result = await web_app_client.post(
        '/v2/configs/remove/drafts/check/', json=arguments,
    )
    check_body = await result.json()
    assert check_body == expected_check
    if 'change_doc_id' not in check_body:
        return
    result = await web_app_client.delete(
        '/v2/configs/remove/drafts/apply/', json=check_body['data'],
    )
    apply_body = await result.json()
    assert apply_body == expected_apply
    if is_failed and result.status == 200:
        pytest.fail('Apply status is 200, wait other status')

    # check values after
    values_after = await common.get_values(
        web_context, name, service_name, stage_name,
    )
    # print(values_after, after_exists)
    for key, value_exists in dataclasses.asdict(after_exists).items():
        if value_exists:
            assert values_after[key] is not None, key
        else:
            assert values_after[key] is None, key

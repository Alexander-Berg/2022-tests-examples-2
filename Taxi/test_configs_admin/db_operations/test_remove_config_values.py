import dataclasses
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from configs_admin import exceptions
from configs_admin.api_helpers import configs
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
    exception: Optional[exceptions.ConfigNotFound] = None
    params: Optional[Dict] = None
    before_exists: Optional[Exists] = None
    after_exists: Optional[Exists] = None


@pytest.mark.parametrize(
    common.get_args(Params),
    [
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                before_exists=Exists(),
                after_exists=Exists(main=False),
            ),
            id='success_remove_main_value',
        ),
        pytest.param(
            *Params(
                name='UNKNOUN_CONFIG',
                exception=exceptions.ConfigNotFound(
                    name='UNKNOUN_CONFIG',
                    details={'errors': ['Main value not found']},
                ),
                before_exists=Exists(main=False),
            ),
            id='fail_remove_non_existed_main_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                service_name='abt',
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(main=True, service=False),
            ),
            id='success_remove_service_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                service_name='unknown_service',
                exception=exceptions.ConfigNotFound(
                    name='TEST_CONFIG',
                    details={
                        'errors': [
                            'Service value for `unknown_service` '
                            'service not found',
                        ],
                    },
                ),
                before_exists=Exists(main=True, service=False),
            ),
            id='fail_remove_non_existed_service_value',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_STAGE',
                stage_name='unstable',
                before_exists=Exists(main=False, stage=True),
                after_exists=Exists(main=False, stage=False),
            ),
            id='success_remove_stage_value',
        ),
        pytest.param(
            *Params(
                name='UNKNOUN_CONFIG',
                stage_name='unknown_stage',
                exception=exceptions.ConfigNotFound(
                    name='UNKNOUN_CONFIG',
                    details={
                        'errors': [
                            'Stage value for `unknown_stage` '
                            'stage not found',
                        ],
                    },
                ),
                before_exists=Exists(main=False, stage=False),
            ),
            id='fail_remove_non_existed_stage_value',
        ),
        # TODO: unlock after add support service values to stages
        # pytest.param(
        #     'TEST_CONFIG',
        #     'abt',
        #     'unstable',
        #     None,
        #     Exists(main=None, service=True, stage=True),
        #     Exists(main=None, service=None, stage=True),
        #     id='success_remove_service_stage_value',
        # ),
        # pytest.param(
        #     'TEST_CONFIG',
        #     'abt',
        #     'unknown_stage',
        #     exceptions.ConfigNotFound(...),
        #     Exists(main=None, service=True, stage=True),
        #     None,
        #     id='fail_remove_non_existed_service_stage_value',
        # ),
    ],
)
async def test_case(
        web_context,
        name,
        service_name,
        stage_name,
        exception,
        params,
        before_exists,
        after_exists,
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

    try:
        arguments: Dict[str, Any] = {
            'context': web_context,
            'name': name,
            'version': None,
            'service_name': service_name,
            'stage_name': stage_name,
        }
        if params:
            arguments.update(params)
        await configs.remove_config_value(**arguments)
    except exceptions.ConfigNotFound as exc:
        assert (
            exception.message == exc.message
        ), f'expected={exception.message},exist={exc.message}'
        assert (
            exception.details == exc.details
        ), f'expected={exception.details},exist={exc.details}'
        return

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

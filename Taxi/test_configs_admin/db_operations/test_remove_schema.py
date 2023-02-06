import dataclasses
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from configs_admin import exceptions
from configs_admin.api_helpers import schemas
from test_configs_admin.db_operations import common


@dataclasses.dataclass
class Exists:
    main: bool = False
    service: bool = False
    stage: bool = False
    schema: bool = True


class Params(NamedTuple):
    name: str
    params: Optional[Dict[str, Any]] = None
    exception: Optional[exceptions.Error] = None
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
            ),
            id='success_remove_schema',
        ),
        pytest.param(
            *Params(
                name='NON_EXISTED_SCHEMA',
                before_exists=Exists(schema=False),
                exception=exceptions.SchemaNotFound(name='NON_EXISTED_SCHEMA'),
                is_failed=True,
            ),
            id='fail_remove_if_schema_not_found',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_MAIN',
                before_exists=Exists(main=True),
                exception=exceptions.SchemaNotRemoved(
                    name='TEST_CONFIG_WITH_MAIN',
                    reason='In [\'main\'] scopes values exists',
                ),
                is_failed=True,
            ),
            id='fail_remove_schema_if_main_value_exists',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_SERVICE',
                before_exists=Exists(service=True),
                exception=exceptions.SchemaNotRemoved(
                    name='TEST_CONFIG_WITH_SERVICE',
                    reason='In [\'services\'] scopes values exists',
                ),
                is_failed=True,
            ),
            id='fail_remove_schema_if_service_value_exists',
        ),
        pytest.param(
            *Params(
                name='TEST_CONFIG_WITH_VALUES',
                params={'clean_all': True, 'version': 10},
                before_exists=Exists(main=True, service=True),
                after_exists=Exists(schema=False),
            ),
            id='successfull_remove_schema_with_all_values',
        ),
    ],
)
async def test_case(
        web_context,
        name,
        params,
        exception,
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
    try:
        arguments: Dict[str, Any] = {
            'context': web_context,
            'name': name,
            'version': None,
        }
        if params:
            arguments.update(params)
        await schemas.remove_schema(**arguments)
    except exceptions.Error as exc:
        assert (
            exception.message == exc.message
        ), f'expected={exception.message},exist={exc.message}'
        assert (
            exception.details == exc.details
        ), f'expected={exception.details},exist={exc.details}'
        return
    if exception:
        assert False, f'Exception {exception} must be raised'

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

import dataclasses
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from configs_admin.api_helpers import configs
from test_configs_admin.db_operations import common


@dataclasses.dataclass
class Exists:
    main: bool = True
    service: bool = False


class Params(NamedTuple):
    name: str
    expected: Dict
    before_exists: Optional[Exists] = None
    after_exists: Optional[Exists] = None


@pytest.mark.parametrize(
    common.get_args(Params),
    [
        pytest.param(
            *Params(
                name='TEST_CONFIG',
                expected={'main': 1, 'services': 2},
                before_exists=Exists(),
                after_exists=Exists(main=False, service=False),
            ),
            id='success_remove_all_values',
        ),
        pytest.param(
            *Params(
                name='UNKNOUN_CONFIG',
                expected={'main': 0, 'services': 0},
                before_exists=Exists(main=False, service=False),
                after_exists=Exists(main=False, service=False),
            ),
            id='fail_remove_non_existed_config',
        ),
    ],
)
async def test_case(web_context, name, expected, before_exists, after_exists):
    # check values before
    values_before = await common.get_values(web_context, name)
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

    assert expected == await configs.remove_all_config_values(
        web_context, name,
    )

    # check values after
    values_after = await common.get_values(web_context, name)
    # print(values_after, after_exists)
    for key, value_exists in dataclasses.asdict(after_exists).items():
        if value_exists:
            assert values_after[key] is not None, key
        else:
            assert values_after[key] is None, key

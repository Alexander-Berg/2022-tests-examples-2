# pylint: disable=no-member

import os
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from configs_admin import static as static_module


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class Case(NamedTuple):
    current_path: str
    default_path: str
    is_failed: bool = False
    ex_class: Optional[Any] = None
    flags: Dict[str, bool] = {}

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


@pytest.mark.parametrize(
    Case.get_args(),
    [
        pytest.param(
            *Case(
                current_path='no_existsts.yaml',
                default_path='defaults.yaml',
                flags={
                    'enable_check_change_main_value': False,
                    'enable_check_change_service_value': True,
                    'enable_check_namespace': False,
                },
            ),
            id='success without current',
        ),
        pytest.param(
            *Case(
                current_path='current.yaml',
                default_path='defaults.yaml',
                flags={
                    'enable_check_change_main_value': True,
                    'enable_check_change_service_value': False,
                    'enable_check_namespace': False,  # no override
                },
            ),
            id='success with current and partial override defaults',
        ),
        pytest.param(
            *Case(
                current_path='no_existsts.yaml',
                default_path='no_existsts.yaml',
                is_failed=True,
                ex_class=FileNotFoundError,
            ),
            id='fail without default',
        ),
        pytest.param(
            *Case(
                default_path='defaults.yaml',
                current_path='bad_format_current.yaml',
                flags={
                    'enable_check_change_main_value': False,
                    'enable_check_change_service_value': True,
                },
            ),
            id='success no dict in current',
        ),
        pytest.param(
            *Case(
                default_path='defaults.yaml',
                current_path='no_yaml.md',
                flags={
                    'enable_check_change_main_value': False,
                    'enable_check_change_service_value': True,
                },
            ),
            id='no yaml format in current',
        ),
    ],
)
def test(current_path, default_path, is_failed, ex_class, flags):
    current_path = os.path.join(BASE_PATH, 'static', 'default', current_path)
    default_path = os.path.join(BASE_PATH, 'static', 'default', default_path)

    if is_failed:
        with pytest.raises(ex_class):
            static = static_module.StaticConfig.from_files(
                default_path=default_path, current_path=current_path,
            )
        return

    static = static_module.StaticConfig.from_files(
        default_path=default_path, current_path=current_path,
    )

    # test flags
    if flags:
        assert getattr(static, 'flags')
        for flag, value in flags.items():
            assert getattr(static.flags, flag) == value

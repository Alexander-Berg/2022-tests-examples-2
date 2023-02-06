# pylint: skip-file
# flake8: noqa
import os
import os.path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

import pytest

from testsuite.utils import json_util

SECDIST_DATA: dict = {   'apikeys': {},
                         'settings_override': {   'TVM_SERVICES': {   'fake': {   'id': 2345,
                                                                                  'secret': 'secret'}}}}


@pytest.fixture(scope='session')
def secdist_service_generate(
        mockserver_info, testsuite_build_dir,
):
    def mockserver_substitute(path: str) -> str:
        return 'http://%s:%d%s' % (
            mockserver_info.host,
            mockserver_info.port,
            path,
        )

    options: Dict[str, Callable[[str], Any]] = {
        'mockserver': mockserver_substitute,
    }
    secdist_path = str(testsuite_build_dir / 'configs' / 'secdist.json')
    os.makedirs(
        os.path.dirname(secdist_path),
        exist_ok=True,
    )
    with open(secdist_path, 'w', encoding='utf-8') as f:
        f.write(json_util.dumps(_substitute_value(SECDIST_DATA, options)))


def _substitute_list(
        seq: List[Any], options: Dict[str, Callable[[str], Any]]) -> List[Any]:
    return [_substitute_value(value, options) for value in seq]


def _substitute_value(
        value: Any, options: Dict[str, Callable[[str], Any]]) -> Any:
    if isinstance(value, dict):
        value = _substitute_dict(value, options)
    elif isinstance(value, list):
        value = _substitute_list(value, options)
    return value


def _substitute_dict(
        dct: Dict[str, Any],
        options: Dict[str, Callable[[str], Any]]) -> Dict[str, Any]:
    if len(dct) == 1:
        [[key, value]] = dct.items()
        if key.startswith('$'):
            return options[key[1:]](value)

    return {
        key: _substitute_value(value, options)
        for key, value in dct.items()
    }

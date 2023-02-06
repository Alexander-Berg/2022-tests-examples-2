import subprocess
from typing import Iterable
from typing import List

import pytest
import yatest.common  # pylint: disable=import-error

pytest_plugins = ['codegen.tests.plugins.ref_comparer']


@pytest.fixture(scope='session', name='uservices_path')
def _uservices_path() -> str:
    return yatest.common.source_path('taxi/uservices')


@pytest.fixture(scope='session')
def code_search(uservices_path):
    ag_path = yatest.common.binary_path('contrib/tools/ag/ag')

    def _run_code_search(
            text: str, paths: Iterable[str], *, cwd: str = uservices_path,
    ) -> List[str]:
        command = [
            ag_path,
            '--files-with-matches',
            '--file-search-regex',
            '\\.[hc]pp$',
            text,
            *paths,
        ]

        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE)
        if result.returncode == 0:
            return [
                path
                for path in result.stdout.decode('utf-8').split('\n')
                if path
            ]
        if result.returncode == 1:
            # ag returns 1 when no matches are found
            return []
        raise subprocess.CalledProcessError(result.returncode, cmd=command)

    return _run_code_search

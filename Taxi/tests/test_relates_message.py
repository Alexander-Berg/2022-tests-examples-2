from typing import List
from typing import NamedTuple

import pytest

from taxi_buildagent.tools import relates_message


class Params(NamedTuple):
    message: str
    expected_issues: List[str]
    expected_testing: str = ''
    expected_pr: str = ''
    arcadia_format: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                message='Relates:ABC-123  ,ABC-124,ABC-125    ',
                expected_issues=['ABC-123', 'ABC-124', 'ABC-125'],
            ),
            id='normal',
        ),
        pytest.param(
            Params(
                message="""
feat tlog: pass billing_client_id for subvention events
Enrich performer data for subvention events with billing_client_id

Relates: TAXIBILLING-721
        """.strip(),
                expected_issues=['TAXIBILLING-721'],
            ),
            id='github-1',
        ),
        pytest.param(
            Params(
                message="""
feat all: reduce rps on configs service
Relates: TAXIINFRA-260

Issue: TAXIGRAPH-452
        """.strip(),
                expected_issues=['TAXIINFRA-260'],
            ),
            id='github-2',
        ),
        pytest.param(
            Params(
                message="""
Fix cmake for lib
Relates: TAXIGRAPH-285

([arc::pullid] c9c13d02-a8f729a3-4a9ec153-9fed2ea7)

REVIEW: 745143
        """.strip(),
                expected_issues=['TAXIGRAPH-285'],
                arcadia_format=True,
            ),
            id='arcadia-1',
        ),
        pytest.param(
            Params(
                message="""
Cmake config files TAXIGRAPH-296 Relates:TAXIGRAPH-296
Поставляем cmake файлы с описанием установочных путей, чтобы подцеплять их из
CMakeLists в такси.

Relates: TAXIGRAPH-296

REVIEW: 737213
        """.strip(),
                expected_issues=['TAXIGRAPH-296'],
                arcadia_format=True,
            ),
            id='arcadia-2',
        ),
        pytest.param(
            Params(
                message="""
feat core: some core feature

It is very detail description of my task.

Issue: TAXIGRAPH-296, TAXIGRAPH-329

REVIEW: 828313
        """.strip(),
                expected_issues=['TAXIGRAPH-296', 'TAXIGRAPH-329'],
                arcadia_format=True,
            ),
            id='arcadia-3',
        ),
        pytest.param(
            Params(
                message="""
feat core: some core feature

It is very detail description of my task.

Issue: TAXIGRAPH-296

Relates: TAXIGRAPH-329
   Issue: TAXIGRAPH-133

REVIEW: 828313
        """.strip(),
                expected_issues=[
                    'TAXIGRAPH-133',
                    'TAXIGRAPH-296',
                    'TAXIGRAPH-329',
                ],
                arcadia_format=True,
            ),
            id='arcadia-4',
        ),
        pytest.param(
            Params(
                message="""
Testing: Проверял в unstable, покрыто автотестами.
Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_testing='Проверял в unstable, покрыто автотестами.',
            ),
            id='normal with testing tag',
        ),
        pytest.param(
            Params(
                message="""
Tested: Проверял в unstable, покрыто автотестами.
Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_testing='Проверял в unstable, покрыто автотестами.',
            ),
            id='normal with tested tag',
        ),
        pytest.param(
            Params(
                message="""
Testing: Первый тэг тестинга.
Tests: Второй тэг тестинга.
Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_testing='Первый тэг тестинга. Второй тэг тестинга.',
            ),
            id='normal with double testing',
        ),
        pytest.param(
            Params(
                message="""
It is very detail description of my task.

Testing: На прод не влияет. Хотя могла бы!
А этот текст не должен попасть в описание тестирования.

Relates: TAXITOOLS-123, TAXITOOLS-456
        """.strip(),
                expected_issues=['TAXITOOLS-123', 'TAXITOOLS-456'],
                expected_testing='На прод не влияет. Хотя могла бы!',
            ),
            id='normal with testing and description',
        ),
        pytest.param(
            Params(
                message="""
feat driver-profiles: add handle (#1869)

Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_pr='1869',
            ),
            id='pr number in subject',
        ),
        pytest.param(
            Params(
                message='feat driver-profiles: add handle (#1869)',
                expected_issues=[],
                expected_pr='1869',
            ),
            id='pr number in one line commit',
        ),
        pytest.param(
            Params(
                message="""
feat driver-profiles (1869): add handle

Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_pr='',
            ),
            id='wrong pr number in subject',
        ),
        pytest.param(
            Params(
                message="""
feat driver-profiles: add handle (#1234) test

Relates: TAXITOOLS-123
        """.strip(),
                expected_issues=['TAXITOOLS-123'],
                expected_pr='',
            ),
            id='wrong pr number in subject 2',
        ),
        pytest.param(
            Params(
                message="""
feat hejmdal: add trie to service name

Relates: [TAXIH-12](https://st/TAXIH-12), https://st/TAXIH-53 TAXIH-341 4ST-4f
        """.strip(),
                expected_issues=['TAXIH-12', 'TAXIH-341', 'TAXIH-53'],
                expected_pr='',
            ),
            id='strange arcadia relates',
        ),
        pytest.param(
            Params(
                message="""
feat hejmdal: add trie to service name

Relates: TAXIH-12,https://st/TAXIH-53 A-1
        """.strip(),
                expected_issues=['TAXIH-12', 'TAXIH-53'],
                expected_pr='',
            ),
            id='wrong short ticket',
        ),
    ],
)
def test_relates_message(params: Params):
    issues = relates_message.parse_relates_message(
        params.message, arcadia_format=params.arcadia_format,
    )
    assert issues == params.expected_issues

    if params.expected_testing:
        testing = relates_message.parse_testing_message(params.message)
        assert testing == params.expected_testing

    if params.expected_pr:
        pr_number = relates_message.parse_pr_number(params.message)
        assert pr_number == params.expected_pr

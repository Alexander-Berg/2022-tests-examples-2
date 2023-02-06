import itertools
import os
import typing

import pytest

import check_files_format
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import schemas


class Params(typing.NamedTuple):
    teamcity_build_fail: typing.Sequence[dict]
    info_changed_by_format: typing.Sequence[typing.Tuple[str, str]] = ()
    teamcity_error_report: typing.Optional[dict] = None
    db_settings: typing.Optional[str] = ''
    config_declarations_path: typing.Optional[str] = ''
    argv: typing.Optional[typing.Sequence[str]] = ()
    develop_changes: typing.Sequence[repository.Commit] = ()


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                argv=['--format-command', 'make format'],
                teamcity_build_fail=[],
            ),
            id='check_format_correctness empty',
        ),
        pytest.param(
            Params(
                info_changed_by_format=[
                    ('something.py', 'gif with cats is the best\n'),
                ],
                teamcity_error_report={
                    'something.py': (
                        'diff --git a/something.py b/something.py\n'
                        'index 1111111..1111111 111111\n'
                        '--- a/something.py\n'
                        '+++ b/something.py\n'
                        '@@ -1 +1,2 @@\n'
                        ' content for some file\n'
                        '+gif with cats is the best'
                    ),
                },
                teamcity_build_fail=[
                    {
                        'description': 'Format checking is failed',
                        'identity': None,
                    },
                ],
                argv=['--format-command', 'make format'],
            ),
            id='check_format_correctness single file',
        ),
        pytest.param(
            Params(
                info_changed_by_format=[
                    ('taxi/core/order-events.yaml', 'python code\n'),
                    (
                        'taxi/configs/config.txt',
                        'some another text\noriginal text\n',
                    ),
                    (
                        'taxi/somefile.yaml',
                        'inequal wrong string\nyet another text\n',
                    ),
                ],
                teamcity_error_report={
                    'taxi/core/order-events.yaml': (
                        'diff --git a/taxi/core/order-events.yaml '
                        'b/taxi/core/order-events.yaml\n'
                        'index fa9215b..d44b0b9 100644\n'
                        '--- a/taxi/core/order-events.yaml\n'
                        '+++ b/taxi/core/order-events.yaml\n'
                        '@@ -1 +1,2 @@\n'
                        ' content for some yaml file\n'
                        '+python code'
                    ),
                    'taxi/configs/config.txt': (
                        'diff --git a/taxi/configs/config.txt '
                        'b/taxi/configs/config.txt\n'
                        'index fa9215b..d44b0b9 100644\n'
                        '--- a/taxi/configs/config.txt\n'
                        '+++ b/taxi/configs/config.txt\n'
                        '@@ -1 +1,3 @@\n'
                        ' yet another content for config file\n'
                        '+some another text\n'
                        '+original text'
                    ),
                    'taxi/somefile.yaml': (
                        'diff --git a/taxi/somefile.yaml b/taxi/'
                        'somefile.yaml\n'
                        'index 20093c9..26dab4f 100644\n'
                        '--- a/taxi/somefile.yaml\n'
                        '+++ b/taxi/somefile.yaml\n'
                        '@@ -1 +1,3 @@\n'
                        ' schema info of some file\n'
                        '+inequal wrong string\n'
                        '+yet another text'
                    ),
                },
                teamcity_build_fail=[
                    {'description': 'Checking is failed', 'identity': None},
                ],
                argv=[
                    '--format-command',
                    'make format',
                    '--error-message',
                    'Checking is failed',
                ],
            ),
            id='check_format_correctness multiple files',
        ),
        pytest.param(
            Params(
                info_changed_by_format=[
                    (
                        'schemas_repo/db_settings.yaml',
                        """
adjust_stats:
  settings:
    collection: adjust_stats
    connection: stats
    database: dbstats
geofences:
  indexes:
  - key:
    - name: updated
      type: descending
  settings:
    collection: geofences
    connection: gprstimings
    database: gprstimings
yt_imports:
  settings:
    collection: yt_imports
    connection: misc
    database: dbmisc
""".lstrip(),
                    ),
                ],
                db_settings='taxi/core/db_settings.yaml',
                teamcity_build_fail=[
                    {
                        'description': (
                            'db_settings.yaml changed but does not match'
                            ' schemas master. See https://wiki.yandex-te'
                            'am.ru/taxi/backend/datastorage/#proverkadbs'
                            'ettings.yaml for details'
                        ),
                        'identity': 'db_settings.yaml',
                    },
                ],
                develop_changes=[
                    repository.Commit(
                        'new commit',
                        ['taxi/core/db_settings.yaml'],
                        files_content="""
adjust_stats:
  settings:
    connection: stats
    database: dbstats
geofences:
  indexes:
  - key:
    - name: updated
      type: descending
  settings:
    connection: gprstimings
""".lstrip(),
                    ),
                ],
            ),
            id='check check_db_settings',
        ),
        pytest.param(
            Params(
                db_settings='taxi/core/db_settings.yaml',
                teamcity_build_fail=[],
                develop_changes=[
                    repository.Commit(
                        'delete db_settings.yaml',
                        ['taxi/core/db_settings.yaml'],
                        do_delete=True,
                    ),
                ],
            ),
            id='db_settings deleted',
        ),
    ],
)
def test_check_files_format(
        tmpdir,
        monkeypatch,
        chdir,
        teamcity_report_test_problem,
        teamcity_report_problems,
        commands_mock,
        params: Params,
):
    monkeypatch.setenv('DB_SETTINGS', params.db_settings)
    repo = backend.init(tmpdir)
    repo_dir = tmpdir.join('repo')
    if params.develop_changes:
        repository.apply_commits(repo, params.develop_changes)
    schemas.init(repo_dir)

    monkeypatch.chdir(repo.working_tree_dir)
    chdir(repo.working_tree_dir)

    @commands_mock('make')
    def _make(args, **kwargs):
        for diff_pair in params.info_changed_by_format:
            file_path = os.path.join(repo.working_tree_dir, diff_pair[0])
            with open(file_path, 'a') as fout:
                fout.write(diff_pair[1])
        return ''

    check_files_format.main(params.argv)

    assert teamcity_report_problems.calls == params.teamcity_build_fail

    if not params.db_settings:
        for problem_calls_entry in teamcity_report_test_problem.calls:
            teamcity_error_report = params.teamcity_error_report or {}
            true_test_content = teamcity_error_report.get(
                problem_calls_entry['test_name'],
            )
            assert true_test_content
            calls_info = problem_calls_entry['problem_message'].split('\n')
            params_info = true_test_content.split('\n')
            for calls_line, params_line in itertools.zip_longest(
                    calls_info, params_info,
            ):
                is_index_present = (
                    calls_line
                    and params_line
                    and calls_line.startswith('index')
                    and params_line.startswith('index')
                )
                if is_index_present:
                    continue
                assert calls_line == params_line

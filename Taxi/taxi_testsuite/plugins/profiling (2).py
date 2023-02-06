"""Profiling plugin for pytest, based on standard ``pytest-profiling`` plugin
https://pypi.org/project/pytest-profiling/

Modified to use ``yappi`` profiler instead of ``cProfile`` so that coroutine
timings are calculated properly.
"""

import errno
import hashlib
import pathlib
import pstats
import typing

import pytest

try:
    import yappi
except ImportError:
    yappi = None

LARGE_FILENAME_HASH_LEN = 8


class ProfilingPlugin:
    _fixture_setup_timings: typing.Dict[str, typing.List[float]]

    def __init__(
            self,
            directory: str,
            profile_builtins: bool,
            profile_threads: bool,
    ):
        self._dir = pathlib.Path(
            'prof' if directory is None else directory[0],
        ).resolve()
        self._profile_builtins = profile_builtins
        self._profile_threads = profile_threads
        self._fixture_setup_timings = {}
        self._report_paths: typing.List[str] = []
        self._combined_report_path = self._dir / 'combined.prof'

    def pytest_sessionstart(self, session):
        try:
            self._dir.mkdir(exist_ok=True, parents=True)
        except OSError:
            pass

    def pytest_sessionfinish(self, session, exitstatus):
        if self._report_paths:
            combined = pstats.Stats(self._report_paths[0].as_posix())
            for prof in self._report_paths[1:]:
                combined.add(prof.as_posix())

            combined.dump_stats(self._combined_report_path)

    def pytest_terminal_summary(self, terminalreporter):
        if self._combined_report_path:
            terminalreporter.write(
                'Profiling (from {prof}):\n'.format(
                    prof=self._combined_report_path,
                ),
            )
            pstats.Stats(
                self._combined_report_path.as_posix(), stream=terminalreporter,
            ).strip_dirs().sort_stats('cumulative').print_stats(20)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        t0 = yappi.get_clock_time()
        yield
        t1 = yappi.get_clock_time()
        name = f'{fixturedef.argname}_setup_fixture'
        records = self._fixture_setup_timings.get(name, None)
        if records is None:
            records = list()
            self._fixture_setup_timings[name] = records
        records.append(t1 - t0)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        prof_filename = self._dir.joinpath(
            _clean_filename(item.name) + '.prof',
        )
        try:
            prof_filename.parent.mkdir(exist_ok=True, parents=True)
        except OSError:
            pass
        yappi.set_clock_type('wall')
        yappi.start(
            builtins=self._profile_builtins,
            profile_threads=self._profile_threads,
        )
        yield
        yappi.stop()
        prof: yappi.YFuncStats = yappi.get_func_stats()
        try:
            prof.save(prof_filename, type='pstat')
        except EnvironmentError as err:
            if err.errno != errno.ENAMETOOLONG:
                raise

            if len(item.name) < LARGE_FILENAME_HASH_LEN:
                raise

            hash_str = hashlib.md5(item.name.encode('utf-8')).hexdigest()[
                :LARGE_FILENAME_HASH_LEN
            ]
            prof_filename = self._dir.joinpath(hash_str + '.prof')
            prof.save(prof_filename, type='pstat')
        self._report_paths.append(prof_filename)


def pytest_addoption(parser):
    group = parser.getgroup('profiling')
    group.addoption(
        '--profile',
        action='store_true',
        help='Generate profiling information',
    )
    group.addoption(
        '--profile-no-builtins',
        action='store_true',
        help=(
            'Set True to skip profiling builtin functions. '
            'Profiling overhead will decrease, but profiling report will '
            'become harder to understand.'
        ),
    )
    group.addoption(
        '--profile-no-threads',
        action='store_true',
        help='Set True to profile only main thread',
    )
    group.addoption(
        '--pstats-dir',
        nargs=1,
        help='configure the dump directory of profile data files',
    )


def pytest_configure(config):
    if config.option.profile:
        if yappi is None:
            raise RuntimeError(
                'Cannot profile tests: missing required package yappi',
            )
        config.pluginmanager.register(
            ProfilingPlugin(
                directory=config.option.pstats_dir,
                profile_builtins=not config.option.profile_no_builtins,
                profile_threads=not config.option.profile_no_threads,
            ),
        )


def _clean_filename(s):
    forbidden_chars = set('/?<>\\:*|"')
    return ''.join(
        c if c not in forbidden_chars and ord(c) < 127 else '_' for c in s
    )

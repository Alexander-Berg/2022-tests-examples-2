import yatest.common

from sandbox.projects.geosuggest.component import log
from sandbox.sdk2.path import Path


def _daemon_log():
    return Path(yatest.common.source_path('sandbox/projects/geosuggest/component/ut/data/daemon.log'))


def test_time():
    return log.get_startup_time_stats(_daemon_log())


def test_memory():
    return log.get_startup_memory_stats(_daemon_log())


def test_not_exists():
    return log.get_startup_time_stats(Path('invalid_path.log'))

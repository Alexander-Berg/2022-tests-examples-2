import logging
import pathlib
import typing

import pytest

logger = logging.getLogger()


class ServiceLogsDumper:
    def __init__(self):
        self._file_pos = {}

    def register_log(self, path: pathlib.Path):
        self._file_pos[path] = 0

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        rep = outcome.get_result()
        if rep.when == 'setup':
            if rep.outcome == 'failed':
                self._dump_logs()
            self._update_positions()
        elif rep.when == 'call' and rep.outcome == 'failed':
            self._dump_logs()

    def _update_positions(self):
        for path in self._file_pos:
            self._file_pos[path] = path.stat().st_size

    def _dump_logs(self):
        if not self._file_pos:
            return

        logger.info('Dumping service logs because of failure')
        for path in self._file_pos:
            if not path.exists():
                logger.info('Path %s don\'t exist! Don\'t dump it!', path)
                continue
            self._dump_single_log(path)
        logger.info('Done dumping service logs')

    def _dump_single_log(self, path):
        logger.info('Dump log in file %s', path)
        newpos = path.stat().st_size
        pos = self._file_pos[path]
        with path.open('r') as fp:
            fp.seek(pos)
            for line in fp:
                pos += len(line)
                line = line.strip()
                logger.info('%s', line)
                if pos >= newpos:
                    break


@pytest.fixture(scope='session')
def service_logs_dumper(pytestconfig) -> typing.Optional[ServiceLogsDumper]:
    plugin = pytestconfig.pluginmanager.get_plugin('service_logs_dumper')
    return plugin


def pytest_configure(config):
    config.pluginmanager.register(ServiceLogsDumper(), 'service_logs_dumper')

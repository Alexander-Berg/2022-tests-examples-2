# -*- coding: utf-8 -*-
import glob
import itertools
import json
import logging
import os
import shutil
import uuid
from abc import ABCMeta, abstractmethod

import pytest
import requests

from portal.function_tests.util.common import env

logger = logging.getLogger(__name__)
YASMAGENT_API = 'http://portal-yasm.wdevx.yandex.ru:11005'


def _is_monitoring():
    return env.is_monitoring()


def pytest_configure(config):
    monitoring_notifier = MonitoringNotifier()
    monitoring_notifier.register(YASM_NOTIFIER)
    config.pluginmanager.register(monitoring_notifier, 'monitoring_notifier')


class MonitoringNotifier(object):
    def __init__(self):
        self.reports = []
        self.notifiers = []

    def register(self, notifier):
        self.notifiers.append(notifier)

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        if call.when == 'setup':
            rep = outcome.get_result()
            for notifier in self.notifiers:
                notifier.update_notify_info(item, rep)

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self.reports.append(report)

    def pytest_sessionstart(self, session):
        if _is_monitoring():
            if not getattr(session.config, 'slaveinput', None):
                for notifier in self.notifiers:
                    notifier.prepare()

    def pytest_sessionfinish(self, session, exitstatus):
        if _is_monitoring():
            if not getattr(session.config, 'slaveinput', None):
                logger.debug('Enabling monitoring notifier')
                logger.debug('Total test reports: {}'.format(len(self.reports)))
                for notifier in self.notifiers:
                    notifier.notify(self.reports)
            else:
                for notifier in self.notifiers:
                    notifier.notify_slaves()


class TestStats(object):
    def __init__(self, passed, failed, skipped):
        self.passed = passed
        self.failed = failed
        self.skipped = skipped

    @staticmethod
    def from_reports(reports):
        passed = len([report for report in reports if report.outcome == 'passed'])
        failed = len([report for report in reports if report.outcome == 'failed'])
        skipped = len([report for report in reports if report.outcome == 'skipped'])
        return TestStats(passed, failed, skipped)

    def __repr__(self):
        return 'passed={}, failed={}, skipped={}'.format(self.passed, self.failed, self.skipped)


class BaseNotifier(object):
    __metaclass__ = ABCMeta

    def prepare(self):
        pass

    @abstractmethod
    def _get_marker_data(self, marker):
        pass

    @abstractmethod
    def update_notify_info(self, item, report):
        pass

    @abstractmethod
    def notify(self, reports):
        pass

    def notify_slaves(self):
        pass


class YasmNotifier(BaseNotifier):
    _dir = 'yasm'
    signals = {}

    def prepare(self):
        shutil.rmtree(self._dir, ignore_errors=True)
        os.mkdir(self._dir)

    def _get_marker_data(self, marker):
        if marker is None:
            return None
        return marker.kwargs.get('signal', None)

    def add_to_signal(self, signal, value):
        current = self.signals.get(signal, 0)
        self.signals[signal] = current + value

    def update_notify_info(self, item, report):
        marker = item.keywords.get('yasm')
        report.yasm = self._get_marker_data(marker)

    def notify_slaves(self):
        with open('{}/{}.json'.format(self._dir, uuid.uuid4()), 'w+') as data:
            data.write(json.dumps(self.signals))

    def _get_signals_from_dir(self):
        files = glob.glob('{}/*.json'.format(self._dir))
        signals = {}
        for file in files:
            with open(file) as f:
                data = f.read()
                json_data = json.loads(data)
                for k, v in json_data.iteritems():
                    curr = signals.get(k, 0)
                    signals[k] = curr + v
        return signals

    def notify(self, reports):
        yasm_reports = [report for report in reports if report.yasm is not None]
        grouped_reports = YasmNotifier._group_by_signal(yasm_reports)

        signals = self._get_signals_from_dir()
        for k, v in signals.iteritems():
            curr = self.signals.get(k, 0)
            self.signals[k] = curr + v
        logger.debug('Yasm signals from files:\n' + json.dumps(self.signals, indent=4))

        for signal, stats in grouped_reports.iteritems():
            for status in ['passed', 'skipped', 'failed']:
                self.add_to_signal(signal.format(status), getattr(stats, status))

        logger.debug('Aggregated yasm signals:\n' + json.dumps(self.signals, indent=4))
        self._send(self.signals)

    def _send(self, signals):
        try:
            if len(signals) == 0:
                logger.debug('Nothing to send to yasm')
                return
            values = [{'name': k, 'val': v} for k, v in signals.iteritems()]

            data = [{
                'ttl': 900,
                'tags': {
                    'itype': 'mordafunc'
                },
                'values': values
            }]
            logger.debug('Sending yasm signals:\n' + json.dumps(data, indent=4))

            response = requests.post(
                url=YASMAGENT_API,
                json=data,
                timeout=5
            )
            if response.status_code != 200:
                logger.error('Failed to send yasm metrics. Response status_code={}'.format(response.status_code))
        except Exception:
            logger.exception('Failed to send yasm metrics')

    @staticmethod
    def _group_by_signal(reports):
        sorted_reports = sorted(reports, key=lambda x: x.yasm)
        groups = {}

        for yasm_signal, g in itertools.groupby(sorted_reports, lambda x: x.yasm):
            groups[yasm_signal] = TestStats.from_reports(list(g))

        return groups


YASM_NOTIFIER = YasmNotifier()


@pytest.fixture(scope='session')
def yasm():
    return YasmNotifier()

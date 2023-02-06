# coding=utf-8

import datetime
import unittest

import mock
import pytest
import pytz

from sandbox.projects.browser.booking import common
from sandbox.projects.browser.booking.config import (
    EstimationConfig,
)
from sandbox.projects.browser.booking.estimator import (
    Estimator,
    EVENT_TYPE_BUILD_BETA,
    ARTIFACT_TYPE_DEPLOY_ALPHA,
)

TEST_PROJECT_KEY = 'desktop'
TEST_RELEASES = [
    mock.MagicMock(version='20.1.0'),
    mock.MagicMock(version='20.1.1'),
    mock.MagicMock(version='20.1.2'),
]
TEST_EVENTS = [
    mock.MagicMock(id=1, title=u'Сборка Альфы',
                   type=EVENT_TYPE_BUILD_BETA,
                   date=pytz.UTC.localize(datetime.datetime(2020, 1, 1, 0, 0, 0))),
    mock.MagicMock(id=2, title=u'Регрессия Альфы'),
]
TEST_BOOKING_INFO = mock.MagicMock(booking_id=123)
TEST_BOOKING_CONFIG = mock.MagicMock(estimation=mock.MagicMock(
    before_hours=48, method=EstimationConfig.METHOD_ALPHA))


class TestEstimator(unittest.TestCase):
    def test_get_regression_type(self):
        assert Estimator.get_regression_type(EstimationConfig.METHOD_BETA, 2) == 'Win_Beta2_Diff.yaml'

    def test_split_release_version(self):
        assert Estimator.split_release_version('12.3.4') == ('12.3', 4)

    def test_get_branch_name(self):
        assert Estimator.get_branch_name('12.3.4') == 'master-12.3.4/rc'

    def test_get_estimation_task_params(self):
        PARAMS = {
            'description': '- project: "KEY"\n- release: "43.2.1"\n- event  : "TITLE"\n',
            'regression_type': 'Win_RC1_Diff.yaml',
            'scope_filter': '',
            'build_id': 222,
            'old_build_id': 111,
        }
        assert Estimator.get_estimation_task_params(
            'KEY', mock.MagicMock(version='43.2.1'), mock.MagicMock(title='TITLE'),
            EstimationConfig.METHOD_RC, 111, 222) == PARAMS

    def test_get_estimation(self):
        estimator = Estimator(mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
                              common.MSK_TIMEZONE.localize(datetime.datetime(2020, 1, 1)))
        estimator.get_branded_build = mock.MagicMock(return_value=111)
        estimator.get_deploy_build_id = mock.MagicMock(return_value=333)
        estimator.get_tc_build_id = mock.MagicMock(return_value=222)
        estimator.get_estimation_task_params = mock.MagicMock(return_value={'param': 'value'})

        estimation = estimator.get_estimation(
            TEST_PROJECT_KEY,
            {r.version: r for r in TEST_RELEASES}, TEST_RELEASES[1],
            TEST_EVENTS, TEST_EVENTS[1],
            TEST_BOOKING_INFO, TEST_BOOKING_CONFIG)
        assert estimation is not None
        assert estimation.project_key == TEST_PROJECT_KEY
        assert estimation.release_version == '20.1.1'
        assert estimation.event_id == 2
        assert estimation.booking_id == 123
        assert estimation.sandbox_task_params == {'param': 'value'}
        assert estimation.sandbox_task_id is None

        assert estimator.get_branded_build.mock_calls == [
            mock.call(333),
        ]
        assert estimator.get_deploy_build_id.mock_calls == [
            mock.call(TEST_PROJECT_KEY, TEST_RELEASES[0], ARTIFACT_TYPE_DEPLOY_ALPHA),
        ]
        assert estimator.get_tc_build_id.mock_calls == [
            mock.call('master', 0, '20.1.1'),
        ]


@pytest.mark.parametrize('releases, version, prev_version, next_version', [
    (['20.10.3', '20.11.0', '20.11.1', '20.11.2', '20.11.3', '20.12.0'],
     '20.11.0', '20.10.3', '20.11.1'),
    (['20.10.3', '20.11.0', '20.11.1', '20.11.2', '20.11.3', '20.12.0'],
     '20.11.1', '20.11.0', '20.11.2'),
    (['20.10.3', '20.11.0', '20.11.1', '20.11.2', '20.11.3', '20.12.0'],
     '20.11.2', '20.11.1', '20.11.3'),
    (['20.10.3', '20.11.0', '20.11.1', '20.11.2', '20.11.3', '20.12.0'],
     '20.11.3', '20.11.2', '20.12.0'),
])
def test_get_neighbors(releases, version, prev_version, next_version):
    estimator = Estimator(mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
                          common.MSK_TIMEZONE.localize(datetime.datetime.now()))
    prev_release, next_release = estimator.get_neighbors(
        {r: mock.MagicMock(version=r) for r in releases}, version)
    assert prev_version == prev_release.version
    assert next_version == next_release.version

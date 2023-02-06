import glob
import os
import mock
import pytest
import time

from sandbox.projects.browser.util import configurable_trigger


@pytest.fixture()
def patch_releases_info():
    now = int(time.time())

    MOCK_RELEASES_INFO = [
        {
            u'milestones': [
                {u'date': now - 50, u'kind': u'branch'},
                {u'date': now - 10, u'kind': u'broteam'},
                {u'date': now + 172750, u'kind': u'second_ff'},
                {u'date': now + 182750, u'kind': u'release:rc'},
            ],
            u'platforms': [u'mac'],
            u'branch': u'master-19.10.1/rc',
            u'real_branch': u'master-19.10.1/rc',
            u'version': u'19.10.1',
        },
        {
            u'milestones': [
                {u'date': now + 350, u'kind': u'branch'},
                {u'date': now + 400, u'kind': u'broteam'},
                {u'date': now + 173050, u'kind': u'second_ff'},
                {u'date': now + 174050, u'kind': u'release:rc'},
            ],
            u'platforms': [u'win', u'mac'],
            u'branch': u'master-19.10.2/rc',
            u'real_branch': u'master-19.10.2/rc',
            u'version': u'19.10.2',
        },
        {
            u'milestones': [
                {u'date': now - 50, u'kind': u'branch'},
                {u'date': now - 50, u'kind': u'broteam'},
                {u'date': now + 172750, u'kind': u'second_ff'},
                {u'date': now + 182750, u'kind': u'release:rc'},
            ],
            u'platforms': [u'win'],
            u'real_branch': u'master-19.10.3/rc',
            u'branch': u'master-19.10.3/rc',
            u'version': u'19.10.3',
        },
    ]
    with mock.patch.object(configurable_trigger, 'get_releases_info',
                           return_value=MOCK_RELEASES_INFO) as _fixture:
        yield _fixture


def valid_configs():
    import yatest.common

    configs = glob.glob(os.path.join(
        os.path.abspath(yatest.common.test_source_path()),
        'valid_configs',
        '*.yaml',
    ))

    for config in configs:
        yield pytest.param(config, id=os.path.basename(config))


def invalid_configs():
    import yatest.common

    configs = glob.glob(os.path.join(
        os.path.abspath(yatest.common.test_source_path()),
        'invalid_configs',
        '*.yaml',
    ))

    for config in configs:
        yield pytest.param(config, id=os.path.basename(config))


@pytest.mark.parametrize('config_path', valid_configs())
def test_valid_config(config_path, patch_releases_info):
    return configurable_trigger.load_config_if_valid(config_path)


@pytest.mark.parametrize('config_path', invalid_configs())
def test_invalid_config(config_path, patch_releases_info):
    with pytest.raises(Exception) as exc_info:
        configurable_trigger.load_config_if_valid(config_path)
    return str(exc_info.value)


@pytest.mark.parametrize('branches', [
    [
        'master',
        'master-android',
        'master-ios',
        'master-19.7.0/rc',
        'master-20.7/pre',
        'master-20.3/android/pre',
        'master-19.3.1/rc',
        'master-19.6.0/android/rc',
        'master-19.6.4/android/rc',
        'merge-77.0.3838/0',
        'merge-77.0.3838/2',
        'pull-requests/148823',
    ],
])
@pytest.mark.parametrize(
    'rules, answer', [
        ([
            '+:master.*', '-:master-android', '-:master-ios', '-:master-(.*)/android/(.*)'
        ], {'master', 'master-19.3.1/rc', 'master-19.7.0/rc', 'master-20.7/pre'}),
        (['+:merge-(.*)'], {'merge-77.0.3838/0', 'merge-77.0.3838/2'}),
        ([
            '+:master', '+:master-ios', '+:master-android', '+:master-.*/rc',
            '-:master-.*/android/rc',
            r'+:master-.*\.0/android/rc',
            '-:master-19.3.1/rc'
        ], {'master', 'master-ios', 'master-android', 'master-19.7.0/rc', 'master-19.6.0/android/rc'}),
        (['+:pull-requests/(.*)'], {'pull-requests/148823'})
    ]
)
def test_branch_filtration(branches, rules, answer):
    assert configurable_trigger.get_relevant_branches(branches, rules) == answer


@pytest.mark.parametrize(
    'releases, rules, answer', [
        (
            {'platforms': ['mac', 'win']},
            ['win'],
            True
        ),
        (
            {'platforms': ['win']},
            ['mac'],
            False
        ),
        (
            {'platforms': ['win']},
            None,
            True
        ),
        (
            {'platforms': ['win', 'linux', 'mac']},
            ['mac', 'ios', 'android'],
            True
        ),
    ]
)
def test_platform_fits(releases, rules, answer):
    assert configurable_trigger.platform_fits(releases, rules) == answer


@pytest.fixture()
def file_tree():
    return ['a.file', 'b.file',
            'cc/a_feature.file', 'cc/b_feature.file']


@pytest.mark.parametrize(
    'file_globs, answer', [
        (['+:a.file'], True),
        (['-:a.file'], False),
        (['+:a.file', '-:b.file'], True),
        (['+:*feature*'], True),
        (['+:cc/**', '-:*feature*'], False),
        (['+:cc/**', '-:*feature*', '+:*b_feature*'], True)
    ]
)
def test_glob_filtering(file_globs, answer, file_tree):
    assert configurable_trigger.filter_files_against_globs(file_tree, file_globs) == answer


def test_empty_globs():
    with pytest.raises(ValueError) as exc_info:
        configurable_trigger.filter_files_against_globs(file_tree, [])
    return str(exc_info)

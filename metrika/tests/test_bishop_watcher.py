from datetime import datetime

import pytest

import metrika.pylib.file as mtf


IS_CONFIG_UPDATE_REQUIRED_TEST_PARAMETERS = [
    "funcs_results,expected_result",
    [
        # 0
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': False,
                'is_config_md5_changes': False,
                'is_config_version_changed': False,
            },
            {
                'update_required': False,
                'reason': None,
            }
        ),
        # 1
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': False,
                'is_config_md5_changes': False,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 2
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': False,
                'is_config_md5_changes': True,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 3
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': False,
                'is_config_md5_changes': True,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 4
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': True,
                'is_config_md5_changes': False,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 5
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': True,
                'is_config_md5_changes': False,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 6
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': True,
                'is_config_md5_changes': True,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 7
        (
            {
                'is_config_missing_on_fs': False,
                'is_config_state_missing': True,
                'is_config_md5_changes': True,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 8
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': False,
                'is_config_md5_changes': False,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 9
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': False,
                'is_config_md5_changes': False,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 10
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': False,
                'is_config_md5_changes': True,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 11
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': False,
                'is_config_md5_changes': True,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 12
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': True,
                'is_config_md5_changes': False,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 13
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': True,
                'is_config_md5_changes': False,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 14
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': True,
                'is_config_md5_changes': True,
                'is_config_version_changed': False,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
        # 15
        (
            {
                'is_config_missing_on_fs': True,
                'is_config_state_missing': True,
                'is_config_md5_changes': True,
                'is_config_version_changed': True,
            },
            {
                'update_required': True,
                'reason': 'This is reason',
            }
        ),
    ],
]


def test_is_config_missing_on_fs_true(bishop_watcher, missing_config):
    assert bishop_watcher.is_config_missing_on_fs(missing_config)


def test_is_config_missing_on_fs_false(bishop_watcher, exists_config):
    assert not bishop_watcher.is_config_missing_on_fs(exists_config)


def test_is_config_state_missing_true(bishop_watcher, exists_config):
    assert bishop_watcher.is_config_state_missing(exists_config)


def test_is_config_state_missing_false(bishop_watcher, exists_config):
    bishop_watcher.state[exists_config.path] = {'version': 1}
    assert not bishop_watcher.is_config_state_missing(exists_config)


def test_is_config_md5_changes_true(bishop_watcher, exists_config):
    bishop_watcher.state[exists_config.path] = {'md5': 'this is changed md5'}

    changed, fs_md5, state_md5 = bishop_watcher.is_config_md5_changes(exists_config)
    assert changed
    assert fs_md5 == '5d41402abc4b2a76b9719d911017c592'
    assert state_md5 == 'this is changed md5'


def test_is_config_md5_changes_false(bishop_watcher, exists_config):
    expected_md5 = '5d41402abc4b2a76b9719d911017c592'
    bishop_watcher.state[exists_config.path] = {'md5': expected_md5}

    changed, fs_md5, state_md5 = bishop_watcher.is_config_md5_changes(exists_config)
    assert not changed
    assert fs_md5 == state_md5 == expected_md5


def test_is_config_version_changed_true(monkeypatch, bishop_watcher, exists_config):
    def mock_get_config_version(*args, **kwargs):
        return 666

    monkeypatch.setattr(bishop_watcher, 'get_config_version', mock_get_config_version)

    bishop_watcher.state[exists_config.path] = {'version': 777}

    changed, remote_version, state_version = bishop_watcher.is_config_version_changed(exists_config)
    assert changed
    assert remote_version != state_version
    assert remote_version == 666
    assert state_version == 777


def test_is_config_version_changed_false(monkeypatch, bishop_watcher, exists_config):
    def mock_get_config_version(*args, **kwargs):
        return 777

    monkeypatch.setattr(bishop_watcher, 'get_config_version', mock_get_config_version)

    bishop_watcher.state[exists_config.path] = {'version': 777}

    changed, remote_version, state_version = bishop_watcher.is_config_version_changed(exists_config)
    assert not changed
    assert remote_version == state_version == 777


@pytest.mark.parametrize(*IS_CONFIG_UPDATE_REQUIRED_TEST_PARAMETERS)
def test_is_config_update_reqired(monkeypatch, bishop_watcher, exists_config, funcs_results, expected_result):
    def mock_is_config_missing_on_fs(config):
        return funcs_results['is_config_missing_on_fs']

    def mock_is_config_state_missing(config):
        return funcs_results['is_config_state_missing']

    def mock_is_config_md5_changes(config):
        return funcs_results['is_config_md5_changes'], '', ''

    def mock_is_config_version_changed(config):
        return funcs_results['is_config_version_changed'], 1, 1

    monkeypatch.setattr(bishop_watcher, 'is_config_missing_on_fs', mock_is_config_missing_on_fs)
    monkeypatch.setattr(bishop_watcher, 'is_config_state_missing', mock_is_config_state_missing)
    monkeypatch.setattr(bishop_watcher, 'is_config_md5_changes', mock_is_config_md5_changes)
    monkeypatch.setattr(bishop_watcher, 'is_config_version_changed', mock_is_config_version_changed)

    update_required, reason = bishop_watcher.is_config_update_required(exists_config)

    assert update_required == expected_result['update_required']
    assert bool(reason) == bool(expected_result['reason'])


def test_update_config(monkeypatch, bishop_watcher, exists_config):
    mocked_data = 'some data'
    mocked_data_md5 = '1e50210a0202497fb79bc38b6ade6c34'
    mocked_version = 333
    mocked_format = 'plaintext'

    def mock_get_config(self, *args, **kwargs):
        return mocked_version, mocked_format, mocked_data

    def mock_atomic_write(self, *args, **kwargs):
        return True

    monkeypatch.setattr(bishop_watcher, 'get_config', mock_get_config)
    monkeypatch.setattr(mtf, 'atomic_write', mock_atomic_write)

    state_before_update = bishop_watcher.state.get(exists_config.path)
    assert state_before_update is None

    bishop_watcher.update_config(exists_config)
    state = bishop_watcher.state[exists_config.path]

    assert state['version'] == mocked_version
    assert state['md5'] == mocked_data_md5
    assert isinstance(state['updated_at'], datetime)


def test_status(bishop_watcher):
    state_value = 'The State!'
    bishop_watcher.state = state_value
    status = bishop_watcher.status()
    assert status['state'] == state_value

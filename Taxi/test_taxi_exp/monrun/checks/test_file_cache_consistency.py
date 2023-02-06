import datetime
import inspect
import os
import time
from typing import NamedTuple
from typing import Optional

import pytest

from taxi_exp import settings
from taxi_exp.monrun.checks import file_cache_consistency_monitoring


@pytest.fixture
def relative_dir_path():
    def _wrapper(dirname):
        caller_filename = inspect.stack()[1][1]
        caller_dir = os.path.dirname(os.path.abspath(caller_filename))
        _, file_name = os.path.split(caller_filename)
        return os.path.join(
            caller_dir, 'static', file_name.replace('.py', ''), dirname,
        )

    return _wrapper


class Case(NamedTuple):
    expected_answer: str
    cache_folder: str
    updated_time: Optional[datetime.datetime]
    cache_is_updated: bool


@pytest.mark.parametrize(
    'expected_answer, cache_folder, updated_time, cache_is_updated',
    [
        pytest.param(
            *Case(
                '0; All files is consistent',
                'file_cache_with_only_index',
                None,
                True,
            ),
            id='file_cache_with_only_index',
        ),
        pytest.param(
            *Case(
                '0; All files is consistent',
                'empty_file_cache_folder',
                None,
                True,
            ),
            id='empty_file_cache_folder',
        ),
        pytest.param(
            *Case(
                '0; All files is consistent',
                'file_cache_folder_with_registered_files',
                datetime.datetime(year=2000, month=1, day=1),
                True,
            ),
            marks=pytest.mark.now('2000-01-01'),
            id='file_cache_folder_with_unregistered_files_and_without_update',
        ),
        pytest.param(
            *Case(
                '0; All files is consistent',
                'file_cache_folder_with_registered_files',
                datetime.datetime(year=2000, month=1, day=1),
                True,
            ),
            marks=(
                pytest.mark.pgsql('taxi_exp', files=['one_file.sql']),
                pytest.mark.now('3000-01-01'),
                pytest.mark.config(
                    EXP_MONITORING_SETTINGS={
                        file_cache_consistency_monitoring.CHECK_NAME: {
                            'need_check_hash': True,
                        },
                    },
                ),
            ),
            id='file_cache_folder_with_registered_files_and_without_update',
        ),
        pytest.param(
            *Case(
                '1; Files name cache has bad format',
                'bad_file_cache_format',
                datetime.datetime(year=2000, month=1, day=1),
                False,
            ),
            marks=(pytest.mark.now('2000-01-01'),),
            id='warn_if_bad_file_cache_format',
        ),
        pytest.param(
            *Case(
                (
                    '1;  `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` '
                    'has lost size and hash from postgres;'
                ),
                'file_cache_folder_with_registered_files',
                None,
                True,
            ),
            marks=(
                pytest.mark.pgsql(
                    'taxi_exp', files=['one_file_without_size.sql'],
                ),
                pytest.mark.now('3000-01-01'),
                pytest.mark.config(
                    EXP_MONITORING_SETTINGS={
                        file_cache_consistency_monitoring.CHECK_NAME: {
                            'need_check_hash': True,
                        },
                    },
                ),
            ),
            id='warn_if_db_not_has_size_or_hash',
        ),
        pytest.param(
            *Case(
                '2;  `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` has incorrect size;',
                'file_cache_folder_with_registered_files',
                None,
                True,
            ),
            marks=(
                pytest.mark.pgsql(
                    'taxi_exp', files=['one_file_with_incorrect_size.sql'],
                ),
                pytest.mark.now('3000-01-01'),
            ),
            id='crit_if_file_size_incorrect',
        ),
        pytest.param(
            *Case(
                '2;  `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` has incorrect hash;',
                'file_cache_folder_with_registered_files',
                None,
                True,
            ),
            marks=(
                pytest.mark.pgsql(
                    'taxi_exp', files=['one_file_with_incorrect_hash.sql'],
                ),
                pytest.mark.now('3000-01-01'),
                pytest.mark.config(
                    EXP_MONITORING_SETTINGS={
                        file_cache_consistency_monitoring.CHECK_NAME: {
                            'need_check_hash': True,
                        },
                    },
                ),
            ),
            id='crit_if_file_hash_incorrect',
        ),
    ],
)
async def test_file_cache_monitoring(
        expected_answer,
        cache_folder,
        updated_time,
        cache_is_updated,
        patch,
        taxi_exp_client,
        relative_dir_path,
        monkeypatch,
):  # pylint: disable=redefined-outer-name

    path_to_cache = relative_dir_path(cache_folder)
    monkeypatch.setattr(
        settings, 'FILES_SNAPSHOT_PATH', path_to_cache, raising=True,
    )

    save = _Calls()

    @patch(
        'taxi_exp.monrun.checks.'
        'file_cache_consistency_monitoring.FileNameCache.save',
    )
    def _save(*args, **kwargs):
        save.times_called += 1

    if updated_time is not None:
        mod_time = time.mktime(updated_time.timetuple())
        os.utime(path_to_cache, (mod_time, mod_time))

    # pylint: disable=protected-access
    answer = await file_cache_consistency_monitoring._check(
        taxi_exp_client.app, file_cache_consistency_monitoring.CHECK_NAME,
    )

    assert answer.replace('\t', '    ') == expected_answer
    if cache_is_updated:
        assert save.times_called > 0


class _Calls:
    times_called = 0

import os
import shutil

import pytest

from taxi.core import async
from taxi_maintenance.stuff import execute_scripts


@pytest.mark.skipif(True, reason='flaps, fix in TAXIPLATFORM-3834')
@pytest.mark.asyncenv('blocking')
def test_execute_script_run_and_kill(patch, tmpdir):
    tmp_dir = os.path.join(str(tmpdir), '123', 'src')

    @patch('taxi.external.scripts.get_running_count')
    @async.inline_callbacks
    def get_running_count(*args, **kwargs):
        yield
        async.return_value({'num_running': 0, 'max_num_running': 1})

    @patch('taxi.external.scripts.get_next')
    @async.inline_callbacks
    def get_next(*args, **kwargs):
        yield
        async.return_value({
            'id': '123',
            'url': 'http://github.com/taxi/tools/blob/commit/test.py',
            'local_relative_path': 'test.py',
            'arguments': [],
            'python_path': '/usr/lib/yandex/taxi-imports',
            'features': ['pythonpath_inplace'],
        })

    @patch('taxi.external.scripts.download_script')
    @async.inline_callbacks
    def download_script(*args, **kwargs):
        yield

    @patch('taxi.external.scripts.mark_as')
    @async.inline_callbacks
    def mark_as(*args, **kwargs):
        yield

    @patch('taxi.internal.scripts_manager.os_utils.get_checkouted_repo_root')
    def get_checkouted_repo_root(*args, **kwargs):
        return tmp_dir

    @patch('taxi.external.scripts.upload_logs')
    @async.inline_callbacks
    def upload_logs(*args, **kwargs):
        yield

    @patch('taxi.external.scripts.upload_script')
    @async.inline_callbacks
    def upload_script(*args, **kwargs):
        yield

    @patch('taxi.external.scripts.finish_upload')
    @async.inline_callbacks
    def finish_upload(*args, **kwargs):
        yield

    @patch('taxi.external.scripts.get_next_command')
    @async.inline_callbacks
    def get_next_command(*args, **kwargs):
        yield
        async.return_value({
            'sleep_for': 1,
            'command': {
                'id': 123,
                'name': 'send_signal',
                'args': [9],
                'kwargs': {},
            }
        })

    @patch('taxi.external.scripts.apply_command')
    @async.inline_callbacks
    def apply_command(*args, **kwargs):
        yield

    try:
        os.makedirs(tmp_dir)
    except OSError:
        shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)

    with open(os.path.join(tmp_dir, 'test.py'), 'w') as fp:
        fp.write("""import time; time.sleep(1); print 'finished'""")

    try:
        execute_scripts.do_stuff()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    mark_as_calls = mark_as.calls
    assert len(mark_as_calls) == 2
    assert {x['args'][0] for x in mark_as_calls} == {
        '/scripts/123/mark-as-running/',
        '/scripts/123/mark-as-failed/',
    }
    assert mark_as_calls[1]['kwargs']['json'] == {
        'reason': 'script returned non-zero',
        'code': -9,
    }
    assert len(get_next_command.calls) == 1
    assert len(apply_command.calls) == 1

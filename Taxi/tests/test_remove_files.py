import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint


def test_remove_old_files(engine, max_days_store=31):

    # create old file and check that it will be deleted

    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)
    path_to_segments.mkdir(parents=True, exist_ok=True)

    path_to_log = Path('/tmp/yandex/cctv/processor/cctv-processor.log')
    old_date = datetime.utcnow() - timedelta(days=max_days_store, seconds=1)
    old_file_name = old_date.strftime('%Y-%m-%d_%H:%M:%S_test_file') + '.mkv'
    old_file_path = path_to_segments / old_file_name
    old_file_path.touch(exist_ok=True)

    if path_to_log.exists():
        path_to_log.unlink()

    try:
        pprint('start running')
        test_process = engine.run(
            Path(
                'processor/tests/config/yandex-cctv-processor-config-remove-files-test.yaml',
            ),
        )
        time.sleep(10)
        test_process.terminate()
        time.sleep(10)  # give time to actually finish execution
    except Exception as ex:
        pprint(ex)

    assert not old_file_path.exists()
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)


# TODO:
# Get free space and check that file will be deleted

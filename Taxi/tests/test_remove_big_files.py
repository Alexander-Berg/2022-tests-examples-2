import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint


def test_remove_big_files(engine):

    # create big file and check that it will be deleted

    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)
    path_to_segments.mkdir(parents=True, exist_ok=True)

    path_to_log = Path('/tmp/yandex/cctv/processor/cctv-processor.log')
    file_paths = []
    now = datetime.utcnow()
    for i in range(1, 4):
        old_date = now - timedelta(minutes=5 * i)
        old_file_name = (
            old_date.strftime('%Y-%m-%d_%H:%M:%S_test_file') + '.mkv'
        )
        old_file_path = path_to_segments / old_file_name
        file_paths.append(old_file_path)
        old_file_path.touch(exist_ok=True)

        with open(old_file_path, 'wb') as f:
            f.truncate(1024 * 1024 * 1024 - 2048)

    old_date = now - timedelta(minutes=5)

    old_file_name = old_date.strftime('%Y-%m-%d_%H:%M:%S_test_file') + '.mp4'
    old_file_path = path_to_segments / old_file_name
    file_paths.append(old_file_path)
    old_file_path.touch(exist_ok=True)

    with open(old_file_path, 'wb') as f:
        f.truncate(1024 * 1024 * 1024 - 4096)

    old_file_name = old_date.strftime('%Y-%m-%d_%H:%M:%S_test_fila') + '.mkv'
    old_file_path = path_to_segments / old_file_name
    file_paths.append(old_file_path)
    old_file_path.touch(exist_ok=True)

    with open(old_file_path, 'wb') as f:
        f.truncate(1024 * 1024 * 1024 - 2048)

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

    # only the freshest should remain
    # among the freshest - with the least size
    # among them - with least name
    assert file_paths[0].exists()
    for i in range(1, len(file_paths)):
        assert not file_paths[i].exists()
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)


# TODO:
# Get free space and check that file will be deleted

import shutil
import subprocess
import time
from pathlib import Path
from pprint import pprint


def test_store_to_disk(engine):
    path_to_segments = Path(
        '/tmp/yandex/cctv/processor/stored_videos/ffmpeg_video_file',
    )
    shutil.rmtree(path_to_segments, ignore_errors=True)
    path_to_log = Path('/tmp/yandex/cctv/processor/cctv-processor.log')
    if path_to_log.exists():
        path_to_log.unlink()

    try:
        pprint('start running')
        test_process = engine.run(
            Path(
                'build/processor/yandex-cctv-processor-config-store-test.yaml',
            ),
        )
        time.sleep(61)
        test_process.terminate()
        time.sleep(10)  # give time to actually finish execution
        pprint(test_process.stdout)
    except Exception as ex:
        pprint(ex)

    find_rotate = False
    if path_to_segments.exists():
        videos = [video.stem for video in path_to_segments.iterdir()]
        for video_name in videos:
            if video_name[-2:] == '00':
                find_rotate = True

    assert find_rotate
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)

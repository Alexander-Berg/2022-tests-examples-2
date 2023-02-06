import pytest

import shutil
from pathlib import Path
import logging
import asyncio
import os
import base64
from datetime import datetime


def _check_event_box(event_box):
    assert 'x' in event_box
    assert 'y' in event_box
    assert 'w' in event_box
    assert 'h' in event_box
    assert isinstance(event_box['x'], (float, int))
    assert isinstance(event_box['y'], (float, int))
    assert isinstance(event_box['w'], (float, int))
    assert isinstance(event_box['h'], (float, int))


def _check_event_signature(event_signature):
    assert len(event_signature) > 0
    for value in event_signature:
        assert isinstance(value, (float, int))


event_count = 0


def _check_base64(encoded, timestamp_ms):
    global event_count
    event_count += 1
    ts_string = datetime.utcfromtimestamp(int(timestamp_ms) // 1000).strftime(
        '%Y-%m-%d_%H:%M:%S',
    )
    filename = f'{ts_string}_{event_count}.jpg'
    path = Path(
        '/tmp/yandex/cctv/processor/detected_boxes/ffmpeg_video_file/'
        + filename,
    )
    assert path.exists()
    with open(str(path), 'rb') as f:
        encoded_py = base64.b64encode(f.read()).decode()
        assert encoded == encoded_py


def _check_event(signature_event):
    global event_count
    assert 'model_id' in signature_event
    assert 'camera_id' in signature_event
    assert 'timestamp_ms' in signature_event
    assert 'signature' in signature_event
    assert 'box' in signature_event
    assert 'confidence' in signature_event
    assert 'detected_object' in signature_event
    assert isinstance(signature_event['model_id'], str)
    assert isinstance(signature_event['camera_id'], str)
    assert isinstance(signature_event['detected_object'], str)
    assert isinstance(signature_event['timestamp_ms'], (float, int))
    assert isinstance(signature_event['signature'], list)
    assert isinstance(signature_event['confidence'], (float, int))
    _check_event_signature(signature_event['signature'])
    _check_event_box(signature_event['box'])
    _check_base64(
        signature_event['detected_object'], signature_event['timestamp_ms'],
    )
    if event_count % 2 == 0:
        assert 'frame' in signature_event
        assert isinstance(signature_event['frame'], str)
    else:
        assert 'frame' not in signature_event


@pytest.fixture
async def processor(mockserver):
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)
    path_to_log = Path('/tmp/yandex/cctv/processor/cctv-processor.log')

    if path_to_log.exists():
        path_to_log.unlink()

    event_log_dir = Path('/tmp/yandex/cctv/processor/events-log')
    if event_log_dir.exists():
        shutil.rmtree('/tmp/yandex/cctv/processor/events-log')

    box_dir = Path('/tmp/yandex/cctv/processor/detected_boxes')
    if box_dir.exists():
        shutil.rmtree('/tmp/yandex/cctv/processor/detected_boxes')

    global test_process
    test_process = None
    try:
        test_process = await asyncio.subprocess.create_subprocess_exec(
            'build/processor/yandex-cctv-processor',
            '-c',
            'build/processor/yandex-cctv-processor-config-store-boxes.yaml',
            stdout=asyncio.subprocess.PIPE,
        )
    except Exception as ex:
        logging.error(ex)
        assert False
    yield test_process
    test_process.terminate()
    await asyncio.sleep(5)  # give time to actually finish execution
    if isinstance(test_process.stdout, asyncio.StreamReader):
        logging.info((await test_process.stdout.read()).decode('utf-8'))


async def test_store_box(processor, mockserver):
    # waiting for the process to start and process several frames
    await asyncio.sleep(10)
    request = await mockserver.get_handler().wait_call()
    assert 'events' in request.body
    assert isinstance(request.body['events'], list)
    for event in request.body['events']:
        _check_event(event)
    event_log_dir = Path('/tmp/yandex/cctv/processor/events-log')
    assert not event_log_dir.exists()
    box_dir = Path('/tmp/yandex/cctv/processor/detected_boxes')
    assert box_dir.exists()
    assert len(os.listdir('/tmp/yandex/cctv/processor/detected_boxes')) != 0
    shutil.rmtree('/tmp/yandex/cctv/processor/detected_boxes')
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)

import pytest

import shutil
from pathlib import Path
import logging
import asyncio


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


def _check_event(signature_event):
    assert 'model_id' in signature_event
    assert 'camera_id' in signature_event
    assert 'timestamp_ms' in signature_event
    assert 'signature' in signature_event
    assert 'box' in signature_event
    assert 'confidence' in signature_event
    assert 'frame' not in signature_event
    assert 'detected_object' in signature_event
    assert isinstance(signature_event['model_id'], str)
    assert isinstance(signature_event['camera_id'], str)
    assert isinstance(signature_event['timestamp_ms'], (float, int))
    assert isinstance(signature_event['signature'], list)
    assert isinstance(signature_event['confidence'], (float, int))
    assert isinstance(signature_event['detected_object'], str)
    _check_event_signature(signature_event['signature'])
    _check_event_box(signature_event['box'])


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

    global test_process
    test_process = None
    try:
        test_process = await asyncio.subprocess.create_subprocess_exec(
            'build/processor/yandex-cctv-processor',
            '-c',
            'build/processor/yandex-cctv-processor-config-post-event-test.yaml',
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


async def test_post_event(processor, mockserver):
    # waiting for the process to start and process several frames
    await asyncio.sleep(5)
    request = await mockserver.get_handler().wait_call()
    assert 'events' in request.body
    assert isinstance(request.body['events'], list)
    for event in request.body['events']:
        _check_event(event)
    event_log_dir = Path('/tmp/yandex/cctv/processor/events-log')
    assert not event_log_dir.exists()
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)

import pytest

import shutil
from pathlib import Path
import logging
import asyncio

import json


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
            'build/processor/yandex-cctv-processor-config-get-configs-test.yaml',
            stdout=asyncio.subprocess.PIPE,
        )
    except Exception as ex:
        logging.error(ex)
        assert False
    yield test_process
    await asyncio.sleep(10)
    test_process.terminate()
    await asyncio.sleep(5)  # give time to actually finish execution
    if isinstance(test_process.stdout, asyncio.StreamReader):
        logging.warning((await test_process.stdout.read()).decode('utf-8'))


async def test_get_configs(processor, mockserver):
    # waiting for the process to start and process several frames
    await asyncio.sleep(10)
    response = await mockserver.get_handler().wait_call()
    with open('tests/data/config.json') as f:
        assert response.body == json.load(f)
    assert response.code == 200
    response = await mockserver.get_handler().wait_call()
    assert response.code == 304
    assert response.body == {}
    path_to_segments = Path('/tmp/yandex/cctv/processor/stored_videos')
    shutil.rmtree(path_to_segments, ignore_errors=True)

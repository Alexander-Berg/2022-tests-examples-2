import asyncio
import glob
import os.path

import pytest

from libstall import json_pp as json
from stall.lqueue import LQueue


# pylint: disable=invalid-name
class TCfg:
    def __init__(self):
        self.handle_mode = 'raise'
        self.lock = asyncio.Lock()


test_config = TCfg()


async def handle(objects): # pylint: disable=unused-argument
    if test_config.handle_mode == 'raise':
        raise RuntimeError('test')


@pytest.mark.parametrize('mode', ['normal', 'raise'])
async def test_nopush(tap, tmpdir, mode):
    tap.plan(5)

    async with test_config.lock:
        test_config.handle_mode = mode

        tap.ok(os.path.isdir(tmpdir), 'директория создана %s' % tmpdir)
        pusher = LQueue(cache_dir=tmpdir, pusher=__name__)
        tap.ok(pusher, 'инстанцирован')

        done = await pusher.flush(0.5)

        tap.eq(glob.glob(os.path.join(tmpdir, '*')), [], 'нет файлов')

        tap.ok(done, 'дождались сброса буфера (файлов не было)')

        tap.ok(True, 'не зависло ничего при пустом каталоге')
    tap()


@pytest.mark.parametrize('mode', ['normal', 'raise'])
async def test_push(tap, tmpdir, mode):
    tap.plan(8)
    async with test_config.lock:
        test_config.handle_mode = mode

        tap.ok(os.path.isdir(tmpdir), 'директория создана %s' % tmpdir)
        pusher = LQueue(cache_dir=tmpdir, pusher=__name__)
        tap.ok(pusher, 'инстанцирован')

        file_name = await pusher.push({'hello': 'world'}, {'a': 'b'})

        tap.ok(file_name, 'pushed')
        tap.ok(os.path.isfile(file_name), 'isfile')
        with open(file_name, 'r') as fh:
            for line in fh:
                tap.ok(line, 'строка прочитана')
                res = json.loads(line)

                tap.eq(res, [{'hello': 'world'}, {'a': 'b'}], 'значение')

        done = await pusher.flush(.5)

        if mode == 'raise':
            tap.ok(not done, 'не дождались сброса буфера')
            tap.ne(glob.glob(os.path.join(tmpdir, '*')), [], 'неотправленное')
        else:
            tap.ok(done, 'дождались сброса буфера')
            tap.eq(glob.glob(os.path.join(tmpdir, '*')), [], 'нет файлов')
    tap()


async def test_push_no_process(tap, tmpdir):
    tap.plan(7)
    async with test_config.lock:
        tap.ok(os.path.isdir(tmpdir), 'директория создана %s' % tmpdir)
        pusher = LQueue(cache_dir=tmpdir)
        tap.ok(pusher, 'инстанцирован')

        file_name = await pusher.push({'hello': 'world'}, {'a': 'b'})

        tap.ok(file_name, 'pushed')
        tap.ok(os.path.isfile(file_name), 'isfile')
        with open(file_name, 'r') as fh:
            for line in fh:
                tap.ok(line, 'строка прочитана')
                res = json.loads(line)

                tap.eq(res, [{'hello': 'world'}, {'a': 'b'}], 'значение')

        with tap.raises(RuntimeError, 'Выбрасывает исключение'):
            await pusher.flush(.5)

    tap()

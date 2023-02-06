import glob
import os.path

from libstall import json_pp as json
from stall.lqueue import LQueue


async def test_push(api, tmpdir):
    t = await api()

    t.tap.plan(12)

    pusher = LQueue(cache_dir=tmpdir)
    t.tap.ok(pusher, 'инстанцирован')
    t.app.pusher = pusher

    await t.post_ok('api_lqueue_push', json=[
    ])
    t.status_is(200, diag=True)

    t.tap.eq(glob.glob(os.path.join(tmpdir, '*')),
             [],
             'от пустого пуша нет вреда')
    t.json_is('code', 'OK')
    t.json_is('sent', 0)

    await t.post_ok('api_lqueue_push', json=[
        {'hello': 'world'},
        {'abc': 'cde'},
    ])
    t.status_is(200, diag=True)

    t.json_is('code', 'OK')
    t.json_is('sent', 2)

    files = glob.glob(os.path.join(tmpdir, '*'))

    with open(files[0], 'r') as fh:
        res = json.loads(fh.read())

        t.tap.eq(res,
                 [
                     {'hello': 'world'},
                     {'abc': 'cde'},
                 ],
                 'значение в файле')

    t.tap.eq(len(files), 1, 'один файлик создан')
    t.tap()

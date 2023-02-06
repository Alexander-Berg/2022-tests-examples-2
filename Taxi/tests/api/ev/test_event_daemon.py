# pylint: disable=protected-access,unused-argument

import asyncio
import itertools
from unittest import mock
from unittest.mock import sentinel

from stall.model import event
from stall.model.event import Event


async def test_event_cache_daemon_fail(tap, monkeypatch, api, mongo):
    idloop = id(asyncio.get_event_loop())

    monkeypatch.setattr(
        Event, '_update_cache',
        mock.Mock(
            wraps=Event._update_cache,
            side_effect=itertools.chain(
                itertools.repeat(Exception('daemon fails'), 1),
                itertools.repeat(sentinel.DEFAULT)
            )
        )
    )

    fake_log = mock.Mock(spec=event.log)
    monkeypatch.setattr(event, 'log', fake_log)

    def _check_tasks_processing(desc):
        tap.ok(idloop in Event.daemon, 'idloop initialized')
        tap.ok(all(not it.done() for it in desc['task']._children),
               'all tasks processing')

    with tap:
        t = await api()

        await _make_take_request(t)

        tap.ok(idloop in Event.daemon, 'idloop initialized')
        desc = Event.daemon[idloop]

        _check_tasks_processing(desc)
        fake_log.exception.assert_not_called()

        await asyncio.sleep(1)

        _check_tasks_processing(desc)
        fake_log.exception.assert_called_once()
        fake_log.exception.reset_mock()

        await asyncio.sleep(1)

        _check_tasks_processing(desc)
        fake_log.exception.assert_not_called()

        await _make_take_request(t)

        _check_tasks_processing(desc)
        fake_log.exception.assert_not_called()

        await asyncio.sleep(1)

        _check_tasks_processing(desc)
        fake_log.exception.assert_not_called()


async def _make_take_request(t):
    await t.post_ok('api_ev_take',
                    json={'keys': [[1, 2, 3]], 'timeout': 3},
                    desc='нет state')
    t.status_is(200, diag=True)

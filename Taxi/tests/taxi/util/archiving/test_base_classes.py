import asyncio
import datetime

import bson
import freezegun
import pytest

from taxi.util.archiving import base_classes


@pytest.mark.parametrize(
    'objects,nflushes,odd',
    [
        (list(range(35)), 3, 5),
        (list(range(3)), 0, 3),
        (list(range(10)), 1, 0),
        (list(range(20)), 2, 0),
    ],
)
@pytest.mark.nofilldb()
async def test_base_bulk(objects, nflushes, odd):
    class DummyBulk(base_classes.BaseBulk):
        async def execute(self):
            flushes.append(self.objects)

    flushes = []
    bulk = DummyBulk(10)
    for obj in objects:
        await bulk.add(obj)

    objects2 = []

    assert nflushes == len(flushes)
    for chunk in flushes:
        assert len(chunk) == bulk.bulk_size
        objects2.extend(chunk)
    assert len(bulk.objects) == odd

    flushes = []
    await bulk.flush()
    if odd:
        assert len(flushes) == 1  # pylint: disable=len-as-condition
        objects2.extend(flushes[0])
    else:
        assert not flushes

    assert objects == objects2


@pytest.mark.parametrize(
    'items,expected',
    [
        ('abcd', [(0, 'a'), (1, 'b'), (2, 'c'), (3, 'd')]),
        ('ab!cd', [(0, 'a'), (1, 'b'), '!', (3, 'c'), (4, 'd')]),
        ('ab!!cd', [(0, 'a'), (1, 'b'), '!', '!', (4, 'c'), (5, 'd')]),
        ('ab!!!!cd', [(0, 'a'), (1, 'b'), '!', '!', '!', '!']),
    ],
)
@pytest.mark.nofilldb()
async def test_doc_getter(items, expected):
    class CustomExc(Exception):
        pass

    class DocGetter(base_classes.BaseDocGetter):
        _exceptions = (CustomExc,)

        items_enumerator = enumerate(items)

        def _get_cursor(self):
            async def _cursor():
                for savepoint, _item in self.items_enumerator:
                    if _item == '!':
                        result.append('!')
                        raise CustomExc
                    doc = bson.BSON.encode(
                        {'savepoint': savepoint, 'msg': _item},
                    )
                    yield bson.raw_bson.RawBSONDocument(doc)

            return _cursor()

        def _get_savepoint(self, obj):
            return obj['savepoint']

    result = []
    getter = DocGetter('savepoint', 0)
    try:
        async for item in getter:
            # pylint: disable=protected-access
            assert getter._savepoint == item['savepoint']
            result.append((item['savepoint'], item['msg']))
    except CustomExc:
        pass
    assert result == expected


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'delay, tick_seconds, expected_sleep_times',
    [
        (0, [0, 0], []),
        (5, [6, 1], [4.0]),
        (1, [1, 1], []),
        (10, [0, 0], [10.0, 10.0]),
        (-1, [10, 10], []),
        (0, [20, 20], []),
        (3, [1.6, 1.2], [1.4, 1.8]),
    ],
)
async def test_sleep_limiter(
        monkeypatch, delay, expected_sleep_times, tick_seconds,
):
    sleep_times = []

    # SleepLimiter doesn't call this function when to_sleep == 0
    async def _fake_sleep(to_sleep):
        sleep_times.append(to_sleep)

    monkeypatch.setattr(asyncio, 'sleep', _fake_sleep)
    sleep_limiter = base_classes.SleepLimiter()
    now = datetime.datetime.utcnow()
    with freezegun.freeze_time(now) as frozen_datetime:
        for i in range(3):
            async with sleep_limiter.sleep_between(delay):
                pass
            if i != 2:
                now = now + datetime.timedelta(seconds=tick_seconds[i])
                frozen_datetime.move_to(now)
    # pylint: disable=consider-using-enumerate
    for i in range(len(sleep_times)):
        assert pytest.approx(sleep_times[i]) == expected_sleep_times[i]

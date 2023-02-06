# pylint: disable=line-too-long, protected-access
import pytest

from taxi.logs import utils


@pytest.mark.parametrize(
    ['traceback', 'filtered_lines', 'no_middlewares'],
    [
        (
            (
                'Traceback (most recent call last):\n'
                '  File "/app/taxi_corp/api/middlewares.py", line 37, in middleware_handler\n'  # noqa
                '    return await handler(request)\n'
                '  File "/usr/lib/python3.7/asyncio/coroutines.py", line 110, in __next__\n'  # noqa
                '    return self.gen.send(None)\n'
                '  File "/app/taxi_corp/api/middlewares.py", line 110, in middleware_handler\n'  # noqa
                '    return await handler(request, *args, **kwargs)\n'
                '  File "/usr/lib/python3.7/asyncio/coroutines.py", line 110, in __next__\n'  # noqa
                '    return self.gen.send(None)\n'
                '  File "/app/taxi_corp/api/handlers/ping.py", line 12, in ping\n'  # noqa
                '    None.get(\'lol\')\n'
                'AttributeError: \'NoneType\' object has no attribute \'get\'\n'  # noqa
            ),
            [
                'taxi_corp/api/middlewares.py:37',
                'taxi_corp/api/middlewares.py:110',
                'taxi_corp/api/handlers/ping.py:12',
            ],
            False,
        ),
        (
            (
                'Traceback (most recent call last):\n'
                '  File "/app/taxi_corp/api/middlewares.py", line 37, in middleware_handler\n'  # noqa
                '    return await handler(request)\n'
                '  File "/usr/lib/python3.7/asyncio/coroutines.py", line 110, in __next__\n'  # noqa
                '    return self.gen.send(None)\n'
                '  File "/app/taxi_corp/api/middlewares.py", line 110, in middleware_handler\n'  # noqa
                '    return await handler(request, *args, **kwargs)\n'
                '  File "/usr/lib/python3.7/asyncio/coroutines.py", line 110, in __next__\n'  # noqa
                '    return self.gen.send(None)\n'
                '  File "/app/taxi_corp/api/handlers/ping.py", line 12, in ping\n'  # noqa
                '    None.get(\'lol\')\n'
                'AttributeError: \'NoneType\' object has no attribute \'get\'\n'  # noqa
            ),
            ['taxi_corp/api/handlers/ping.py:12'],
            True,
        ),
        (
            (
                'Traceback (most recent call last):\n'
                '  File "a.py", line 52, in <module>\n'
                '  func2()\n'
                '  File "a.py", line 49, in func2\n'
                '  func()\n'
                '  File "a.py", line 43, in func\n'
                '  raise Exception(\'Dummy\')\n  Exception: Dummy\n'
            ),
            [],
            False,
        ),
        ('Absolutely random string', [], False),
    ],
)
async def test_get_corp_error_paths(traceback, filtered_lines, no_middlewares):
    assert (
        utils.get_error_paths(
            traceback, ['/taxi/', '/taxi_corp/'], '/app', no_middlewares,
        )
        == filtered_lines
    )


@pytest.mark.parametrize(
    ['path', 'filters', 'expected'],
    [
        (
            'File \"/app/taxi_corp/api/middlewares.py\", line 37, in middleware_handler',  # noqa
            ['/taxi/', '/taxi_corp/'],
            True,
        ),
        ('/some/random/path', ['/taxi/', '/taxi_corp/'], False),
        ('/some/random/correct/path/', ['/correct/'], True),
    ],
)
async def test_string_contains_filter(path, filters, expected):
    assert utils._is_correct_traceback_line(path, filters) == expected

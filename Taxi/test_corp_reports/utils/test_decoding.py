import logging

import pytest

from corp_reports.utils import decoding


@pytest.mark.parametrize(
    'item, log_message',
    [
        ('asdasdsd', 'Try decoding row as string'),
        (b'some string', 'Try decoding row as bytes'),
        (
            [b'some string', 'asdasdsd', ['asdasd']],
            'Try decoding row as list, decoding elements recursive',
        ),
        (tuple(), 'Decoding failed - unrecognized type'),
    ],
)
async def test_decoding_on_level_info(item, log_message, caplog):
    caplog.set_level(logging.INFO)
    decoding.decode_to_cyrillic(item)
    assert log_message in caplog.text


@pytest.mark.parametrize(
    'item, iserror',
    [([b'some string', 'asdasdsd', ['asdasd']], False), (tuple(), True)],
)
async def test_decoding_on_level_error(item, caplog, iserror):
    caplog.set_level(logging.ERROR)
    decoding.decode_to_cyrillic(item)
    if iserror:
        assert caplog.text
    else:
        assert not caplog.text

# pylint: disable=protected-access
import pytest

from replication.targets.yt import yt_targets


@pytest.mark.parametrize(
    'test_input, expected',
    [
        ('farm_hash(store_stock_id)', ['store_stock_id']),
        ('farm_hash(order_id, lsn)', ['order_id', 'lsn']),
        ('farm_hash(arg1, arg2, arg3)', ['arg1', 'arg2', 'arg3']),
    ],
)
async def test_yt_parse_expression(test_input, expected):
    assert yt_targets.TableMeta._parse_expression(test_input) == expected


@pytest.mark.parametrize(
    'test_input, expected',
    [
        ('farm_hash', 'Incorrect expression \'farm_hash\''),
        ('farm_hash()', 'Empty arguments list passed to function farm_hash()'),
        (
            'function1(arg1, arg2)',
            'Unknown function name \'function1\' '
            'was passed to \'expression\'',
        ),
    ],
)
async def test_yt_parse_expression_exceptions(test_input, expected):
    with pytest.raises(yt_targets.YTConfigurationError, match=expected):
        yt_targets.TableMeta._parse_expression(test_input)

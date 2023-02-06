import pytest

from support_info import utils


@pytest.mark.parametrize(
    'text,fmt_args,fmt_kwargs,expected_result',
    [
        ('{text} and {undefined}', (), {'text': 'TEXT'}, 'TEXT and ---'),
        (
            '{text} {text2}',
            (),
            {'text': 't1', 'text2': 't2', 't3': 't'},
            't1 t2',
        ),
        ('{} and {}', ('TEXT', 'TEXT2'), dict(), 'TEXT and TEXT2'),
    ],
)
def test_get_coupon_value(text, fmt_args, fmt_kwargs, expected_result):
    formatter = utils.BlankFormatter(default='---')
    assert formatter.format(text, *fmt_args, **fmt_kwargs) == expected_result

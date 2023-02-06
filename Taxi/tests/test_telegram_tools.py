import pytest

from taxi_buildagent import telegram_tools


@pytest.mark.parametrize(
    'value,expected',
    [
        pytest.param('', '', id='empty'),
        pytest.param('_`*[', '\\_\\`\\*\\[', id='escaping_chars'),
        pytest.param(
            ''.join([chr(i) for i in range(32, 127)]),
            ''.join(
                [
                    f'\\{chr(i)}' if chr(i) in '_`*[' else chr(i)
                    for i in range(32, 127)
                ],
            ),
            id='all_ascii',
        ),
    ],
)
def test_markdown_escape(value, expected):
    assert telegram_tools.markdown_escape(value) == expected, (
        'view telegram api for details: '
        'https://core.telegram.org/bots/api#markdown-style'
    )

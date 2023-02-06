import typing

import pytest

from taxi import i18n
from taxi import translations


@pytest.mark.parametrize('default_language', [None, 'ru'])
def test_threading_context(default_language):
    i18n.init(default_language=default_language)
    context = i18n.get_context()

    assert context.mode == 'threading'
    if default_language:
        assert context.languages == (default_language,)
    else:
        assert context.languages == tuple()

    assert i18n._('Hello, world') == 'Hello, world'
    assert i18n._('Hello, world', 37) == 'Hello, world'


@pytest.mark.parametrize('default_language', [None, 'ru'])
def test_threading_handler(default_language):
    i18n.init(translate_handler=_translate, default_language=default_language)

    context = i18n.get_context()

    assert context.mode == 'threading'
    if default_language:
        assert context.languages == (default_language,)
        assert i18n._('Hello, world') == _translate(
            'Hello, world', default_language, None,
        )
        assert i18n._('Hello, world', 37) == _translate(
            'Hello, world', default_language, 37,
        )
    else:
        assert context.languages == tuple()
        assert i18n._('Hello, world') == 'Hello, world'
        assert i18n._('Hello, world', 37) == 'Hello, world'


@pytest.mark.parametrize('default_language', ['fn', None])
def test_threading_set_context(default_language):
    i18n.init(translate_handler=_translate, default_language=default_language)

    context = i18n.get_context()
    assert context.mode == 'threading'
    assert i18n.get_context() == context, 'context'

    if default_language:
        assert context.languages == (default_language,)
        assert i18n._('Hello') == _translate('Hello', default_language)
        assert i18n._('Hello', 37) == _translate('Hello', default_language, 37)
    else:
        assert context.languages == tuple()
        assert i18n._('Hello, world') == 'Hello, world'
        assert i18n._('Hello, world', 37) == 'Hello, world'

    with i18n.set_context(languages=['ru']) as context_with:
        assert i18n.get_context() == context_with
        assert context_with != context
        assert context_with.mode == 'threading'
        if default_language:
            assert context_with.languages == ('ru', default_language)
        else:
            assert context_with.languages == ('ru',)
        assert i18n._('Hello, world') == _translate('Hello, world', 'ru')
        assert i18n._('Hell', 37) == _translate('Hell', 'ru', 37)

    assert i18n.get_context() == context, '__exit__ restored context'


@pytest.mark.parametrize('default_language', [None, 'ru'])
async def test_task_context(default_language):
    i18n.init(default_language=default_language)
    context = i18n.get_context()

    assert context.mode == 'task'
    if default_language:
        assert context.languages == (default_language,)
    else:
        assert context.languages == tuple()

    assert i18n._('Hello, world') == 'Hello, world'
    assert i18n._('Hello, world', 42) == 'Hello, world'


@pytest.mark.parametrize('default_language', [None, 'ru'])
async def test_task_handler(default_language):
    i18n.init(translate_handler=_translate, default_language=default_language)

    context = i18n.get_context()

    assert context.mode == 'task'
    if default_language:
        assert context.languages == (default_language,)
        assert i18n._('Hello, world') == _translate(
            'Hello, world', default_language, None,
        )
        assert i18n._('Hello, world', 37) == _translate(
            'Hello, world', default_language, 37,
        )
    else:
        assert context.languages == tuple()
        assert i18n._('Hello, world') == 'Hello, world'
        assert i18n._('Hello, world', 37) == 'Hello, world'


@pytest.mark.parametrize('default_language', ['fn', None])
async def test_task_set_context(default_language):
    i18n.init(translate_handler=_translate, default_language=default_language)

    context = i18n.get_context()
    assert context.mode == 'task'
    assert i18n.get_context() == context, 'context'

    if default_language:
        assert context.languages == (default_language,)
        assert i18n._('Hello') == _translate('Hello', default_language)
        assert i18n._('Hello', 37) == _translate('Hello', default_language, 37)
    else:
        assert context.languages == tuple()
        assert i18n._('Hello, world') == 'Hello, world'
        assert i18n._('Hello, world', 37) == 'Hello, world'

    async with i18n.set_context(languages=['ru']) as context_with:
        assert i18n.get_context() == context_with
        assert context_with != context
        assert context_with.mode == 'task'
        if default_language:
            assert context_with.languages == ('ru', default_language)
        else:
            assert context_with.languages == ('ru',)
        assert i18n._('Hello, world') == _translate('Hello, world', 'ru')
        assert i18n._('Hell', 37) == _translate('Hell', 'ru', 37)

    assert i18n.get_context() == context, '__exit__ restored context'


def _translate(
        message: str,
        language: str,
        num: typing.Optional[int] = None,
        keyset: typing.Union[translations.TranslationBlock, str, None] = None,
) -> str:
    return '{}:{}#{}'.format(language, message, num)

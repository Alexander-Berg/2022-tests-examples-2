import pytest


def _get_calls(mock):
    calls = []
    while mock.has_calls:
        calls.append(mock.next_call())
    assert not mock.has_calls
    return calls


@pytest.fixture(name='abc_mock')
def _abc_mock(mockserver):
    @mockserver.json_handler('/client-abc/v3/services/')
    def _handler(request):
        return {'results': []}

    return _handler


async def test_use_from_secdist(library_context, abc_mock):
    await library_context.abc_api.service('slug', [])

    calls = _get_calls(abc_mock)
    assert len(calls) == 1
    assert calls[0]['request'].headers['Authorization'] == 'OAuth abc_oauth'


async def test_redefine(library_context, abc_mock):
    with library_context.abc_api.oauth('redefined'):
        await library_context.abc_api.service('slug', [])

    calls = _get_calls(abc_mock)
    assert len(calls) == 1
    assert calls[0]['request'].headers['Authorization'] == 'OAuth redefined'


async def test_no_redefinition_no_none(library_context, abc_mock):
    with library_context.abc_api.oauth(None):
        await library_context.abc_api.service('slug', [])

    calls = _get_calls(abc_mock)
    assert len(calls) == 1
    assert calls[0]['request'].headers['Authorization'] == 'OAuth abc_oauth'

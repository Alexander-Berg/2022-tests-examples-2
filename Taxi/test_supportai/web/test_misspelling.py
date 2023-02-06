import pytest

from supportai.utils import misspelling


@pytest.fixture(name='mock_spellchecker')
def _mock_spellchecker(mockserver):
    def define(response: dict):
        @mockserver.json_handler('/spellchecker/misspell.json/check')
        async def _(_):
            return mockserver.make_response(
                status=response.get('status', 200),
                json=response.get('json', {}),
            )

    return define


@pytest.fixture(name='correct_request')
def _correct_request():
    return {'dialog': {'messages': [{'text': 'поддержка'}]}, 'features': []}


@pytest.fixture(name='incorrect_request')
def _incorrect_request():
    return {'dialog': {'messages': [{'text': 'подiржка'}]}, 'features': []}


@pytest.fixture(name='unsolved_request')
def _unsolved_request():
    return {'dialog': {'messages': [{'text': 'подiiiiiржка'}]}, 'features': []}


async def test_correction_correct(
        web_context, mock_spellchecker, correct_request,
):
    mock_spellchecker(
        {
            'code': 200,
            'json': {
                'code': 200,
                'lang': '',
                'rule': '',
                'flags': 0,
                'r': 0,
                'f': {},
            },
        },
    )
    after_text = await misspelling.correct(
        web_context, 'test', correct_request['dialog']['messages'][0]['text'],
    )

    assert correct_request['dialog']['messages'][0]['text'] == after_text


async def test_correction_incorrect(
        web_context, mock_spellchecker, incorrect_request,
):
    mock_spellchecker(
        {
            'code': 201,
            'json': {
                'code': 201,
                'lang': 'ru,en',
                'rule': 'Misspell',
                'flags': 0,
                'r': 10000,
                'srcText': 'п(o)д(i)ржка',
                'text': 'п(о)д(де)ржка',
                'f': {},
            },
        },
    )
    after_text = await misspelling.correct(
        web_context,
        'test',
        incorrect_request['dialog']['messages'][0]['text'],
    )

    assert incorrect_request['dialog']['messages'][0]['text'] != after_text


async def test_correction_unsolved(
        web_context, mock_spellchecker, unsolved_request,
):
    mock_spellchecker(
        {
            'code': 202,
            'json': {
                'code': 202,
                'lang': 'ru,en',
                'rule': '',
                'flags': 0,
                'r': 0,
                'f': {},
            },
        },
    )
    after_text = await misspelling.correct(
        web_context, 'test', unsolved_request['dialog']['messages'][0]['text'],
    )

    assert unsolved_request['dialog']['messages'][0]['text'] == after_text

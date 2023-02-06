import http

import pytest


@pytest.mark.config(CHATTERBOX_STOP_WORDS_LIST=[r'\d'])
async def test_comment_with_stop_word(cbox):
    response = await cbox.post(
        '/v1/tasks/5b2cae5552682a976914c2a1/communicate_with_tvm',
        data={'comment': 'haha 5 haha'},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    assert await response.json() == {
        'code': 'error',
        'message': 'errors.comment_with_stop_word',
        'status': 'error',
    }

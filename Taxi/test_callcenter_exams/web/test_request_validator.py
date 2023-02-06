import pytest

from test_callcenter_exams import conftest
from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize(
    ['exam_id', 'question_id', 'code', 'resp', 'body'],
    [
        (
            'exam_1',
            'q_23',
            409,
            {
                'code': 'bad_state',
                'message': 'exam_id: exam_1, question_id: q_1',
            },
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            'expired_exam',
            'q_1',
            409,
            {'code': 'exam_expired', 'message': 'Exam Expired'},
            blackbox.PASSPORT_RESPONSE_USER_5,
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_validator(
        patch, web_app_client, exam_id, question_id, code, resp, body,
):
    @patch('callcenter_exams.api.pass_question.handle')
    async def _check(request, context):
        assert False  # should fail in request validator

    test_request = {
        'exam_data': {'question_id': question_id, 'exam_id': exam_id},
    }

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/pass_question',
        json=test_request,
        headers=conftest.pasport_headers(body['uid']['value']),
    )

    assert response.status == code
    assert await response.json() == resp

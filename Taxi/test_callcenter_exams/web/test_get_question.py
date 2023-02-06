import pytest

from test_callcenter_exams import conftest


BASE_RESPONSE = {
    'question_id': 'q_1',
    'question_position': 1,
    'questions_count': 3,
    'audio_link': 'link_1',
}

NON_FIRST_QUESTION_RESPONSE = {
    'question_id': 'q_2',
    'question_position': 2,
    'questions_count': 4,
    'audio_link': 'link_2',
}


@pytest.mark.parametrize(
    ['code', 'yandex_uid', 'exam_id', 'expected_response'],
    [
        (
            # base
            200,
            'user_1',
            'exam_1',
            BASE_RESPONSE,
        ),
        (
            # non-first question
            200,
            'user_4',
            'exam_5',
            NON_FIRST_QUESTION_RESPONSE,
        ),
        (
            # auth
            400,
            None,
            'some_exam_id',
            None,
        ),
        (
            # incorrect exam_id
            409,
            'user_1',
            'exam_2',
            None,
        ),
        (
            # invalid exam_id
            409,
            'user_1',
            'invalid_exam_id',
            None,
        ),
        (
            # finished exam
            404,
            'user_5',
            'exam_6',
            None,
        ),
        (
            # invalid user_id
            404,
            'invalid_user',
            'exam_5',
            None,
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_get_question(
        web_app_client, code, yandex_uid, exam_id, expected_response,
):

    test_request = {'exam_id': exam_id}

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/get_question',
        json=test_request,
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == code
    if code != 200:
        return
    response_json = await response.json()
    assert 1 <= response_json.get('seconds_left') <= 1800
    response_json.pop('seconds_left')
    assert response_json == expected_response

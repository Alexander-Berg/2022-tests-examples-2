import pytest

from taxi.clients import personal

from callcenter_exams.api import pass_question
from test_callcenter_exams import conftest


@pytest.mark.parametrize(
    [
        'exam_id',
        'question_id',
        'resp_code',
        'score',
        'next_question',
        'yandex_uid',
        'expected_comment',
    ],
    [
        pytest.param(
            'exam_1',
            'q_1',
            200,
            1,
            'q_2',
            'user_1',
            'startrack_comment',
            id='simple_test',
        ),
        pytest.param(
            'exam_2',
            'q_3',
            200,
            0,
            None,
            'user_2',
            'startrack_comment_no_fio',
            id='autofinish_after_last_question',
        ),
        pytest.param(
            'exam_3', 'q_3', 500, '', '', 'user_3', None, id='no_cur_answer',
        ),
        pytest.param(
            'exam_4',
            'q_2',
            500,
            '',
            '',
            'user_4',
            None,
            id='no_correct_answer',
        ),
        pytest.param(
            'demo_exam',
            'q_1',
            400,
            '',
            '',
            'user_4',
            None,
            id='demo_exam_test',
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
@pytest.mark.now('2019-12-11T12:00:00+0000')
async def test_handler(
        web_app_client,
        patch,
        mock_sticker_send,
        monkeypatch,
        pgsql,
        exam_id,
        question_id,
        resp_code,
        score,
        next_question,
        yandex_uid,
        expected_comment,
        load,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text):
        assert ticket == 'TSC-2'
        expected = load(expected_comment).strip('\n')
        got_lines = text.split('\n')
        for i, line in enumerate(got_lines):
            time_line = '**Время:**'
            if line.startswith(time_line):
                got_lines[i] = time_line
        got = '\n'.join(got_lines)
        assert got == expected
        return

    async def response_patch(*args, **kwargs):
        return {'id': 'user_id', 'email': 'user_email'}

    monkeypatch.setattr(personal.PersonalApiClient, 'find', response_patch)

    test_request = {
        'exam_data': {'question_id': question_id, 'exam_id': exam_id},
        'final_action': 'cancel',
    }

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/pass_question',
        json=test_request,
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == resp_code
    if resp_code == 200:
        response_data = dict(await response.json())
        data_keys = list(response_data.keys())
        assert data_keys in (['has_finished'], ['next_question'])
        if data_keys == ['has_finished']:
            assert response_data['has_finished'] is True
            assert mock_sticker_send.handle_urls.times_called == 1
        else:
            assert response_data['next_question'] == next_question

        with pgsql['callcenter_exams'].cursor() as cursor:
            cursor.execute(
                f'SELECT cur_question_id, score FROM '
                f'callcenter_exams.exams_pass WHERE exam_id=\'{exam_id}\'',
            )
            assert cursor.rowcount == 1
            res = cursor.fetchone()
            assert res[1] == score
            assert res[0] == next_question

            cursor.execute(
                f'SELECT question_id, result, question_stat, '
                f'correct_answer FROM '
                f'callcenter_exams.questions_pass WHERE '
                f'exam_id=\'{exam_id}\' '
                f'and question_id=\'{question_id}\'',
            )
            assert cursor.rowcount == 1
            res = cursor.fetchone()
            assert res[1] == score
            assert res[2]['final_action'] == 'cancel'
            if res[0] == 'q_1':
                correct_answer = {
                    'orderscancel': 1,
                    'final_action': 'cancel',
                    'other': 'other_info',
                }
            if res[0] == 'q_3':
                correct_answer = {'orderscancel': 1}
            assert res[3] == correct_answer
            if next_question:
                cursor.execute(
                    f'SELECT * FROM '
                    f'callcenter_exams.questions_pass WHERE '
                    f'exam_id=\'{exam_id}\' '
                    f'and question_id=\'{next_question}\'',
                )
            assert cursor.rowcount == 1


@pytest.mark.parametrize(
    ['geopoint', 'correct'],
    [
        pytest.param([37.625951, 55.759150], True),
        pytest.param([37.627188, 55.758524], False),
    ],
)
async def test_check_answer_distance(geopoint, correct):
    answer = {'orderscancel': 1, 'trash': 'aaaa'}
    cur_answer = {'orderscancel': 1, 'trash': 'aaaa'}
    ordersdraft_correct = {
        'route': [
            {'geopoint': [37.625513, 55.759035]},
            {'geopoint': [37.6259, 55.75909]},
        ],
        'other_filed': 'some_val',
    }
    ordersdraft_current = {
        'route': [{'geopoint': geopoint}, {'geopoint': [37.6259, 55.75909]}],
        'other_filed': 'some_val',
    }
    answer['ordersdraft'] = dict(ordersdraft_correct)
    cur_answer['ordersdraft'] = dict(ordersdraft_current)
    assert pass_question.check_answer(answer, cur_answer, None, 0.1) == correct


async def test_check_answer():
    cur_answer = {'orderscancel': 1}

    answer = {}
    final_action = None
    max_dist = 0.05
    assert not pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )

    answer = {'orderscancel': 1, 'trash': 'aaaa'}
    assert pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )

    answer['final_action'] = 'hangUp'
    assert not pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )
    final_action = 'hangUp'
    assert pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )
    ordersdraft = {
        'route': [
            {'geopoint': [37.625513, 55.759035]},
            {'geopoint': [37.6259, 55.75909]},
        ],
        'other_filed': 'some_val',
    }
    answer['ordersdraft'] = dict(ordersdraft)
    assert not pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )
    ordersdraft['other_filed'] = 'another_val'
    cur_answer['ordersdraft'] = dict(ordersdraft)
    assert pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )

    answer['ordersdraft']['payment'] = {'type': 'cash'}
    cur_answer['ordersdraft']['payment'] = {'type': 'card'}
    assert not pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )
    cur_answer['ordersdraft']['payment'] = {'type': 'cash'}
    assert pass_question.check_answer(
        answer, cur_answer, final_action, max_dist,
    )

import os.path

import pytest

from test_callcenter_exams import conftest


@conftest.main_configuration
@pytest.mark.now('2019-09-27T09:25:37')
@pytest.mark.parametrize(
    ['code', 'exam_id', 'yandex_uid'],
    [
        (
            # base with specific correct_answer
            200,
            'exam_1',
            'user_1',
        ),
        (
            # base with default correct_answer
            200,
            'exam_2',
            'user_1',
        ),
        (
            # auth
            400,
            'some_exam_id',
            None,
        ),
        (
            # incorrect user_id
            400,
            'exam_3',
            'user_1',
        ),
        (
            # invalid exam_id
            404,
            'invalid_exam_id',
            'user_1',
        ),
        (
            # incorrect exam_id
            400,
            'exam_4',
            'user_1',
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_finish_exam(
        web_app_client, patch, yandex_uid, code, exam_id, pgsql,
):
    test_request = {'exam_id': exam_id}

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(
            body, _timeout_ms=None, _attempts=None, log_extra=None,
    ):
        expected_answer_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/test_finish_exam/exam_report_changed.html'
            if exam_id == 'exam_1'
            else 'static/test_finish_exam/exam_report.html',
        )
        with open(expected_answer_file, 'r') as file:
            expected_body = file.read().strip('\n')

        assert body.body == expected_body

    @patch('callcenter_exams.views.finish_exam._get_exam_duration')
    def _get_duration(*args, **kwargs):
        return '1'

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/finish_exam',
        json=test_request,
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == code
    if code != 200:
        return
    assert await response.read() == b''

    # check that data is updated and correct
    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            f"""SELECT exam_id,
                       variant_id,
                       user_id,
                       cur_question_id,
                       start_time,
                       end_time,
                       score,
                       user_name,
                       group_name,
                       ticket_id
                FROM callcenter_exams.exams_pass
                WHERE exam_id=\'{exam_id}\'""",
        )
        assert cursor.rowcount == 1
        exam_pass_result = cursor.fetchone()

    user_id, cur_question_id = exam_pass_result[2:4]
    end_time = exam_pass_result[5]
    if user_id:
        assert user_id == 'user_1'
    assert not cur_question_id
    assert end_time
    assert _send_mail.call


@conftest.main_configuration
@pytest.mark.now('2019-09-27T09:25:37')
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_finish_with_group(web_app_client, patch, mockserver):
    @patch('callcenter_exams.views.finish_exam._get_exam_duration')
    def _get_duration(*args, **kwargs):
        return '1'

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(
            body, _timeout_ms=None, _attempts=None, log_extra=None,
    ):
        expected_answer_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/test_finish_exam/exam_report_2.html',
        )
        with open(expected_answer_file, 'r') as file:
            expected_body = file.read().strip('\n')

        assert body.body == expected_body

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/finish_exam',
        json={'exam_id': 'exam_5'},
        headers=conftest.pasport_headers('user_1'),
    )

    assert response.status == 200, await response.text()
    assert await response.read() == b''


@conftest.main_configuration
@pytest.mark.now('2019-09-27T09:25:37')
@pytest.mark.config(
    CC_EXAMS_MAP_JSON_TO_TEXT={
        '{\'final_action\': \'become_driver_form\'}': 'стать водителем',
    },
)
@pytest.mark.parametrize(
    ['code', 'exam_id', 'yandex_uid', 'sql_file_name', 'expected_comment'],
    [
        pytest.param(
            200,
            'exam_7',
            'user_1',
            'exam_report_1.html',
            'startrack_comment_human_readable_1',
            id='simple_map_json_to_text',
        ),
        pytest.param(
            200,
            'exam_8',
            'user_1',
            'exam_report_3.html',
            'startrack_comment_human_readable_2',
            id='logic_with_order',
        ),
    ],
)
@pytest.mark.pgsql(
    'callcenter_exams', files=['callcenter_exams_for_map_json_to_text.sql'],
)
async def test_finish_exam_map_json_to_text(
        web_app_client,
        patch,
        yandex_uid,
        sql_file_name,
        expected_comment,
        code,
        exam_id,
        pgsql,
        load,
):
    test_request = {'exam_id': exam_id}

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(
            body, _timeout_ms=None, _attempts=None, log_extra=None,
    ):
        expected_answer_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/test_finish_exam/',
            sql_file_name,
        )
        with open(expected_answer_file, 'r') as file:
            expected_body = file.read().strip('\n')

        assert body.body == expected_body

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text):
        assert ticket == 'EXAM-123'
        expected = load(expected_comment).strip('\n')
        got_lines = text.split('\n')
        for i, line in enumerate(got_lines):
            time_line = '**Время:**'
            if line.startswith(time_line):
                got_lines[i] = time_line
        got = '\n'.join(got_lines)
        assert got == expected
        return

    @patch('callcenter_exams.views.finish_exam._get_exam_duration')
    def _get_duration(*args, **kwargs):
        return '1'

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/flow/v1/finish_exam',
        json=test_request,
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == code
    if code != 200:
        return
    assert await response.read() == b''

    # check that data is updated and correct
    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            f"""SELECT exam_id,
                       variant_id,
                       user_id,
                       cur_question_id,
                       start_time,
                       end_time,
                       score,
                       user_name,
                       group_name,
                       ticket_id
                FROM callcenter_exams.exams_pass
                WHERE exam_id=\'{exam_id}\'""",
        )
        assert cursor.rowcount == 1
        exam_pass_result = cursor.fetchone()

    user_id, cur_question_id = exam_pass_result[2:4]
    end_time = exam_pass_result[5]
    if user_id:
        assert user_id == 'user_1'
    assert not cur_question_id
    assert end_time
    assert _send_mail.call

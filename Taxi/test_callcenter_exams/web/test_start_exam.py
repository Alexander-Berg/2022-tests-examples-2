import pytest

from test_callcenter_exams import conftest


HANDLE_URL = '/cc/v1/callcenter-exams/flow/v1/start_exam'


@pytest.mark.config(CC_EXAMS_ATTEMPTS_LIMIT=2)
@pytest.mark.parametrize(
    ['code', 'yandex_uid', 'expected_exam_id'],
    [
        (200, 'user_1', None),
        (400, None, None),
        (200, 'user_3', 'exam_4'),
        (409, 'many_attempts_user', None),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_start_exam(
        web_app_client, code, yandex_uid, expected_exam_id, pgsql,
):
    response = await web_app_client.post(
        HANDLE_URL,
        json={'user_name': 'Uasya'},
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == code
    if code != 200:
        return

    response_json = await response.json()
    exam_id = response_json['exam_id']
    if expected_exam_id:
        assert exam_id == expected_exam_id

    # check that data is created and correct
    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            'SELECT user_id, ticket_id, user_name '
            'FROM callcenter_exams.exams_pass '
            f'WHERE exam_id=\'{exam_id}\'',
        )
        assert cursor.rowcount == 1
        exam_pass_result = cursor.fetchone()

        if code == 200 and not expected_exam_id:
            cursor.execute(
                'SELECT * FROM '
                'callcenter_exams.questions_pass WHERE '
                f'exam_id=\'{exam_id}\'',
            )
            assert cursor.rowcount == 1

    assert exam_pass_result[1] is None
    user_id = exam_pass_result[0]
    if user_id:
        assert user_id == yandex_uid
    if expected_exam_id is None:  # new exam
        assert exam_pass_result[-1] == 'Uasya'


@pytest.mark.config(CC_EXAMS_ALLOWED_TICKETS=['EXAM'])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_start_with_group_and_ticket(web_app_client, patch, pgsql):
    user_name = 'Vasyutka'
    group_name = 'vezet_hiring'
    ticket_id = 'EXAM-123'
    yandex_uid = 'user_1'

    response = await web_app_client.post(
        HANDLE_URL,
        json={
            'user_name': user_name,
            'group': group_name,
            'ticket_id': ticket_id,
        },
        headers=conftest.pasport_headers(yandex_uid),
    )

    assert response.status == 200, await response.text()

    response_json = await response.json()
    exam_id = response_json['exam_id']
    assert len(exam_id) == 32  # new uuid

    # check that data is created and correct
    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            'SELECT user_id, user_name, group_name, ticket_id '
            'FROM callcenter_exams.exams_pass '
            f'WHERE exam_id=\'{exam_id}\'',
        )
        assert cursor.rowcount == 1
        exam_pass_result = cursor.fetchone()

    assert exam_pass_result[0] == yandex_uid
    assert exam_pass_result[1] == user_name
    assert exam_pass_result[2] == group_name
    assert exam_pass_result[3] == ticket_id


@pytest.mark.config(CC_EXAMS_ALLOWED_TICKETS=['EXAM'])
@pytest.mark.now('2021-05-16T05:05:57.253Z')
@conftest.main_configuration
@pytest.mark.parametrize(
    ['ticket_id', 'group', 'expected_status'],
    [
        ('EXAM-123', 'v', 200),
        ('exam-123', 'v', 400),
        ('EXAM', 'v', 400),
        ('EXAM-123 ', 'v', 400),
        ('blablabla', 'v', 400),
        ('EXAM-123', '1234aaAA._-', 200),
        ('EXAM-123', 'группа', 400),
        ('EXAM-123', 'v vezet', 400),
        (None, 'v', 400),
        ('EXAMM-123', 'v', 400),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_start_exam_validation(
        web_app_client, ticket_id, group, expected_status,
):
    body = {'group': group}
    if ticket_id:
        body['ticket_id'] = ticket_id
    response = await web_app_client.post(
        HANDLE_URL, json=body, headers=conftest.pasport_headers('user_1'),
    )

    assert response.status == expected_status


@pytest.mark.config(CC_EXAMS_ATTEMPTS_LIMIT=2)
@pytest.mark.parametrize(
    ['yandex_uid'],
    [('user_1',), ('<h1>xss<h1>',), ('user_3',), ('many_attempts_user',)],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_bad_user_name(web_app_client, yandex_uid, pgsql):
    response = await web_app_client.post(
        HANDLE_URL,
        json={'user_name': yandex_uid},
        headers=conftest.pasport_headers('user_3'),
    )
    assert response.status == 400


@pytest.mark.config(CC_EXAMS_ATTEMPTS_LIMIT=2)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_too_long_user_name(web_app_client, pgsql):
    response = await web_app_client.post(
        HANDLE_URL,
        json={'user_name': 'a' * 51},
        headers=conftest.pasport_headers('user_3'),
    )
    assert response.status == 400

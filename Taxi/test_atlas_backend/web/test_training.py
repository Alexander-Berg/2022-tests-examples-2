# pylint: disable=C0103, W0603
import datetime

import bson
import pytest

from generated.models import sticker as sticker_api


NOW = datetime.datetime(2020, 10, 20, 0, 0, 0)


async def test_delete_question(web_app_client, db):
    id_to_del = '5bad10ab94c14209ed7800a9'
    # test happy path
    find_result = await db.atlas_training_questions.find_one(
        {'_id': bson.ObjectId(id_to_del)},
    )
    assert find_result is not None

    response = await web_app_client.post(
        '/api/training/delete_question', json={'_id': id_to_del},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'delete_status': 'success'}

    find_result = await db.atlas_training_questions.find_one(
        {'_id': bson.ObjectId(id_to_del)},
    )
    assert find_result is None

    # test delete missed _id
    response = await web_app_client.post(
        '/api/training/delete_question', json={'_id': id_to_del},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'delete_status': 'success'}


async def test_drop_answers(web_app_client, db):
    response = await web_app_client.get('/api/training/drop_answers')
    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'ok'}

    documents_count = await db.atlas_training_user_answers.count({})
    assert documents_count == 0


async def test_get_all_questions(web_app_client, db):
    response = await web_app_client.get('/api/training/get_all_questions')
    assert response.status == 200
    content = await response.json()
    assert len(content) == 3
    assert sorted(content, key=lambda x: x['_id'])[0] == {
        '_id': '5bad10ab94c14209ed7800a9',
        'answer_options': {
            '1': '50-100',
            '2': '1000-1500',
            '3': '5000-10000',
            '4': '10000-15000',
        },
        'correct_answer': '3',
        'question': (
            'В каких пределах лежит число поездок (метрика \'[Training] '
            'Поездки\') в Пекине в самый загруженный час дня на первых двух '
            'неделях сентября 2018 года?'
        ),
        'topic': 'Atlas Pixel',
        'topic_ru': 'Atlas Pixel',
        'type': 'single_answer',
    }


@pytest.mark.parametrize('username', ['training_user'])
async def test_get_question(username, atlas_blackbox_mock, web_app_client, db):
    request_body = {'topic': 'Atlas Pixel'}
    response = await web_app_client.post(
        '/api/training/get_question', json=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        '_id': '5bad127694c14209ed7800c0',
        'answer_options': {
            '1': '08:00',
            '2': '09:00',
            '3': '14:00',
            '4': '15:00',
            '5': '16:00',
            '6': '23:00',
        },
        'is_finished': False,
        'question': (
            'В какие часы в период с 2018-09-06 00:00 по 2018-09-06 21:00 '
            'средний surge (метрика \'[Training] Средний surge\') в Пекине '
            'поднимался выше 1.15?'
        ),
        'topic': 'Atlas Pixel',
        'type': 'multiple_answer',
    }


@pytest.mark.parametrize('username', ['training_user'])
async def test_get_question_empty(
        username, atlas_blackbox_mock, web_app_client, db,
):
    request_body = {'topic': 'Atlas Pixel'}
    await db.atlas_training_user_answers.insert_one(
        {
            'correct_answer': False,
            'login': 'training_user',
            'question_id': '5bad127694c14209ed7800c0',
            'timestamp': '2020-12-24 10:17:48.898370',
            'topic': 'Atlas Pixel',
        },
    )
    response = await web_app_client.post(
        '/api/training/get_question', json=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'topic': 'Atlas Pixel', 'is_finished': True}


is_mail_sended = False


@pytest.mark.config(
    ATLAS_BACKEND_EMAIL_ROBOT_CONFIG={'login': 'email_robot@yandex-team.ru'},
)
@pytest.mark.config(
    ATLAS_TRAINING={
        'excluded_emails': [
            'other_user_chef@yandex-team.ru',
            'other_user2_chef@yandex-team.ru',
        ],
    },
)
@pytest.mark.parametrize(
    'username, correct, total, response_status',
    [
        ('training_user', 1, 2, 200),
        ('other_user', 1, 1, 200),
        ('new_user', 0, 0, 400),
    ],
)
async def test_get_result(
        load_json,
        username,
        correct,
        total,
        response_status,
        atlas_blackbox_mock,
        patch,
        web_app_client,
):
    persons_response = load_json('persons_response.json')
    global is_mail_sended
    is_mail_sended = False

    @patch('staff_api.components.StaffClient.get_person')
    async def _get_person(login, fields):
        persons_response['name']['first']['ru'] = username
        persons_response['name']['last']['ru'] = 'Ололоев'
        persons_response['department_group']['department']['heads'][0][
            'person'
        ]['login'] = (
            username + '_chef'
        )  # to test not sending mails to excluded_emails

        return persons_response

    @patch('smtplib.SMTP.sendmail')
    def _sendmail(from_addr, to_addrs, msg):
        assert from_addr == 'email_robot@yandex-team.ru'
        assert to_addrs == [
            f'{username}_chef@yandex-team.ru',
            f'{username}@yandex-team.ru',
        ]
        global is_mail_sended
        is_mail_sended = True

    @patch(
        'generated.clients.sticker.StickerClient.'
        'queue_send_mail_request_internal',
    )
    async def _queue_send_mail_request_internal(
            send_mail_request: sticker_api.SendMailRequestInternal,
    ):
        data = send_mail_request.serialize()
        assert 'email_robot@yandex-team.ru' in data['body']
        assert data['send_to'] == f'{username}_chef@yandex-team.ru'
        assert data['copy_send_to'] == [f'{username}@yandex-team.ru']
        global is_mail_sended
        is_mail_sended = True

    topic = 'Atlas Pixel'
    topic_request = {'topic': topic}
    response = await web_app_client.post(
        '/api/training/get_result', json=topic_request,
    )
    assert response.status == response_status
    content = await response.json()
    if response.status == 400:
        assert content == {
            'error': (
                f'User {username} has no answers for given topic `{topic}`'
            ),
        }
        return

    assert content == {'total': total, 'correct': correct}
    # check that mail was not sended to other_user_chef@yandex-team.ru,
    # because it is in excluded_mails
    if username == 'other_user':
        assert not is_mail_sended
    else:
        assert is_mail_sended


@pytest.mark.parametrize('username', ['training_user'])
async def test_get_topics(username, atlas_blackbox_mock, web_app_client):
    response = await web_app_client.get('/api/training/get_topics')
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'questions_avail': 1,
            'questions_total': 3,
            'topic': 'Atlas Pixel',
            'topic_name': 'Atlas Pixel',
        },
    ]


async def test_upload_question(web_app_client, db):
    new_question = {
        'answer_options': {
            '1': '106552',
            '2': '104952',
            '3': '104934',
            '4': '104872',
        },
        'correct_answer': '4',
        'question': (
            'Сколько поездок (метрика "[Training] Поездки") было совершено в '
            'Пекине в период с 2018-09-10 00:00 по 2018-09-10 23:59?'
        ),
        'topic': 'Atlas Pixel',
        'topic_ru': 'Atlas Pixel',
        'type': 'single_answer',
    }
    response = await web_app_client.post(
        '/api/training/upload_question', json=new_question,
    )
    assert response.status == 200
    content = await response.json()

    assert content == {'upload_status': 'success'}

    find_result = await db.atlas_training_questions.find().to_list(None)
    assert len(find_result) == 4
    find_result = sorted(find_result, key=lambda x: x['question'])
    assert find_result[3]['question'] == (
        'Сколько поездок (метрика "[Training] Поездки") было совершено в '
        'Пекине в период с 2018-09-10 00:00 по 2018-09-10 23:59?'
    )


async def test_upload_question_bad(web_app_client, db):
    bad_question = {'answer_options': {}, 'correct_answer': ''}
    response = await web_app_client.post(
        '/api/training/upload_question', json=bad_question,
    )
    assert response.status == 400
    content = await response.json()

    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {'reason': 'question is required property'},
        'message': 'Some parameters are invalid',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'username, answers_count, question_id, answer, expected_correct',
    [
        ('training_user', 2, '5bad10ab94c14209ed7800a9', ['3'], True),
        ('other_user', 1, '5bad127694c14209ed7800c0', ['1', '4'], True),
        ('new_user', 0, '5bad127694c14209ed7800c0', ['1', '5'], False),
        ('new_user', 0, '5bad11d094c14209ed7800b8', ['2'], False),
    ],
)
async def test_validate_answer(
        username,
        answers_count,
        answer,
        expected_correct,
        question_id,
        atlas_blackbox_mock,
        web_app_client,
        db,
):
    answers = await db.atlas_training_user_answers.find(
        {'login': username},
    ).to_list(None)
    assert len(answers) == answers_count

    request_body = {'_id': question_id, 'answer': answer}
    response = await web_app_client.post(
        '/api/training/validate_answer', json=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'correct': expected_correct}

    new_answer = await db.atlas_training_user_answers.find_one(
        {
            'login': username,
            'question_id': question_id,
            'timestamp': (
                '2020-10-20 00:00:00'  # first test is duplicate answer
            ),
        },
    )
    del new_answer['_id']

    assert new_answer == {
        'correct_answer': expected_correct,
        'login': username,
        'question_id': question_id,
        'timestamp': '2020-10-20 00:00:00',
        'topic': 'Atlas Pixel',
    }

import pytest

INSERT_ANSWERS = """
INSERT INTO holidays.user_answers (
    yandex_uid,
    session,
    answers
) VALUES ('{}', '{}', '{}')
"""

GET_ALL_ANSWERS = """
SELECT
    yandex_uid,
    session,
    bound_sessions,
    answers,
    updated
FROM holidays.user_answers;
"""

HANDLER = pytest.mark.parametrize(
    'handler',
    [
        'lavka/v1/holidays/v1/get-new-year-answers',
        'internal/v1/holidays/v1/get-new-year-answers',
    ],
)


def get_answers(pgsql):
    cursor = pgsql['grocery_holidays'].cursor()

    cursor.execute(GET_ALL_ANSWERS)
    result = list(cursor)
    for row in result:
        # Проверяем что поле updated не None
        assert row[4] is not None
    return result


def set_answers(pgsql, answers, yandex_uid='', session='session'):
    cursor = pgsql['grocery_holidays'].cursor()

    query = INSERT_ANSWERS
    query = query.format(
        yandex_uid, session, str(answers).replace('[', '{').replace(']', '}'),
    )

    cursor.execute(query)


def check_response(response, answers, handler):
    assert response.json()['answers'] == answers
    if 'lavka' not in handler:
        return
    character = answers[1] - 1 + (answers[3] - 1) * 4
    assert response.json()['head_info'] == {
        'character_image': f'char_{character}',
        'title': f'title_{character}',
        'subtitle': f'subtitle_{character}',
        'share_link': f'share_{character}',
    }


HEAD_INFO_CONFIG = pytest.mark.config(
    GROCERY_HOLIDAYS_NEW_YEAR_2022_INFO={
        'questions_size': 4,
        'character_questions': [1, 3],
        'characters_info': [
            {
                'id': i,
                'character_image': f'char_{i}',
                'title': f'title_{i}',
                'subtitle': f'subtitle_{i}',
                'share_link': f'share_{i}',
            }
            for i in range(16)
        ],
    },
)

# Проверяем что достаем верные ответы
@HEAD_INFO_CONFIG
@HANDLER
@pytest.mark.parametrize(
    'yandex_uid,session,headers',
    [
        ('', 'taxi:session', {'X-YaTaxi-Session': 'taxi:session'}),
        (
            'test_uid',
            'taxi:session',
            {'X-Yandex-UID': 'test_uid', 'X-YaTaxi-Session': 'taxi:session_2'},
        ),
    ],
)
async def test_get_answers(
        taxi_grocery_holidays, pgsql, yandex_uid, session, headers, handler,
):
    answers = [1, 2, 2, 4, 3]
    set_answers(pgsql, yandex_uid=yandex_uid, answers=answers, session=session)
    response = await taxi_grocery_holidays.post(handler, headers=headers)
    assert response.status == 200
    check_response(response, answers, handler)


# Проверяем что если появился уид то он обновится в базе
@HEAD_INFO_CONFIG
@HANDLER
async def test_uid_update(taxi_grocery_holidays, pgsql, handler):
    yandex_uid = 'test_uid'
    session_1 = 'taxi:session_1'
    session_2 = 'taxi:session_2'
    answers = [1, 2, 2, 4, 3]
    set_answers(pgsql, answers=answers, session=session_1)

    # Проверяем что уид в таблице обновляется
    response = await taxi_grocery_holidays.post(
        handler,
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': session_2,
            'X-YaTaxi-Bound-Sessions': session_1,
        },
    )
    assert response.status == 200
    check_response(response, answers, handler)
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][0] == yandex_uid
    assert in_db[0][3] == answers


# Проверяем что если не нашли в базе возвращаем 404
@HEAD_INFO_CONFIG
@HANDLER
async def test_no_answers_set(taxi_grocery_holidays, handler):
    response = await taxi_grocery_holidays.post(
        handler,
        headers={
            'X-Yandex-UID': 'yandex_uid',
            'X-YaTaxi-Session': 'taxi:session',
            'X-YaTaxi-Bound-Sessions': 'taxi:session_1',
        },
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'ANSWERS_NOT_FOUND',
        'message': 'No user answers in db.',
    }


@HEAD_INFO_CONFIG
@HANDLER
async def test_unauthorized(taxi_grocery_holidays, handler):
    response = await taxi_grocery_holidays.post(handler, headers={})
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}

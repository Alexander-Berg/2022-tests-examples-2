import pytest

GET_ALL_ANSWERS = """
SELECT
    yandex_uid,
    session,
    bound_sessions,
    answers,
    updated
FROM holidays.user_answers;
"""


def get_answers(pgsql):
    cursor = pgsql['grocery_holidays'].cursor()

    cursor.execute(GET_ALL_ANSWERS)
    result = list(cursor)
    for row in result:
        # Проверяем что поле updated не None
        assert row[4] is not None
    return result


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

# Проверяем что ответы сохраняеются в базе
# Без уида по сессии, а после добавления уида обновляется
# Так же проверяем обновление ответов
@HEAD_INFO_CONFIG
async def test_answers_insert(taxi_grocery_holidays, pgsql):
    yandex_uid = 'test_uid'
    session_1 = 'taxi:session_1'
    answers_1 = [1, 2, 2, 4, 3]
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': answers_1},
        headers={'X-YaTaxi-Session': session_1},
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert in_db[0][1] == session_1
    assert in_db[0][3] == answers_1
    session_2 = 'taxi:session_2'

    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': answers_1},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': session_2,
            'X-YaTaxi-Bound-Sessions': session_1,
        },
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][0] == yandex_uid
    assert in_db[0][1] == session_2
    assert in_db[0][3] == answers_1
    character = in_db[0][3][1] - 1 + (in_db[0][3][3] - 1) * 4
    assert response.json() == {
        'answers': answers_1,
        'head_info': {
            'character_image': f'char_{character}',
            'title': f'title_{character}',
            'subtitle': f'subtitle_{character}',
            'share_link': f'share_{character}',
        },
    }

    answers_2 = [2, 2, 3, 4, 1]
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': answers_2},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': session_2,
            'X-YaTaxi-Bound-Sessions': session_1,
        },
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][0] == yandex_uid
    assert in_db[0][1] == session_2
    assert in_db[0][3] == answers_2
    character = in_db[0][3][1] - 1 + (in_db[0][3][3] - 1) * 4
    assert response.json() == {
        'answers': answers_2,
        'head_info': {
            'character_image': f'char_{character}',
            'title': f'title_{character}',
            'subtitle': f'subtitle_{character}',
            'share_link': f'share_{character}',
        },
    }


# Проверяем что при отсутствии uid сохраняем по session
@HEAD_INFO_CONFIG
async def test_no_uid(taxi_grocery_holidays, pgsql):
    session = 'taxi:session_id'

    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': [1, 2, 2, 4, 3]},
        headers={'X-YaTaxi-Session': session},
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][1] == session
    assert in_db[0][3] == response.json()['answers']
    character = in_db[0][3][1] - 1 + (in_db[0][3][3] - 1) * 4
    assert response.json()['head_info'] == {
        'character_image': f'char_{character}',
        'title': f'title_{character}',
        'subtitle': f'subtitle_{character}',
        'share_link': f'share_{character}',
    }


# Проверяем что обновляется сессия
@HEAD_INFO_CONFIG
async def test_session_migration(taxi_grocery_holidays, pgsql):
    session_1 = 'taxi:session_1'
    answers_1 = [1, 2, 2, 4, 3]
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': answers_1},
        headers={'X-YaTaxi-Session': session_1},
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][1] == session_1
    assert in_db[0][3] == answers_1
    session_2 = 'taxi:session_2'
    answers_2 = [2, 2, 3, 4, 1]
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': answers_2},
        headers={
            'X-YaTaxi-Session': session_2,
            'X-YaTaxi-Bound-Sessions': session_1,
        },
    )
    assert response.status == 200
    in_db = get_answers(pgsql)
    assert len(in_db) == 1
    assert in_db[0][1] == session_2
    assert in_db[0][3] == answers_2
    character = in_db[0][3][1] - 1 + (in_db[0][3][3] - 1) * 4
    assert response.json() == {
        'answers': answers_2,
        'head_info': {
            'character_image': f'char_{character}',
            'title': f'title_{character}',
            'subtitle': f'subtitle_{character}',
            'share_link': f'share_{character}',
        },
    }


# Проверяем что ответы не сохраняеются если их не 5
@HEAD_INFO_CONFIG
async def test_wrong_answers_size(taxi_grocery_holidays):
    yandex_uid = 'test_uid'
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': [1, 2, 3, 4]},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': 'taxi:session',
        },
    )
    assert response.status == 400


# Проверяем что ответы не сохраняются если какой-то ответ больше 4
@HEAD_INFO_CONFIG
async def test_wrong_answers_number(taxi_grocery_holidays, pgsql):
    yandex_uid = 'test_uid'
    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/set-new-year-answers',
        json={'answers': [1, 5, 3, 4, 1]},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': 'taxi:session',
        },
    )
    assert response.status == 400

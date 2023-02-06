import pytest


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.bad': {'ru': '', 'en': ''},
        'user_chat_csat.horrible': {'ru': '', 'en': ''},
        'user_chat_csat.good': {'ru': '', 'en': ''},
        'user_chat_csat.normal': {'ru': '', 'en': ''},
        'user_chat_csat.amazing': {'ru': '', 'en': ''},
        'user_chat_csat_reasons.template_answer': {'ru': '', 'en': ''},
        'user_chat_csat_reasons.problem_not_solved': {'ru': '', 'en': ''},
        'user_chat_csat_reasons.disagree_solution': {'ru': '', 'en': ''},
        'user_chat_csat_reasons.long_answer': {'ru': '', 'en': ''},
    },
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
def test_get_user_messages(taxi_protocol, load, db, now):
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}

    # First request
    response = taxi_protocol.post('3.0/get_user_messages', request)
    assert response.status_code == 200
    assert response.json() == {
        'chat_open': True,
        'chat_visible': True,
        'ask_csat': False,
        'new_messages': 2,
        'avatar_url': '',
        'support_name': '',
        'messages': [
            {
                'author': 'user',
                'body': 'Привет!',
                'type': 'text',
                'timestamp': '2017-06-29T07:55:32+0000',
            },
            {
                'author': 'support',
                'body': 'Добрый день!',
                'type': 'text',
                'timestamp': '2017-06-29T07:56:32+0000',
            },
            {
                'author': 'support',
                'body': 'Чем могу помочь?',
                'type': 'text',
                'timestamp': '2017-06-29T07:56:42+0000',
            },
        ],
    }

    # First request changes document state in mongo - check that:
    chat_doc = db.user_chat_messages.find_one(
        {'user_id': 'b300bda7d41b4bae8d58dfa93221ef16'},
    )
    assert chat_doc['new_messages'] == 0
    assert chat_doc['send_push'] is False
    assert chat_doc['updated'] == now

    # No visible chats result in a pre-defined empty response
    db.user_chat_messages.update(
        {'user_id': 'b300bda7d41b4bae8d58dfa93221ef16'},
        {'$set': {'visible': False}},
    )
    response = taxi_protocol.post('3.0/get_user_messages', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'messages': [],
        'chat_open': False,
        'chat_visible': False,
        'new_messages': 0,
    }


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.bad': {'ru': 'Плохо', 'en': 'Bad'},
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat.good': {'ru': 'Хорошо', 'en': 'Good'},
        'user_chat_csat.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'user_chat_csat.amazing': {'ru': 'Отлично', 'en': 'Amazing'},
        'user_chat_csat_reasons.template_answer': {
            'ru': 'Ответ шаблоном',
            'en': 'Template answer',
        },
        'user_chat_csat_reasons.problem_not_solved': {
            'ru': 'Проблема не решена',
            'en': 'Problem not solved',
        },
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
    },
)
@pytest.mark.parametrize(
    'user_id,ask_csat,result',
    [
        (
            'c18ef4392ec74a70b1aa2d21751546bd',
            True,
            {
                'chat_open': True,
                'chat_visible': True,
                'ask_csat': True,
                'new_messages': 2,
                'avatar_url': '',
                'support_name': '',
                'csat_options': [
                    {
                        'option_key': 'horrible',
                        'option_name': 'Ужасно',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'bad',
                        'option_name': 'Плохо',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'normal',
                        'option_name': 'Нормально',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'good',
                        'option_name': 'Хорошо',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'amazing',
                        'option_name': 'Отлично',
                        'reasons': [],
                    },
                ],
                'messages': [
                    {
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2017-06-29T07:55:32+0000',
                    },
                ],
            },
        ),
        (
            'f5a915894568481caff43fc46ac82cf9',
            True,
            {
                'chat_open': True,
                'chat_visible': True,
                'ask_csat': True,
                'new_messages': 2,
                'avatar_url': '',
                'support_name': '',
                'csat_options': [
                    {
                        'option_key': 'horrible',
                        'option_name': 'Horrible',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'bad',
                        'option_name': 'Bad',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'normal',
                        'option_name': 'Normal',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'good',
                        'option_name': 'Good',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'amazing',
                        'option_name': 'Amazing',
                        'reasons': [],
                    },
                ],
                'messages': [
                    {
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2017-06-29T07:55:32+0000',
                    },
                ],
            },
        ),
        (
            '910b2bd07c404047a4a8cfecacae64dc',
            False,
            {
                'chat_open': True,
                'chat_visible': True,
                'ask_csat': False,
                'new_messages': 2,
                'avatar_url': '',
                'support_name': '',
                'messages': [
                    {
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2017-06-29T07:55:32+0000',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
def test_get_user_messages_csat(
        taxi_protocol, user_id, ask_csat, result, load, db, now,
):
    request = {'id': user_id}
    response = taxi_protocol.post('3.0/get_user_messages', request)
    assert response.status_code == 200
    response = response.json()
    assert response['ask_csat'] == ask_csat
    assert response == result

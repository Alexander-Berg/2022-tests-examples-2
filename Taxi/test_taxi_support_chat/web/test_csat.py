import datetime

import bson
import pytest

from taxi.util import dates

CHAT_WAITING_QA = '5e285103779fb3831c8b4bde'
CHAT_WAITING_FINISH = '5e285103779fb3831c8b4bdd'
CHAT_COMPLETE = '5e285103779fb3831c8b4bdc'
CHAT_WO_CSAT_DIALOG = '5e285103779fb3831c8b4bd9'
CHAT_WAITING_AMAZING_REASON = '5e285103779fb3831c8b4bdb'
CHAT_NOT_FOUND = '5e285103779fb3831c8b4bbb'
CHAT_ARCHIVED = '5e285103779fb3831c8b4baa'

MOCK_NOW = '2018-07-18T11:20:00.000000'


@pytest.mark.translations(
    client_messages={
        'csat.value.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'csat.value.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'csat.value.amazing': {'ru': 'Восхитительно', 'en': 'Amazing'},
        'csat.questions.ask_quality': {
            'ru': 'Оцените качество поддержки',
            'en': 'How do you like support quality?',
        },
        'csat.questions.ask_amazing_reason': {
            'ru': 'Почему так клёво?',
            'en': 'Why so amazing?',
        },
        'csat.questions.ask_finish': {
            'ru': 'Изменить оценку',
            'en': 'Change opinion',
        },
        'csat.reason.thank_you': {'ru': 'Спасибо', 'en': 'Thank you'},
        'csat.transition.change_rating': {
            'ru': 'Поменять оценку',
            'en': 'Change rating',
        },
        'csat.transition.change_reason': {
            'ru': 'Поменять причину',
            'en': 'Change reason',
        },
    },
)
@pytest.mark.config(
    SUPPORT_CHAT_CSAT_CONTROL_ENABLED=True,
    DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
    PRO_APP_CLOSE_DIALOG_CSAT_DELAY=1,
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data, chat_id, exp3_response_key, exp3_next_response_key,'
    'expected_response_key, expected_exp3_args, expected_exp3_next_args,'
    'expected_dialog_key',
    [
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_rating_amazing',
            },
            CHAT_WAITING_QA,
            'waiting_qa_rating',
            'waiting_qa_amazing_reason',
            'waiting_qa_amazing_reason',
            {'user_locale': 'ru', 'csat_dialog_state': 'waiting_qa_rating'},
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'waiting_qa_amazing_reason',
            },
            'waiting_qa_amazing_reason',
        ),
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_reason_help_ok',
            },
            CHAT_WAITING_AMAZING_REASON,
            'waiting_qa_amazing_reason',
            'qa_amazing_waiting_finish',
            'qa_amazing_waiting_finish',
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'waiting_qa_amazing_reason',
            },
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'qa_amazing_waiting_finish',
            },
            'qa_amazing_waiting_finish',
        ),
        (
            {'request_id': 'some_request_id', 'action_id': 'change_reason'},
            CHAT_WAITING_FINISH,
            'qa_amazing_waiting_finish',
            'waiting_qa_amazing_reason',
            'waiting_qa_amazing_reason',
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'qa_amazing_waiting_finish',
            },
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'waiting_qa_amazing_reason',
            },
            'waiting_qa_amazing_reason2',
        ),
        (
            {'request_id': 'some_request_id', 'action_id': 'change_rating'},
            CHAT_WAITING_FINISH,
            'qa_amazing_waiting_finish',
            'waiting_qa_rating',
            'waiting_qa_rating',
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'qa_amazing_waiting_finish',
            },
            {'user_locale': 'ru', 'csat_dialog_state': 'waiting_qa_rating'},
            'waiting_qa_rating',
        ),
    ],
)
async def test_success(
        web_app_client,
        web_context,
        load_json,
        mock_uuid4,
        mock_exp3_get_values,
        stq,
        data,
        chat_id,
        exp3_response_key,
        exp3_next_response_key,
        expected_response_key,
        expected_exp3_args,
        expected_exp3_next_args,
        expected_dialog_key,
):
    exp3_response_map = load_json('exp3_responses.json')
    expected_responses = load_json('expected_responses.json')
    expected_dialog = load_json('expected_csat_dialog.json')
    mocked_exp3 = mock_exp3_get_values(
        exp3_response_map.get(exp3_response_key),
        exp3_response_map.get(exp3_next_response_key),
    )
    response = await web_app_client.post(f'/v1/chat/{chat_id}/csat', json=data)
    assert response.status == 200
    response_body = await response.json()
    assert response_body == expected_responses[expected_response_key]
    exp3_calls = mocked_exp3.calls
    if expected_exp3_args is None:
        assert not exp3_calls
    else:
        exp3_args = {
            arg.name: arg.value for arg in exp3_calls[0]['experiments_args']
        }
        assert expected_exp3_args.items() <= exp3_args.items()
    if expected_exp3_next_args is None:
        assert len(exp3_calls) < 2
    else:
        exp3_next_args = {
            arg.name: arg.value for arg in exp3_calls[1]['experiments_args']
        }
        assert expected_exp3_next_args.items() <= exp3_next_args.items()

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    if expected_dialog_key is None:
        assert 'csat_dialog' not in chat_doc
    else:
        assert chat_doc['csat_dialog'] == expected_dialog[expected_dialog_key]
    eta = dates.parse_timestring(MOCK_NOW, timezone='utc')
    eta += datetime.timedelta(
        minutes=web_context.config.PRO_APP_CLOSE_DIALOG_CSAT_DELAY,
    )
    stq_csat_complete_call = stq.support_chat_dialog_csat_complete.next_call()
    assert stq_csat_complete_call['eta'] == eta
    assert stq_csat_complete_call['args'] == [chat_id, MOCK_NOW]

    # Test idempotency
    response = await web_app_client.post(f'/v1/chat/{chat_id}/csat', json=data)
    assert response.status == 200

    response_body = await response.json()
    assert response_body == expected_responses[expected_response_key]

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    if expected_dialog_key is None:
        assert 'csat_dialog' not in chat_doc
    else:
        assert chat_doc['csat_dialog'] == expected_dialog[expected_dialog_key]
        assert chat_doc['open']
        assert chat_doc['visible']
        assert chat_doc['ask_csat']


@pytest.mark.config(
    SUPPORT_CHAT_CSAT_CONTROL_ENABLED=True,
    DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
)
@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.parametrize(
    'data, chat_id, exp3_response_key, expected_code',
    [
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_reason_thank_you',
            },
            CHAT_NOT_FOUND,
            'waiting_qa_rating',
            404,
        ),
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_reason_thank_you',
            },
            CHAT_ARCHIVED,
            'waiting_qa_rating',
            409,
        ),
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_reason_thank_you',
            },
            CHAT_WAITING_QA,
            'waiting_qa_rating',
            409,
        ),
        (
            {'request_id': 'some_request_id', 'action_id': 'change_rating'},
            CHAT_WO_CSAT_DIALOG,
            'waiting_qa_rating',
            409,
        ),
        (
            {'request_id': 'some_request_id', 'action_id': 'change_rating'},
            CHAT_WO_CSAT_DIALOG,
            'waiting_qa_rating',
            409,
        ),
        (
            {
                'request_id': 'some_request_id',
                'action_id': 'set_reason_thank_you',
            },
            CHAT_COMPLETE,
            None,
            409,
        ),
        (
            {
                'request_id': 'last_request_id',
                'action_id': 'set_rating_horrible',
            },
            CHAT_WAITING_AMAZING_REASON,
            None,
            409,
        ),
        (
            {'request_id': 'last_request_id', 'action_id': 'change_reason'},
            CHAT_WAITING_AMAZING_REASON,
            None,
            409,
        ),
    ],
)
async def test_error(
        web_app_client,
        web_context,
        load_json,
        mock_uuid4,
        mock_exp3_get_values,
        data,
        chat_id,
        exp3_response_key,
        expected_code,
):
    exp3_response_map = load_json('exp3_responses.json')
    mock_exp3_get_values(exp3_response_map.get(exp3_response_key))
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    response = await web_app_client.post(f'/v1/chat/{chat_id}/csat', json=data)
    assert response.status == expected_code
    if expected_code != 404:
        new_chat_doc = await web_context.mongo.user_chat_messages.find_one(
            {'_id': bson.ObjectId(chat_id)},
        )
        assert chat_doc.get('csat_dialog') == new_chat_doc.get('csat_dialog')

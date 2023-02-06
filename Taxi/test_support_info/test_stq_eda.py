import uuid

import pytest

from taxi import discovery
from taxi.clients import plotva_ml
from taxi.clients import startrack

from support_info import stq_task

UUID = 'b9ca3ae6562644bb9d1c9595ee4e3905'


@pytest.mark.translations(
    support_info={
        'eda.tracker_summary': {
            'ru': (
                'Обращение в сервис доставки еды Яндекс.Еда '
                'по заказу {order_id}'
            ),
        },
        'eda.tracker_description': {
            'ru': (
                '{feedback_comment}\n'
                'Оценка: {rating}\n'
                '{feedback_predefined_comments}\n'
                'Обратная связь запрошена: {answer_requested}'
            ),
        },
    },
)
@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={
        'support-taxi': {
            'some_field': 'SomeField',
            'rating': 'ratingFood',
            'feedback_comment': 'feedback_comment',
            'feedback_predefined_comments': 'feedback_predefined_comments',
            'ml_request_id': 'mlRequestId',
            'macro_id_ml': 'macroIdMl',
            'status_ml': 'statusMl',
            'tags_ml': 'tagsMl',
            'model_status_ml': 'modelStatusMl',
            'missed_dishes_ml': 'missedDishesMl',
            'topic_ml': 'topicMl',
            'most_probable_topic_ml': 'mostProbableTopicMl',
            'topics_probabilities_ml': 'topicsProbabilitiesMl',
        },
    },
    SUPPORT_INFO_EATS_ML_REQUEST=True,
)
@pytest.mark.parametrize(
    (
        'stq_kwargs',
        'expected_ml_request',
        'ml_response',
        'expected_create_ticket',
    ),
    [
        (
            {
                'request_id': '123',
                'user_email': 'user@yandex.ru',
                'personal_email_id': 'personal_email_id',
                'metadata': {},
                'message_text': 'Ticket creation reason',
                'tags': [],
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            {
                'ml_request_id': 'b9ca3ae6562644bb9d1c9595ee4e3905',
                'user_id': 'personal_email_id',
            },
            {
                'macro_id': 1,
                'status': 'ok',
                'tags': ['ar_checked', 'model_1'],
                'model_status': 'ok',
                'missed_dishes': [
                    {
                        'situation_type': 'отсутствует',
                        'type': 'борщ',
                        'count': 1,
                    },
                ],
                'topic': 'some_topic',
                'most_probable_topic': 'some_most_topic',
                'topics_probabilities': [0.5, 0.2, 0.3],
            },
            {
                'custom_fields': {
                    'emailFrom': 'user@yandex.ru',
                    'emailTo': ['support@yandex.ru'],
                    'emailCreatedBy': 'support@yandex.ru',
                    'ratingFood': '',
                    'feedback_comment': '',
                    'feedback_predefined_comments': '',
                    'macroIdMl': '1',
                    'missedDishesMl': 'отсутствует 1 борщ',
                    'modelStatusMl': 'ok',
                    'mostProbableTopicMl': 'some_most_topic',
                    'statusMl': 'ok',
                    'topicMl': 'some_topic',
                    'topicsProbabilitiesMl': '0.5, 0.2, 0.3',
                    'mlRequestId': UUID,
                },
                'queue': 'TESTQUEUE',
                'summary': (
                    'Обращение в сервис доставки еды Яндекс.Еда по заказу '
                ),
                'description': '\nОценка: \n\nОбратная связь запрошена: Нет',
                'tags': ['ar_checked', 'model_1', 'eda_mail_ticket'],
                'unique': '123-eda',
            },
        ),
        (
            {
                'request_id': '123',
                'user_email': 'user@yandex.ru',
                'personal_email_id': 'personal_email_id',
                'metadata': {
                    'some_field': 'value',
                    'order_id': '123_order',
                    'feedback': {'rating': 5},
                    'is_feedback_requested': True,
                    'delivery_at': '2020-04-21T13:28:48+0300',
                    'delivered_at': '2020-04-21T13:25:11+0300',
                    'payments': [1, 2, 3, 4, 5],
                },
                'message_text': 'Ticket creation reason',
                'tags': ['some_tag_from_food'],
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            {
                'feedback': {'is_required': True, 'rating': 5},
                'is_feedback_requested': True,
                'ml_request_id': UUID,
                'order_id': '123_order',
                'some_field': 'value',
                'user_id': 'personal_email_id',
                'delay_time': -217,
                'delivered_at': '2020-04-21T13:25:11+0300',
                'delivery_at': '2020-04-21T13:28:48+0300',
                'payments': {
                    'applepay': 3,
                    'card': 1,
                    'cash': 2,
                    'googlepay': 4,
                    'prepaid': 5,
                },
            },
            {
                'macro_id': 2,
                'status': 'not_reply',
                'tags': ['ar_checked', 'model_2'],
                'model_status': 'not_reply',
                'missed_dishes': [
                    {
                        'situation_type': 'отсутствует',
                        'type': 'борщ',
                        'count': 1,
                    },
                    {
                        'situation_type': 'перепутано',
                        'type': 'вок',
                        'count': 2,
                    },
                ],
                'topic': 'some_topic',
                'most_probable_topic': 'some_most_topic',
                'topics_probabilities': [0.5, 0.2, 0.3],
            },
            {
                'custom_fields': {
                    'emailFrom': 'user@yandex.ru',
                    'emailTo': ['support@yandex.ru'],
                    'emailCreatedBy': 'support@yandex.ru',
                    'SomeField': 'value',
                    'ratingFood': '5',
                    'feedback_comment': '',
                    'feedback_predefined_comments': '',
                    'macroIdMl': '2',
                    'missedDishesMl': 'отсутствует 1 борщ, перепутано 2 вок',
                    'modelStatusMl': 'not_reply',
                    'mostProbableTopicMl': 'some_most_topic',
                    'statusMl': 'not_reply',
                    'topicMl': 'some_topic',
                    'topicsProbabilitiesMl': '0.5, 0.2, 0.3',
                    'mlRequestId': UUID,
                },
                'queue': 'TESTQUEUE',
                'summary': (
                    'Обращение в сервис доставки еды Яндекс.Еда'
                    ' по заказу 123_order'
                ),
                'description': '\nОценка: 5\n\nОбратная связь запрошена: Да',
                'tags': [
                    'some_tag_from_food',
                    'ar_checked',
                    'model_2',
                    'eda_mail_ticket',
                ],
                'unique': '123-eda',
            },
        ),
        (
            {
                'request_id': '123',
                'user_email': 'user@yandex.ru',
                'personal_email_id': 'personal_email_id',
                'metadata': {
                    'locale': 'bad_locale',
                    'feedback': {
                        'rating': 3,
                        'comment': 'test_comment',
                        'predefined_comments': 'test_predefined',
                    },
                },
                'message_text': 'Ticket creation reason',
                'tags': [],
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            {
                'feedback': {
                    'comment': 'test_comment',
                    'is_required': False,
                    'predefined_comments': 'test_predefined',
                    'rating': 3,
                },
                'locale': 'bad_locale',
                'ml_request_id': UUID,
                'user_id': 'personal_email_id',
            },
            {'status': 'not_reply', 'tags': ['ar_checked']},
            {
                'custom_fields': {
                    'emailFrom': 'user@yandex.ru',
                    'emailTo': ['support@yandex.ru'],
                    'emailCreatedBy': 'support@yandex.ru',
                    'ratingFood': '3',
                    'feedback_comment': 'test_comment',
                    'feedback_predefined_comments': 'test_predefined',
                    'mlRequestId': UUID,
                    'statusMl': 'not_reply',
                },
                'queue': 'TESTQUEUE',
                'summary': (
                    'Обращение в сервис доставки еды Яндекс.Еда ' 'по заказу '
                ),
                'description': 'Ticket creation reason',
                'tags': ['ar_checked', 'eda_mail_ticket'],
                'unique': '123-eda',
            },
        ),
        (
            {
                'request_id': '123',
                'user_email': 'user@yandex.ru',
                'personal_email_id': 'personal_email_id',
                'metadata': {
                    'locale': 'ru',
                    'feedback': {
                        'rating': 3,
                        'comment': 'test_comment',
                        'predefined_comments': ['t1', 't2'],
                    },
                    'order_nr': '200421-1234573',
                    'created_at': '2020-04-21T13:04:55+0300',
                    'delivery_at': '2020-04-21T13:25:11+0300',
                    'delivered_at': '2020-04-21T13:28:48+0300',
                    'composition': [
                        {
                            'type': 'Блюдо 1',
                            'count': 1,
                            'amount': 1200,
                            'options': [],
                        },
                        {
                            'type': 'Блюдо 2',
                            'count': 1,
                            'amount': 61,
                            'options': [],
                        },
                    ],
                    'payments': [1261, 0, 0, 0, 0],
                    'promo': [],
                    'person_count': 1,
                    'promocode_used': False,
                    'total_amount': 1261,
                    'is_delay': False,
                    'is_order_feedback': True,
                    'is_feedback_requested': False,
                    'app_type': 'superapp',
                    'is_lavka': True,
                    'user_grade': 'neutral',
                    'user_name': 'user_name',
                    'is_empty_comment': False,
                    'is_pharmacy': False,
                },
                'message_text': 'Ticket creation reason',
                'tags': [],
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            {
                'app_type': 'superapp',
                'composition': [
                    {
                        'amount': 1200,
                        'count': 1,
                        'options': [],
                        'type': 'Блюдо 1',
                    },
                    {
                        'amount': 61,
                        'count': 1,
                        'options': [],
                        'type': 'Блюдо 2',
                    },
                ],
                'created_at': '2020-04-21T13:04:55+0300',
                'delay_time': 217,
                'delivered_at': '2020-04-21T13:28:48+0300',
                'delivery_at': '2020-04-21T13:25:11+0300',
                'feedback': {
                    'comment': 'test_comment',
                    'is_required': False,
                    'predefined_comments': ['t1', 't2'],
                    'rating': 3,
                },
                'is_delay': False,
                'is_empty_comment': False,
                'is_feedback_requested': False,
                'is_lavka': True,
                'is_order_feedback': True,
                'is_pharmacy': False,
                'locale': 'ru',
                'ml_request_id': UUID,
                'order_nr': '200421-1234573',
                'payments': {
                    'applepay': 0,
                    'card': 1261,
                    'cash': 0,
                    'googlepay': 0,
                    'prepaid': 0,
                },
                'person_count': 1,
                'promo': [],
                'promocode_used': False,
                'total_amount': 1261,
                'user_grade': 'neutral',
                'user_id': 'personal_email_id',
                'user_name': 'user_name',
            },
            None,
            {
                'custom_fields': {
                    'emailFrom': 'user@yandex.ru',
                    'emailTo': ['support@yandex.ru'],
                    'emailCreatedBy': 'support@yandex.ru',
                    'ratingFood': '3',
                    'feedback_comment': 'test_comment',
                    'feedback_predefined_comments': '[\'t1\', \'t2\']',
                    'mlRequestId': UUID,
                },
                'queue': 'TESTQUEUE',
                'summary': (
                    'Обращение в сервис доставки еды Яндекс.Еда ' 'по заказу '
                ),
                'description': (
                    'test_comment\nОценка: 3\n[\'t1\', \'t2\']\n'
                    'Обратная связь запрошена: Нет'
                ),
                'tags': ['eda_mail_ticket'],
                'unique': '123-eda',
            },
        ),
    ],
)
async def test_create_eda_mail_ticket(
        support_info_app_stq,
        mock_st_create_ticket,
        stq_kwargs,
        expected_ml_request,
        ml_response,
        expected_create_ticket,
        patch_aiohttp_session,
        patch,
        response_mock,
):
    plotva_ml_service = discovery.find_service('plotva-ml')

    @patch_aiohttp_session(plotva_ml_service.url, 'POST')
    def _dummy_autoreply(method, url, **kwargs):
        assert method == 'post'
        assert url == plotva_ml_service.url + '/eats/support/v1'
        assert kwargs['json'] == expected_ml_request
        if not ml_response:
            raise plotva_ml.BaseError
        return response_mock(json=ml_response)

    @patch('uuid.uuid4')
    def _uuid4(*args, **kwargs):
        return uuid.UUID(hex=UUID)

    await stq_task.create_eda_mail_ticket_stq(
        support_info_app_stq, **stq_kwargs,
    )
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket


@pytest.mark.translations(
    support_info={
        'eda.tracker_summary': {
            'ru': (
                'Обращение в сервис доставки еды Яндекс.Еда '
                'по заказу {order_id}'
            ),
        },
    },
)
async def test_eda_mail_ticket_conflict(support_info_app_stq, patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket_from_data')
    async def _ticket_create(*args, **kwargs):
        raise startrack.ConflictError

    await stq_task.create_eda_mail_ticket_stq(
        support_info_app_stq,
        request_id='123',
        user_email='user@yandex.ru',
        personal_email_id='personal_email_id',
        message_text='Ticket creation reason',
        startrack_queue='TESTQUEUE',
        destination_email='support@yandex.ru',
        metadata={},
        tags=[],
    )
    assert _ticket_create.calls


@pytest.mark.translations(
    support_info={
        'eda.chat_feedback': {
            'ru': (
                '(Танкер) Отзыв:\n'
                '{feedback_comment}\n'
                'Оценка: {rating}\n'
                '{pretty_predefined_comments}'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'stq_kwargs,expected_meta,expected_message,expected_tags',
    [
        (
            {
                'request_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'user_app': 'native',
                'locale': 'ru',
                'feedback': {
                    'comment': 'Random comment',
                    'rating': 5,
                    'predefined_comments': [],
                    'is_feedback_requested': True,
                },
            },
            {
                'request_id': '123',
                'order_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'app': 'native',
                'locale': 'ru',
                'feedback': {
                    'comment': 'Random comment',
                    'rating': 5,
                    'predefined_comments': [],
                    'is_feedback_requested': True,
                },
                'feedback_comment': 'Random comment',
                'rating': 5,
                'answer_requested': 'Да',
                'is_feedback_ticket': True,
            },
            '(Танкер) Отзыв:\nRandom comment\nОценка: 5',
            ['eda_chat_ticket'],
        ),
        (
            {
                'request_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'user_app': 'superapp',
                'locale': 'ru',
                'feedback': {
                    'comment': '',
                    'rating': 3,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': True,
                },
            },
            {
                'request_id': '123',
                'order_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'app': 'superapp',
                'locale': 'ru',
                'feedback': {
                    'comment': '',
                    'rating': 3,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': True,
                },
                'rating': 3,
                'feedback_predefined_comments': ['Predefined', 'Comments'],
                'pretty_predefined_comments': 'Predefined, Comments',
                'answer_requested': 'Да',
                'is_feedback_ticket': True,
            },
            '(Танкер) Отзыв:\n\nОценка: 3\nPredefined, Comments',
            ['eda_chat_ticket'],
        ),
        (
            {
                'request_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'user_app': 'native',
                'locale': 'en',
                'feedback': {
                    'comment': 'Random comment',
                    'rating': 1,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': False,
                },
            },
            {
                'request_id': '123',
                'order_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'app': 'native',
                'locale': 'en',
                'feedback': {
                    'comment': 'Random comment',
                    'rating': 1,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': False,
                },
                'feedback_comment': 'Random comment',
                'rating': 1,
                'feedback_predefined_comments': ['Predefined', 'Comments'],
                'pretty_predefined_comments': 'Predefined, Comments',
                'answer_requested': 'Нет',
                'is_feedback_ticket': True,
            },
            'Отзыв: Random comment',
            ['eda_chat_ticket'],
        ),
        (
            {
                'request_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'user_app': 'native',
                'locale': 'en',
                'feedback': {
                    'comment': '',
                    'rating': 1,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': True,
                },
            },
            {
                'request_id': '123',
                'order_id': '123',
                'eats_user_id': 'eats_user_id',
                'user_phone_pd_id': 'phone_id',
                'app': 'native',
                'locale': 'en',
                'feedback': {
                    'comment': '',
                    'rating': 1,
                    'predefined_comments': ['Predefined', 'Comments'],
                    'is_feedback_requested': True,
                },
                'rating': 1,
                'feedback_predefined_comments': ['Predefined', 'Comments'],
                'pretty_predefined_comments': 'Predefined, Comments',
                'answer_requested': 'Да',
                'is_feedback_ticket': True,
            },
            'Отзыв: Predefined, Comments',
            ['eda_chat_ticket'],
        ),
    ],
)
async def test_create_eda_chat_ticket(
        support_info_app_stq,
        patch,
        response_mock,
        patch_aiohttp_session,
        stq_kwargs,
        expected_meta,
        expected_message,
        expected_tags,
):
    chatterbox_url = discovery.find_service('chatterbox').url
    support_chat_url = discovery.find_service('support_chat').url

    @patch('uuid.uuid4')
    def _uuid4(*args, **kwargs):
        return uuid.UUID(hex=UUID)

    @patch_aiohttp_session(support_chat_url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        assert kwargs['json']['owner']['role'] == 'eats_app_client'
        assert kwargs['json']['owner']['id'] == stq_kwargs['eats_user_id']
        assert kwargs['json']['message']['text'] == expected_message
        return response_mock(json={'id': 'chat_id'})

    @patch_aiohttp_session(chatterbox_url, 'POST')
    def _dummy_chatterbox_request(method, url, **kwargs):
        real_tags = [
            action['tag']
            for action in kwargs['json']['metadata']['update_tags']
        ]
        real_tags.sort()
        assert real_tags == expected_tags

        real_meta = {}
        for meta_action in kwargs['json']['metadata']['update_meta']:
            real_meta[meta_action['field_name']] = meta_action['value']

        assert real_meta == expected_meta
        return response_mock(json={'id': 'task_id'})

    await stq_task.create_eda_chat_ticket_stq(
        support_info_app_stq, **stq_kwargs,
    )

    assert len(_dummy_chatterbox_request.calls) == 1
    assert len(_dummy_support_chat_request.calls) == 1

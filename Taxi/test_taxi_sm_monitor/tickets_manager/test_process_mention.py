import datetime
from typing import Set

import pytest
import pytz

from taxi_sm_monitor.api.youscan import constants
from taxi_sm_monitor.api.youscan import utils


@pytest.fixture
def territories_response():
    return {'countries': [{'_id': 'rus', 'code2': 'ru'}]}


@pytest.fixture
def territories_status():
    return 200


@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={
        'support-taxi': {
            'country': 'country',
            'youscan_author_name': 'authorName',
        },
    },
    YOUSCAN_PROFILES={
        'support-taxi': {
            'st-profile': 'support-taxi',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'taxi': 'taxi'},
        },
    },
    SUPPORTAI_PROFILES={'taxi': {'ml-project-id': 'smm_taxi'}},
    YOUSCAN_STARTRACK_PROFILES=['support-taxi', 'support-zen'],
    YOUSCAN_TOPIC_GROUP_SWITCH_TO_SUPPORTAI={'taxi': True, 'zen': True},
)
@pytest.mark.translations(
    support_tickets={
        'youscan_ticket.subject.post': {'ru': 'Youscan упоманиние: Пост'},
        'youscan_ticket.description': {
            'ru': (
                'Информация об авторе:\n'
                'Имя: {author_name}\n'
                'Ссылка на аватар: {author_avatar_url}\n'
                'Никнейм: {author_nickname}\n'
                'Ссылка на профиль: {author_url}\n'
                'Аудитория: {author_subscribers}\n\n'
                'Карточка страницы публикации:\n'
                'Имя: {channel_name}\n'
                'Ссылка на аватар: {channel_avatar_url}\n'
                'Никнейм: {channel_nickname}\n'
                'Ссылка на профиль: {channel_url}\n'
                'Аудитория: {channel_subscribers}\n\n'
                'Информация о упоминание:\n'
                'Ссылка на картинку в сообщении: {image_url}\n'
                'Тональность упоминания: {sentiment}\n'
                'Сумма всех реакций: {engagement}\n'
                'Номер темы мониторинга: {topic_id}\n'
                'Номер упоминания в теме: {mention_id}\n'
                'Группа темы: {topic_group}\n'
                'Язык сообщения: {language}\n'
                'Страна автора: {country}\n'
                'Номер дисскусии публикации: {discussion_id}\n'
                'Название темы: {topic_name}\n'
                'Количество лайков: {likes}\n'
                'Ссылка на сообщение: {url}\n'
                'Названия источника: {source_name}\n'
                'Тип публикации: {post_type}\n'
                'Тип площадки, на которой размещена публикации: '
                '{resource_type}\n'
                'Количество репостов: {reposts}\n'
                'Оценка сообщения как спам: {spam}\n'
                'Уникальный номер публикации упоминания: {post_id}\n'
                'Количество комментариев: {comments}\n'
                'Время публикации: {published}\n'
                'Название тематики: {theme_name}\n'
                'Уникальный номер тематики: {theme_id}'
            ),
        },
    },
)
async def test_process_mention_success(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        mock_territories_all_countries,
        patch_support_ai,
):
    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'},
    )
    patch_support_ai()
    mention = {
        'topic_group': 'taxi',
        'image_url': 'https://userapi.com//a657/SOIK8ZU-fHg.jpg',
        'sentiment': 'neutral',
        'engagement': 0,
        'topic_id': 83499,
        'mention_id': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'language': 'rus',
        'country': 'ru',
        'discussion_id': '-185605318_50',
        'topic_name': 'Yandex.Taxi Водители',
        'likes': 0,
        'url': 'https://vk.com/wall-185605318_50',
        'author': {
            'name': 'Таксопарк РВК',
            'avatar_url': 'https://userapi.com/PSplRx50_7I.jpg?ava=1',
            'nickname': 'taxoparkrbk',
            'url': 'http://vk.com/club185605318',
            'subscribers': 1205,
        },
        'source_name': 'vk.com',
        'post_type': 'post',
        'resource_type': 'social',
        'reposts': 0,
        'channel': {
            'name': 'Таксопарк РВК',
            'avatar_url': 'https://userapi.com/PSplRx50_7I.jpg?ava=1',
            'nickname': 'taxoparkrbk',
            'url': 'http://vk.com/club185605318',
            'subscribers': 1205,
        },
        'spam': False,
        'post_id': '-185605318_50',
        'comments': 0,
        'published': datetime.datetime(
            2019, 10, 14, 20, 57, 19, tzinfo=pytz.utc,
        ),
        'theme_name': 'Yandex.Taxi Водители',
        'theme_id': 83499,
    }

    await taxi_sm_monitor_app_stq.ticket_manager.process_mention(mention)
    response = create_func.calls[0]['kwargs']['json']
    assert response == {
        'summary': 'Youscan упоманиние: Пост',
        'queue': {'key': 'YOUSCAN'},
        'description': (
            'Информация об авторе:\n'
            'Имя: Таксопарк РВК\n'
            'Ссылка на аватар: https://userapi.com/PSplRx50_7I.jpg?ava=1\n'
            'Никнейм: taxoparkrbk\n'
            'Ссылка на профиль: http://vk.com/club185605318\n'
            'Аудитория: 1205\n\n'
            'Карточка страницы публикации:\n'
            'Имя: Таксопарк РВК\n'
            'Ссылка на аватар: https://userapi.com/PSplRx50_7I.jpg?ava=1\n'
            'Никнейм: taxoparkrbk\n'
            'Ссылка на профиль: http://vk.com/club185605318\n'
            'Аудитория: 1205\n\n'
            'Информация о упоминание:\n'
            'Ссылка на картинку в сообщении: '
            'https://userapi.com//a657/SOIK8ZU-fHg.jpg\n'
            'Тональность упоминания: neutral\n'
            'Сумма всех реакций: 0\n'
            'Номер темы мониторинга: 83499\n'
            'Номер упоминания в теме: 42095240\n'
            'Группа темы: taxi\n'
            'Язык сообщения: rus\n'
            'Страна автора: rus\n'
            'Номер дисскусии публикации: -185605318_50\n'
            'Название темы: Yandex.Taxi Водители\n'
            'Количество лайков: 0\n'
            'Ссылка на сообщение: https://vk.com/wall-185605318_50\n'
            'Названия источника: vk.com\n'
            'Тип публикации: post\n'
            'Тип площадки, на которой размещена публикации: social\n'
            'Количество репостов: 0\n'
            'Оценка сообщения как спам: False\n'
            'Уникальный номер публикации упоминания: -185605318_50\n'
            'Количество комментариев: 0\n'
            'Время публикации: 2019-10-14 20:57:19+00:00\n'
            'Название тематики: Yandex.Taxi Водители\n'
            'Уникальный номер тематики: 83499'
        ),
        'type': {'key': 'task'},
        'unique': 'test_42095240_83499_youscan',
        'country': 'rus',
        'comment': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'authorName': 'Таксопарк РВК',
        'tags': ['1', '2', constants.ML_STATUS_NOT_REPLY],
    }
    assert mock_territories_all_countries.get_all_countries.times_called


async def test_process_mention_double_request(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        patch_support_ai,
):
    create_func = patch_created_startrack_ticket(response={}, status=409)
    patch_support_ai()

    mention = {
        'topic_group': 'taxi',
        'mention_id': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'topic_id': 83499,
        'topic_name': 'Yandex.Taxi Водители',
        'url': 'https://vk.com/wall-185605318_50',
        'post_type': 'post',
        'resource_type': 'social',
        'spam': False,
        'published': datetime.datetime(
            2019, 10, 14, 20, 57, 19, tzinfo=pytz.utc,
        ),
    }

    await taxi_sm_monitor_app_stq.ticket_manager.process_mention(mention)
    assert create_func.calls


@pytest.mark.config(
    YOUSCAN_TOPIC_GROUP_SWITCH_TO_SUPPORTAI={'taxi': True, 'zen': True},
    STARTRACK_CUSTOM_FIELDS_MAP={
        'support-taxi': {
            'topic_ml': 'topicMl',
            'most_probable_topic_ml': 'mostProbableTopicMl',
            'topics_probabilities_ml': 'topicsProbabilitiesMl',
            'macro_id_ml': 'macroIdMl',
            'status_ml': 'statusMl',
            'model_ml': 'modelMl',
            'ml_request_id': 'mlRequestId',
        },
    },
    YOUSCAN_PROFILES={
        'support-taxi': {
            'st-profile': 'support-taxi',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'taxi': 'taxi'},
        },
    },
    SUPPORTAI_PROFILES={'taxi': {'ml-project-id': 'smm_taxi'}},
    YOUSCAN_STARTRACK_PROFILES=['support-taxi', 'support-zen'],
)
@pytest.mark.parametrize(
    ('ml_response', 'expected_tags', 'expected_custom_fields'),
    (
        (
            {
                'close': {},
                'features': {
                    'sure_topic': 'some_topic',
                    'most_probable_topic': 'some_topic',
                    'probabilities': [
                        {'topic_name': 'first_name', 'probability': 0.8},
                        {'topic_name': 'second_name', 'probability': 0.1},
                    ],
                },
            },
            {constants.ML_STATUS_NOT_REPLY},
            {
                'topicMl': 'some_topic',
                'mostProbableTopicMl': 'some_topic',
                'topicsProbabilitiesMl': 'first_name-0.8, second_name-0.1',
                'modelMl': '/supportai-api/v1/support_internal',
                'statusMl': 'not_reply',
            },
        ),
        (
            {
                'features': {
                    'sure_topic': 'some_topic',
                    'most_probable_topic': 'some_topic',
                    'probabilities': [
                        {'topic_name': 'first_name', 'probability': 0.8},
                        {'topic_name': 'second_name', 'probability': 0.1},
                    ],
                },
            },
            set(),
            {
                'topicMl': 'some_topic',
                'mostProbableTopicMl': 'some_topic',
                'topicsProbabilitiesMl': 'first_name-0.8, second_name-0.1',
                'modelMl': '/supportai-api/v1/support_internal',
            },
        ),
        (
            {
                'features': {
                    'most_probable_topic': 'some_topic',
                    'probabilities': [],
                },
            },
            set(),
            {
                'mostProbableTopicMl': 'some_topic',
                'topicsProbabilitiesMl': '',
                'topicMl': 'some_topic',
                'modelMl': '/supportai-api/v1/support_internal',
            },
        ),
        (
            {
                'features': {
                    'most_probable_topic': 'some_topic',
                    'probabilities': [],
                },
                'tag': {'add': ['1', '2']},
            },
            {'1', '2'},
            {
                'mostProbableTopicMl': 'some_topic',
                'topicMl': 'some_topic',
                'topicsProbabilitiesMl': '',
                'modelMl': '/supportai-api/v1/support_internal',
            },
        ),
        (
            {
                'close': {},
                'features': {
                    'most_probable_topic': 'some_topic',
                    'probabilities': [],
                },
                'tag': {'add': ['1', '2']},
            },
            {'1', '2', constants.ML_STATUS_NOT_REPLY},
            {
                'mostProbableTopicMl': 'some_topic',
                'topicMl': 'some_topic',
                'topicsProbabilitiesMl': '',
                'modelMl': '/supportai-api/v1/support_internal',
                'statusMl': 'not_reply',
            },
        ),
    ),
)
async def test_process_mention_ml(
        taxi_sm_monitor_app_stq,
        mock_territories_all_countries,
        patch_created_startrack_ticket,
        patch_support_ai,
        ml_response: dict,
        expected_tags: Set[str],
        expected_custom_fields: dict,
):
    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'},
    )
    patch_support_ai(response=ml_response)

    mention = {
        'topic_group': 'taxi',
        'mention_id': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'topic_id': 83499,
        'topic_name': 'Yandex.Taxi Водители',
        'url': 'https://vk.com/wall-185605318_50',
        'post_type': 'post',
        'resource_type': 'social',
        'spam': False,
        'published': datetime.datetime(
            2019, 10, 14, 20, 57, 19, tzinfo=pytz.utc,
        ),
    }

    await taxi_sm_monitor_app_stq.ticket_manager.process_mention(mention)
    create_func_call_json = create_func.calls[0]['kwargs']['json']

    assert expected_tags <= set(create_func_call_json.get('tags', []))

    for field, value in create_func_call_json.items():
        if field.endswith('Ml'):
            assert expected_custom_fields[field] == value

    assert 'mlRequestId' in create_func_call_json

    for field, value in expected_custom_fields.items():
        assert create_func_call_json[field] == value


@pytest.mark.parametrize('ml_status', (400, 401, 403, 500))
async def test_process_mention_ml_errors(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        mock_territories_all_countries,
        patch_support_ai,
        ml_status: int,
):
    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'},
    )

    patch_support_ai(status=ml_status)

    mention = {
        'topic_group': 'taxi',
        'mention_id': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'topic_id': 83499,
        'topic_name': 'Yandex.Taxi Водители',
        'url': 'https://vk.com/wall-185605318_50',
        'post_type': 'post',
        'resource_type': 'social',
        'spam': False,
        'published': datetime.datetime(
            2019, 10, 14, 20, 57, 19, tzinfo=pytz.utc,
        ),
    }

    await taxi_sm_monitor_app_stq.ticket_manager.process_mention(mention)
    assert create_func.calls


@pytest.mark.config(
    YOUSCAN_TOPIC_GROUP_SWITCH_TO_SUPPORTAI={'taxi': True, 'zen': True},
)
@pytest.mark.parametrize('ml_project_id', ['smm_taxi', ''])
async def test_process_mention_ml_config(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        mock_territories_all_countries,
        patch_support_ai,
        ml_project_id: str,
):
    _, profile_config = utils.get_youscan_profile_and_config(
        taxi_sm_monitor_app_stq.config, None,
    )
    supportai_profile = taxi_sm_monitor_app_stq.config.SUPPORTAI_PROFILES[
        'taxi'
    ]
    supportai_profile['ml-project-id'] = ml_project_id
    assert profile_config
    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'},
    )

    ml_func = patch_support_ai()

    mention = {
        'topic_group': 'taxi',
        'mention_id': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'topic_id': 83499,
        'topic_name': 'Yandex.Taxi Водители',
        'url': 'https://vk.com/wall-185605318_50',
        'post_type': 'post',
        'resource_type': 'social',
        'spam': False,
        'published': datetime.datetime(
            2019, 10, 14, 20, 57, 19, tzinfo=pytz.utc,
        ),
    }

    await taxi_sm_monitor_app_stq.ticket_manager.process_mention(mention)
    assert create_func.calls
    if ml_project_id:
        assert ml_func.calls
    else:
        assert not ml_func.calls

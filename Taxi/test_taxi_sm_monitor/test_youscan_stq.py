import uuid

import pytest

from taxi_sm_monitor import stq_task
from taxi_sm_monitor.api.youscan import constants


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
            'ml_request_id': 'mlRequestId',
        },
        'support-zen': {
            'country': 'country',
            'youscan_author_name': 'authorName',
            'ml_request_id': 'mlRequestId',
        },
    },
    YOUSCAN_PROFILES={
        'support-taxi': {
            'st-profile': 'support-taxi',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'yandex_taxi': 'taxi'},
        },
        'support-zen': {
            'st-profile': 'support-zen',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'yandex_taxi': 'taxi'},
        },
    },
    SUPPORTAI_PROFILES={
        'taxi': {'ml-project-id': 'smm_taxi'},
        'zen': {'ml-project-id': 'smm_dzen'},
    },
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
@pytest.mark.parametrize(
    'profile,startrack_url',
    (
        (None, 'http://test-startrack-url/'),
        ('support-taxi', 'http://test-startrack-url/'),
        ('support-zen', 'http://zen.test-startrack-url/'),
    ),
)
async def test_youscan_stq(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        mock_territories_all_countries,
        patch_support_ai,
        patch,
        profile,
        startrack_url,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'}, startrack_url=startrack_url,
    )
    patch_support_ai()
    mention = {
        'topicGroup': 'taxi',
        'imageUrl': 'true',
        'sentiment': 'neutral',
        'engagement': 0,
        'topicId': 83499,
        'mentionId': 42095240,
        'text': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'language': 'rus',
        'country': 'ru',
        'discussionId': '-185605318_50',
        'topicName': 'Yandex.Taxi Водители',
        'likes': 0,
        'url': 'https://vk.com/wall-185605318_50',
        'author': {
            'name': 'Таксопарк РВК',
            'avatarUrl': 'https://userapi.com/PSplRx50_7I.jpg?ava=1',
            'nickname': 'taxoparkrbk',
            'url': 'http://vk.com/club185605318',
            'subscribers': 1205,
        },
        'sourceName': 'vk.com',
        'postType': 'post',
        'resourceType': 'social',
        'reposts': 0,
        'channel': {
            'name': 'Таксопарк РВК',
            'avatarUrl': 'https://userapi.com/PSplRx50_7I.jpg?ava=1',
            'nickname': 'taxoparkrbk',
            'url': 'http://vk.com/club185605318',
            'subscribers': 1205,
        },
        'spam': False,
        'postId': '-185605318_50',
        'comments': 0,
        'published': '2019-10-14T20:57:19Z',
        'themeName': 'Yandex.Taxi Водители',
        'themeId': 83499,
    }

    expected_response = {
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
            'Ссылка на картинку в сообщении: true\n'
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
            'Время публикации: 2019-10-14T20:57:19Z\n'
            'Название тематики: Yandex.Taxi Водители\n'
            'Уникальный номер тематики: 83499'
        ),
        'mlRequestId': '00000000000040008000000000000000',
        'type': {'key': 'task'},
        'unique': 'test_42095240_83499_youscan',
        'country': 'rus',
        'authorName': 'Таксопарк РВК',
        'comment': 'Подключение <b>водителей</b> к <b>таксометру</b> сервиса',
        'tags': ['1', '2', constants.ML_STATUS_NOT_REPLY],
    }
    await stq_task.youscan_task(
        taxi_sm_monitor_app_stq, mention, profile=profile,
    )
    response = create_func.calls[0]['kwargs']['json']
    assert response == expected_response
    assert mock_territories_all_countries.get_all_countries.times_called

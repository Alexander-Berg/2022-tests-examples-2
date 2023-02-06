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
@pytest.mark.parametrize(
    ('mention', 'expected_response'),
    [
        (
            {
                'topicGroup': 'taxi',
                'topicId': 83500,
                'topicName': 'Yandex.Zen Показы',
                'mentionId': 42,
                'url': 'https://vk.com/wall-185605318_50',
                'published': '2019-10-14T20:57:19Z',
                'postType': 'post',
                'resourceType': 'social',
                'spam': False,
            },
            {
                'summary': 'Youscan упоманиние: Пост',
                'queue': {'key': 'YOUSCAN'},
                'type': {'key': 'task'},
                'tags': ['1', '2', constants.ML_STATUS_NOT_REPLY],
                'mlRequestId': '00000000000040008000000000000000',
                'unique': 'test_42_83500_youscan',
                'description': (
                    'Информация об авторе:\n'
                    'Имя: \n'
                    'Ссылка на аватар: \n'
                    'Никнейм: \n'
                    'Ссылка на профиль: \n'
                    'Аудитория: \n\n'
                    'Карточка страницы публикации:\n'
                    'Имя: \n'
                    'Ссылка на аватар: \n'
                    'Никнейм: \n'
                    'Ссылка на профиль: \n'
                    'Аудитория: \n\n'
                    'Информация о упоминание:\n'
                    'Ссылка на картинку в сообщении: \n'
                    'Тональность упоминания: \n'
                    'Сумма всех реакций: \n'
                    'Номер темы мониторинга: 83500\n'
                    'Номер упоминания в теме: 42\n'
                    'Группа темы: taxi\n'
                    'Язык сообщения: \n'
                    'Страна автора: \n'
                    'Номер дисскусии публикации: \n'
                    'Название темы: Yandex.Zen Показы\n'
                    'Количество лайков: \n'
                    'Ссылка на сообщение: https://vk.com/wall-185605318_50\n'
                    'Названия источника: \n'
                    'Тип публикации: post\n'
                    'Тип площадки, на которой размещена публикации: social\n'
                    'Количество репостов: \n'
                    'Оценка сообщения как спам: False\n'
                    'Уникальный номер публикации упоминания: \n'
                    'Количество комментариев: \n'
                    'Время публикации: 2019-10-14T20:57:19Z\n'
                    'Название тематики: \n'
                    'Уникальный номер тематики: '
                ),
            },
        ),
        (
            {
                'topicGroup': 'taxi',
                'country': 'ru',
                'region': 'russia',
                'city': 'MSK',
                'topicId': 12,  #
                'topicName': 'some name',  #
                'mentionId': 123,  #
                'sourceName': 'VK',
                'author': {
                    'url': 'vk.com',
                    'name': 'Some Name',
                    'nickname': 'nick',
                    'avatarUrl': 'vk.com',
                    'subscribers': 1000,
                },
                'channel': {
                    'url': 'vk.com',
                    'name': 'Some Name',
                    'avatarUrl': 'vk.com',
                    'subscribers': 1000,
                },
                'tags': ['a', 'b', 'c'],
                'title': 'Title',
                'text': 'text with key word',
                'url': 'vk.com',  #
                'published': '2019-10-14T20:57:19Z',  #
                'addedAt': '2019-10-14T20:57:19Z',
                'sentiment': 'bad',
                'imageUrl': 'vk.com',
                'language': 'ru',
                'postType': 'post',  #
                'resourceType': 'social',  #
                'spam': False,  #
                'postId': '123',
                'parentPostId': '123',
                'discussionId': '1',
                'likes': 1234,
                'reposts': 1234,
                'comments': 1234,
                'engagement': 1234,
            },
            {
                'summary': 'Youscan упоманиние: Пост',
                'queue': {'key': 'YOUSCAN'},
                'type': {'key': 'task'},
                'tags': [
                    'a',
                    'b',
                    'c',
                    '1',
                    '2',
                    constants.ML_STATUS_NOT_REPLY,
                ],
                'mlRequestId': '00000000000040008000000000000000',
                'unique': 'test_123_12_youscan',
                'authorName': 'Some Name',
                'comment': 'text with key word',
                'country': 'rus',
                'description': (
                    'Информация об авторе:\n'
                    'Имя: Some Name\n'
                    'Ссылка на аватар: vk.com\n'
                    'Никнейм: nick\n'
                    'Ссылка на профиль: vk.com\n'
                    'Аудитория: 1000\n\n'
                    'Карточка страницы публикации:\n'
                    'Имя: Some Name\n'
                    'Ссылка на аватар: vk.com\n'
                    'Никнейм: \n'
                    'Ссылка на профиль: vk.com\n'
                    'Аудитория: 1000\n\n'
                    'Информация о упоминание:\n'
                    'Ссылка на картинку в сообщении: vk.com\n'
                    'Тональность упоминания: bad\n'
                    'Сумма всех реакций: 1234\n'
                    'Номер темы мониторинга: 12\n'
                    'Номер упоминания в теме: 123\n'
                    'Группа темы: taxi\n'
                    'Язык сообщения: ru\n'
                    'Страна автора: rus\n'
                    'Номер дисскусии публикации: 1\n'
                    'Название темы: some name\n'
                    'Количество лайков: 1234\n'
                    'Ссылка на сообщение: vk.com\n'
                    'Названия источника: VK\n'
                    'Тип публикации: post\n'
                    'Тип площадки, на которой размещена публикации: social\n'
                    'Количество репостов: 1234\n'
                    'Оценка сообщения как спам: False\n'
                    'Уникальный номер публикации упоминания: 123\n'
                    'Количество комментариев: 1234\n'
                    'Время публикации: 2019-10-14T20:57:19Z\n'
                    'Название тематики: \n'
                    'Уникальный номер тематики: '
                ),
            },
        ),
    ],
)
async def test_youscan_mention_processing_with_different_fields(
        taxi_sm_monitor_app_stq,
        patch_created_startrack_ticket,
        mock_territories_all_countries,
        patch_support_ai,
        patch,
        mention,
        expected_response,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    create_func = patch_created_startrack_ticket(
        response={'key': 'TAXITEST-1'},
        startrack_url='http://test-startrack-url/',
    )
    patch_support_ai()
    await stq_task.youscan_task(taxi_sm_monitor_app_stq, mention, profile=None)
    response = create_func.calls[0]['kwargs']['json']
    assert response == expected_response
    if 'country' in mention:
        assert mock_territories_all_countries.get_all_countries.times_called

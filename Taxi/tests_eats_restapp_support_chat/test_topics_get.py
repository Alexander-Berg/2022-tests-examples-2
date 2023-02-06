# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest


@pytest.fixture
def _mock_daas(mockserver, load_json):
    @mockserver.json_handler('/daas/v1/documents/load/eda-restaurants')
    def _mock(request):
        return load_json('daas_backend_response.json')


@pytest.mark.config(
    EATS_RESTAPP_SUPPORT_CHAT_EXCLUDE_TOPICS=['Выберите вопрос'],
)
async def test_topics_get(
        _mock_daas, taxi_eats_restapp_support_chat, load_json,
):
    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/topics',
    )

    assert response.status == 200

    topics = response.json()['topics']
    expected_topics = load_json('topics.json')['topics']
    assert len(topics) == len(expected_topics)
    assert sorted(topics) == sorted(expected_topics)

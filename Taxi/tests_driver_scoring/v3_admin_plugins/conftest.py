import pytest


class TagsTopicsItemsContext:
    def __init__(self):
        self.mode = 'default'

    def set_mode(self, mode):
        self.mode = mode


@pytest.fixture(name='mock_tags_v1_topics_items', autouse=True)
def mock_tags_v1_topics_items(mockserver):
    context = TagsTopicsItemsContext()

    @mockserver.json_handler('/tags/v1/topics/items')
    def _tags_topics_items(request):
        if context.mode == 'default':
            tags_in_topic = {'tag1', 'tag2', 'tag3', 'tag4'}
            assert 'topic' in request.query
            assert request.query['topic'] == 'driver_scoring'
            assert 'tag_name' in request.query
            if request.query['tag_name'] not in tags_in_topic:
                return mockserver.make_response(
                    f'Tag {request.query["tag_name"]} was not found',
                    status=404,
                )
            return {
                'items': [
                    {
                        'topic': 'driver_scoring',
                        'tag': request.query['tag_name'],
                        'is_financial': False,
                    },
                ],
                'limit': 10,
                'offset': 0,
            }

        if context.mode == 'status_4xx':
            return mockserver.make_response(
                f'What is wrong with you', status=400,
            )

        if context.mode == 'status_5xx':
            return mockserver.make_response(
                f'What is wrong with us', status=500,
            )

        return mockserver.make_response(
            f'Incorrect mock_tags_v1_topics_items mode', status=500,
        )

    return context

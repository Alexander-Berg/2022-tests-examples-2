import pytest


@pytest.fixture(name='tags_topics_items', autouse=True)
def tags_v1_topics_items(mockserver):
    @mockserver.json_handler('/tags/v1/topics/items')
    def _tags_topics_items(request):
        assert 'topic' in request.query
        return {
            'items': [
                {
                    'topic': 'driver_scoring',
                    'tag': 'tag1',
                    'is_financial': False,
                },
                {
                    'topic': 'driver_scoring',
                    'tag': 'tag2',
                    'is_financial': False,
                },
                {
                    'topic': 'driver_scoring',
                    'tag': 'tag3',
                    'is_financial': False,
                },
                {
                    'topic': 'driver_scoring',
                    'tag': 'tag4',
                    'is_financial': False,
                },
            ],
            'limit': 1000,
            'offset': 0,
        }

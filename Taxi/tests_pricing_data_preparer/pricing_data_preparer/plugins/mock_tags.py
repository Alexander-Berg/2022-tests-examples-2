# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest


class TagsContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {'tags': []}

    def set_tags(self, tags):
        response = {'tags': tags}
        self.response = response

    def clear(self):
        self.response = {'tags': []}

    def check_request(self, request):
        data = json.loads(request.get_data())
        assert 'match' in data and data['match']


@pytest.fixture
def tags():
    return TagsContext()


@pytest.fixture
def mock_tags(mockserver, tags):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def tags_match_handler(request):
        tags.check_request(request)
        return tags.process(mockserver)

    return tags_match_handler

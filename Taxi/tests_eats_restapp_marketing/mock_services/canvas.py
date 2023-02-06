# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture(name='mock_canvas')
def mock_canvas(mockserver):
    class Context:
        @property
        def upload_archive_times_called(self) -> int:
            return upload_archive.times_called

        @property
        def create_creatives_times_called(self) -> int:
            return create_creatives.times_called

        @property
        def upload_cratives_times_called(self) -> int:
            return upload_cratives.times_called

    ctx = Context()

    @mockserver.json_handler('/canvas-api/html5/source')
    def upload_archive(request):
        return mockserver.make_response(status=201, json={'id': 'archive_id'})

    @mockserver.json_handler('/canvas-api/html5/batch')
    def create_creatives(request):
        return mockserver.make_response(
            status=200, json={'id': 'batch_id', 'creatives': [{'id': 111}]},
        )

    @mockserver.json_handler('/canvas-api/html5/direct/creatives')
    def upload_cratives(request):
        return mockserver.make_response(status=200, response='[111]')

    return ctx

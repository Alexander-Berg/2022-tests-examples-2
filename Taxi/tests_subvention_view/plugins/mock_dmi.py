# encoding=utf-8
import pytest


@pytest.fixture(name='dmi', autouse=True)
def _mock_dmi(mockserver):
    class DMIContext:
        def __init__(self):
            self.virtual_tags = None
            self.virtual_tags_response = []

        def set_virtual_tags(self, virtual_tags):
            self.virtual_tags_response = virtual_tags

    context = DMIContext()

    @mockserver.json_handler('/driver-mode-index/v1/driver/virtual_tags')
    def _virtual_tags(request):
        return {'virtual_tags': context.virtual_tags_response}

    context.virtual_tags = _virtual_tags

    return context

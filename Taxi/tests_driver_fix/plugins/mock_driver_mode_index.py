from typing import List

import pytest


@pytest.fixture(name='mock_driver_mode_index', autouse=True)
def _mock_dmi(mockserver):
    class Context:
        def __init__(self):
            self.virtual_tags = []
            self.mock_v1_driver_virtual_tags = {}

        def set_virtual_tags(self, virtual_tags: List[str]):
            self.virtual_tags = virtual_tags

    context = Context()

    @mockserver.json_handler('/driver-mode-index/v1/driver/virtual_tags')
    def v1_driver_virtual_tags(request):
        return {'virtual_tags': context.virtual_tags}

    context.mock_v1_driver_virtual_tags = v1_driver_virtual_tags

    return context

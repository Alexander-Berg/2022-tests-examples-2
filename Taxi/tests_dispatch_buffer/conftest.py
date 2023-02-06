# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from dispatch_buffer_plugins import *  # noqa: F403 F401


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param(
            'agglomeration_settings',
            marks=[
                pytest.mark.experiments3(
                    filename='agglomeration_settings.json',
                ),
            ],
        ),
    ],
)
def _exp_agglomeration_settings():
    pass

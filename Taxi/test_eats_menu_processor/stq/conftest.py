import pytest

from eats_menu_processor.stq import processing


@pytest.fixture
def run_processing(task_info, stq3_context):
    async def wrapper(*args, **kwargs):
        await processing.task(stq3_context, task_info, *args, **kwargs)

    return wrapper

import pytest


@pytest.fixture(autouse=True)
def use_mock_supportai_tasks(mock_tasks_processing_handles):
    pass

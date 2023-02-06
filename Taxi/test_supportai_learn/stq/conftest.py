import pytest


@pytest.fixture(autouse=True)
def turn_on_setup_ml_app(setup_ml_app):
    pass


@pytest.fixture(autouse=True)
def use_mock_supportai_tasks(mock_tasks_processing_handles):
    pass

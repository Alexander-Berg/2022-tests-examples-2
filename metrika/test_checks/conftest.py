import pytest


@pytest.fixture()
def decider_mock():
    class DeciderMock:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
            self.audit = []

        def add_audit(self, **kwargs):
            self.audit.append(kwargs)

    return DeciderMock


@pytest.fixture()
def client_mock():
    class ClientMock:
        def __init__(self, tasks):
            self.tasks = tasks

        def get_not_loaded_tasks(self):
            return self.tasks

    return ClientMock

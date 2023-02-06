import pytest


@pytest.fixture
def stq_mocked_queues():
    return [
        'queue1',
        'queue2',
        'queue3',
        'test',
    ]

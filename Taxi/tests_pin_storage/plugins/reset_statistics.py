import pytest


@pytest.fixture(autouse=True)
def reset_statistics(testpoint):
    @testpoint('pin-storage::components::Statistics::Reset')
    def _testpoint(_):
        pass

    return _testpoint

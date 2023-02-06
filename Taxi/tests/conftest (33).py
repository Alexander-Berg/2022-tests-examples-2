import os.path
import pytest

from easytap import Tap


class PytestTap(Tap):
    def done_testing(self) -> bool:
        if super().done_testing():
            return True
        raise RuntimeError('Failed tests')

    def __call__(self):
        return self.done_testing()


@pytest.fixture
def tap():
    return PytestTap()


@pytest.fixture
def test_cfg_dir():
    def wrapper(variant):
        directory = os.path.dirname(__file__)
        return os.path.join(directory, 'cfg', variant)
    return wrapper

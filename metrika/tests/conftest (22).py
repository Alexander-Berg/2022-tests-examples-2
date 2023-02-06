import pytest

import metrika.pylib.monitoring as mmon


@pytest.fixture
def accumulator():
    accum = mmon.Accumulator()
    return accum

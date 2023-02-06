import pytest


class Places:

    def __init__(self):
        self.in_moscow = [
            [37.58799716246824, 55.73452861215414],
            [37.642743, 55.734684],
            [37.6436004905, 55.7334752687],
            [37.5, 55.7],
            [37.587997, 55.734528],
            [37.619099, 55.621984],
            [37.581740, 55.774966],
        ]
        self.airports = []


@pytest.fixture
def places():
    return Places()

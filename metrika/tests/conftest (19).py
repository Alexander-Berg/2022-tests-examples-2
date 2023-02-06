import pytest

import metrika.pylib.certificate as mpc


@pytest.fixture
def cert():
    return mpc.Certificate(
        filename='filename',
        check_filename_exist=False,
    )

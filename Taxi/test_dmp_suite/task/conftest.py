import pytest
import mock


@pytest.fixture(autouse=True)
def ctl_mock():
    from test_dmp_suite.task import utils

    ctl = utils.WrapCtlMock()
    patch_ = mock.patch('connection.ctl.get_ctl', return_value=ctl)
    with patch_:
        yield ctl

from contextlib import suppress

import mock
import pytest

from core.errors import GpfdistNotStartedError, GpfdistError
from gpfdist import yt_to_gp_base
from .helpers import gen_process_log


@pytest.mark.parametrize('logs, expect_raise', [
    ([], pytest.raises(GpfdistNotStartedError)),
    (gen_process_log(50), pytest.raises(GpfdistError)),
    (gen_process_log(99, force_last_percent=99.99), pytest.raises(GpfdistError)),  # в gp_to_yt другой тип ошибки
    (gen_process_log(100), suppress()),  # без падения
])
def test_raise_by_process_log_yt_to_gp(logs, expect_raise):
    fake_storage = mock.Mock()
    fake_storage.get_process_log = mock.Mock(return_value=logs)
    with mock.patch('gpfdist.yt_to_gp_base.metadata_storage', new=fake_storage):
        with expect_raise:
            yt_to_gp_base._raise_by_process_log('uuid')

from contextlib import suppress

import mock
import pytest

from core.errors import GpfdistNotStartedError, GpfdistError, YTWriterCommitError
from gpfdist import gp_to_yt_base
from gpfdist.transforms.yt_writer import PRE_COMMIT_PERCENT  # используем константу из врайтера
from . helpers import gen_process_log

@pytest.mark.parametrize('cnt, expected', (
        (0, []),
        (5, [(0, 5)]),
        (10, [(0, 10)]),
        (15, [(0, 10), (10, 15)]),
))
def test_page_intervals(cnt, expected):
    result = list(gp_to_yt_base._page_intervals(cnt=cnt, page_size=10))
    assert result == expected


@pytest.mark.parametrize('logs, expect_raise', [
    ([], pytest.raises(GpfdistNotStartedError)),
    (gen_process_log(50), pytest.raises(GpfdistError)),
    (gen_process_log(99, force_last_percent=PRE_COMMIT_PERCENT), pytest.raises(YTWriterCommitError)),
    (gen_process_log(100), suppress()), # без падения
])
def test_raise_by_process_log_gp_to_yt(logs, expect_raise):
    fake_storage = mock.Mock()
    fake_storage.get_process_log = mock.Mock(return_value=logs)
    with mock.patch('gpfdist.gp_to_yt_base.metadata_storage', new=fake_storage):
        with expect_raise:
            gp_to_yt_base._raise_by_process_log('uuid')

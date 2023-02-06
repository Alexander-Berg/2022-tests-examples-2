import pytest

from taxi_billing_subventions.personal_uploads import models


@pytest.mark.nofilldb()
def test_is_terminal():
    is_terminal_by_status = {
        models.UploadStatus.INIT: False,
        models.UploadStatus.IN_PROGRESS: False,
        models.UploadStatus.SUCCEEDED: True,
        models.UploadStatus.FAILED: True,
    }
    for status in models.UploadStatus:
        expected = is_terminal_by_status[status]
        assert status.is_terminal is expected

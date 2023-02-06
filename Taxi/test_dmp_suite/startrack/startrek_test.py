import pytest
import mock
from dmp_suite.startrek.utils import StartrackAttachmentDownloader
from dmp_suite.exceptions import DWHError
from .impl import *


@mock.patch("connection.startrek.get_startrek_client", mock.MagicMock(return_value=MockStartrack()))
@pytest.mark.parametrize(
    "target_file, is_raise, expected", [
        (NOT_EXISTED_ATTACHMENT_NAME, True, {'is_error': True}),
        (NOT_EXISTED_ATTACHMENT_NAME, False, {'result': []}),
        (EXISTED_ATTACHMENT_NAME, False, {'result': [CREATED_AT_SECOND]}),
    ]
)
def test_download_task_attachment(target_file, is_raise, expected):
    st = StartrackAttachmentDownloader(TEST_TASK)
    
    if expected.get('is_error'):
        with pytest.raises(DWHError):
            st.download_task_attachment(target_file=target_file, target_folder='', is_raise=is_raise)
    else:
        st.download_task_attachment(target_file=target_file, target_folder='', is_raise=is_raise)
        attachment_downloaded = [i.createdAt for i in st._issue.attachments if i.is_downloaded]
        assert attachment_downloaded == expected.get('result')


@mock.patch("connection.startrek.get_startrek_client", mock.MagicMock(return_value=MockStartrack()))
@pytest.mark.parametrize(
    "status, expected", [
        (CURRENT_STATUS, True),
        (NEW_STATUS, False),
    ]
)
def test_check_status(status, expected):
    st = StartrackAttachmentDownloader(TEST_TASK)
    assert st.check_status(status) == expected


@mock.patch("connection.startrek.get_startrek_client", mock.MagicMock(return_value=MockStartrack()))
@pytest.mark.parametrize(
    "status, expected", [
        (CURRENT_STATUS, {'is_error': True}),
        (NEW_STATUS, {}),
    ]
)
def test_change_status(status, expected):
    st = StartrackAttachmentDownloader(TEST_TASK)
    if expected.get('is_error'):
        with pytest.raises(DWHError):
            st.change_status(status)
    else:
        st.change_status(status)
        assert st.check_status(status)

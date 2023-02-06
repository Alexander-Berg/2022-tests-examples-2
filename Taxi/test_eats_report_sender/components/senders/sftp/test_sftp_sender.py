import pytest

from eats_report_sender.components.senders import exceptions
from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


async def test_should_create_file_on_sftp(
        patch,
        stq3_context,
        load_json,
        mock_assh,
        mock_assh__connect,
        mock_assh__file,
        monkeypatch,
):

    files_list = ['reports/test_link_1.json', 'reports/test_link_2.json']

    @patch(
        'eats_report_sender.components.senders'
        '.sftp_sender.SftpSender.get_files_list_by_dir',
    )
    async def _file_list_mock(*args, **kwargs):
        return files_list

    @patch(
        'eats_report_sender.components.senders'
        '.sftp_sender.SftpSender._download_content',
    )
    async def _download_content_mock(*args, **kwargs):
        return b'file_content'

    report_data = load_json('report_data.json')['correct']
    report = api_module.Report.deserialize(report_data)
    await stq3_context.sftp_sender.send(report)
    # 1 connect
    assert mock_assh__connect.start_sftp_client.call_count == 1
    # few writes under 1 connection
    assert mock_assh__file.write.call_count == len(files_list)


async def test_should_raise_exception_if_cannot_find_credentials(
        stq3_context, load_json, patch,
):

    with pytest.raises(exceptions.CannotFindCredentialsException):
        await stq3_context.sftp_sender.send(
            api_module.Report.deserialize(
                load_json('report_data.json')['without_credentials'],
            ),
        )


async def test_get_credentials_as_string(stq3_context):

    credentials = stq3_context.sftp_sender.get_sftp_credentials(
        'brand_name_credentials_as_str',
    )
    assert credentials == {
        'host': 'test_sftp',
        'port': 22,
        'username': 'test',
        'password': 'test',
        'folder': 'test',
    }

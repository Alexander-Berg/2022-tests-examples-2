from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


async def test_should_create_file_on_mds(
        patch, stq3_context, load_json, mockserver,
):

    files_list = ['reports/test_link_1.json', 'reports/test_link_2.json']

    @patch(
        'eats_report_sender.components.senders'
        '.mds_sender.MDSSender.get_files_list_by_dir',
    )
    async def _file_list_mock(*args, **kwargs):
        return files_list

    @patch(
        'eats_report_sender.components.senders'
        '.mds_sender.MDSSender._download_content',
    )
    async def _download_content_mock(*args, **kwargs):
        return b'file_content'

    @mockserver.handler('/partner-mds-s3', prefix=True)
    async def _partner_mds(request):
        assert request.method == 'PUT'
        assert request.path in {
            '/partner-mds-s3/test_bucket/test_link_1.json',
            '/partner-mds-s3/test_bucket/test_link_2.json',
        }
        return mockserver.make_response()

    report_data = load_json('report_data.json')
    report = api_module.Report.deserialize(report_data)
    await stq3_context.mds_sender.send(report)

    assert _partner_mds.times_called == len(files_list)

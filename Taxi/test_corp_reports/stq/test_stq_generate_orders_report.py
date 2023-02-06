from corp_reports.internal import xlsx
from corp_reports.stq import corp_generate_orders_report


class DummyOrderReport(xlsx.XlsxReport):
    DATE_FORMAT = '%d.%m.%Y'
    TIME_FORMAT = '%H:%M:%S'

    def to_xlsx(self):
        return b'some binary data'

    def get_widgets(self):
        pass


async def test_generate_orders_report_happy_path(stq3_context, patch, db):
    @patch('corp_reports.internal.orders.eats2.report.Eats2Report.generate')
    async def _generate(*args, **kwargs):
        return DummyOrderReport(stq3_context.translations, locale='ru')

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(*args, **kwargs):
        assert kwargs['file_obj'] == b'some binary data'
        return 'mds_key'

    report_id = 'new_task_id000'
    await corp_generate_orders_report.task(stq3_context, report_id=report_id)

    task = await db.corp_reports.find_one({'_id': report_id})
    assert task['status'] == 'complete'
    assert (
        task['report_file']['content_type']
        == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    assert (
        task['report_file']['file_name']
        == 'orders_report_01_01_2020__01_02_2020.xlsx'
    )
    assert task['report_file']['mds_key'] == 'mds_key'


async def test_report_not_found(stq3_context):
    report_id = 'non-existing_id'
    # no errors raised when report is not found
    await corp_generate_orders_report.task(stq3_context, report_id=report_id)

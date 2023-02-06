# pylint: disable=redefined-outer-name
from sber_int_api.generated.cron import run_cron


async def test_cron_task(cron_context, patch):
    @patch('sber_int_api.email_api.mail.get_latest_email')
    def _get_latest_email(context):
        return {
            'test1@mail.ru': {'Message-Id': '1', 'Date': '1'},
            'test2@mail.ru': {'Message-Id': '2', 'Date': '2'},
        }

    @patch('sber_int_api.email_api.mail.get_xml_file')
    def _get_xml_file(message):
        return b''

    @patch('sber_int_api.email_api.xml.parse_requests')
    def _parse_requests(incoming_xml):
        return [], [], []

    @patch('sber_int_api.email_api.mail.send_email')
    def _send_email(*args):
        pass

    await run_cron.main(
        ['sber_int_api.crontasks.sync_email_requests', '-t', '0'],
    )

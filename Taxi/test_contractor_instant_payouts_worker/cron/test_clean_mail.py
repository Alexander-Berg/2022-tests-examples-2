# pylint: disable=redefined-outer-name
import pytest

from contractor_instant_payouts_worker.generated.cron import run_cron


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['tinkoff_settings'] = {
        'tinkoff_email_password': '123',
        'tinkoff_email_login': 'login@yandex-team.ru',
    }
    return simple_secdist


@pytest.mark.now('2020-08-22T23:00:00+03:00')
@pytest.mark.config(
    TINKOFF_MAIL_SETTINGS={
        'tinkoff_email': 'pobegi4@mail.ru',
        'imap_host': 'imap.yandex-team.ru',
        'imap_port': 993,
        'limit_count': 1,
    },
)
async def test_clean_mail(patch, load_binary):
    @patch('imaplib.IMAP4.open')
    @patch('imaplib.IMAP4._connect')
    @patch('imaplib.IMAP4.select')
    @patch('imaplib.IMAP4.logout')
    def _init(*args, **kwargs):
        pass

    @patch('imaplib.IMAP4.login')
    def _login(user, password):
        assert user == 'login@yandex-team.ru'
        assert password == '123'

    @patch('imaplib.IMAP4.search')
    def _search(*args):
        return 'OK', [b'1 2']

    @patch('imaplib.IMAP4.fetch')
    def _fetch(num, *args):
        return (
            'OK',
            [
                [
                    (b'1 (RFC822 {7738}', load_binary('email1.txt')),
                    b' FLAGS (\\Seen))',
                ],
                [
                    (b'2 (RFC822 {7739}', load_binary('email2.txt')),
                    b' FLAGS (\\Seen))',
                ],
            ][int(num) - 1],
        )

    @patch('imaplib.IMAP4.store')
    def _store(item, flag, deleted):
        assert flag == '+FLAGS'
        assert deleted == '\\Deleted'
        assert item in (b'1', b'2')
        return 'OK', None

    await run_cron.main(
        ['contractor_instant_payouts_worker.crontasks.clean_mail', '-t', '0'],
    )

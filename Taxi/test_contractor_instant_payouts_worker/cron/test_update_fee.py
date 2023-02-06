# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from contractor_instant_payouts_worker.generated.cron import run_cron


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['tinkoff_settings'] = {
        'tinkoff_email_password': '123',
        'tinkoff_email_login': 'login@yandex-team.ru',
    }
    return simple_secdist


@pytest.mark.pgsql(
    'contractor_instant_payouts', files=['contractor_instant_payouts.sql'],
)
@pytest.mark.config(
    TINKOFF_MAIL_SETTINGS={
        'tinkoff_email': 'pobegi4@mail.ru',
        'imap_host': 'imap.yandex-team.ru',
        'imap_port': 993,
    },
)
async def test_update_fee_1_mail(patch, load_binary, cron_context):
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
        return 'OK', [b'1']

    @patch('imaplib.IMAP4.fetch')
    def _fetch(num, *args):
        return (
            'OK',
            [
                [
                    (b'1 (RFC822 {7738}', load_binary('email1.txt')),
                    b' FLAGS (\\Seen))',
                ],
            ][int(num) - 1],
        )

    @patch('imaplib.IMAP4.store')
    def _store(*args):
        return 'OK', None

    await run_cron.main(
        [
            'contractor_instant_payouts_worker.crontasks.insert_transfer_fee',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        query, _ = cron_context.sqlt('get_all_payouts.sqlt', {})
        rows = await connection.fetch(query)
        assert len(rows) == 3
        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('00000000-0011-1001-1111-000000000000', None, '2020-01-01'),
            (
                '00000000-0001-0001-0001-000000000000',
                decimal.Decimal('10.0000'),
                datetime.datetime.now().strftime('%Y-%m-%d'),
            ),
            (
                '00000000-0011-1001-0001-000000000000',
                decimal.Decimal('12.1200'),
                datetime.datetime.now().strftime('%Y-%m-%d'),
            ),
        ]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
@pytest.mark.pgsql(
    'contractor_instant_payouts', files=['contractor_instant_payouts.sql'],
)
@pytest.mark.config(
    TINKOFF_MAIL_SETTINGS={
        'tinkoff_email': 'pobegi4@mail.ru',
        'imap_host': 'imap.yandex-team.ru',
        'imap_port': 993,
    },
)
async def test_update_fee_no_mails(patch, load_binary, cron_context):
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
        return 'OK', [b'']

    await run_cron.main(
        [
            'contractor_instant_payouts_worker.crontasks.insert_transfer_fee',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        query, _ = cron_context.sqlt('get_all_payouts.sqlt', {})
        rows = await connection.fetch(query)
        assert len(rows) == 3
        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('00000000-0001-0001-0001-000000000000', None, '2020-01-01'),
            ('00000000-0011-1001-0001-000000000000', None, '2020-01-01'),
            ('00000000-0011-1001-1111-000000000000', None, '2020-01-01'),
        ]


@pytest.mark.pgsql(
    'contractor_instant_payouts', files=['contractor_instant_payouts.sql'],
)
@pytest.mark.config(
    TINKOFF_MAIL_SETTINGS={
        'tinkoff_email': 'pobegi4@mail.ru',
        'imap_host': 'imap.yandex-team.ru',
        'imap_port': 993,
    },
)
async def test_update_fee_2_mails(patch, load_binary, cron_context):
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
    def _store(*args):
        return 'OK', None

    await run_cron.main(
        [
            'contractor_instant_payouts_worker.crontasks.insert_transfer_fee',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        query, _ = cron_context.sqlt('get_all_payouts.sqlt', {})
        rows = await connection.fetch(query)
        assert len(rows) == 3
        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                '00000000-0001-0001-0001-000000000000',
                decimal.Decimal('10.0000'),
                datetime.datetime.now().strftime('%Y-%m-%d'),
            ),
            (
                '00000000-0011-1001-0001-000000000000',
                decimal.Decimal('12.1200'),
                datetime.datetime.now().strftime('%Y-%m-%d'),
            ),
            (
                '00000000-0011-1001-1111-000000000000',
                decimal.Decimal('1.200'),
                datetime.datetime.now().strftime('%Y-%m-%d'),
            ),
        ]

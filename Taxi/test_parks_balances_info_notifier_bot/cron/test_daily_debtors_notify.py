# pylint: disable=redefined-outer-name
import pytest

from parks_balances_info_notifier_bot.generated.cron import run_cron


EXPECTED_ROW = {
    'park_id': '643753732483',
    'billing_client_id': '1351771670',
    'logistic_balance': -10000.0,
    'logistic_dynamic_threshold': -5000.0,
}

EXPECTED_MESSAGE_TABLE = (
    '!!!Статистика за день!!!\n\n'
    'Количество парков-должников: 7\n'
    '@test_user_login1 - 2\n'
    '@test_user_login2 - 1\n'
    '\nСсылка на таблицу: mocked_share_url'
)

EXPECTED_MESSAGE = (
    '!!!Статистика за день!!!\n\n'
    'Количество парков-должников: 7\n'
    '@test_user_login1 - 3\n'
    '@test_user_login2 - 3\n'
    '@test_user_login3 - 1\n'
    '@test_user_login5 - no parks\n'
    '\nСсылка на таблицу: mocked_share_url'
)


@pytest.fixture
def patch_yql(patch, load_json, mockserver):
    class YqlSqlOperationRequest:
        def run(self):
            pass

        @property
        def web_url(self):
            return 'mocked_web_url'

        @property
        def share_url(self):
            return 'mocked_share_url'

        @property
        def status(self):
            return 'COMPLETED'

        @property
        def operation_id(self):
            return 'operation_id'

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlSqlOperationRequest')
    def patch_operation_request(*args, **kwargs):
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlOperationStatusRequest')
    def patch_status_request(*args, **kwargs):
        return YqlSqlOperationRequest()


@pytest.mark.config(
    PARKS_BALANCES_INFO_NOTIFIER_BOT_ENABLED_CHAT_IDS=[12345601],
    PARKS_BALANCES_INFO_NOTIFIER_BOT_MANAGER_PARK_IDS={
        'test_user_login1': {
            'enabled': True,
            'park_ids': ['643753732483', '643753732683'],
        },
        'test_user_login2': {'enabled': True, 'park_ids': ['643753732583']},
    },
)
async def test_test_daily_debtors_notify_tables(
        yt_apply, yt_client, patch_yql, load_json, telegram,
):
    table = (
        '//home/unittests/unittests/features/parks-balances-info-notifier-bot/'
        'parks_debtors_cron_tmp'
    )
    yt_client.create_table(
        table,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': load_json('schema.json'),
        },
    )
    yt_client.write_table(table, load_json('test_daily_debtors_notify.json'))
    await run_cron.main(
        [
            'parks_balances_info_notifier_bot.crontasks.daily_debtors_notify',
            '-t',
            '0',
        ],
    )

    assert 'parks_debtors_cron' in set(
        yt_client.list(
            '//home/unittests/unittests/features/'
            'parks-balances-info-notifier-bot',
        ),
    )

    result_table_name = (
        '//home/unittests/unittests/features/parks-balances-info-notifier-bot/'
        'parks_debtors_cron'
    )

    assert next(yt_client.read_table(result_table_name)) == EXPECTED_ROW

    assert telegram.last_request.json['chat_id'] == 12345601
    assert telegram.last_request.json['text'] == EXPECTED_MESSAGE_TABLE


@pytest.mark.config(
    PARKS_BALANCES_INFO_NOTIFIER_BOT_ENABLED_CHAT_IDS=[1234560192],
    PARKS_BALANCES_INFO_NOTIFIER_BOT_MANAGER_PARK_IDS={
        'test_user_login1': {
            'enabled': True,
            'park_ids': [
                '628753732483',
                '643753732483',
                '643753732499',
                '643753732683',
                '643753732685',
                '650101000000',
            ],
        },
        'test_user_login2': {
            'enabled': True,
            'park_ids': [
                '643753732583',
                '643753799999',
                '650000000000',
                '650000000099',
                '650000000899',
                '650001000000',
                '650091000000',
            ],
        },
        'test_user_login3': {
            'enabled': True,
            'park_ids': ['650011000000', '660000000000'],
        },
        'test_user_login4': {
            'enabled': False,
            'park_ids': ['650022000000', '660000000000'],
        },
        'test_user_login5': {'enabled': True, 'park_ids': []},
    },
)
async def test_test_daily_debtors_notify_message(
        yt_apply, yt_client, patch_yql, load_json, telegram,
):
    table = (
        '//home/unittests/unittests/features/parks-balances-info-notifier-bot/'
        'parks_debtors_cron_tmp'
    )
    yt_client.create_table(
        table,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': load_json('schema.json'),
        },
    )
    yt_client.write_table(table, load_json('test_daily_debtors_notify.json'))
    await run_cron.main(
        [
            'parks_balances_info_notifier_bot.crontasks.daily_debtors_notify',
            '-t',
            '0',
        ],
    )

    assert telegram.last_request.json['chat_id'] == 1234560192
    assert telegram.last_request.json['text'] == EXPECTED_MESSAGE

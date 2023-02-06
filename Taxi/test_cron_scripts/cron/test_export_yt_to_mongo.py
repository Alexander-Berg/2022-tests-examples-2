import datetime

import freezegun
import pytest

from infranaim.models.configs import external_config


@freezegun.freeze_time('2018-12-31T23:00:00')
@pytest.mark.parametrize(
    'name',
    [
        'ordinary',
        'locked',
        'non_existent_table',
        'collection_non_existent',
        'table_is_old',
        'no_actual_schedule',
        'daily',
    ]
)
def test_export(
        patch,
        load_json,
        mongo_create_indexes,
        get_mongo,
        run_export_yt_to_mongo,
        name,
):
    data = load_json('export_yt_to_mongo_config.json')[name]
    external_config.INFRANAIM_EXPORT_YT_TO_MONGO_SCHEDULE = data

    @patch('infranaim.clients.yt.YtClient.read_yt_table')
    def _read_table(*args, **kwargs):
        return [
            {
                'id': 1,
                'calm': 'down',
            },
        ]

    @patch('infranaim.clients.yt.YtClient.table_exists')
    def _table_exists(route: str):
        if route == 'NON_EXISTENT':
            return False
        return True

    @patch('infranaim.clients.yt.YtClient.modification_time')
    def _modification_time(route: str):
        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        if name == 'table_is_old':
            return now_utc - datetime.timedelta(days=7)
        return datetime.datetime.now(tz=datetime.timezone(
            datetime.timedelta(hours=3)),
        )

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        if name in ['ordinary', 'no_actual_schedule']:
            assert kwargs.get('chat_name') == 'LOGS'

    mongo = get_mongo
    mongo_create_indexes(mongo)
    run_export_yt_to_mongo(mongo)

    if name in ['ordinary', 'locked', 'no_actual_schedule', 'daily']:
        if name == 'ordinary':
            assert list(mongo.active_drivers.find())
            assert mongo.cron_locks.count_documents({}) == 2
        elif name == 'no_actual_schedule':
            assert list(mongo.driver_phones_in_use.find())
            assert mongo.cron_locks.count_documents({}) == 1
        else:
            assert mongo.cron_locks.count_documents({}) == 2
    else:
        assert mongo.cron_locks.count_documents({}) == 3
    assert not list(mongo.driver_plates_in_use.find())

    if name != 'locked':
        assert _telegram.calls
    else:
        assert not _telegram.calls

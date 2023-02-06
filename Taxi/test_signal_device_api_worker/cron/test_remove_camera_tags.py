# pylint: disable=unused-variable
import dateutil.parser
import pytest

from testsuite.utils import ordered_object

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.remove_camera_tags',
    '-t',
    '0',
]


@pytest.fixture(name='tags')
def _tags(mockserver):
    class Context:
        def __init__(self):
            self.remove_tags = []

        def set_signalq_remove_tags(self, *, entities):
            self.remove_tags = [
                {'name': name, 'entity': entity}
                for name in [
                    'car_with_signalq_online',
                    'car_with_signalq_online_night',
                ]
                for entity in entities
            ]

    context = Context()

    @mockserver.json_handler('/tags/v2/upload')
    def v2_upload(request):
        assert 'append' not in request.json
        request_json = request.json['remove']
        assert len(request_json) == 1
        remove = request_json[0]
        assert remove['entity_type'] == 'park_car_id'
        assert len(remove['tags']) == len(context.remove_tags)
        ordered_object.assert_eq(
            remove['tags'], context.remove_tags, paths=[''],
        )
        return {}

    return context


def _delete_records_from_events(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('DELETE FROM signal_device_api.events')


def _delete_records_from_statuses(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('DELETE FROM signal_device_api.statuses')


def _check_new_last_tag_deleted_at(deleted_at, pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT last_deleted_tag_at FROM signal_device_api.last_tags_deleted',
    )
    db_result = list(db)
    assert len(db_result) == 1
    assert db_result[0][0] == dateutil.parser.parse(deleted_at)


def _check_not_active_tags(park_car_ids, pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT park_id, car_id '
        'FROM signal_device_api.car_device_bindings '
        'WHERE NOT is_tag_active',
    )
    db_result = list(db)
    assert len(db_result) == len(park_car_ids)
    db_park_car_ids = {f'{row[0]}_{row[1]}' for row in db_result}
    if not isinstance(park_car_ids, set):
        park_car_ids = set(park_car_ids)
    assert park_car_ids == db_park_car_ids


@pytest.mark.pgsql('signal_device_api_meta_db', files=['setup_data.sql'])
@pytest.mark.now('2020-12-12T00:20:00+00:00')
async def test_ok(pgsql, tags):
    tags.set_signalq_remove_tags(
        entities=['p1_c1', 'p4_c1', 'p3_c3', 'p7_c7', 'p10_c12'],
    )

    await run_cron.main(CRON_PARAMS)

    _check_new_last_tag_deleted_at('2020-12-12 00:05:00+00:00', pgsql)
    _check_not_active_tags(
        {'p12_c14', 'p2_c2', 'p1_c1', 'p4_c1', 'p3_c3', 'p7_c7', 'p10_c12'},
        pgsql,
    )


@pytest.mark.pgsql('signal_device_api_meta_db', files=['setup_data.sql'])
@pytest.mark.now('2020-12-12T00:20:00+00:00')
async def test_no_statuses(pgsql, tags):
    tags.set_signalq_remove_tags(entities=['p7_c7', 'p10_c12'])
    _delete_records_from_statuses(pgsql)

    await run_cron.main(CRON_PARAMS)

    _check_new_last_tag_deleted_at('2020-12-12 00:00:00+00:00', pgsql)
    _check_not_active_tags({'p12_c14', 'p2_c2', 'p7_c7', 'p10_c12'}, pgsql)


@pytest.mark.pgsql('signal_device_api_meta_db', files=['setup_data.sql'])
@pytest.mark.now('2020-12-12T00:20:00+00:00')
async def test_no_events(pgsql, tags):
    tags.set_signalq_remove_tags(entities=['p1_c1', 'p4_c1', 'p3_c3'])
    _delete_records_from_events(pgsql)

    await run_cron.main(CRON_PARAMS)

    _check_new_last_tag_deleted_at('2020-12-12 00:05:00+00:00', pgsql)
    _check_not_active_tags(
        {'p12_c14', 'p2_c2', 'p1_c1', 'p4_c1', 'p3_c3'}, pgsql,
    )


@pytest.mark.pgsql('signal_device_api_meta_db', files=['setup_data.sql'])
@pytest.mark.now('2020-12-12T00:10:00+00:00')
async def test_no_tags_to_remove(pgsql, mockserver):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        assert False

    await run_cron.main(CRON_PARAMS)

    _check_new_last_tag_deleted_at('2020-12-12 00:00:00+00:00', pgsql)
    _check_not_active_tags({'p12_c14', 'p2_c2'}, pgsql)

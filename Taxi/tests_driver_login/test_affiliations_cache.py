import pytest

CACHE_NAME = 'affiliations-cache'


def _make_record(park_id, driver_id, state):
    return {
        'record_id': 'id',
        'park_id': park_id,
        'local_driver_id': driver_id,
        'state': state,
        'original_driver_park_id': 'id',
        'original_driver_id': 'id',
        'creator_uid': 'id',
        'created_at': '2020-01-01T00:00:00+03:00',
        'modified_at': '2020-01-01T00:00:00+03:00',
    }


@pytest.fixture(name='fleet_rent')
def _fleet_rent(mockserver):
    class Context:
        def __init__(self):
            self.handler_all = None
            self.records = []
            self.cursor = ''

        def set_data(self, records, cursor=None):
            self.records = [_make_record(*record) for record in records]
            if cursor is not None:
                self.cursor = cursor

    context = Context()

    @mockserver.json_handler('/fleet-rent/v1/sys/affiliations/all')
    def _fleet_rent_all(request):
        return {
            'records': context.records,
            'limit': 1000,  # not checked
            'cursor': context.cursor,
        }

    context.handler_all = _fleet_rent_all

    return context


@pytest.mark.uservice_oneshot(disable_first_update=[CACHE_NAME])
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_login_affiliation_cache(
        taxi_driver_login, testpoint, mocked_time, fleet_rent,
):
    @testpoint('affiliations_update')
    def affiliations_update(data):
        return data

    await taxi_driver_login.enable_testpoints()

    fleet_rent.set_data(
        [
            ('park_1', 'driver_1', 'park_recalled'),
            ('park_1', 'driver_2', 'active'),
        ],
        'some_cursor',
    )

    # full update
    await taxi_driver_login.invalidate_caches(
        clean_update=True, cache_names=[CACHE_NAME],
    )

    start_data = (await affiliations_update.wait_call())['data']
    assert start_data['type'] == 'full'
    assert start_data['size'] == 0
    assert start_data['cursor'] == '(none)'

    finish_data = (await affiliations_update.wait_call())['data']
    assert finish_data['type'] == 'finish'
    assert finish_data['size'] == 1
    assert finish_data['cursor'] == 'some_cursor'

    assert fleet_rent.handler_all.times_called == 1

    await taxi_driver_login.write_cache_dumps(names=[CACHE_NAME])
    await taxi_driver_login.read_cache_dumps(names=[CACHE_NAME])

    fleet_rent.set_data(
        [('park_2', 'driver_3', 'active'), ('park_2', 'driver_4', 'new')],
        'another_cursor',
    )

    # dumped updates must not be performed at the exact same time
    mocked_time.sleep(1)

    # incremental update
    await taxi_driver_login.invalidate_caches(
        clean_update=False, cache_names=[CACHE_NAME],
    )

    start_data = (await affiliations_update.wait_call())['data']
    assert start_data['type'] == 'incremental'
    assert start_data['size'] == 1
    assert start_data['cursor'] == 'some_cursor'

    finish_data = (await affiliations_update.wait_call())['data']
    assert finish_data['type'] == 'finish'
    assert finish_data['size'] == 2
    assert finish_data['cursor'] == 'another_cursor'

    assert fleet_rent.handler_all.times_called == 2

    await taxi_driver_login.write_cache_dumps(names=[CACHE_NAME])
    await taxi_driver_login.read_cache_dumps(names=[CACHE_NAME])

    # change affiliation states
    fleet_rent.set_data(
        [
            ('park_1', 'driver_1', 'park_recalled'),
            ('park_1', 'driver_2', 'active'),
            ('park_3', 'driver_5', 'active'),
        ],
        'yet_another_cursor',
    )

    # incremental update
    await taxi_driver_login.invalidate_caches(
        clean_update=False, cache_names=[CACHE_NAME],
    )

    start_data = (await affiliations_update.wait_call())['data']
    assert start_data['type'] == 'incremental'
    assert start_data['size'] == 2
    assert start_data['cursor'] == 'another_cursor'

    finish_data = (await affiliations_update.wait_call())['data']
    assert finish_data['type'] == 'finish'
    assert finish_data['size'] == 3
    assert finish_data['cursor'] == 'yet_another_cursor'

    assert fleet_rent.handler_all.times_called == 3

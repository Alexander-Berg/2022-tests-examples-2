import pytest

import testsuite


@pytest.mark.skip('flaps will be fixed in TAXIACCESSDATA-286')
@pytest.mark.config(
    PARKS_IMPORTER_WORK_MODE={
        'mode': 'enabled',
        'chunk-size': 1,
        'interval-ms': 1000,
    },
)
async def test_worker(taxi_parks_commute, testpoint, mongodb):
    @testpoint('parks_importer_worker_start_enabled')
    def start(data):
        pass

    @testpoint('parks_importer_worker_finish')
    def finish(data):
        pass

    for _ in range(0, 2):
        try:
            await start.wait_call()
            await finish.wait_call()
        except testsuite.utils.callinfo.CallQueueTimeoutError:
            assert False

    result_real_clids = {
        park['_id']: {'real_clids': park.get('real_clids', [])}
        for park in mongodb.parks.find({}, ['real_clids'])
    }

    assert result_real_clids == {
        'clid1': {
            'real_clids': [
                {'clid': 'park_id1', 'name': 'name1', 'extra': 'extra1'},
                {'clid': 'park_id3', 'name': 'name3'},
                {'clid': 'park_id4', 'name': 'name4'},
            ],
        },
        'clid2': {'real_clids': [{'clid': 'park_id2', 'name': 'name2'}]},
    }

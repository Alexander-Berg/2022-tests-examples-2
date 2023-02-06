import datetime

import pytest

HANDLER_PATH = 'v1/service/driver/unblock_by_params'
CHECK_HANDLER_PATH = 'v1/service/driver/unblock_by_params/check'

TIMESTAMP = datetime.datetime(2016, 5, 6, 9, 0, 0, 0)
TWO_DAYS_BEFORE = TIMESTAMP - datetime.timedelta(days=2)

UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_2 = '5b05621ee6c22ea2654849c0'


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.parametrize('response_error', [True, False])
@pytest.mark.parametrize('dryrun', [True, False])
@pytest.mark.parametrize(
    'tst_request, unique_driver_ids',
    [
        ({}, []),
        (
            {
                'type': 'activity',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'zone': 'spb',
                'rules': ['lasdkjkfsa'],
            },
            [UDID_1],
        ),
        (
            {
                'type': 'complete_scores',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'zone': 'spb',
                'rules': ['lasdkjkfsa'],
            },
            [UDID_1],
        ),
        (
            {'type': 'activity', 'later_than': '2016-02-25T12:12:12.000000Z'},
            [UDID_1],
        ),
        (
            {
                'type': 'complete_scores',
                'later_than': '2016-02-25T12:12:12.000000Z',
            },
            [UDID_1],
        ),
        (
            {'later_than': '2016-02-25T12:12:12.000000Z', 'zone': 'spb'},
            [UDID_1, UDID_2],
        ),
        (
            {
                'later_than': '2016-02-25T12:12:12.000000Z',
                'rules': ['lasdkjkfsa'],
            },
            [UDID_1, UDID_2],
        ),
        (
            {
                'later_than': '2016-02-25T12:12:12.000000Z',
                'earlier_than': '2016-05-25T12:12:12.000000Z',
            },
            [UDID_1, UDID_2],
        ),
        (
            {
                'type': 'activity',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'earlier_than': '2016-05-25T12:12:12.000000Z',
                'rules': ['lasdkjkfsa'],
            },
            [UDID_1],
        ),
        (
            {
                'type': 'complete_scores',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'earlier_than': '2016-05-25T12:12:12.000000Z',
                'rules': ['lasdkjkfsa'],
            },
            [UDID_1],
        ),
        (
            {
                'type': 'activity',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'earlier_than': '2016-02-26T12:12:12.000000Z',
                'rules': ['lasdkjkfsa'],
            },
            [],
        ),
        (
            {
                'type': 'complete_scores',
                'later_than': '2016-02-25T12:12:12.000000Z',
                'earlier_than': '2016-02-26T12:12:12.000000Z',
                'rules': ['lasdkjkfsa'],
            },
            [],
        ),
        (
            {
                'type': 'actions',
                'later_than': '2017-02-25T12:12:12.000000Z',
                'zone': 'spb',
            },
            [],
        ),
        ({'later_than': '2016-02-25T12:12:12.000000Z'}, [UDID_1, UDID_2]),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
async def test_unblock_drivers_by_params(
        mockserver,
        taxi_driver_metrics,
        response_error,
        dryrun,
        tst_request,
        unique_driver_ids,
):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def process_unblocking(*args, **kwargs):
        if response_error:
            return mockserver.make_response('internal error', status=500)
        return {}

    tst_request['dryrun'] = dryrun

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=tst_request)
    content = await response.json()

    if not tst_request.get('later_than'):
        assert response.status == 400
        assert content['code'] == 'invalid-input'
    if not dryrun and not response_error and unique_driver_ids:
        assert response.status == 200
        assert sorted(content['unique_driver_ids']) == sorted(
            unique_driver_ids,
        )
        assert process_unblocking.times_called
    elif not dryrun and unique_driver_ids and response_error:
        assert content['errors']
    else:
        assert not process_unblocking.times_called


async def test_unblock_by_params_drivers_check(web_app_client):
    request = {
        'type': 'activity',
        'later_than': '2016-02-25T12:12:12.000000Z',
        'earlier_than': '2016-02-26T12:12:12.000000Z',
        'rules': ['lasdkjkfsa'],
    }

    response = await web_app_client.post(CHECK_HANDLER_PATH, json=request)

    assert response.status == 200
    response_json = await response.json()
    assert response_json['data'] == request

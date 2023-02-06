import pytest

from taxi_driver_metrics.generated.cron import run_cron

TST_LAST_REVISION = '33'
TST_UDID = 'tst_udid'


@pytest.mark.config(
    DRIVER_METRICS_DATA_MINER={
        'new_unique_drivers': {'enabled': True, 'batch_size': 2, 'limit': 1},
    },
)
async def test_overall(stq3_context, mockserver, mock, patch, stq):
    #  TODO: figure out what to do with revision
    @mockserver.json_handler('/unique-drivers/v1/driver/new/')
    def patch_request(*args, **kwargs):
        return {
            'last_revision': TST_LAST_REVISION,
            'drivers': [{'id': TST_UDID, 'source': 'new_license_id'}],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _(*args, **kwargs):
        return {
            'profiles': [
                {
                    'unique_driver_id': TST_UDID,
                    'data': [
                        {
                            'park_id': 'park1',
                            'driver_profile_id': 'profile1',
                            'park_driver_profile_id': 'park1_profile1',
                        },
                        {
                            'park_id': 'park2',
                            'driver_profile_id': 'profile2',
                            'park_driver_profile_id': 'park2_profile2',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _(*args, **kwargs):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_profile1',
                    'data': {
                        'created_date': '2020-01-01T00:00:00Z',
                        'park_id': 'park1',
                    },
                },
                {
                    'park_driver_profile_id': 'park2_profile2',
                    'data': {
                        'created_date': '2020-01-02T00:00:00Z',
                        'park_id': 'park2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _(*args, **kwargs):
        request = args[0].json
        assert request == {'query': {'park': {'ids': ['park2']}}}
        return {
            'parks': [
                {
                    'id': 'park2',
                    'login': 'asd',
                    'name': 'dsa',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'demo_mode': False,
                    'city_id': 'nab_chelny',
                    'locale': 'ru',
                    'country_id': 'rus',
                    'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
                },
            ],
        }

    with stq.flushing():
        await run_cron.main(
            ['taxi_driver_metrics.crontasks.data_miner', '-t', '0'],
        )
        assert stq.driver_metrics_client.times_called == 1

        call = stq.driver_metrics_client.next_call()

        assert call['args'][0]['udid'] == TST_UDID

        await run_cron.main(
            ['taxi_driver_metrics.crontasks.data_miner', '-t', '0'],
        )
        assert stq.driver_metrics_client.times_called == 1
        call = stq.driver_metrics_client.next_call()
        data = call['args'][0]
        data.pop('timestamp')
        assert data == {
            'extra_data': {
                'park_city': 'nab_chelny',
                'park_country': 'rus',
                'park_locale': 'ru',
            },
            'dbid_uuid': 'park2_profile2',
            'idempotency_token': '/new_udid/tst_udid/new_license_id',
            'reason': 'new_license_id',
            'type': 'new_unique_driver',
            'udid': 'tst_udid',
        }
        assert patch_request.times_called == 2

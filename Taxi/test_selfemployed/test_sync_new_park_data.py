import pytest

from testsuite.utils import http

from selfemployed.generated.cron import run_cron


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.pgsql(
                'selfemployed_main', files=['ownpark_forms.sql'],
            ),
        ),
        pytest.param(
            marks=pytest.mark.pgsql(
                'selfemployed_main', files=['ownpark_forms_conflict.sql'],
            ),
        ),
    ],
)
async def test_sync_new_park_data_conflict(
        se_cron_context,
        mockserver,
        mock_salesforce,
        mock_fleet_synchronizer,
        mock_tags,
        mock_selfreg,
):
    @mock_salesforce('/services/data/v46.0/sobjects/Account/sf_acc_id')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'ParkId__c,DriverId__c'}
        return {'ParkId__c': 'cp1', 'DriverId__c': 'cd1'}

    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {'mapping': []}

    @mock_tags('/v2/upload')
    async def _tags_upload(request):
        assert request.json == {
            'provider_id': 'selfemployed',
            'append': [
                {
                    'entity_type': 'park',
                    'tags': [{'name': 'selfemployed', 'entity': 'cp1'}],
                },
            ],
        }
        return {}

    @mock_selfreg('/internal/selfreg/v1/new-contractor-callback')
    async def _selfreg_callback(request):
        assert request.method == 'POST'
        body = request.json
        assert body == {
            'selfreg_id': 'selfregid1',
            'park_id': 'cp1',
            'driver_profile_id': 'cd1',
            'source': 'selfemployed',
        }
        return {}

    await run_cron.main(
        ['selfemployed.crontasks.sync_new_park_data', '-t', '0'],
    )

    updated_forms = await se_cron_context.pg.main_ro.fetch(
        """
        SELECT phone_pd_id, state, created_park_id, created_contractor_id
        FROM se.ownpark_profile_forms_common
        """,
    )

    assert [
        {
            'phone_pd_id': 'PHONE_PD_ID1',
            'state': 'FINISHED',
            'created_park_id': 'cp1',
            'created_contractor_id': 'cd1',
        },
    ] == [dict(form) for form in updated_forms]

import pytest

from testsuite.utils import http


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status)
        VALUES ('PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED');
        INSERT INTO se.finished_profiles
            (park_id, contractor_profile_id, phone_pd_id, inn_pd_id,
             do_send_receipts)
        VALUES ('park_id', 'contractor_profile_id', 'PHONE_PD_ID', 'INN_PD_ID',
                FALSE),
            ('park_id1', 'contractor_profile_id1', 'PHONE_PD_ID', 'INN_PD_ID',
             FALSE);
        """,
    ],
)
@pytest.mark.parametrize(
    'do_send_receipts,expect_changed', [(True, True), (False, False)],
)
async def test_ok(
        se_client,
        se_web_context,
        mock_personal,
        mock_fleet_synchronizer,
        do_send_receipts,
        expect_changed,
        stq,
):
    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {
            'mapping': [
                {
                    'app_family': 'taximeter',
                    'park_id': 'park_id',
                    'driver_id': 'contractor_profile_id',
                },
                {
                    'app_family': 'uberdriver',
                    'park_id': 'park_id1',
                    'driver_id': 'contractor_profile_id1',
                },
            ],
        }

    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+71234567890', 'id': 'PHONE_PD_ID'}

    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/set-send-receipts',
        headers={
            'X-Park-ID': 'park_id',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        params={
            'contractor_profile_id': 'contractor_profile_id',
            'do_send_receipts': str(do_send_receipts).lower(),
        },
    )
    assert response.status == 200

    profiles = await se_web_context.pg.main_master.fetch(
        'SELECT do_send_receipts, increment FROM se.finished_profiles',
    )

    max_increment = len(profiles) * (1 + int(expect_changed))
    for profile in profiles:
        profile_dict = dict(profile)
        assert profile_dict['increment'] <= max_increment
        profile_dict.pop('increment')

        assert dict(profile_dict) == dict(do_send_receipts=do_send_receipts)
    assert stq.selfemployed_fns_tag_contractor.times_called == 1
    assert stq.selfemployed_fns_tag_contractor.next_call()['kwargs'] == {
        'trigger_id': (
            'quasi_reporting_enabled'
            if do_send_receipts
            else 'quasi_reporting_disabled'
        ),
        'park_id': 'park_id',
        'contractor_id': 'contractor_profile_id',
    }

from aiohttp import web
import pytest

TEST_DOC_ID = 1234567890


@pytest.mark.config(
    BILLING_COUNTRIES_WITH_ORDER_BILLINGS_SUBVENTION_NETTING={
        'rus': '2020-07-05',
    },
    BILLING_TLOG_SERVICE_IDS={'subvention/netted': 111},
    SUBVENTION_ANTIFRAUD_NEEDED_STARTUP_WINDOW=2,
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='old',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='both',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new',
            ),
        ),
    ],
)
@pytest.mark.now('2020-12-30T00:00:00.0Z')
async def test_taxi_geo_booking_shift(
        mockserver,
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_subvention_communications,
        mock_antifraud,
        mock_driver_work_modes,
        mock_tlog,
        mock_replication,
        mock_parks_replica,
        mock_driver_profiles,
        mock_taxi_agglomerations,
        reschedulable_stq_runner,
        load_json,
):
    responses = load_json('responses.json')

    docs = do_mock_billing_docs([load_json('taxi_shift.json')])
    do_mock_billing_accounts(existing_balances=responses['balances'])
    do_mock_billing_reports()
    mock_driver_work_modes('dwm_responses.json')
    mock_subvention_communications()
    mock_antifraud(
        [
            responses['antifraud_delay_response'],
            responses['antifraud_pay_response'],
        ],
    )
    mock_replication(responses['contracts'])

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    def _v1_parks_billing_client_id_retrieve(request):
        return web.json_response(responses['billing_client_id'])

    @mock_parks_replica('/v1/parks/retrieve')
    def _v1_parks_retrieve(request):
        return web.json_response(responses['parks'])

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _v1_driver_profiles_retrieve(request):
        return web.json_response(responses['driver_profiles'])

    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _v1_geo_nodes_get_mvp_oebs_id(request):
        return web.json_response(responses['mvp_oebs_id'])

    queue = stq_runner.billing_functions_taxi_geo_booking_shift
    await reschedulable_stq_runner(queue, TEST_DOC_ID)

    assert docs.update_requests == load_json('updates.json')

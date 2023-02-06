import pytest

from tests_ivr_dispatcher import cargo_support_flow_utils as cargo
from tests_ivr_dispatcher import utils


@cargo.SCENARIO_CONFIGS
@pytest.mark.parametrize(
    ['scenario', 'tags_first', 'tags_second', 'nearest_zone', 'tariff_class'],
    [
        pytest.param(
            cargo.SWITCH_TO_SUPPORT_SCENARIO,
            [],
            [cargo.PERFORMER_TAG],
            cargo.NEAREST_ZONE,
            cargo.COURIER_TARIFF,
            id='Switch to support',
            marks=pytest.mark.now('2021-01-01T012:00:00+0000'),
        ),
        pytest.param(
            cargo.INAPPROPRIATE_PERFORMER_SCENARIO,
            [],
            [],
            cargo.NEAREST_ZONE,
            cargo.COURIER_TARIFF,
            id='Performer does not have tags',
            marks=pytest.mark.now('2021-01-01T012:00:00+0000'),
        ),
        pytest.param(
            cargo.INAPPROPRIATE_PERFORMER_SCENARIO,
            [cargo.PERFORMER_TAG],
            [cargo.PERFORMER_TAG],
            'inappropriate_zone',
            cargo.COURIER_TARIFF,
            id='Inappropriate location',
            marks=pytest.mark.now('2021-01-01T012:00:00+0000'),
        ),
        pytest.param(
            cargo.INAPPROPRIATE_PERFORMER_SCENARIO,
            [cargo.PERFORMER_TAG],
            [cargo.PERFORMER_TAG],
            cargo.NEAREST_ZONE,
            'econom',
            id='Inappropriate tariff class',
            marks=pytest.mark.now('2021-01-01T012:00:00+0000'),
        ),
    ],
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mockserver,
        mock_driver_profiles,
        cargo_support_flow_store,
        cargo_support_flow_statuses,
        cargo_support_flow_order_core,
        scenario,
        tags_first,
        tags_second,
        nearest_zone,
        tariff_class,
):
    cargo_support_flow_order_core(tariff_class, nearest_zone)

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _mock_driver_tags(request):
        driver = request.json['drivers'][-1]
        tags = (
            tags_first
            if driver['dbid'] == utils.DEFAULT_PARK_ID
            else tags_second
        )
        return {
            'drivers': [
                {'dbid': driver['dbid'], 'uuid': driver['uuid'], 'tags': tags},
            ],
        }

    for action, reply in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply

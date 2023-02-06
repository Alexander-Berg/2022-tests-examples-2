import datetime

import pytest

from insurance.stq import assign_insurer


@pytest.mark.config(
    INSURANCE_GEOAREAS=['moscow'],
    INSURANCE_COUNTRIES=['rus', 'blr'],
    INSURERS_TIMETABLE={'blr': [{'days': [17], 'name': 'Name 2'}]},
    INSURANCE_DISABLED_AGENTS=['007'],
)
@pytest.mark.parametrize(
    'order_id, zone, agent_id, expect_insurer_id',
    [
        pytest.param(
            'rus_order', 'moscow', None, 'insurer_rus', id='random ' 'choose',
        ),
        pytest.param(
            'blr_order', 'minsk', None, 'insurer_blr', id='timetable choose',
        ),
        pytest.param('agent_order', 'minsk', '007', None, id='disabled agent'),
    ],
)
async def test_stq_assign_insurer(
        stq3_context,
        mock_taxi_tariffs,
        mock_order_core,
        load_json,
        order_id,
        zone,
        agent_id,
        expect_insurer_id,
):
    @mock_taxi_tariffs('/v1/tariff_zones')
    async def _mock_zones(*args, **kwargs):
        return load_json('zones.json')

    @mock_order_core('/v1/tc/order-fields')
    def _order_core(request):
        return load_json('order_core_response.json')[order_id]

    @mock_order_core('/v1/tc/set-order-fields')
    def _order_core_set(request):
        assert request.json == {
            'call_processing': False,
            'order_id': order_id,
            'update': {'set': {'insurer_id': expect_insurer_id}},
            'user_id': 'user_id',
            'version': 'DAAAAAAABgAMAAQABgAAANJZFXNxAQAA',
        }
        return {}

    await assign_insurer.task(
        stq3_context,
        order_id=order_id,
        agent_id=agent_id,
        user_id='user_id',
        nearest_zone=zone,
        due=datetime.datetime(2021, 1, 17, 10, 20, 0),
    )

    if not agent_id:
        assert _order_core_set.times_called == 1
    else:
        assert _order_core_set.times_called == 0

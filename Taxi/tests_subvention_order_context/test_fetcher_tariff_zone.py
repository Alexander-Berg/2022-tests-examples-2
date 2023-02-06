import copy

import pytest

from . import test_common


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'driver_point, nearest_zone, expected_tariff_zone',
    [
        ([37.5444031, 55.7054503], 'moscow1', 'moscow'),  # inside polygon
        ([38.1074524, 55.6713893], 'moscow1', 'moscow1'),  # outside polygon
        (
            [36.90840238790664, 55.347194847462745],
            'moscow1',
            'moscow1',
        ),  # polygon edge point
        ([0.01, 0.01], 'moscow1', 'moscow1'),
    ],
)
async def test_fetcher_tariff_zone(
        mongodb, stq_runner, driver_point, nearest_zone, expected_tariff_zone,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    del context_data['value']['tariff_zone']
    context_data['value']['driver_point'] = driver_point
    mongodb.subvention_order_context.insert_one(context_data)

    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    kwargs['nz'] = nearest_zone

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['tariff_zone'] == expected_tariff_zone

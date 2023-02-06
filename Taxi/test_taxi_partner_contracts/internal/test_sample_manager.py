import pytest

from taxi_partner_contracts.internal import sample_manager
from taxi_partner_contracts.models import flows
from taxi_partner_contracts.models import samples_db


async def test_all_linked_samples(db: pytest.fixture):
    all_flows = [item async for item in flows.Flow.get_all_flows(db)]
    all_samples_dict = await samples_db.Sample.get_samples(db)
    flow = all_flows[0]
    for stage in flow.stages_objects.values():
        linked_samples = sample_manager.all_linked_samples(
            stage, all_samples_dict,
        )
        linked_samples_set = set(linked_samples.keys())
        if stage.primary_key == '__default__':
            assert linked_samples_set == {'sample_1', 'sample_3'}
        elif stage.primary_key == 'second_stage':
            assert linked_samples_set == {'sample_2'}

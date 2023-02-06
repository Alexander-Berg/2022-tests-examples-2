import pytest

from eats_order_integration.generated.service.swagger.models import (
    api as models,
)
from eats_order_integration.internal import entities
from test_eats_order_integration import stq as stq_test


@pytest.fixture(name='order_update_stq_runner')
def _order_update_stq_runner(stq_runner, load_json):
    async def call_stq(kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'

        await stq_runner.eats_order_integration_update_order.call(
            task_id='task_id',
            args=(),
            kwargs=models.StqUpdateOrderKwargs(
                **load_json('update_order_kwargs.json')[kwargs_name],
            ).serialize(),
        )

    return call_stq


@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_not_update_order_if_disabled_in_experiment(
        stq,
        order_update_stq_runner,
        order_integration_mock,
        partner_mocks,
        processing_mocks,
        order_tech_info_mock,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_update_stq_runner()
    assert not stq.eats_order_integration_update_order.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.client_experiments3(file_with_default_response='exp3_empty.json')
@pytest.mark.pgsql('eats_order_integration', files=['engines.sql'])
async def test_should_fallback_to_core_if_cannot_find_engine(
        stq,
        order_update_stq_runner,
        order_integration_mock,
        order_tech_info_mock,
        partner_mocks,
        processing_mocks,
        load_json,
        client_experiments3,
        stq3_client,
):
    await stq3_client.invalidate_caches()
    processing_mocks()
    await order_update_stq_runner()
    assert not stq.eats_order_integration_update_order.has_calls
    assert stq.eats_order_integration_fallback_to_core.has_calls
    stq_test.check_fallback_to_core(
        stq.eats_order_integration_fallback_to_core,
        order_id='order_id',
        action=entities.Action.UPDATE_ORDER.value,
    )

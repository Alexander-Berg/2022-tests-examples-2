# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import contract_activation as ca


NOTICE_KWARGS = {'reason': 'debt', 'external_contract_id': '101/01'}


@pytest.fixture
def cargo_broker(cron_context):
    return ca.CargoContractActivateNoticeBroker.make(
        cron_context, notice_kwargs=NOTICE_KWARGS,
    )


@pytest.fixture
def taxi_broker(cron_context):
    return ca.TaxiContractActivateNoticeBroker.make(
        cron_context, notice_kwargs=NOTICE_KWARGS,
    )


async def test_template_kwargs(cargo_broker, taxi_broker):
    assert await cargo_broker.get_template_kwargs() == NOTICE_KWARGS
    assert await taxi_broker.get_template_kwargs() == NOTICE_KWARGS


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('TaxiContractActivateNotice')
    assert registry.get('CargoContractActivateNotice')

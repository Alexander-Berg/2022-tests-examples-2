# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import low_balance_notice


NOTICE_KWARGS = {
    'old_balance': '150',
    'new_balance': '50',
    'contract_id': '10101',
    'external_id': '101/01',
}


@pytest.fixture
def broker(cron_context):
    return low_balance_notice.LowBalanceNoticeBroker.make(
        cron_context, notice_kwargs=NOTICE_KWARGS,
    )


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() == {
        'sum': '50',
        'contract_id': '101/01',
    }


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('LowBalanceNotice')

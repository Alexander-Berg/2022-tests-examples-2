# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import big_quasi_notice


@pytest.fixture
def broker(cron_context):
    return big_quasi_notice.BigQuasiNoticeBroker.make(cron_context)


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() is None


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('BigQuasiNotice')

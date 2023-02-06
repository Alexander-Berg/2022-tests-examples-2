# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import limit_is_over_notice


@pytest.fixture
def broker(cron_context):
    return limit_is_over_notice.LimitIsOverNoticeBroker.make(cron_context)


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() is None


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('LimitIsOverNotice')

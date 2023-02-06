import pytest

from configs_admin.db_wrappers import locks


@pytest.mark.filldb(uconfigs_meta='empty')
async def test_case(web_context):
    await locks.lock_group_and_configs(
        web_context, actual_commit='', names=[], group='',
    )

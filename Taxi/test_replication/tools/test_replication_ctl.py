# pylint: disable=protected-access, redefined-outer-name
import datetime

import pytest

from replication import create_context
from replication.replication.classes import state_unit
from replication.tools import replication_ctl

NOW = datetime.datetime(2018, 2, 22, 23, 41)


@pytest.mark.nofilldb()
def test_actions_attrs():
    for action in replication_ctl.ACTIONS:
        assert hasattr(state_unit.ReplicationStateWrapper, action)
        assert callable(getattr(state_unit.ReplicationStateWrapper, action))


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'argv,expected_json_filename',
    [
        (
            ['--update-all-meta-info'],
            'all_meta_update_db_replication_state.json',
        ),
        (
            [
                '--destinations',
                'test_rule_struct',
                '--client-names',
                'hahn',
                '--actions',
                'update_info',
                '--initial-ts',
                'set,2018-02-22T23:42:00+00:00',
            ],
            'set_initial_ts_db_replication_state.json',
        ),
        (
            [
                '--destinations',
                'test_initialize_columns_bson_raw_rebuild_data',
                '--client-names',
                'hahn',
                '--actions',
                'update_info',
                '--initial-ts',
                'unset',
            ],
            'unset_initial_ts_db_replication_state.json',
        ),
    ],
)
async def test_update_all_meta_info(
        run_ctl_script, db, load_py_json, argv, expected_json_filename,
):
    await run_ctl_script(argv)

    db_data = {
        state['_id']: state async for state in db.replication_state.find()
    }
    expected_data = {
        state['_id']: state for state in load_py_json(expected_json_filename)
    }
    assert db_data == expected_data


@pytest.fixture
def run_ctl_script():
    async def _run(argv):
        async with create_context.context_scope() as context:
            await replication_ctl.amain(
                replication_ctl.parse_args(argv), context,
            )

    return _run

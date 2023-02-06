# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_data_to_yt.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS=SF_DATA_LOAD_LOOKUPS,
)
async def test_load_data_to_yt(pgsql, yt_apply, cron_context):
    await run_cron.main(['sf_data_load.crontasks.load_data_to_yt', '-t', '0'])
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103
    path = '//home/taxi/unittests/features/internal-b2b/sf-data-load/b2b'
    data = list(await yt.read_table(path))
    assert data == [
        {
            'sf_id': 'failed',
            'sf_object': 'Task',
            'value': '{"OwnerId": "a"}',
            'time_operation': 1655448620.0,
        },
        {
            'sf_id': '1',
            'sf_object': 'Task',
            'value': '{"WhoId": "b"}',
            'time_operation': 1655448620.0,
        },
        {
            'sf_id': '2',
            'sf_object': 'Task',
            'value': '{"Type": "case"}',
            'time_operation': 1655448620.0,
        },
    ]

    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute(
        f"""
                SELECT * FROM sf_data_load.load_to_yt""",
    )
    data = cursor.fetchall()
    assert not data

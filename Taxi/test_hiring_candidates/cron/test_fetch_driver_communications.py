# pylint: disable=redefined-outer-name
import pytest

from hiring_candidates.generated.cron import run_cron
from hiring_candidates.generated.service.postgres_queries import query_names
from hiring_candidates.internal import database_operations as dbops
from test_hiring_candidates import conftest


@pytest.mark.usefixtures('mock_yt_fetch_table', 'mock_yt_search')
@conftest.main_configuration
async def test_fetch_driver_communications(cron_context):
    await run_cron.main(
        ['hiring_candidates.crontasks.fetch_driver_communications', '-t', '0'],
    )
    communications = await dbops.fetch_query_from_template(
        context=cron_context,
        template_name=query_names.GET_DRIVER_COMMUNICATION_INFO_TMPL,
        args_dict={
            'args': {
                'personal_license_id': 'ed6825f249934cf3ae154b83a5516711',
                'personal_phone_id': None,
                'expire_dt': '1999-01-01',
                'city': 'Воронеж',
            },
        },
        log_extra=None,
    )
    assert communications
    communications = await dbops.fetch_query_from_template(
        context=cron_context,
        template_name=query_names.GET_DRIVER_COMMUNICATION_INFO_TMPL,
        args_dict={
            'args': {
                'personal_license_id': 'ed5825f249934cf3ae154b83a5516711',
                'personal_phone_id': None,
                'expire_dt': '3000-01-01',
                'city': None,
            },
        },
        log_extra=None,
    )
    assert not communications

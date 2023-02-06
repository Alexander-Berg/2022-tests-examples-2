# pylint: disable=redefined-outer-name,unused-variable,global-statement
import pytest

from selfemployed.generated.cron import run_cron
from . import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'confirmed', NOW(), NOW()),
            ('smz2', 'inn2', 'p2', 'd2', 'bad_permissions', NOW(), NOW()),
            ('smz3', 'inn3', 'p3', 'd3', 'rejected', NOW(), NOW()),
            ('smz4', 'inn4', 'p4', 'd4', 'new', NOW(), NOW()),
            ('smz5', 'inn5', 'p5', 'd5', 'bad_permissions', NOW(), NOW())
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_check_permissions(mock_token_update, patch):
    msg_id_ = 'msg_id'

    @patch('selfemployed.fns.client.Client.get_permissions')
    async def get_permissions(inn):
        assert inn in ['inn2', 'inn3', 'inn5']
        return msg_id_

    @patch('selfemployed.fns.client.Client.get_permissions_response')
    async def get_permissions_response(msg_id):
        assert msg_id == msg_id_
        return ['INCOME_REGISTRATION', 'INCOME_LIST', 'CANCEL_INCOME']

    await run_cron.main(
        ['selfemployed.crontasks.check_permissions', '-t', '0'],
    )

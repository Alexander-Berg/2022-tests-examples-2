# pylint: disable=redefined-outer-name,unused-variable
import pytest

from selfemployed.scripts import run_script
from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_check_fns_status(se_cron_context, patch):
    inn_ = '12345'
    msg_id_ = '54321'

    @patch('selfemployed.fns.client.Client.get_details')
    async def get_details(inn):
        assert inn == inn_
        return msg_id_

    @patch('selfemployed.fns.client.Client.get_details_response')
    def get_details_response(msg_id):
        assert msg_id == msg_id_
        return 'F', 'I', 'O'

    await run_script.main(
        ['selfemployed.scripts.check_fns_status', '-t', '0', '--inn', inn_],
    )

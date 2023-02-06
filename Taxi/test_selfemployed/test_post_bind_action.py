import pytest

from selfemployed.db import dbmain
from selfemployed.fns import client as client_fns
from selfemployed.helpers import actions


async def test_request_bind_ok(se_web_context, patch):
    phone = '+71234567890'
    request_id = '123'

    @patch('taxi.clients.selfreg.SelfregClient.get_profile')
    async def _get_profile(*args, **kwargs):
        return {'phone_number': phone}

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_by_phone(*args, **kwargs):
        return request_id

    @patch('selfemployed.db.dbmain.update_nalog_app_status')
    async def _update_nalog_app_status(*args, **kwargs):
        pass

    result_id = await actions.request_bind_nalog_app(
        se_web_context, 'selfreg', '1d', phone,
    )

    assert result_id == request_id
    assert len(_update_nalog_app_status.calls) == 1


async def test_request_bind_no_fns(se_web_context, patch):
    phone = '+71234567890'
    request_id = None

    @patch('taxi.clients.selfreg.SelfregClient.get_profile')
    async def _get_profile(*args, **kwargs):
        return {'phone_number': phone}

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_by_phone(*args, **kwargs):
        return request_id

    @patch('selfemployed.db.dbmain.update_nalog_app')
    async def _update_nalog_app(*args, **kwargs):
        pass

    result_id = await actions.request_bind_nalog_app(
        se_web_context, 'selfreg', '1d', phone,
    )

    assert result_id == request_id
    assert len(_update_nalog_app.calls) == 1


async def test_request_bind_no_profile(se_web_context, patch):
    phone = '+71234567890'
    request_id = None

    @patch('taxi.clients.selfreg.SelfregClient.get_profile')
    async def _get_profile(*args, **kwargs):
        return {'phone_number': phone}

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_by_phone(*args, **kwargs):
        return request_id

    @patch('selfemployed.db.dbmain.update_nalog_app')
    async def _update_nalog_app(*args, **kwargs):
        raise dbmain.EmptyUpdateError()

    with pytest.raises(dbmain.EmptyUpdateError):
        await actions.request_bind_nalog_app(
            se_web_context, 'selfreg', '1d', phone,
        )


@pytest.mark.parametrize('is_bound', [True, False])
async def test_request_rebind_bound(se_web_context, patch, is_bound):
    phone = '+71234567890'
    request_id = '123'
    found_inn = '123123123'
    # Using mutable container avoid using global vars
    is_bound_container = [is_bound]

    @patch('taxi.clients.selfreg.SelfregClient.get_profile')
    async def _get_profile(*args, **kwargs):
        return {'phone_number': phone}

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind_by_phone(*args, **kwargs):
        if is_bound_container[0]:
            raise client_fns.TaxpayerAlreadyBoundError(
                'Already there',
                client_fns.SmzErrorCode.TAXPAYER_ALREADY_BOUND,
                {'INN': found_inn},
            )
        return request_id

    @patch('selfemployed.helpers.fns.unbind_by_inn')
    async def _unbind_by_inn(app, inn, **kwargs):
        assert is_bound_container[0]
        assert inn == found_inn
        is_bound_container[0] = False

    @patch('selfemployed.db.dbmain.update_nalog_app_status')
    async def _update_nalog_app_status(*args, **kwargs):
        pass

    result_id = await actions.request_bind_nalog_app(
        se_web_context, 'selfreg', '1d', phone,
    )

    assert result_id == request_id
    assert len(_update_nalog_app_status.calls) == 1

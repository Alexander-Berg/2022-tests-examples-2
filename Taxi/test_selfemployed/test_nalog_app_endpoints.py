import pytest

from selfemployed.fns import client as client_fns
from . import conftest


CORRECT_STEP = 'nalog_app'

CORRECT_PHONE_NUMBER = '+77773332244'

CORRECT_DATA = {'step': CORRECT_STEP, 'phone_number': CORRECT_PHONE_NUMBER}

CORRECT_PARAMS = {'driver': 'd1', 'park': 'p1'}


@pytest.mark.parametrize(
    'params',
    [
        {},
        {'driver': '', 'park': '', 'selfreg_id': ''},
        {'selfreg_id': ''},
        {'driver': 'd1', 'park': 'p1', 'selfreg_id': 'sr1'},
        {'driver': 'd1'},
        {'park': 'p1'},
        {'park': 'p1', 'driver': ''},
        {'driver': 'd1', 'park': ''},
    ],
)
async def test_post_nalog_app_401(se_client, params):
    data = CORRECT_DATA
    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 401


@pytest.mark.parametrize(
    'params', [{'driver': 'd1', 'park': 'p1'}, {'selfreg_id': 'sr1'}],
)
async def test_nalog_app_w_request_id(se_client, patch, params):
    data = CORRECT_DATA

    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id, driver_id, phone):
        assert phone == data['phone_number']
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'agreement',
        'step_index': 3,
        'step_count': 7,
    }


@pytest.mark.parametrize(
    'params', [{'driver': 'd1', 'park': 'p1'}, {'selfreg_id': 'sr1'}],
)
async def test_nalog_app_wo_request_id(se_client, patch, params):
    data = CORRECT_DATA

    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id, driver_id, phone):
        assert phone == data['phone_number']
        return None

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'phone_number',
        'step_index': 2,
        'step_count': 7,
    }


@pytest.mark.parametrize(
    'data, status',
    [
        ({'step': CORRECT_STEP, 'phone_number': CORRECT_PHONE_NUMBER}, 200),
        (
            {'step': 'incorrect_step', 'phone_number': CORRECT_PHONE_NUMBER},
            400,
        ),
        ({'phone_number': CORRECT_PHONE_NUMBER}, 400),
        ({'phone_number': CORRECT_PHONE_NUMBER, 'step': ''}, 400),
        ({'step': CORRECT_STEP}, 400),
        ({'step': CORRECT_STEP, 'phone_number': None}, 400),
        ({'step': '', 'phone_number': ''}, 400),
        ({}, 400),
    ],
)
async def test_post_nalog_app_check_data(se_client, patch, data, status):
    params = CORRECT_PARAMS

    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(context, park_id, driver_id, phone):
        return None

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == status


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_nalog_app_409(se_client, patch):
    params = {'selfreg_id': 'sr1'}
    data = CORRECT_DATA

    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(*args, **kwargs):
        raise client_fns.SmzPlatformError(
            'some_error_message', 'some_error_code',
        )

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'no_selfemployed_found',
        'text': 'Вы не являетесь самозанятым',
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_smz_not_found(se_client, patch):
    params = {'driver': 'd1', 'park': 'p1'}
    data = CORRECT_DATA

    @patch('selfemployed.helpers.actions.request_bind_nalog_app')
    async def _bind(*args, **kwargs):
        raise client_fns.SmzPlatformError(
            'some_error_message', 'some_error_code',
        )

    response = await se_client.post(
        '/self-employment/fns-se/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'phone_number',
        'step_index': 2,
        'step_count': 7,
    }

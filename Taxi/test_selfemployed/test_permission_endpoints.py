# pylint: disable=unused-variable
import pytest

from testsuite.utils import http

from . import conftest


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
async def test_401(se_client, params):
    data = {'step': 'permission'}
    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == 401


@pytest.mark.parametrize('data', [{}, {'step': 'intro'}])
async def test_400(se_client, data):
    # Request must have {'step': 'permission'} as body
    params = {'park': '1', 'driver': '1'}
    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400


# TODO: proper tests


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status,
             created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'new',
             NOW(), NOW())
        """,
    ],
)
async def test_bad_status(se_client):
    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 500


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status, park_id,
             created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'confirmed', 'se_park1',
             NOW(), NOW())
        """,
    ],
)
async def test_status_too_big(se_client):
    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_index': 6,
        'step_count': 7,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status,
             created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'confirmed',
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_confirmed_waiting(se_client):
    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'text': '**Создание нового профиля** Подождите 30 секунд',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status, request_id,
             created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'requested', 'req_id',
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_requested_waiting(se_client, patch):
    @patch('selfemployed.helpers.fns.check_bind_status')
    async def _check(context, request_id: str):
        assert request_id == 'req_id'
        return 'IN_PROGRESS', 'inn'

    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'text': (
            '**Разрешение не получено** Откройте «Мой налог» и поставьте '
            'галочку у каждого пункта'
        ),
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, status, request_id, phone,
             created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'p1', 'd1', 'requested', 'req_id', '+70123456789',
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_requested_rejected(se_client, patch):
    @patch('selfemployed.helpers.fns.check_bind_status')
    async def _check(context, request_id: str):
        mapping = {
            'req_id': ('FAILED', 'inn'),
            'req_id2': ('COMPLETED', 'inn'),
        }
        assert request_id in mapping
        return mapping[request_id]

    @patch('selfemployed.helpers.fns.get_fio')
    async def _get_fio(context, inn: str):
        assert inn == 'inn'
        return 'f', 'i', 'o'

    @patch('selfemployed.helpers.actions._check_phone')
    async def _check_phone(*args, **kwargs):
        return

    @patch('selfemployed.helpers.fns.bind_by_phone')
    async def _bind(context, phone: str):
        assert phone == '+70123456789'
        return 'req_id2'

    @patch('selfemployed.api.post_permission._do_use_salesforce')
    async def _do_use_salesforce(*args, **kwargs):
        return True

    @patch('selfemployed.helpers.actions.create_park_driver_sf')
    async def _create_park_driver_sf(*args, **kwargs):
        return 'sf_acc_id'

    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'text': (
            '**Разрешение не получено** Откройте «Мой налог» и поставьте '
            'галочку у каждого пункта'
        ),
    }

    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': 'p1', 'driver': 'd1'},
        json={'step': 'permission'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {'text': conftest.TRANSLATIONS['push_new_profile']['ru']}
    assert len(_bind.calls) == 1


def _make_test_requested_exp_params(is_selfereg, phone_pd_id, use_salesforce):
    return dict(
        consumer='selfemployed/fns-se/permission',
        experiment_name='selfemployed_fns_use_salesforce',
        args=[
            {'name': 'is_selfereg', 'type': 'bool', 'value': is_selfereg},
            {'name': 'phone_pd_id', 'type': 'string', 'value': phone_pd_id},
            *conftest.make_pro_app_exp_kwargs('9.30.0'),
        ],
        value={'use_salesforce': use_salesforce},
    )


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, phone, from_park_id, from_driver_id, status,
             request_id, created_at, modified_at)
        VALUES
            ('smz1', 'phone1', 'selfreg', 'sr1', 'requested',
             'req_id1', NOW(), NOW()),
            ('smz2', 'phone2', 'p1', 'd1', 'requested',
             'req_id2', NOW(), NOW()),
            ('smz3', 'phone3', 'selfreg', 'sr2', 'requested',
             'req_id3', NOW(), NOW()),
            ('smz4', 'phone4', 'p2', 'd2', 'requested',
             'req_id4', NOW(), NOW())
        """,
    ],
)
@pytest.mark.parametrize(
    'req_params,create_method',
    [
        ({'selfreg_id': 'sr1'}, 'create_from_selfreg_pc'),
        ({'park': 'p1', 'driver': 'd1'}, 'create_from_park_driver_pc'),
        ({'selfreg_id': 'sr2'}, 'create_from_selfreg_sf'),
        ({'park': 'p2', 'driver': 'd2'}, 'create_from_park_driver_sf'),
    ],
)
@pytest.mark.client_experiments3(
    **_make_test_requested_exp_params(True, '+phone1_PD_ID', False),
)
@pytest.mark.client_experiments3(
    **_make_test_requested_exp_params(False, '+phone2_PD_ID', False),
)
@pytest.mark.client_experiments3(
    **_make_test_requested_exp_params(True, '+phone3_PD_ID', True),
)
@pytest.mark.client_experiments3(
    **_make_test_requested_exp_params(False, '+phone4_PD_ID', True),
)
async def test_requested(
        se_client, patch, mock_personal, req_params, create_method,
):
    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        assert value.startswith('+')
        return {'value': value, 'id': f'{value}_PD_ID'}

    @patch('selfemployed.helpers.fns.check_bind_status')
    async def _check(context, request_id: str):
        return 'COMPLETED', f'{request_id}_inn'

    @patch('selfemployed.helpers.fns.get_fio')
    async def _details(context, inn: str):
        return 'F', 'I', 'O'

    @patch(f'selfemployed.helpers.actions.{create_method}')
    async def _create(context, se_profile):
        return 'account_id'

    response = await se_client.post(
        '/self-employment/fns-se/permission',
        headers=conftest.DEFAULT_HEADERS,
        params=req_params,
        json={'step': 'permission'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {'text': 'push_new_profile'}
    assert len(_create.calls) == 1

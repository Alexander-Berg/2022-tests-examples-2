# pylint: disable=invalid-name,unused-variable

import datetime

import pytest

from selfemployed.fns import client as client_fns
from test_selfemployed import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, status, inn_pd_id)
        VALUES
            ('phone', 'COMPLETED', 'inn_pd_id');
        INSERT INTO se.finished_profiles
            (park_id, contractor_profile_id,
             phone_pd_id, inn_pd_id, is_own_park)
        VALUES
            ('p1', 'c1',
             'phone', 'inn_pd_id', true),
            ('p3', 'c3',
             'phone', 'inn_pd_id', false);
        INSERT INTO se.finished_ownpark_profile_metadata
            (created_park_id, created_contractor_id,
             initial_park_id, initial_contractor_id,
             phone_pd_id, salesforce_account_id, external_id)
        VALUES
            ('p1', 'c1',
             'p0', 'c0',
             'phone', 'sf_acc_id', '123');
        INSERT INTO profiles
            (id, park_id, driver_id, inn, status, from_park_id, from_driver_id,
             created_at,
             modified_at)
        VALUES
            ('id1', 'p2', 'c2', '000000', 'COMPLETED', 'selfreg', '123456',
             to_timestamp('2022-03-30', 'YYYY-MM-DD')::timestamp,
             to_timestamp('2022-03-30', 'YYYY-MM-DD')::timestamp);
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'park_id, contractor_id, fns_error_code, expected_response',
    [
        (
            'p1',
            'c1',
            None,
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v2',
                        'Прямой партнер',
                        'Изначальный профиль: p0_c0',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'Зарегистрирован 2022-03-30 00:00:00+00:00, '
                        'отвязан 2022-03-30 00:00:00+00:00',
                        'Выданные права: [\'1\', \'2\']',
                    ),
                ),
            },
        ),
        (
            'p1',
            'c1',
            'TAXPAYER_UNBOUND',
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v2',
                        'Прямой партнер',
                        'Изначальный профиль: p0_c0',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'СМЗ отвязан',
                    ),
                ),
            },
        ),
        (
            'p1',
            'c1',
            'TAXPAYER_UNREGISTERED',
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v2',
                        'Прямой партнер',
                        'Изначальный профиль: p0_c0',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'Больше не самозанятый',
                    ),
                ),
            },
        ),
        (
            'p2',
            'c2',
            None,
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v1',
                        'Обновлялся 2022-03-30 00:00:00',
                        'Прямой партнер',
                        'Изначальный профиль: selfreg_123456',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'Зарегистрирован 2022-03-30 00:00:00+00:00, '
                        'отвязан 2022-03-30 00:00:00+00:00',
                        'Выданные права: [\'1\', \'2\']',
                    ),
                ),
            },
        ),
        (
            'p2',
            'c2',
            'TAXPAYER_UNBOUND',
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v1',
                        'Обновлялся 2022-03-30 00:00:00',
                        'Прямой партнер',
                        'Изначальный профиль: selfreg_123456',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'СМЗ отвязан',
                    ),
                ),
            },
        ),
        (
            'p2',
            'c2',
            'TAXPAYER_UNREGISTERED',
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v1',
                        'Обновлялся 2022-03-30 00:00:00',
                        'Прямой партнер',
                        'Изначальный профиль: selfreg_123456',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'Больше не самозанятый',
                    ),
                ),
            },
        ),
        (
            'p3',
            'c3',
            None,
            {
                'is_selfemployed': True,
                'status': '\n'.join(
                    (
                        'Профиль СМЗ v2',
                        'Парковый СМЗ',
                        'inn_pd_id: inn_pd_id',
                        'Отправлять чеки: True',
                        'Последний год превышения дохода: None',
                        'Статус привязки COMPLETED',
                        'Зарегистрирован 2022-03-30 00:00:00+00:00, '
                        'отвязан 2022-03-30 00:00:00+00:00',
                        'Выданные права: [\'1\', \'2\']',
                    ),
                ),
            },
        ),
        (
            'non_existent',
            'non_existent',
            None,
            {'is_selfemployed': False, 'status': 'Не самозанятый'},
        ),
    ],
)
async def test_status(
        se_client,
        patch,
        mock_personal,
        park_id,
        contractor_id,
        fns_error_code,
        expected_response,
):
    reg_time = datetime.datetime.fromisoformat('2022-03-30 00:00:00+00:00')
    unreg_time = datetime.datetime.fromisoformat('2022-03-30 00:00:00+00:00')
    permissions = ['1', '2']

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request):
        assert request.json == {'id': 'inn_pd_id', 'primary_replica': False}
        return {'value': '000000', 'id': 'inn_pd_id'}

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request):
        assert request.json == {'value': '000000', 'validate': True}
        return {'value': '000000', 'id': 'inn_pd_id'}

    @patch('selfemployed.fns.client.Client.get_details')
    async def get_details(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.get_registration_details_response')
    async def get_details_response(*args, **kwargs):
        if fns_error_code:
            raise client_fns.SmzPlatformError('Error', fns_error_code)
        return reg_time, unreg_time

    @patch('selfemployed.fns.client.Client.get_permissions')
    async def get_permissions(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.get_permissions_response')
    async def get_permissions_response(*args, **kwargs):
        if fns_error_code:
            raise client_fns.SmzPlatformError('Error', fns_error_code)
        return permissions

    response = await se_client.get(
        '/admin/selfemployed-status',
        params={'park_id': park_id, 'driver_id': contractor_id},
    )

    assert response.status == 200
    content = await response.json()
    assert expected_response == content

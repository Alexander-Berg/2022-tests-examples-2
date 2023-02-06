import pytest

from testsuite.utils import http


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status)
        VALUES ('phone_pd_id1', 'inn_pd_id1', 'COMPLETED'),
            ('phone_pd_id2', 'inn_pd_id2', 'COMPLETED');
        INSERT INTO se.finished_profiles
            (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES
            ('park_id', 'contractor_profile_id1',
             'phone_pd_id1', 'inn_pd_id1'),
            ('park_id', 'contractor_profile_id2',
             'phone_pd_id2', 'inn_pd_id2')
        """,
    ],
)
async def test_ok(se_client, mock_driver_profiles):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['park_id_contractor_profile_id2'],
            'projection': ['data.park_id', 'data.uuid', 'data.full_name'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park_id_contractor_profile_id2',
                    'data': {
                        'park_id': 'park_id',
                        'uuid': 'contractor_profile_id2',
                        'full_name': {
                            'first_name': 'Имя',
                            'last_name': 'Фамилия',
                            'middle_name': 'Отчество',
                        },
                    },
                },
            ],
        }

    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/list-bound-contractors',
        headers={
            'X-Park-ID': 'park_id',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        params={'limit': 1, 'offset': 1},
    )
    assert response.status == 200

    data = await response.json()
    assert data == {
        'contractors': [
            {
                'contractor_profile_id': 'contractor_profile_id2',
                'full_name': 'Фамилия И. О.',
                'nalogru_status': 'COMPLETE',
                'do_send_receipts': True,
            },
        ],
        'limit': 1,
        'offset': 1,
        'total': 2,
    }

import pytest

from testsuite.utils import http


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings (phone_pd_id, inn_pd_id, status)
        VALUES ('PH1', 'INN1', 'COMPLETED');
        INSERT INTO se.finished_profiles
        (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES ('p1', 'c1', 'PH1', 'INN1');
        """,
    ],
)
@pytest.mark.parametrize(
    'park_id, driver_id, expected_status',
    [['p1', 'c1', 200], ['p2', 'c2', 400]],
)
async def test_ok(
        se_client,
        se_web_context,
        patch,
        mock_personal,
        park_id,
        driver_id,
        expected_status,
):
    @mock_personal('/v1/tins/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'INN1', 'primary_replica': False}
        return {'value': '01234567890', 'id': 'INN1'}

    @patch('selfemployed.services.nalogru.Service.bind_by_inn')
    async def _bind_by_inn(inn):
        assert inn == '01234567890'
        return 'request_id'

    response = await se_client.post(
        '/service/rebind/', json={'park_id': park_id, 'driver_id': driver_id},
    )
    assert response.status == expected_status

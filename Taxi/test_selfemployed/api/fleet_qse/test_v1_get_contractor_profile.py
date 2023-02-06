import pytest

from testsuite.utils import http


@pytest.mark.pgsql('selfemployed_main', files=['finished_unbound.sql'])
async def test_complete(se_client, mock_personal):
    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+71234567890', 'id': 'PHONE_PD_ID'}

    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/get-contractor-profile',
        headers={
            'X-Park-ID': 'park_id',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        params={'contractor_profile_id': 'finished_unbound'},
    )
    assert response.status == 200

    data = await response.json()
    assert data == {
        'profile_status': 'COMPLETE',
        'nalogru_status': 'UNBOUND',
        'phone': '+71234567890',
        'do_send_receipts': False,
    }


@pytest.mark.pgsql('selfemployed_main', files=['incomplete.sql'])
async def test_incomplete(se_client, mock_personal):
    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+71234567890', 'id': 'PHONE_PD_ID'}

    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/get-contractor-profile',
        headers={
            'X-Park-ID': 'park_id',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        params={'contractor_profile_id': 'incomplete'},
    )
    assert response.status == 200

    data = await response.json()
    assert data == {
        'profile_status': 'INCOMPLETE',
        'phone': '+71234567890',
        'requested_at': '2021-08-01T00:00:00+03:00',
        'is_accepted': False,
    }


async def test_not_found(se_client):
    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/get-contractor-profile',
        headers={
            'X-Park-ID': 'park_id',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        params={'contractor_profile_id': 'nonexistent'},
    )
    assert response.status == 404

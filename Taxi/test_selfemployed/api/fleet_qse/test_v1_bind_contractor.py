import pytest

from selfemployed.use_cases import park_bind_quasi_se
from test_selfemployed import conftest


@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False)
async def test_ok(se_client, patch):
    @patch('selfemployed.use_cases.park_bind_quasi_se.Component.__call__')
    async def bind(
            park_id: str,
            contractor_profile_id: str,
            phone_raw: str,
            consumer_user_agent: str,
            yandex_uid: str,
            ticket_provider: str,
    ):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert phone_raw == '+7 (012) 345-67-89'
        assert consumer_user_agent == 'YaBro'
        assert yandex_uid == '123'
        assert ticket_provider == 'yandex'
        return

    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/bind-contractor',
        headers={
            'X-Park-ID': 'park_id',
            'User-Agent': 'YaBro',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+7 (012) 345-67-89',
        },
    )

    assert bind.calls
    assert response.status == 200


@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=False)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_unregistered(se_client, patch):
    @patch('selfemployed.use_cases.park_bind_quasi_se.Component.__call__')
    async def bind(
            park_id: str,
            contractor_profile_id: str,
            phone_raw: str,
            consumer_user_agent: str,
            yandex_uid: str,
            ticket_provider: str,
    ):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert phone_raw == '+7 (012) 345-67-89'
        assert consumer_user_agent == 'YaBro'
        assert yandex_uid == '123'
        assert ticket_provider == 'yandex'
        raise park_bind_quasi_se.TaxpayerUnregistered()

    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/bind-contractor',
        headers={
            'X-Park-ID': 'park_id',
            'User-Agent': 'YaBro',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+7 (012) 345-67-89',
        },
    )

    assert bind.calls

    response_data = await response.json()
    assert response_data == {
        'code': 'TAXPAYER_NOT_FOUND',
        'message': 'В ФНС нет налогоплательщика, зарегистрированного по этому телефону',  # noqa: E501
    }
    assert response.status == 409


@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=True)
async def test_additional_terms_accepted(se_client, patch):
    @patch('selfemployed.use_cases.park_bind_quasi_se.Component.__call__')
    async def bind(
            park_id: str,
            contractor_profile_id: str,
            phone_raw: str,
            consumer_user_agent: str,
            yandex_uid: str,
            ticket_provider: str,
    ):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert phone_raw == '+7 (012) 345-67-89'
        assert consumer_user_agent == 'YaBro'
        assert yandex_uid == '123'
        assert ticket_provider == 'yandex'
        return

    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/bind-contractor',
        headers={
            'X-Park-ID': 'park_id',
            'User-Agent': 'YaBro',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+7 (012) 345-67-89',
        },
    )

    assert bind.calls
    assert response.status == 200


@pytest.mark.now('2021-12-22T15:17:34+03:00')
@pytest.mark.config(SELFEMPLOYED_PARKS_ADDITIONAL_TERMS_ENABLED=True)
async def test_additional_terms_not_accepted(se_client, patch):
    @patch('selfemployed.use_cases.park_bind_quasi_se.Component.__call__')
    async def bind(
            park_id: str,
            contractor_profile_id: str,
            phone_raw: str,
            consumer_user_agent: str,
            yandex_uid: str,
            ticket_provider: str,
    ):
        assert park_id == 'park_id'
        assert contractor_profile_id == 'contractor_profile_id'
        assert phone_raw == '+7 (012) 345-67-89'
        assert consumer_user_agent == 'YaBro'
        assert yandex_uid == '1234'
        assert ticket_provider == 'yandex'
        raise park_bind_quasi_se.AdditionalTermsNotAccepted()

    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/bind-contractor',
        headers={
            'X-Park-ID': 'park_id',
            'User-Agent': 'YaBro',
            'X-Yandex-UID': '1234',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+7 (012) 345-67-89',
        },
    )

    assert bind.calls

    response_data = await response.json()
    assert response_data == {
        'code': 'ADDITIONAL_TERMS_NOT_ACCEPTED',
        'message': 'Required to accept additional terms of service',
    }
    assert response.status == 409

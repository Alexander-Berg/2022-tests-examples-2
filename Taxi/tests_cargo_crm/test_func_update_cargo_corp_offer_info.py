import pytest

from tests_cargo_crm import const

CORP_CLIENT_ID = 'corporate_client_identifier_test'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
INFO_TAG = 'offer_info_form'
SYSTEM_REQUEST_MODE = 'system'
MANAGER_REQ_PARAMS = {'ticket_id': const.TICKET_ID, 'flow': 'phoenix'}


@pytest.fixture(name='offer_forms')
def _load_offer_forms(load_json):
    return load_json('offer_forms.json')


@pytest.mark.parametrize(
    'country, cargo_corp_code, expected_code',
    (('rus', 200, 200), ('isr', 200, 200), ('rus', 500, 500)),
)
async def test_func_create_cargo_corp_employee(
        taxi_cargo_crm,
        offer_forms,
        mockserver,
        country,
        cargo_corp_code,
        expected_code,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/offer/upsert',
    )
    def _handler(request):
        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.headers['X-Request-Mode'] == SYSTEM_REQUEST_MODE
        assert request.json == {
            'extra_info': offer_forms[country],
            'extra_info_tag': INFO_TAG,
        }

        return mockserver.make_response(status=cargo_corp_code, json={})

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'offer_info_form': offer_forms[country],
    }

    response = await taxi_cargo_crm.post(
        '/functions/by-flow/update-cargo-corp-offer-info',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert response.status_code == expected_code

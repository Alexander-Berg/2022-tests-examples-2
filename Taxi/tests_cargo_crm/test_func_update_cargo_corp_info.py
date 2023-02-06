import pytest


CORP_CLIENT_ID = 'some_long_id_string_of_length_32'
COMPANY = {
    'name': 'test_company_name_edited',
    'country': 'Russia',
    'segment': 'Аптеки',
    'city': 'Moscow',
    'email': '',
    'website': 'service.ru',
}
COMPANY_PD = {'email_pd_id': 'test_id'}
MOCK_NOW = '2021-05-31T19:00:00+00:00'


@pytest.mark.parametrize(
    (
        'corp_client_id',
        'has_company_info_pd_email',
        'has_company_info_email',
        'expected_code',
        'edit_response_code',
    ),
    (
        pytest.param(CORP_CLIENT_ID, True, False, 200, 200, id='ok'),
        pytest.param(
            CORP_CLIENT_ID[::-1],
            True,
            False,
            500,
            200,
            id='bad-corp_client_id-1',
        ),
        pytest.param(
            CORP_CLIENT_ID, True, False, 500, 404, id='bad-corp_client_id-2',
        ),
        pytest.param(CORP_CLIENT_ID, True, False, 500, 409, id='bad-revision'),
        pytest.param(
            CORP_CLIENT_ID, False, False, 200, 200, id='no_email_pd_id',
        ),
        pytest.param(
            CORP_CLIENT_ID,
            False,
            True,
            200,
            200,
            id='no_email_pd_id_but_email_filled',
        ),
    ),
)
async def test_func_update_cargo_corp(
        taxi_cargo_crm,
        mockserver,
        personal_ctx,
        personal_handler_bulk_retrieve,
        corp_client_id,
        has_company_info_pd_email,
        has_company_info_email,
        expected_code,
        edit_response_code,
):
    @mockserver.json_handler('/cargo-corp/internal/cargo-corp/v1/client/info')
    def _info_handler(request):
        if request.headers['X-B2B-Client-Id'] != CORP_CLIENT_ID:
            return mockserver.make_response(
                status=404,
                json={'code': 'not_found', 'message': 'Unknown corp_client'},
            )
        return mockserver.make_response(
            status=200,
            json={
                'corp_client_id': request.headers['X-B2B-Client-Id'],
                'revision': 1,
                'company': {'name': 'test_company_name'},
                'created_ts': MOCK_NOW,
                'updated_ts': MOCK_NOW,
            },
        )

    @mockserver.json_handler('/cargo-corp/internal/cargo-corp/v1/client/edit')
    def _edit_handler(request):
        expected = {
            'name': COMPANY['name'],
            'url': COMPANY['website'],
            'city': COMPANY['city'],
            'country': COMPANY['country'],
            'segment': COMPANY['segment'],
        }
        if has_company_info_pd_email:
            expected['emails'] = [{'text': 'test@service.ru'}]
        assert request.json['company'] == expected
        assert request.json['revision'] == 1

        if edit_response_code == 200:
            response_json = {
                'corp_client_id': request.headers['X-B2B-Client-Id'],
                'revision': request.json['revision'],
                'company': request.json['company'],
                'created_ts': MOCK_NOW,
                'updated_ts': MOCK_NOW,
            }
        elif edit_response_code == 404:
            response_json = {
                'code': 'not_found',
                'message': 'Unknown corp_client',
            }
        else:
            response_json = {
                'code': 'not_actual_revision',
                'message': 'Your revision is not actual',
            }

        return mockserver.make_response(
            status=edit_response_code, json=response_json,
        )

    personal_ctx.set_emails([{'id': 'test_id', 'value': 'test@service.ru'}])

    request = {
        'corp_client_id': corp_client_id,
        'yandex_uid': 'yandex_uid',
        'company_info_form': COMPANY,
    }
    if has_company_info_email:
        company_copy = COMPANY.copy()
        company_copy.update({'email': 'test@service.ru'})
        request['company_info_form'] = company_copy
    if has_company_info_pd_email:
        request['company_info_pd_form'] = COMPANY_PD
    else:
        request['company_info_pd_form'] = {}

    response = await taxi_cargo_crm.post(
        '/functions/update-cargo-corp-info', json=request,
    )
    assert response.status_code == expected_code

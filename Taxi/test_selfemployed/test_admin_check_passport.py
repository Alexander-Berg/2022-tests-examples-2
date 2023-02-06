import pytest

from selfemployed.fns import client as client_fns
from test_selfemployed import conftest


CORRECT_DATA = {
    'first_name': 'Ivan',
    'last_name': 'Ivanov',
    'middle_name': 'Ivanovich',
    'birthday': '1999-12-31',
    'passport_series': '1234',
    'passport_number': '123456',
}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'inns, fns_error_code, expected_status, expected_response',
    [
        (['1234'], None, 200, {'message': 'Паспорт действителен'}),
        (
            [],
            'TAXPAYER_NOT_FOUND',
            404,
            {'text': 'Паспорт недействителен', 'code': 'TAXPAYER_NOT_FOUND'},
        ),
        (
            None,
            'INTERNAL_ERROR',
            404,
            {'text': 'Some FNS Error', 'code': 'INTERNAL_ERROR'},
        ),
    ],
)
async def test_check_passport(
        se_client,
        patch,
        inns,
        fns_error_code,
        expected_status,
        expected_response,
):
    @patch('selfemployed.fns.client.Client.get_inn_by_personal_info')
    async def get_inn_by_personal_info(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.get_inn_by_personal_info_response')
    async def get_response(*args, **kwargs):
        if inns is None:
            raise client_fns.SmzPlatformError('Some FNS Error', fns_error_code)
        elif not inns:
            raise client_fns.TaxpayerNotFoundError('Not Found', fns_error_code)
        else:
            return inns

    response = await se_client.post(
        '/admin/selfemployed-check-passport', json=CORRECT_DATA,
    )

    assert len(get_inn_by_personal_info.calls) == 1
    assert len(get_response.calls) == 1

    assert response.status == expected_status
    content = await response.json()
    assert expected_response == content

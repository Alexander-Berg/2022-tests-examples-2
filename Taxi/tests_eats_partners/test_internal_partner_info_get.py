import pytest


@pytest.mark.pgsql(
    'eats_partners', files=['insert_partner_data_with_personal.sql'],
)
@pytest.mark.parametrize(
    'response_code,partner_id,response_json,with_blocked,' 'resolve_personal',
    [
        (200, 1, 'response_1.json', False, True),
        (404, 2, 'response_2_not_found.json', False, True),
        (404, 3, 'response_3.json', False, True),
        (200, 1, 'response_1.json', True, True),
        (200, 2, 'response_2.json', True, True),
        (404, 3, 'response_3.json', True, True),
        (200, 1, 'response_4.json', True, False),
    ],
)
async def test_internal_partners_info_with_retrieve(
        taxi_eats_partners,
        mockserver,
        response_code,
        partner_id,
        response_json,
        with_blocked,
        load_json,
        pgsql,
        mock_personal_retrieve,
        resolve_personal,
):
    response = await taxi_eats_partners.get(
        '/internal/partners/v1/info?partner_id={}'
        '&with_blocked={}'
        '&resolve_personal={}'.format(
            partner_id, with_blocked, resolve_personal,
        ),
    )

    assert response.status_code == response_code
    assert response.json() == load_json(response_json)

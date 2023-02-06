# flake8: noqa
import pytest


@pytest.mark.pgsql('eats_restapp_authorizer', files=('data_creds.sql',))
@pytest.mark.parametrize(
    'ids, logins, expected_response',
    [
        pytest.param([], [], {'partners': []}, id='empty_params'),
        pytest.param(None, None, {'partners': []}, id='empty_params_none'),
        pytest.param(None, [], {'partners': []}, id='empty_params_none_ids'),
        pytest.param(
            [], None, {'partners': []}, id='empty_params_none_logins',
        ),
        pytest.param(
            [111, 222, 333, 444], [], {'partners': []}, id='not_exist_ids',
        ),
        pytest.param(
            [],
            ['aaaa', 'bbbb', 'cccc'],
            {'partners': []},
            id='not_exist_logins',
        ),
        pytest.param(
            [111, 222, 333, 444],
            ['aaaa', 'bbbb', 'cccc'],
            {'partners': []},
            id='not_exist_ids_and_logins',
        ),
        pytest.param(
            [1],
            [],
            {'partners': [{'partner_id': 1, 'login': 'nananuna'}]},
            id='one_id',
        ),
        pytest.param(
            [],
            ['nananuna'],
            {'partners': [{'partner_id': 1, 'login': 'nananuna'}]},
            id='one_login',
        ),
        pytest.param(
            [1, 2, 50],
            [],
            {
                'partners': [
                    {'partner_id': 1, 'login': 'nananuna'},
                    {'partner_id': 2, 'login': 'nananuna_2'},
                    {'partner_id': 50, 'login': 'nananuna_5'},
                ],
            },
            id='get by ids',
        ),
        pytest.param(
            [],
            ['nananuna', 'nananuna_3', 'nananuna_4'],
            {
                'partners': [
                    {'partner_id': 1, 'login': 'nananuna'},
                    {'partner_id': 3, 'login': 'nananuna_3'},
                    {'partner_id': 40, 'login': 'nananuna_4'},
                ],
            },
            id='get by logins',
        ),
        pytest.param(
            [1, 2, 50],
            ['nananuna', 'nananuna_3', 'nananuna_4'],
            {
                'partners': [
                    {'partner_id': 1, 'login': 'nananuna'},
                    {'partner_id': 2, 'login': 'nananuna_2'},
                    {'partner_id': 3, 'login': 'nananuna_3'},
                    {'partner_id': 40, 'login': 'nananuna_4'},
                    {'partner_id': 50, 'login': 'nananuna_5'},
                ],
            },
            id='get by all',
        ),
        pytest.param(
            [1, 2, 333, 444],
            ['nananuna', 'nananuna_555', 'nananuna_5'],
            {
                'partners': [
                    {'partner_id': 1, 'login': 'nananuna'},
                    {'partner_id': 2, 'login': 'nananuna_2'},
                    {'partner_id': 50, 'login': 'nananuna_5'},
                ],
            },
            id='get_diff_data',
        ),
    ],
)
async def test_search_credentials_partner(
        taxi_eats_restapp_authorizer, pgsql, ids, logins, expected_response,
):
    request = {}
    if logins is not None:
        request['logins'] = logins
    if ids is not None:
        request['partner_ids'] = ids
    response = await taxi_eats_restapp_authorizer.post(
        '/internal/partner/search', json=request,
    )

    assert response.status_code == 200
    assert response.json() == expected_response

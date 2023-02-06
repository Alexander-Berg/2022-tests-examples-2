import pytest

from generated.clients import candidates
from generated.models import candidates as models


@pytest.mark.parametrize(
    'request_body, response_status, actual_result, expected_result',
    [
        (
            {
                'filtration': 'searchable',
                'point': [37.50746960043908, 55.95927626239531],
                'destination': [37.6113510131836, 55.75492739141213],
                'order': {'calc': {'alternative_type': 'combo_inner'}},
                'combo': {'need_inactive': True},
                'data_keys': [],
            },
            200,
            candidates.ListProfilesPost200(
                models.Profiles.deserialize(
                    {
                        'drivers': [
                            {
                                'position': [37.554078, 55.90902],
                                'id': (
                                    'a3608f8f7ee84e0b9c21862beef7e48d_'
                                    'f5332506408a4defbbe16d013a17d24b'
                                ),
                                'dbid': 'a3608f8f7ee84e0b9c21862beef7e48d',
                                'uuid': 'f5332506408a4defbbe16d013a17d24b',
                            },
                            {
                                'position': [37.448634, 55.879285],
                                'id': (
                                    '7f74df331eb04ad78bc2ff25ff88a8f2_'
                                    '9edd10b91d984ab0b37af89cdb33abae'
                                ),
                                'dbid': '7f74df331eb04ad78bc2ff25ff88a8f2',
                                'uuid': '9edd10b91d984ab0b37af89cdb33abae',
                            },
                        ],
                    },
                ),
            ),
            {
                'drivers': [
                    {
                        'position': [37.554078, 55.90902],
                        'id': (
                            'a3608f8f7ee84e0b9c21862beef7e48d_'
                            'f5332506408a4defbbe16d013a17d24b'
                        ),
                        'dbid': 'a3608f8f7ee84e0b9c21862beef7e48d',
                        'uuid': 'f5332506408a4defbbe16d013a17d24b',
                    },
                    {
                        'position': [37.448634, 55.879285],
                        'id': (
                            '7f74df331eb04ad78bc2ff25ff88a8f2_'
                            '9edd10b91d984ab0b37af89cdb33abae'
                        ),
                        'dbid': '7f74df331eb04ad78bc2ff25ff88a8f2',
                        'uuid': '9edd10b91d984ab0b37af89cdb33abae',
                    },
                ],
            },
        ),
        (
            {
                'filtration': 'searchable',
                'point': [375.6113510131836, 55.75492739141213],
                'destination': [37.50746960043908, 555.95927626239531],
                'order': {'calc': {'alternative_type': 'combo_inner'}},
                'combo': {'need_inactive': True},
                'data_keys': [],
            },
            400,
            candidates.ListProfilesPost404(
                models.Error.deserialize(
                    {'code': '404', 'message': 'Not Found'},
                ),
            ),
            {
                'code': 'BadRequest::Candidates',
                'message': 'Invalid request parameters',
            },
        ),
    ],
)
async def test_get_combo_drivers(
        web_app_client,
        atlas_blackbox_mock,
        patch,
        request_body,
        response_status,
        actual_result,
        expected_result,
):
    # pylint: disable=unused-variable
    @patch('generated.clients.candidates.CandidatesClient.list_profiles_post')
    async def list_profiles_post(
            *args, **kwargs,
    ) -> candidates.ListProfilesPost200:
        nonlocal response_status

        if response_status == 200:
            return actual_result

        raise actual_result

    response = await web_app_client.post('/api/v1/drivers', json=request_body)
    assert response.status == response_status
    content = await response.json()
    assert content == expected_result
